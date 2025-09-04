from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from app.queries import project_queries as pq
import os
from datetime import datetime  
from functools import wraps
from app.database import get_db_connection

# Define the student blueprint
student_routes = Blueprint('student', __name__)

# Login Required Decorator for Students
def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:  # Check if the student is logged in
            flash("You need to log in to access this page.", "danger")
            return redirect(url_for('auth.student_login'))  # Redirect to student login if not authenticated
        return f(*args, **kwargs)
    return decorated_function



# Student Dashboard Route
@student_routes.route('/dashboard')
@student_login_required
def student_dashboard():
    if 'student_id' not in session:
        flash("Session error - please login again", "danger")
        return redirect(url_for('auth.student_login'))

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        student_id = session['student_id']

        # 1. Get student full name
        cursor.execute("""
            SELECT u.firstname, u.lastname 
            FROM students s
            JOIN users u ON s.userid = u.userid
            WHERE s.studentid = %s
        """, (student_id,))
        student = cursor.fetchone()
        student_name = f"{student[0]} {student[1]}" if student else "Student"

        # 2. Get total task count assigned to student
        cursor.execute("""
            SELECT COUNT(DISTINCT t.taskid)
            FROM tasks t
            JOIN taskassignments ta ON t.taskid = ta.taskid
            LEFT JOIN projects p ON t.taskid = p.taskid AND 
                (p.studentid = %s OR p.submitter_id = %s)
            WHERE ta.studentid = %s 
               OR ta.classid IN (SELECT classid FROM class_students WHERE studentid = %s)
               OR ta.groupid IN (SELECT groupid FROM groupmembers WHERE studentid = %s)
        """, (student_id, student_id, student_id, student_id, student_id))
        task_count = cursor.fetchone()[0]

        # 3. Get total number of projects submitted or participated in
        cursor.execute("""
            SELECT COUNT(*)
            FROM projects
            WHERE studentid = %s OR submitter_id = %s
        """, (student_id, student_id))
        project_count = cursor.fetchone()[0]

        # 4. Get the latest 3 submitted projects (with task name, date submitted, and file type)
        cursor.execute("""
            SELECT t.title AS task_title, p.submission_time, p.file_type
            FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            WHERE p.studentid = %s OR p.submitter_id = %s
            ORDER BY p.submission_time DESC
            LIMIT 3
        """, (student_id, student_id))
        latest_projects = cursor.fetchall()

        # 5. Get competencies demonstrated
        cursor.execute("""
            SELECT COUNT(DISTINCT c.competencyid)
            FROM task_competencies tc
            JOIN projects p ON tc.taskid = p.taskid
            JOIN competencies c ON tc.competencyid = c.competencyid
            WHERE p.studentid = %s OR p.submitter_id = %s
        """, (student_id, student_id))
        competencies_count = cursor.fetchone()[0]

    except Exception as e:
        task_count = 0
        project_count = 0
        student_name = "Student"
        latest_projects = []
        competencies_count = 0
        flash(f"Error loading dashboard data: {str(e)}", "danger")

    finally:
        conn.close()

    return render_template('student/student_dashboard.html',
                           student_name=student_name,
                           task_count=task_count,
                           project_count=project_count,
                           competencies_count=competencies_count,
                           latest_projects=latest_projects)


# Student Profile Route
@student_routes.route('/profile')
@student_login_required
def student_profile():
    return render_template('student/student_profile.html')  # Updated path

# Student Progress Charts Route
@student_routes.route('/progress-charts')
@student_login_required
def progress_charts():
    return render_template('student/progress_charts.html')  # Updated path

# Student Reports Route
@student_routes.route('/reports')
@student_login_required
def reports():
    return render_template('student/reports.html')  # Updated path

# Student Notifications Route
@student_routes.route('/notifications')
@student_login_required
def notifications():
    return render_template('student/notifications.html')  # Updated path

# Student Settings Route
@student_routes.route('/settings')
@student_login_required
def settings():
    return render_template('student/settings.html')  # Updated path


# implementation of student tasks view

@student_routes.route('/tasks')
@student_login_required
def student_tasks():
    if 'student_id' not in session:
        flash("Session error - please login again", "danger")
        return redirect(url_for('auth.student_login'))

    student_id = session['student_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify student exists
        cursor.execute("SELECT * FROM students WHERE studentid = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash("Student record not found", "danger")
            return redirect(url_for('student.student_dashboard'))

        # Get class IDs
        cursor.execute("SELECT classid FROM class_students WHERE studentid = %s", (student_id,))
        class_ids = [row[0] for row in cursor.fetchall()]
        
        # Get group IDs
        cursor.execute("SELECT groupid FROM groupmembers WHERE studentid = %s", (student_id,))
        group_ids = [row[0] for row in cursor.fetchall()]
        
        # Fetch tasks with submission status
        query = """
            SELECT 
                t.taskid, 
                t.title, 
                t.taskdescription as description, 
                t.duedate,
                u.firstname, 
                u.lastname,
                CASE
                    WHEN p.projectid IS NOT NULL THEN 'Submitted'
                    WHEN t.duedate < CURRENT_DATE THEN 'Overdue'
                    ELSE 'Pending'
                END AS task_status,
                p.is_late as is_late
            FROM tasks t
            JOIN teachers te ON t.teacherid = te.teacherid
            JOIN users u ON te.userid = u.userid
            JOIN taskassignments ta ON t.taskid = ta.taskid
            LEFT JOIN projects p ON t.taskid = p.taskid AND 
                (p.studentid = %s OR p.submitter_id = %s OR 
                 (ta.groupid IS NOT NULL AND p.groupid = ta.groupid))
            WHERE 
                ta.studentid = %s OR
                (ta.classid IS NOT NULL AND ta.classid = ANY(%s::int[])) OR
                (ta.groupid IS NOT NULL AND ta.groupid = ANY(%s::int[]))
            GROUP BY t.taskid, u.firstname, u.lastname, p.projectid, p.is_late
        """
        cursor.execute(query, (student_id, student_id, student_id, class_ids, group_ids))
        tasks = cursor.fetchall()
        
    except Exception as e:
        tasks = []
        flash(f"Error loading tasks: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return render_template('student/student_tasks.html', tasks=tasks)



#===============================================
#STUDENT UPLOADING FUNCTIONALITY
#==============================================

@student_routes.route('/upload-project/<int:task_id>', methods=['GET', 'POST'])
@student_login_required
def upload_project(task_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute("""
            SELECT 
                t.taskid, 
                t.title, 
                t.taskdescription, 
                t.duedate,
                u.firstname, 
                u.lastname 
            FROM tasks t
            JOIN teachers te ON t.teacherid = te.teacherid
            JOIN users u ON te.userid = u.userid
            WHERE t.taskid = %s
        """, (task_id,))
        task = cursor.fetchone()

        if not task:
            flash("Task not found", "danger")
            return redirect(url_for('student.student_tasks'))

        # FIRST check if this is a group task by looking at taskassignments
        cursor.execute("""
            SELECT ta.groupid, sg.groupname
            FROM taskassignments ta
            LEFT JOIN studentgroups sg ON ta.groupid = sg.groupid
            WHERE ta.taskid = %s AND ta.groupid IS NOT NULL
            LIMIT 1
        """, (task_id,))
        group_assignment = cursor.fetchone()

        # THEN check if student is in this group (if it's a group task)
        group = None
        if group_assignment:
            cursor.execute("""
                SELECT 1 FROM groupmembers 
                WHERE groupid = %s AND studentid = %s
            """, (group_assignment[0], session['student_id']))
            if cursor.fetchone():
                group = group_assignment

        # Check submission status
        if group:
            cursor.execute("""
                SELECT 1 FROM projects 
                WHERE taskid = %s AND groupid = %s
                LIMIT 1
            """, (task_id, group[0]))
        else:
            cursor.execute("""
                SELECT 1 FROM projects 
                WHERE taskid = %s AND studentid = %s
                LIMIT 1
            """, (task_id, session['student_id']))

        if cursor.fetchone():
            flash("Submission already exists for this task", "warning")
            return redirect(url_for('student.student_tasks'))

        if request.method == 'POST':
            if 'project_file' not in request.files:
                flash("No file selected", "danger")
                return redirect(request.url)
                
            file = request.files['project_file']
            if file.filename == '':
                flash("No file selected", "danger")
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                current_time = datetime.now()
                is_late = current_time.date() > task[3]
                
                # PROPER FOLDER STRUCTURE
                if group:
                    base_dir = os.path.join("projects", "by_group", str(group[0]))
                    save_name = f"task_{task_id}_{int(current_time.timestamp())}{file_ext}"
                else:
                    base_dir = os.path.join("projects", "by_student", str(session['student_id']))
                    save_name = f"task_{task_id}{file_ext}"

                os.makedirs(base_dir, exist_ok=True)
                filepath = os.path.join(base_dir, save_name)
                file.save(filepath)

                # Normalize slashes for DB storage
                db_filepath = filepath.replace(os.sep, '/')
                
                file_size = os.path.getsize(filepath)
                file_type = file_ext[1:] if file_ext else 'unknown'

                # PROPER DB STORAGE
                cursor.execute("""
                    INSERT INTO projects (
                        taskid, 
                        studentid, 
                        groupid, 
                        submitter_id, 
                        file_name, 
                        projectfilepath, 
                        is_late,
                        file_size,
                        file_type,
                        submission_time
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    task_id,
                    None if group else session['student_id'],
                    group[0] if group else None,
                    session['student_id'],
                    filename,
                    db_filepath,  # ✅ fixed slashes
                    is_late,
                    file_size,
                    file_type,
                    current_time
                ))
                conn.commit()

                flash_message = "File uploaded successfully!"
                if is_late:
                    flash_message += " (Late submission)"
                if group:
                    flash_message += f" (Group: {group[1]})"
                flash(flash_message, "success")
                return redirect(url_for('student.student_tasks'))

        return render_template('student/student_upload_project.html', 
                            task=task, 
                            group=group,
                            current_datetime=datetime.now())

    except Exception as e:
        conn.rollback()
        flash(f"Upload failed: {str(e)}", "danger")
        return redirect(url_for('student.student_tasks'))
    finally:
        conn.close()


#======================================================================================
# COMPETENCY RESULTS
#======================================================================================
@student_routes.route('/competency-results')
@student_login_required
def competency_results():
    """Show student their competency assessment results"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get all assessed competencies for the student
        cursor.execute("""
            SELECT 
                ca.assessment_id,
                t.title AS task_title,
                c.competencyname,
                ca.overall_score,
                ca.feedback,
                ca.assessed_at,
                t.taskid,
                c.competencyid
            FROM competency_assessments ca
            JOIN tasks t ON ca.task_id = t.taskid
            JOIN competencies c ON ca.competency_id = c.competencyid
            WHERE ca.student_id = %s
            ORDER BY ca.assessed_at DESC
        """, (session['student_id'],))
        assessments = cursor.fetchall()

        return render_template('student/competency_results.html',
                           assessments=assessments)
    
    except Exception as e:
        flash(f"Error loading results: {str(e)}", "danger")
        return redirect(url_for('student.student_dashboard'))
    finally:
        conn.close()



#====================================
#CRITERIA FEEDBACK 
#===================================

@student_routes.route('/criteria-feedback/<int:assessment_id>')
@student_login_required
def criteria_feedback(assessment_id):
    """Show detailed criteria feedback for an assessment"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Verify student owns this assessment
        cursor.execute("""
            SELECT 1 FROM competency_assessments
            WHERE assessment_id = %s AND student_id = %s
        """, (assessment_id, session['student_id']))
        if not cursor.fetchone():
            flash("You don't have permission to view this", "danger")
            return redirect(url_for('student.competency_results'))

        # Get assessment details
        cursor.execute("""
            SELECT 
                t.title AS task_title,
                c.competencyname,
                ca.overall_score,
                ca.feedback AS general_feedback
            FROM competency_assessments ca
            JOIN tasks t ON ca.task_id = t.taskid
            JOIN competencies c ON ca.competency_id = c.competencyid
            WHERE ca.assessment_id = %s
        """, (assessment_id,))
        assessment = cursor.fetchone()

        # Get criteria ratings and join with the Criteria table to get CriteriaName
        cursor.execute("""
            SELECT 
                cr.criteria_id,
                c.CriteriaName AS criteria_name,  -- Correctly select CriteriaName from the Criteria table
                p.levelname,
                p.scorevalue,
                cr.feedback AS criteria_feedback
            FROM criteria_ratings cr
            JOIN criteria c ON cr.criteria_id = c.CriteriaID  -- Join criteria table to get the name
            JOIN performance p ON cr.performance_level_id = p.performancelevelid
            WHERE cr.assessment_id = %s
            ORDER BY cr.criteria_id
        """, (assessment_id,))
        criteria_ratings = cursor.fetchall()

        return render_template('student/criteria_feedback.html',
                              assessment=assessment,
                              criteria_ratings=criteria_ratings)
    
    except Exception as e:
        flash(f"Error loading feedback: {str(e)}", "danger")
        return redirect(url_for('student.competency_results'))
    finally:
        conn.close()

#======================================================
#student projects
#======================================================
@student_routes.route('/student-projects')
@student_login_required
def student_projects():
    """Show a list of the student's projects"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        student_id = session['student_id']

        # Fetch projects where student is either the owner or the submitter
        cursor.execute("""
            SELECT p.projectid, t.title AS task_title, p.submission_time, p.file_type, p.projectfilepath
            FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            WHERE p.studentid = %s OR p.submitter_id = %s
            ORDER BY p.submission_time DESC
        """, (student_id, student_id))

        projects = cursor.fetchall()

        return render_template('student/student_projects.html', projects=projects)
    
    except Exception as e:
        flash(f"Error loading projects: {str(e)}", "danger")
        return redirect(url_for('student.student_dashboard'))
    
    finally:
        conn.close()
