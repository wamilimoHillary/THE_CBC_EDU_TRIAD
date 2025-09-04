from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime
import os
from app.database import get_db_connection

teacher_routes = Blueprint('teacher', __name__)

def teacher_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.teacher_login'))
        return f(*args, **kwargs)
    return decorated_function

# ======================
# ROUTES
# ======================
@teacher_routes.route('/teachers_dashboard')
@teacher_login_required
def teachers_dashboard():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get class count
        cursor.execute("""
            SELECT COUNT(*) FROM classes 
            WHERE teacherid = %s
        """, (session['teacher_id'],))
        class_count = cursor.fetchone()[0]
        
        return render_template('teacher/teachers_dashboard.html',
                            class_count=class_count,
                            current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('teacher.teachers_dashboard'))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@teacher_routes.route('/view_classes')
@teacher_login_required
def view_classes():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all classes with student counts
        cursor.execute("""
            SELECT c.classid, c.classname, 
                   COUNT(cs.studentid) as student_count
            FROM classes c
            LEFT JOIN class_students cs ON c.classid = cs.classid
            WHERE c.teacherid = %s
            GROUP BY c.classid
            ORDER BY c.classname
        """, (session['teacher_id'],))
        classes = cursor.fetchall()
        
        return render_template('teacher/view_classes.html',
                            classes=classes,
                            current_date=datetime.now().strftime('%B %d, %Y'))
    
    except Exception as e:
        flash(f'Error loading classes: {str(e)}', 'danger')
        return redirect(url_for('teacher.teachers_dashboard'))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@teacher_routes.route('/class/<int:class_id>')
@teacher_login_required
def class_details(class_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify teacher owns this class
        cursor.execute("""
            SELECT 1 FROM classes 
            WHERE classid = %s AND teacherid = %s
        """, (class_id, session['teacher_id']))
        if not cursor.fetchone():
            flash('You do not have access to this class', 'danger')
            return redirect(url_for('teacher.view_classes'))
        
        # Get class details
        cursor.execute("""
            SELECT c.classname, c.academicyear,
                   COUNT(cs.studentid) as student_count
            FROM classes c
            LEFT JOIN class_students cs ON c.classid = cs.classid
            WHERE c.classid = %s
            GROUP BY c.classid
        """, (class_id,))
        class_info = cursor.fetchone()
        
        # Get students in class
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname
            FROM students s
            JOIN users u ON s.userid = u.userid
            JOIN class_students cs ON s.studentid = cs.studentid
            WHERE cs.classid = %s
            ORDER BY u.lastname, u.firstname
        """, (class_id,))
        students = cursor.fetchall()
        
        return render_template('teacher/class_details.html',
                            class_info=class_info,
                            students=students,
                            class_id=class_id)
    
    except Exception as e:
        flash(f'Error loading class: {str(e)}', 'danger')
        return redirect(url_for('teacher.view_classes'))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@teacher_routes.route('/logout')
@teacher_login_required
def teacher_logout():
    """Logout teacher"""
    session.pop('teacher_id', None)
    session.pop('teacher_name', None)
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.teacher_login'))


@teacher_routes.route('/create_task', methods=['GET', 'POST'])
@teacher_login_required
def create_task():
    if 'teacher_id' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('auth.teacher_login'))

    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get dropdown options filtered by this teacher
        cursor.execute("SELECT competencyid, competencyname FROM competencies")
        competencies = cursor.fetchall()
        
        cursor.execute("SELECT classid, classname FROM classes WHERE teacherid = %s", 
                      (session['teacher_id'],))
        classes = cursor.fetchall()
        
        cursor.execute("""
            SELECT sg.groupid, sg.groupname 
            FROM studentgroups sg
            JOIN groupmembers gm ON sg.groupid = gm.groupid
            JOIN class_students cs ON gm.studentid = cs.studentid
            JOIN classes c ON cs.classid = c.classid
            WHERE c.teacherid = %s
            GROUP BY sg.groupid
        """, (session['teacher_id'],))
        groups = cursor.fetchall()
        
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname 
            FROM students s
            JOIN users u ON s.userid = u.userid
            JOIN class_students cs ON s.studentid = cs.studentid
            JOIN classes c ON cs.classid = c.classid
            WHERE c.teacherid = %s
        """, (session['teacher_id'],))
        students = cursor.fetchall()

        if request.method == 'POST':
            # Get form data
            title = request.form['title'].strip()
            description = request.form['description'].strip()
            due_date = request.form['due_date']
            competency_id = request.form.get('competency_id', None)
            
            # Validate required fields
            if not all([title, description, due_date]):
                flash('All required fields must be filled', 'danger')
                return render_template('teacher/create_task.html',
                                    competencies=competencies,
                                    classes=classes,
                                    groups=groups,
                                    students=students,
                                    form_data=request.form)

            # Validate due date is in the future
            try:
                from datetime import datetime
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                today = datetime.now().date()
                if due_date_obj <= today:
                    flash('Due date must be in the future', 'danger')
                    return render_template('teacher/create_task.html',
                                        competencies=competencies,
                                        classes=classes,
                                        groups=groups,
                                        students=students,
                                        form_data=request.form)
            except ValueError:
                flash('Invalid date format', 'danger')
                return render_template('teacher/create_task.html',
                                    competencies=competencies,
                                    classes=classes,
                                    groups=groups,
                                    students=students,
                                    form_data=request.form)

            # Validate at least one assignment target
            student_id = request.form.get('student_id', None)
            class_id = request.form.get('class_id', None)
            group_id = request.form.get('group_id', None)
            
            if not any([student_id, class_id, group_id]):
                flash('Please select at least one assignment target', 'danger')
                return render_template('teacher/create_task.html',
                                    competencies=competencies,
                                    classes=classes,
                                    groups=groups,
                                    students=students,
                                    form_data=request.form)

            # Create the task
            cursor.execute("""
                INSERT INTO tasks (teacherid, title, taskdescription, duedate, createdat)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING taskid
            """, (session['teacher_id'], title, description, due_date))
            task_id = cursor.fetchone()[0]
            
            # Link competency if selected
            if competency_id:
                cursor.execute("""
                    INSERT INTO task_competencies (taskid, competencyid)
                    VALUES (%s, %s)
                """, (task_id, competency_id))
            
            # MODIFIED: Handle assignment based on selected option
            if student_id:
                # Individual student assignment
                cursor.execute("""
                    INSERT INTO taskassignments (taskid, studentid)
                    VALUES (%s, %s)
                """, (task_id, student_id))
            elif class_id:
                # Class assignment - record classid
                cursor.execute("""
                    INSERT INTO taskassignments (taskid, classid)
                    VALUES (%s, %s)
                """, (task_id, class_id))
                
                # Also assign to all students in class
                cursor.execute("""
                    INSERT INTO taskassignments (taskid, studentid)
                    SELECT %s, studentid FROM class_students 
                    WHERE classid = %s
                """, (task_id, class_id))
            elif group_id:
                # Group assignment - record groupid
                cursor.execute("""
                    INSERT INTO taskassignments (taskid, groupid)
                    VALUES (%s, %s)
                """, (task_id, group_id))
                
                # Also assign to all students in group
                cursor.execute("""
                    INSERT INTO taskassignments (taskid, studentid)
                    SELECT %s, studentid FROM groupmembers 
                    WHERE groupid = %s
                """, (task_id, group_id))
            
            conn.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('teacher.manage_tasks'))
            
    except Exception as e:
        if conn:
            conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    # Show the form with dropdown options
    return render_template('teacher/create_task.html',
                         competencies=competencies,
                         classes=classes,
                         groups=groups,
                         students=students)

@teacher_routes.route('/manage_tasks')
@teacher_login_required
def manage_tasks():
    if 'teacher_id' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('auth.teacher_login'))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Updated query with correct submission check
        cursor.execute("""
            SELECT 
                t.taskid, 
                t.title, 
                t.taskdescription, 
                t.duedate, 
                t.createdat,
                COUNT(DISTINCT ta.assignmentid) as assignment_count,
                COUNT(DISTINCT p.projectid) as submission_count,
                CASE 
                    WHEN t.duedate < CURRENT_DATE THEN 'Overdue'
                    ELSE 'Pending'
                END as status,
                STRING_AGG(DISTINCT c.competencyname, ', ') as competencies
            FROM tasks t
            LEFT JOIN taskassignments ta ON t.taskid = ta.taskid
            LEFT JOIN projects p ON t.taskid = p.taskid AND p.submission_time IS NOT NULL
            LEFT JOIN task_competencies tc ON t.taskid = tc.taskid
            LEFT JOIN competencies c ON tc.competencyid = c.competencyid
            WHERE t.teacherid = %s
            GROUP BY t.taskid
            ORDER BY 
                CASE WHEN t.duedate < CURRENT_DATE THEN 0 ELSE 1 END,
                t.duedate ASC
        """, (session['teacher_id'],))

        tasks = cursor.fetchall()
        return render_template('teacher/manage_tasks.html', tasks=tasks)

    except Exception as e:
        flash(f'Error loading tasks: {str(e)}', 'danger')
        return redirect(url_for('teacher.teachers_dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@teacher_routes.route('/task/<int:task_id>')
@teacher_login_required
def view_task(task_id):
    # View task details and submissions
    pass

@teacher_routes.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@teacher_login_required
def edit_task(task_id):
    # Edit an existing task
    pass

@teacher_routes.route('/task/<int:task_id>/delete', methods=['POST'])
@teacher_login_required
def delete_task(task_id):
    # Delete a task
    pass


@teacher_routes.route('/groups', methods=['GET', 'POST'])
@teacher_login_required
def manage_groups():
    if 'teacher_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('auth.teacher_login'))

    conn = get_db_connection()
    try:
        if request.method == 'POST':
            # Handle group creation
            group_name = request.form.get('group_name', '').strip()
            student_ids = request.form.getlist('student_ids')

            if not group_name:
                flash('Group name cannot be empty', 'danger')
            elif not student_ids:
                flash('Select at least one student', 'danger')
            else:
                with conn.cursor() as cursor:
                    # Check for existing group name
                    cursor.execute("""
                        SELECT groupid FROM studentgroups 
                        WHERE teacherid = %s AND groupname = %s
                    """, (session['teacher_id'], group_name))
                    if cursor.fetchone():
                        flash('Group name already exists', 'danger')
                    else:
                        # Create group
                        cursor.execute("""
                            INSERT INTO studentgroups (groupname, teacherid)
                            VALUES (%s, %s) RETURNING groupid
                        """, (group_name, session['teacher_id']))
                        group_id = cursor.fetchone()[0]

                        # Add members
                        for student_id in student_ids:
                            cursor.execute("""
                                INSERT INTO groupmembers (groupid, studentid)
                                VALUES (%s, %s)
                            """, (group_id, student_id))
                        
                        conn.commit()
                        flash(f'Group "{group_name}" created successfully!', 'success')
                        return redirect(url_for('teacher.manage_groups'))

        # Get existing groups and eligible students
        with conn.cursor() as cursor:
            # Teacher's groups
            cursor.execute("""
                SELECT sg.groupid, sg.groupname, 
                       COUNT(gm.studentid) AS member_count
                FROM studentgroups sg
                LEFT JOIN groupmembers gm ON sg.groupid = gm.groupid
                WHERE sg.teacherid = %s
                GROUP BY sg.groupid
                ORDER BY sg.groupname
            """, (session['teacher_id'],))
            groups = cursor.fetchall()

            # Teacher's students
            cursor.execute("""
                SELECT s.studentid, u.firstname, u.lastname
                FROM students s
                JOIN users u ON s.userid = u.userid
                JOIN class_students cs ON s.studentid = cs.studentid
                JOIN classes c ON cs.classid = c.classid
                WHERE c.teacherid = %s
                ORDER BY u.lastname, u.firstname
            """, (session['teacher_id'],))
            students = cursor.fetchall()

        return render_template('teacher/manage_groups.html', 
                            groups=groups,
                            students=students)

    except Exception as e:
        conn.rollback()
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('teacher.manage_groups'))
    finally:
        conn.close()

@teacher_routes.route('/groups/<int:group_id>')
@teacher_login_required
def view_group(group_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verify ownership
            cursor.execute("""
                SELECT groupname FROM studentgroups
                WHERE groupid = %s AND teacherid = %s
            """, (group_id, session['teacher_id']))
            group = cursor.fetchone()
            
            if not group:
                flash('Group not found', 'danger')
                return redirect(url_for('teacher.manage_groups'))

            # Get members
            cursor.execute("""
                SELECT s.studentid, u.firstname, u.lastname
                FROM groupmembers gm
                JOIN students s ON gm.studentid = s.studentid
                JOIN users u ON s.userid = u.userid
                WHERE gm.groupid = %s
                ORDER BY u.lastname
            """, (group_id,))
            members = cursor.fetchall()

        return render_template('teacher/view_group.html',
                            group_name=group[0],
                            members=members)

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('teacher.manage_groups'))
    finally:
        conn.close()


# ======================
# TEACHER ASSESSMENT ROUTES
# ======================

@teacher_routes.route('/submissions')
@teacher_login_required
def view_submissions():
    """View submissions with assessment status tracking"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        teacher_id = session['teacher_id']
        
        cursor.execute("""
            SELECT 
                p.projectid,
                t.title as task_title,
                p.submission_time,
                CASE
                    WHEN p.groupid IS NULL THEN u.firstname || ' ' || u.lastname
                    ELSE (
                        SELECT u2.firstname || ' ' || u2.lastname 
                        FROM students s2
                        JOIN users u2 ON s2.userid = u2.userid
                        WHERE s2.studentid = p.submitter_id
                    )
                END as submitter_name,
                p.is_late,
                t.taskid,
                CASE
                    WHEN p.groupid IS NOT NULL THEN (
                        SELECT c.classname 
                        FROM class_students cs
                        JOIN classes c ON cs.classid = c.classid
                        WHERE cs.studentid IN (
                            SELECT studentid FROM groupmembers WHERE groupid = p.groupid
                        )
                        LIMIT 1
                    )
                    ELSE (
                        SELECT c.classname 
                        FROM class_students cs
                        JOIN classes c ON cs.classid = c.classid
                        WHERE cs.studentid = p.submitter_id
                    )
                END as class_context,
                p.groupid,
                CASE 
                    WHEN p.groupid IS NOT NULL THEN sg.groupname
                    ELSE NULL
                END as group_name,
                p.is_assessed,
                p.assessment_time,
                p.file_name,
                EXISTS (
                    SELECT 1 FROM competency_assessments ca
                    WHERE ca.task_id = t.taskid
                    AND ca.student_id = p.submitter_id
                ) as has_assessment
            FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            LEFT JOIN students s ON p.submitter_id = s.studentid
            LEFT JOIN users u ON s.userid = u.userid
            LEFT JOIN studentgroups sg ON p.groupid = sg.groupid
            WHERE t.teacherid = %s
            AND p.submission_time IS NOT NULL
            ORDER BY p.submission_time DESC
        """, (teacher_id,))
        
        submissions = cursor.fetchall()
        return render_template('teacher/view_submissions.html',
                           submissions=submissions)
    
    except Exception as e:
        flash(f"Error loading submissions: {str(e)}", "danger")
        return redirect(url_for('teacher.teachers_dashboard'))
    finally:
        conn.close()




# ======================      
#ASSESSMENT 
# ======================

@teacher_routes.route('/assess/<int:project_id>', methods=['GET', 'POST'])
@teacher_login_required
def assess_submission(project_id):
    """Complete assessment route with file download and session fixes"""
    conn = None
    cursor = None
    try:
        # Validate session outside transaction
        if 'teacher_id' not in session:
            flash("Please login to access this page", "danger")
            return redirect(url_for('auth.teacher_login'))
        
        teacher_id = session['teacher_id']
        conn = get_db_connection()
        cursor = conn.cursor()

        # First check if already assessed
        cursor.execute("""
            SELECT p.is_assessed FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            WHERE p.projectid = %s AND t.teacherid = %s
        """, (project_id, teacher_id))
        assessment_status = cursor.fetchone()
        
        if assessment_status and assessment_status[0]:
            flash("This submission has already been assessed", "info")
            return redirect(url_for('teacher.view_submissions'))

        # Get submission details (as tuple)
        cursor.execute("""
            SELECT 
                p.projectid, t.taskid, t.title, 
                p.submission_time, p.is_late,
                u.firstname || ' ' || u.lastname as submitter_name,
                c.competencyid, c.competencyname,
                p.groupid, sg.groupname,
                p.submitter_id, p.projectfilepath,
                p.file_name, p.is_assessed
            FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            JOIN task_competencies tc ON t.taskid = tc.taskid
            JOIN competencies c ON tc.competencyid = c.competencyid
            JOIN students s ON p.submitter_id = s.studentid
            JOIN users u ON s.userid = u.userid
            LEFT JOIN studentgroups sg ON p.groupid = sg.groupid
            WHERE p.projectid = %s AND t.teacherid = %s
        """, (project_id, teacher_id))
        submission = cursor.fetchone()

        if not submission:
            flash("Submission not found or you don't have permission", "danger")
            return redirect(url_for('teacher.view_submissions'))

        # Get students to assess (as list of tuples)
        students_to_assess = []
        if submission[8]:  # Group project (groupid at index 8)
            cursor.execute("""
                SELECT s.studentid, u.firstname || ' ' || u.lastname as student_name
                FROM groupmembers gm
                JOIN students s ON gm.studentid = s.studentid
                JOIN users u ON s.userid = u.userid
                WHERE gm.groupid = %s
                ORDER BY student_name
            """, (submission[8],))
            students_to_assess = cursor.fetchall()
        else:  # Individual project
            cursor.execute("""
                SELECT s.studentid, u.firstname || ' ' || u.lastname as student_name
                FROM students s
                JOIN users u ON s.userid = u.userid
                WHERE s.studentid = %s
            """, (submission[10],))  # submitter_id at index 10
            students_to_assess = cursor.fetchall()

        if not students_to_assess:
            flash("No students found for assessment", "warning")
            return redirect(url_for('teacher.view_submissions'))

        # Get assessment criteria (as list of tuples)
        cursor.execute("""
            SELECT criteriaid, criterianame, criteriadescription
            FROM criteria
            WHERE competencyid = %s
            ORDER BY criteriaid
        """, (submission[6],))  # competencyid at index 6
        criteria_list = cursor.fetchall()

        if not criteria_list:
            flash("No assessment criteria configured for this competency", "danger")
            return redirect(url_for('teacher.view_submissions'))

        # Get ALL performance levels (as list of tuples)
        cursor.execute("""
            SELECT 
                performancelevelid, 
                levelname, 
                scorevalue, 
                leveldescription
            FROM performance
            ORDER BY scorevalue DESC
        """)
        performance_levels = cursor.fetchall()

        if not performance_levels:
            flash("No performance levels configured in the system", "danger")
            return redirect(url_for('teacher.view_submissions'))

        # Handle form submission
        if request.method == 'POST':
            try:
                # Commit any pending transaction before starting new one
                if conn:
                    conn.commit()

                student_id = int(request.form.get('student_id', 0))
                if not any(student[0] == student_id for student in students_to_assess):
                    raise ValueError("Invalid student selected")

                # Validate at least one criteria is selected
                if not any(request.form.get(f'criteria_{criteria[0]}') for criteria in criteria_list):
                    raise ValueError("Please select at least one performance level")

                # Begin new transaction
                conn.autocommit = False

                # Create/update assessment
                cursor.execute("""
                    INSERT INTO competency_assessments (
                        student_id, task_id, competency_id, 
                        overall_score, feedback, assessed_at
                    ) VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (student_id, task_id, competency_id) 
                    DO UPDATE SET
                        overall_score = EXCLUDED.overall_score,
                        feedback = EXCLUDED.feedback,
                        assessed_at = NOW()
                    RETURNING assessment_id
                """, (
                    student_id,
                    submission[1],  # taskid
                    submission[6],  # competencyid
                    None,  # Temporary null
                    request.form.get('general_feedback', '').strip()
                ))
                assessment_id = cursor.fetchone()[0]

                # Process criteria assessments
                total_score = 0
                criteria_count = 0
                for criteria in criteria_list:
                    level_id = request.form.get(f'criteria_{criteria[0]}')
                    if level_id:
                        # Verify performance level exists
                        cursor.execute("""
                            SELECT scorevalue 
                            FROM performance 
                            WHERE performancelevelid = %s
                        """, (int(level_id),))
                        result = cursor.fetchone()
                        if not result:
                            raise ValueError(f"Invalid performance level selected")
                        
                        score = result[0]
                        total_score += score
                        criteria_count += 1

                        # Insert criteria rating
                        cursor.execute("""
                            INSERT INTO criteria_ratings (
                                assessment_id, criteria_id, 
                                performance_level_id, feedback
                            ) VALUES (%s, %s, %s, %s)
                            ON CONFLICT (assessment_id, criteria_id) 
                            DO UPDATE SET
                                performance_level_id = EXCLUDED.performance_level_id,
                                feedback = EXCLUDED.feedback
                        """, (
                            assessment_id,
                            criteria[0],
                            level_id,
                            request.form.get(f'feedback_{criteria[0]}', '').strip()
                        ))

                # Calculate and update overall score
                if criteria_count > 0:
                    overall_score = round(total_score / criteria_count, 2)
                    cursor.execute("""
                        UPDATE competency_assessments
                        SET overall_score = %s
                        WHERE assessment_id = %s
                    """, (overall_score, assessment_id))

                # Mark project as assessed
                cursor.execute("""
                    UPDATE projects 
                    SET is_assessed = TRUE, assessment_time = NOW()
                    WHERE projectid = %s
                """, (project_id,))

                conn.commit()
                flash("Assessment saved successfully!", "success")
                return redirect(url_for('teacher.view_submissions'))

            except ValueError as ve:
                if conn:
                    conn.rollback()
                flash(f"Validation error: {str(ve)}", "danger")
            except Exception as e:
                if conn:
                    conn.rollback()
                flash(f"Assessment failed: {str(e)}", "danger")
            return redirect(url_for('teacher.assess_submission', project_id=project_id))

        # For template - use same performance levels for all criteria
        performance_levels_dict = {criteria[0]: performance_levels for criteria in criteria_list}

        # Prepare file download URL - modified to handle Windows paths
        file_url = None
        if submission[11]:  # projectfilepath at index 11
            # Convert DB path (with forward slashes) to system path
            system_path = os.path.normpath(submission[11])
            
            # Verify file exists before creating download link
            if os.path.exists(system_path):
                # Create download endpoint URL
                file_url = url_for('teacher.download_project', project_id=project_id)
            else:
                flash("Submission file not found on server", "warning")

        return render_template('teacher/assessment_form.html',
                           submission=submission,  # Pass raw tuple
                           students=students_to_assess,
                           criteria_list=criteria_list,
                           performance_levels=performance_levels_dict,
                           file_url=file_url,
                           filename=submission[12] if submission[12] else "submission")

    except Exception as e:
        if conn:
            conn.rollback()
        flash(f"System error: {str(e)}", "danger")
        return redirect(url_for('teacher.view_submissions'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#================================
#Download the file
#=================================

@teacher_routes.route('/download-project/<int:project_id>')
@teacher_login_required
def download_project(project_id):
    """Endpoint for downloading project files with proper path handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get project file path
        cursor.execute("""
            SELECT projectfilepath, file_name 
            FROM projects 
            WHERE projectid = %s
        """, (project_id,))
        project = cursor.fetchone()
        
        if not project or not project[0]:
            flash("File not found", "danger")
            return redirect(url_for('teacher.view_submissions'))

        # Convert DB path (with forward slashes) to system path
        system_path = os.path.normpath(project[0])
        
        if not os.path.exists(system_path):
            flash("File not found on server", "danger")
            return redirect(url_for('teacher.view_submissions'))

        # Send file with original filename
        return send_file(
            system_path,
            as_attachment=True,
            download_name=project[1] if project[1] else "submission"
        )

    except Exception as e:
        flash(f"Download failed: {str(e)}", "danger")
        return redirect(url_for('teacher.view_submissions'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()