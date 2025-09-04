from flask import Blueprint, render_template, session,request, redirect, url_for, flash
from app.database import get_db_connection

parent_routes = Blueprint('parent', __name__)

# Custom decorator to restrict access to logged-in parents
def parent_login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'parent_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.parent_login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

#======================================================================
#PARENT DASHBOARD ROUTE
#======================================================================
@parent_routes.route('/dashboard')
@parent_login_required
def parents_dashboard():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        
        # Get parent's name
        cursor.execute("""
            SELECT u.firstname, u.lastname 
            FROM users u
            JOIN parents p ON u.userid = p.userid
            WHERE p.parentid = %s
        """, (session['parent_id'],))
        parent = cursor.fetchone()
        parent_name = f"{parent[0]} {parent[1]}" if parent else "Parent"
        
        # Get all children
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname 
            FROM students s
            JOIN users u ON s.userid = u.userid
            WHERE s.parentid = %s
            ORDER BY u.firstname
        """, (session['parent_id'],))
        children = cursor.fetchall()
     
       
        
        # Get selected child
        selected_child = None
        child_id = request.args.get('child_id')
        if child_id:
            selected_child = next((c for c in children if c[0] == int(child_id)), None)
            print(f"DEBUG: Selected child - {selected_child}")

        return render_template('parent/child_progress.html',
                           parent_name=parent_name,
                           children=children,
                           selected_child=selected_child)
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for('auth.parent_login'))
    finally:
        conn.close()



#===============================================================
#COMPETETENCY OVERVIEW RESULTS
#================================================================
@parent_routes.route('/competency-overview')
@parent_login_required
def competency_overview():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get all children linked to this parent
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname 
            FROM students s
            JOIN users u ON s.userid = u.userid
            WHERE s.parentid = %s
            ORDER BY u.firstname
        """, (session['parent_id'],))
        children = cursor.fetchall()
        
        selected_child = None
        assessments = []
        student_id = request.args.get('student_id')
        
        if student_id:
            # Verify the selected child belongs to this parent
            cursor.execute("""
                SELECT s.studentid, u.firstname, u.lastname 
                FROM students s
                JOIN users u ON s.userid = u.userid
                WHERE s.studentid = %s AND s.parentid = %s
            """, (student_id, session['parent_id']))
            selected_child = cursor.fetchone()
            
            if selected_child:
                # Get assessments for the selected child
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
                """, (student_id,))
                assessments = cursor.fetchall()
                if not assessments:
                    flash(f"No competency results found for {selected_child[1]} {selected_child[2]}", "info")

        return render_template('parent/competency_overview.html',
                           children=children,
                           selected_child=selected_child,
                           assessments=assessments)
    
    except Exception as e:
        flash(f"Error loading results: {str(e)}", "danger")
        return redirect(url_for('parent.parents_dashboard'))
    finally:
        conn.close()


#=========================================================
#CRITERIA FEEDBACK BREAKDOWN
#===========================================================
@parent_routes.route('/criteria-feedback/<int:assessment_id>')
@parent_login_required
def criteria_feedback(assessment_id):
    """Show detailed criteria feedback for a parent's child's assessment"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 1. Verify this assessment belongs to the parent's child
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname
            FROM competency_assessments ca
            JOIN students s ON ca.student_id = s.studentid
            JOIN users u ON s.userid = u.userid
            WHERE ca.assessment_id = %s AND s.parentid = %s
        """, (assessment_id, session['parent_id']))
        child_info = cursor.fetchone()

        if not child_info:
            flash("You don't have permission to view this assessment", "danger")
            return redirect(url_for('parent.competency_overview'))

        # 2. Get assessment details
        cursor.execute("""
            SELECT 
                t.title AS task_title,
                c.competencyname,
                ca.overall_score,
                ca.feedback AS general_feedback,
                ca.assessed_at
            FROM competency_assessments ca
            JOIN tasks t ON ca.task_id = t.taskid
            JOIN competencies c ON ca.competency_id = c.competencyid
            WHERE ca.assessment_id = %s
        """, (assessment_id,))
        assessment = cursor.fetchone()

        # 3. Get criteria ratings and performance details
        cursor.execute("""
            SELECT 
                cr.criteria_id,
                c.CriteriaName AS criteria_name,
                p.levelname,
                p.scorevalue,
                cr.feedback AS criteria_feedback,
                p.LevelDescription
            FROM criteria_ratings cr
            JOIN criteria c ON cr.criteria_id = c.CriteriaID
            JOIN performance p ON cr.performance_level_id = p.performancelevelid
            WHERE cr.assessment_id = %s
            ORDER BY cr.criteria_id
        """, (assessment_id,))
        criteria_ratings = cursor.fetchall()

        return render_template('parent/criteria_feedback.html',
                               assessment=assessment,
                               criteria_ratings=criteria_ratings,
                               child_info=child_info)
    
    except Exception as e:
        flash(f"Error loading feedback: {str(e)}", "danger")
        return redirect(url_for('parent.competency_overview'))
    finally:
        conn.close()

@parent_routes.route('/parent-projects')
@parent_login_required
def parent_projects():
    """Show projects for the selected child"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        parent_id = session['parent_id']
        
        # Get selected child from query parameter, session, or default to first child
        selected_child_id = request.args.get('child_id') or session.get('selected_child_id')
        
        # Get list of children first
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname
            FROM students s
            JOIN users u ON s.userid = u.userid
            WHERE s.parentid = %s
            ORDER BY u.lastname
        """, (parent_id,))
        children = cursor.fetchall()
        
        if not children:
            flash("No children found under your account", "warning")
            return redirect(url_for('parent.parents_dashboard'))
        
        # If no child selected, default to the first one
        if not selected_child_id and children:
            selected_child_id = children[0][0]
            session['selected_child_id'] = selected_child_id
        
        # Verify the child belongs to this parent
        cursor.execute("""
            SELECT s.studentid 
            FROM students s
            JOIN parents p ON s.parentid = p.parentid
            WHERE p.parentid = %s AND s.studentid = %s
        """, (parent_id, selected_child_id))
        
        if not cursor.fetchone():
            flash("Unauthorized access to child data", "danger")
            return redirect(url_for('parent.parents_dashboard'))
        
        # Fetch projects for the selected child
        cursor.execute("""
            SELECT p.projectid, t.title AS task_title, p.submission_time, 
                   p.file_type, p.projectfilepath
            FROM projects p
            JOIN tasks t ON p.taskid = t.taskid
            WHERE p.studentid = %s OR p.submitter_id = %s
            ORDER BY p.submission_time DESC
        """, (selected_child_id, selected_child_id))
        
        projects = cursor.fetchall()
        
        # Get selected child details
        selected_child = next((child for child in children if child[0] == int(selected_child_id)), None)
        
        return render_template('parent/parent_projects.html',
                            projects=projects,
                            children=children,
                            selected_child=selected_child)
    
    except Exception as e:
        print(f"Error loading parent projects: {str(e)}")
        flash("An error occurred while loading projects", "danger")
        return redirect(url_for('parent.parents_dashboard'))
    
    finally:
        conn.close()


# Parent Profile
@parent_routes.route('/profile')
@parent_login_required
def parent_profile():
    return render_template('parent/parent_profile.html')

# Parent Feedback
@parent_routes.route('/feedback')
@parent_login_required
def parent_feedback():
    return render_template('parent/parent_feedback.html')

# Parent Reports
@parent_routes.route('/reports')
@parent_login_required
def parent_reports():
    return render_template('parent/parent_reports.html')

# Parent Notifications
@parent_routes.route('/notifications')
@parent_login_required
def parent_notifications():
    return render_template('parent/parent_notifications.html')

# Parent Settings
@parent_routes.route('/settings')
@parent_login_required
def parent_settings():
    return render_template('parent/parent_settings.html')