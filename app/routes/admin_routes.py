from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from werkzeug.security import generate_password_hash
from app.database import get_db_connection
from app.queries.auth_queries import INSERT_NEW_USER_QUERY, GET_USER_BY_EMAIL_QUERY
from app.queries.admin_queries import (COUNT_TEACHERS_QUERY, COUNT_PARENTS_QUERY,COUNT_STUDENTS_QUERY, 
        COUNT_COMPETENCIES_QUERY,INSERT_NEW_STUDENT_QUERY, GET_ALL_STUDENTS_QUERY, GET_PARENT_BY_EMAIL_QUERY,GET_ALL_PARENTS_QUERY,
        SEARCH_TEACHERS_QUERY,SEARCH_PARENTS_QUERY,SEARCH_STUDENTS_QUERY
                                     )
from datetime import datetime

admin_routes = Blueprint('admin', __name__)

#FUNCTION TO GENERATE HASHED PASSWORD FOR ADMIN
#print(generate_password_hash('12345'))

# Define constants for admin route names
ADMIN_MANAGE_TEACHERS_ROUTE = 'admin.manage_teachers'

# Custom decorator to restrict access to logged-in admins
def admin_login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            flash("Please log in as an admin to access this page.", "warning")
            return redirect(url_for('auth.admin_login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

# Admin Dashboard
@admin_routes.route('/dashboard')
@admin_login_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch the count of teachers
        cursor.execute(COUNT_TEACHERS_QUERY)
        teacher_count = cursor.fetchone()[0]

        # Fetch the count of parents
        cursor.execute(COUNT_PARENTS_QUERY)
        parent_count = cursor.fetchone()[0]

        #fetch the count of students
        cursor.execute(COUNT_STUDENTS_QUERY)
        student_count = cursor.fetchone()[0]

        # Fetch the count of competencies
        cursor.execute(COUNT_COMPETENCIES_QUERY)
        competency_count = cursor.fetchone()[0]

    finally:
        cursor.close()
        conn.close()

    # Pass the counts to the template
    return render_template('admin/admin_dashboard.html', teacher_count=teacher_count, parent_count=parent_count,student_count=student_count,competency_count=competency_count)


# Add Teacher Route
@admin_routes.route('/add_teacher', methods=['POST'])
@admin_login_required
def add_teacher():
    if request.method == 'POST':
        # Extract form data
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        hire_date = request.form['hire-date']

        # Hash the password
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email already exists
            cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("A user with this email already exists.", "danger")
                return redirect(url_for('ADMIN_MANAGE_TEACHERS_ROUTE')) 

            # Insert the new user into the Users table
            cursor.execute(INSERT_NEW_USER_QUERY, (
                first_name,
                last_name,
                email,
                phone,
                password_hash,
                2,  # RoleID = 2 for teachers
                True,  # is_active
                None,  # email_token
                None,  # token_expiry
            ))
            conn.commit()

            # Get the newly created user's ID
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s;", (email,))
            user_id = cursor.fetchone()[0]

            # Insert the new teacher into the Teachers table
            cursor.execute("""
                INSERT INTO Teachers (UserID, HireDate)
                VALUES (%s, %s);
            """, (user_id, hire_date))
            conn.commit()

            flash("Teacher added successfully!", "success")
            return redirect(url_for(ADMIN_MANAGE_TEACHERS_ROUTE))

        except Exception as e:
            print(f"Error adding teacher: {e}")
            conn.rollback()
            flash("An error occurred while adding the teacher.", "danger")

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_teachers'))


#MANAGE TEACHERS ROUTE
@admin_routes.route('/manage-teachers')
@admin_login_required
def manage_teachers():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch all teachers (RoleID = 2) with their hire dates
        cursor.execute("""
            SELECT u.UserID, u.FirstName, u.LastName, u.Email, t.HireDate 
            FROM Users u
            JOIN Teachers t ON u.UserID = t.UserID
            WHERE u.RoleID = 2 order by t.userID;
        """)
        teachers = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching teachers: {e}")
        teachers = []

    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_teachers.html', teachers=teachers)


#search teachers route
@admin_routes.route('/search_teachers', methods=['GET'])
@admin_login_required
def search_teachers():
    search_query = request.args.get('query', '').strip()  # Get the search query from the URL
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if search_query:
            # Add wildcards for partial matching
            search_term = f"%{search_query}%"
            cursor.execute(SEARCH_TEACHERS_QUERY, (search_term, search_term, search_term))
            teachers = cursor.fetchall()
        else:
            # If no search query, return all teachers
            cursor.execute("""
                SELECT t.TeacherID, u.FirstName, u.LastName, u.Email, t.HireDate
                FROM Teachers t
                JOIN Users u ON t.UserID = u.UserID;
            """)
            teachers = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_teachers.html', teachers=teachers)



@admin_routes.route('/search_students', methods=['GET'])
def search_students():
    search_query = request.args.get('query', '').strip()  # Get the search query from the URL
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if search_query:
            # Add wildcards for partial matching
            search_term = f"%{search_query}%"
            cursor.execute(SEARCH_STUDENTS_QUERY, (search_term, search_term, search_term, search_term))
            students = cursor.fetchall()
        else:
            # If no search query, return all students
            cursor.execute("""
                SELECT s.StudentID, u.FirstName, u.LastName, u.Email, s.StudentNumber, s.RegistrationDate
                FROM Students s
                JOIN Users u ON s.UserID = u.UserID;
            """)
            students = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_students.html', students=students)

# Search Parents Route
@admin_routes.route('/search_parents', methods=['GET'])
def search_parents():
    search_query = request.args.get('query', '').strip()  # Get the search query from the URL
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if search_query:
            # Add wildcards for partial matching
            search_term = f"%{search_query}%"
            cursor.execute(SEARCH_PARENTS_QUERY, (search_term, search_term, search_term))
            parents = cursor.fetchall()
        else:
            # If no search query, return all parents
            cursor.execute("""
                SELECT p.ParentID, u.FirstName, u.LastName, u.Email, u.Phone, u.created_at
                FROM Parents p
                JOIN Users u ON p.UserID = u.UserID;
            """)
            parents = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_parents.html', parents=parents)


# Manage Parents Route
@admin_routes.route('/manage_parents')
@admin_login_required
def manage_parents():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch all parents using the updated query
        cursor.execute(GET_ALL_PARENTS_QUERY)
        parents = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching parents: {e}")
        parents = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_parents.html', parents=parents)


# Manage Students Route
@admin_routes.route('/manage_students', methods=['GET', 'POST'])
@admin_login_required
def manage_students():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Extract form data
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        student_number = request.form['student-number']
        registration_date = request.form['registration-date']
        parent_email = request.form['parent-email']  # Optional: Link to parent

        # Hash the password
        password_hash = generate_password_hash(password)

        try:
            # Insert the new user into the Users table
            cursor.execute(INSERT_NEW_USER_QUERY, (
                first_name,
                last_name,
                email,
                phone,
                password_hash,
                1,  # RoleID = 1 for students
                True,  # is_active
                None,  # email_token
                None,  # token_expiry
            ))
            conn.commit()

            # Get the newly created user's ID
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s;", (email,))
            user_id = cursor.fetchone()[0]

            # Get the ParentID if parent_email is provided
            parent_id = None
            if parent_email:
                cursor.execute(GET_PARENT_BY_EMAIL_QUERY, (parent_email,))
                parent = cursor.fetchone()
                if parent:
                    parent_id = parent[0]

            # Insert the new student into the Students table
            cursor.execute(INSERT_NEW_STUDENT_QUERY, (
                user_id,
                parent_id,
                student_number,
                registration_date
            ))
            conn.commit()

            flash("Student added successfully! add to class", "success")
            return redirect(url_for('admin.manage_students'))

        except Exception as e:
            print(f"Error adding student: {e}")
            conn.rollback()
            flash("An error occurred while adding the student.", "danger")

        
            
            

    # Fetch all students to display in the table
    try:
        cursor.execute(GET_ALL_STUDENTS_QUERY)
        students = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_students.html', students=students)


# Generate Reports
@admin_routes.route('/generate_reports')
@admin_login_required
def generate_reports():
    return render_template('admin/generate_reports.html')

#Route to Fetch teacher Details
@admin_routes.route('/get_teacher/<int:teacher_id>', methods=['GET'])
@admin_login_required
def get_teacher(teacher_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.UserID, u.FirstName, u.LastName, u.Email, u.Phone, t.HireDate, u.is_active
            FROM Users u
            JOIN Teachers t ON u.UserID = t.UserID
            WHERE u.UserID = %s;
        """, (teacher_id,))
        teacher = cursor.fetchone()

        if teacher:
            return {
                'UserID': teacher[0],
                'FirstName': teacher[1],
                'LastName': teacher[2],
                'Email': teacher[3],
                'Phone': teacher[4],
                'HireDate': teacher[5].strftime('%Y-%m-%d'),
                'is_active': teacher[6]  # Include is_active field
            }
        else:
            return {'error': 'Teacher not found'}, 404

    finally:
        cursor.close()
        conn.close()


#edit a teacher
@admin_routes.route('/edit_teacher', methods=['POST'])
@admin_login_required
def edit_teacher():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        hire_date = request.form['hire-date']
        is_active = request.form['is_active'] == 'true'  # Convert string to boolean

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE Users
                SET FirstName = %s, LastName = %s, Email = %s, Phone = %s, is_active = %s
                WHERE UserID = %s;
            """, (first_name, last_name, email, phone, is_active, teacher_id))

            cursor.execute("""
                UPDATE Teachers
                SET HireDate = %s
                WHERE UserID = %s;
            """, (hire_date, teacher_id))

            conn.commit()
            flash("Teacher updated successfully!", "success")
        except Exception as e:
            print(f"Error updating teacher: {e}")
            conn.rollback()
            flash("An error occurred while updating the teacher.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_teachers'))


#admin delete a teacher
@admin_routes.route('/delete_teacher', methods=['POST'])
@admin_login_required
def delete_teacher():
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the teacher from the Teachers table
            cursor.execute("DELETE FROM Teachers WHERE UserID = %s;", (teacher_id,))
            # Delete the user from the Users table
            cursor.execute("DELETE FROM Users WHERE UserID = %s;", (teacher_id,))
            conn.commit()
            flash("Teacher deleted successfully!", "success")  # Set flash message
        except Exception as e:
            print(f"Error deleting teacher: {e}")
            conn.rollback()
            flash("An error occurred while deleting the teacher.", "danger")  # Set flash message
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('admin.manage_teachers'))  # Redirect to the manage teachers page

@admin_routes.route('/get_parent/<int:parent_id>', methods=['GET'])
@admin_login_required
def get_parent(parent_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.UserID, u.FirstName, u.LastName, u.Email, u.Phone, u.is_active
            FROM Users u
            JOIN Parents p ON u.UserID = p.UserID
            WHERE u.UserID = %s;
        """, (parent_id,))
        parent = cursor.fetchone()

        if parent:
            return {
                'UserID': parent[0],
                'FirstName': parent[1],
                'LastName': parent[2],
                'Email': parent[3],
                'Phone': parent[4],
                'is_active': parent[5]  # Include is_active field
            }
        else:
            return {'error': 'Parent not found'}, 404

    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_parent', methods=['POST'])
@admin_login_required
def edit_parent():
    if request.method == 'POST':
        parent_id = request.form['parent_id']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        is_active = request.form['is_active'] == 'true'  # Convert string to boolean

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE Users
                SET FirstName = %s, LastName = %s, Email = %s, Phone = %s, is_active = %s
                WHERE UserID = %s;
            """, (first_name, last_name, email, phone, is_active, parent_id))

            conn.commit()
            flash("Parent updated successfully!", "success")
        except Exception as e:
            print(f"Error updating parent: {e}")
            conn.rollback()
            flash("An error occurred while updating the parent.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_parents'))

@admin_routes.route('/delete_parent', methods=['POST'])
@admin_login_required
def delete_parent():
    if request.method == 'POST':
        parent_id = request.form['parent_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the parent from the Parents table
            cursor.execute("DELETE FROM Parents WHERE UserID = %s;", (parent_id,))
            # Delete the user from the Users table
            cursor.execute("DELETE FROM Users WHERE UserID = %s;", (parent_id,))
            conn.commit()
            flash("Parent deleted successfully!", "success")  # Set flash message
        except Exception as e:
            print(f"Error deleting parent: {e}")
            conn.rollback()
            flash("An error occurred while deleting the parent.", "danger")  # Set flash message
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('admin.manage_parents'))  # Redirect to the manage parents page
    


@admin_routes.route('/get_student/<int:student_id>', methods=['GET'])
@admin_login_required
def get_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT u.UserID, u.FirstName, u.LastName, u.Email, u.Phone, s.StudentNumber, s.RegistrationDate, u.is_active
            FROM Users u
            JOIN Students s ON u.UserID = s.UserID
            WHERE u.UserID = %s;
        """, (student_id,))
        student = cursor.fetchone()

        if student:
            return {
                'UserID': student[0],
                'FirstName': student[1],
                'LastName': student[2],
                'Email': student[3],
                'Phone': student[4],
                'StudentNumber': student[5],
                'RegistrationDate': student[6].strftime('%Y-%m-%d'),
                'is_active': student[7]  # Include is_active field
            }
        else:
            return {'error': 'Student not found'}, 404

    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_student', methods=['POST'])
@admin_login_required
def edit_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        student_number = request.form['student-number']
        registration_date = request.form['registration-date']
        is_active = request.form['is_active'] == 'true'  # Convert string to boolean

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Update Users table
            cursor.execute("""
                UPDATE Users
                SET FirstName = %s, LastName = %s, Email = %s, Phone = %s, is_active = %s
                WHERE UserID = %s;
            """, (first_name, last_name, email, phone, is_active, student_id))

            # Update Students table
            cursor.execute("""
                UPDATE Students
                SET StudentNumber = %s, RegistrationDate = %s
                WHERE UserID = %s;
            """, (student_number, registration_date, student_id))

            conn.commit()
            flash("Student updated successfully!", "success")
        except Exception as e:
            print(f"Error updating student: {e}")
            conn.rollback()
            flash("An error occurred while updating the student.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_students'))

@admin_routes.route('/delete_student', methods=['POST'])
@admin_login_required
def delete_student():
    if request.method == 'POST':
        student_id = request.form['student_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Delete the student from the Students table
            cursor.execute("DELETE FROM Students WHERE UserID = %s;", (student_id,))
            # Delete the user from the Users table
            cursor.execute("DELETE FROM Users WHERE UserID = %s;", (student_id,))
            conn.commit()
            flash("Student deleted successfully!", "success")
        except Exception as e:
            print(f"Error deleting student: {e}")
            conn.rollback()
            flash("An error occurred while deleting the student.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_students'))


from app.queries.competency_queries import (
    GET_ALL_COMPETENCIES_QUERY,
    INSERT_COMPETENCY_QUERY,
    GET_COMPETENCY_BY_ID_QUERY,
    UPDATE_COMPETENCY_QUERY,
    DELETE_COMPETENCY_QUERY
)
from app.queries.rubric_queries import (
    GET_ALL_RUBRICS_QUERY,
    GET_CRITERIA_FOR_DROPDOWN_QUERY,
    GET_PERFORMANCE_LEVELS_QUERY,
    INSERT_RUBRIC_QUERY,
    GET_RUBRIC_BY_ID_QUERY,
    UPDATE_RUBRIC_QUERY,
    DELETE_RUBRIC_QUERY
)
from app.queries.criteria_queries import (
    GET_ALL_CRITERIA_QUERY,
    GET_COMPETENCIES_FOR_DROPDOWN_QUERY,
    INSERT_CRITERIA_QUERY,
    GET_CRITERIA_BY_ID_QUERY,
    UPDATE_CRITERIA_QUERY,
    CHECK_CRITERIA_USAGE_QUERY,
    DELETE_CRITERIA_QUERY
)


#==============================================================================================
# ========== COMPETENCY MANAGEMENT ==========
#==============================================================================================

@admin_routes.route('/manage_competencies')
@admin_login_required
def manage_competencies():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_ALL_COMPETENCIES_QUERY)
        competencies = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching competencies: {e}")
        competencies = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_competencies.html', competencies=competencies)

@admin_routes.route('/add_competency', methods=['POST'])
@admin_login_required
def add_competency():
    if request.method == 'POST':
        competency_name = request.form['competency-name']
        competency_description = request.form['competency-description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(INSERT_COMPETENCY_QUERY, (competency_name, competency_description))
            conn.commit()
            flash("Competency added successfully!", "success")
        except Exception as e:
            print(f"Error adding competency: {e}")
            conn.rollback()
            flash("An error occurred while adding the competency.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_competencies'))                                                                         

@admin_routes.route('/get_competency/<int:competency_id>', methods=['GET'])
@admin_login_required
def get_competency(competency_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_COMPETENCY_BY_ID_QUERY, (competency_id,))
        competency = cursor.fetchone()

        if competency:
            return {
                'CompetencyID': competency[0],
                'CompetencyName': competency[1],
                'CompetencyDescription': competency[2]
            }
        else:
            return {'error': 'Competency not found'}, 404
    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_competency', methods=['POST'])
@admin_login_required
def edit_competency():
    if request.method == 'POST':
        competency_id = request.form['competency_id']
        competency_name = request.form['competency-name']
        competency_description = request.form['competency-description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(UPDATE_COMPETENCY_QUERY, (competency_name, competency_description, competency_id))
            conn.commit()
            flash("Competency updated successfully!", "success")
        except Exception as e:
            print(f"Error updating competency: {e}")
            conn.rollback()
            flash("An error occurred while updating the competency.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_competencies'))

@admin_routes.route('/delete_competency', methods=['POST'])
@admin_login_required
def delete_competency():
    if request.method == 'POST':
        competency_id = request.form['competency_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(DELETE_COMPETENCY_QUERY, (competency_id,))
            conn.commit()
            flash("Competency deleted successfully!", "success")
        except Exception as e:
            print(f"Error deleting competency: {e}")
            conn.rollback()
            flash("An error occurred while deleting the competency.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_competencies'))


#===============================================
# ========== CRITERIA MANAGEMENT ==========
#================================================

@admin_routes.route('/manage_criteria')
@admin_login_required
def manage_criteria():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_ALL_CRITERIA_QUERY)
        criteria = cursor.fetchall()

        cursor.execute(GET_COMPETENCIES_FOR_DROPDOWN_QUERY)
        competencies = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching criteria: {e}")
        criteria = []
        competencies = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_criteria.html', 
                         criteria=criteria,
                         competencies=competencies)

@admin_routes.route('/add_criteria', methods=['POST'])
@admin_login_required
def add_criteria():
    if request.method == 'POST':
        competency_id = request.form['competency_id']
        criteria_name = request.form['criteria_name']
        criteria_description = request.form['criteria_description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(INSERT_CRITERIA_QUERY, (competency_id, criteria_name, criteria_description))
            conn.commit()
            flash("Criteria added successfully!", "success")
        except Exception as e:
            print(f"Error adding criteria: {e}")
            conn.rollback()
            flash("An error occurred while adding the criteria.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_criteria'))

@admin_routes.route('/get_criteria/<int:criteria_id>', methods=['GET'])
@admin_login_required
def get_criteria(criteria_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_CRITERIA_BY_ID_QUERY, (criteria_id,))
        criterion = cursor.fetchone()

        if criterion:
            return {
                'CriteriaID': criterion[0],
                'CompetencyID': criterion[1],
                'CriteriaName': criterion[2],
                'CriteriaDescription': criterion[3]
            }
        else:
            return {'error': 'Criteria not found'}, 404
    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_criteria', methods=['POST'])
@admin_login_required
def edit_criteria():
    if request.method == 'POST':
        criteria_id = request.form['criteria_id']
        competency_id = request.form['competency_id']
        criteria_name = request.form['criteria_name']
        criteria_description = request.form['criteria_description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(UPDATE_CRITERIA_QUERY, (competency_id, criteria_name, criteria_description, criteria_id))
            conn.commit()
            flash("Criteria updated successfully!", "success")
        except Exception as e:
            print(f"Error updating criteria: {e}")
            conn.rollback()
            flash("An error occurred while updating the criteria.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_criteria'))

@admin_routes.route('/delete_criteria', methods=['POST'])
@admin_login_required
def delete_criteria():
    if request.method == 'POST':
        criteria_id = request.form['criteria_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(CHECK_CRITERIA_USAGE_QUERY, (criteria_id,))
            rubric_count = cursor.fetchone()[0]
            
            if rubric_count > 0:
                flash("Cannot delete criteria that is used in rubrics. Delete associated rubrics first.", "warning")
            else:
                cursor.execute(DELETE_CRITERIA_QUERY, (criteria_id,))
                conn.commit()
                flash("Criteria deleted successfully!", "success")
        except Exception as e:
            print(f"Error deleting criteria: {e}")
            conn.rollback()
            flash("An error occurred while deleting the criteria.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_criteria'))





@admin_routes.route('/manage_classes')
@admin_login_required
def manage_classes():
    """Display all classes with their assigned teachers"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all classes with teacher names
        cursor.execute("""
            SELECT 
                c.classid, 
                c.classname, 
                c.academicyear, 
                c.createdat,
                t.teacherid,
                u.firstname, 
                u.lastname
            FROM classes c
            JOIN teachers t ON c.teacherid = t.teacherid
            JOIN users u ON t.userid = u.userid
            ORDER BY c.classname
        """)
        classes = cursor.fetchall()
        
        # Get active teachers for dropdown
        cursor.execute("""
            SELECT t.teacherid, u.firstname, u.lastname
            FROM teachers t
            JOIN users u ON t.userid = u.userid
            WHERE u.is_active = TRUE
            ORDER BY u.lastname, u.firstname
        """)
        teachers = cursor.fetchall()
        
        
        
    except Exception as e:
        print(f"Error fetching classes: {str(e)}")
        flash("Error loading classes data", "danger")
        classes = []
        teachers = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template('admin/manage_classes.html', 
                         classes=classes,
                         teachers=teachers)

@admin_routes.route('/add_class', methods=['POST'])
@admin_login_required
def add_class():
    """Handle class creation form submission"""
    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        class_name = request.form.get('class_name', '').strip()
        academic_year = request.form.get('academic_year', '').strip()
        
        # Basic validation
        if not all([teacher_id, class_name, academic_year]):
            flash("All fields are required", "danger")
            return redirect(url_for('admin.manage_classes'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create new class
            cursor.execute("""
                INSERT INTO classes (teacherid, classname, academicyear)
                VALUES (%s, %s, %s)
                RETURNING classid
            """, (teacher_id, class_name, academic_year))
            
            new_class_id = cursor.fetchone()[0]
            conn.commit()
            flash(f"Class '{class_name}' created successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            print(f"Database error: {str(e)}")
            flash("Failed to create class. Please try again.", "danger")
            
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin.manage_classes'))




@admin_routes.route('/get_class/<int:class_id>', methods=['GET'])
@admin_login_required
def get_class(class_id):
    """Fetch class details for editing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.classid, c.classname, c.academicyear, c.teacherid
            FROM classes c
            WHERE c.classid = %s
        """, (class_id,))
        class_data = cursor.fetchone()
        
        if class_data:
            return {
                'classid': class_data[0],
                'classname': class_data[1],
                'academicyear': class_data[2],
                'teacherid': class_data[3]
            }
        else:
            return {'error': 'Class not found'}, 404
            
    except Exception as e:
        print(f"Error fetching class: {str(e)}")
        return {'error': 'Server error'}, 500
    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_class', methods=['POST'])
@admin_login_required
def edit_class():
    """Handle class edit form submission"""
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        teacher_id = request.form.get('teacher_id')
        class_name = request.form.get('class_name', '').strip()
        academic_year = request.form.get('academic_year', '').strip()
        
        # Basic validation
        if not all([class_id, teacher_id, class_name, academic_year]):
            flash("All fields are required", "danger")
            return redirect(url_for('admin.manage_classes'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update class
            cursor.execute("""
                UPDATE classes
                SET teacherid = %s, classname = %s, academicyear = %s
                WHERE classid = %s
            """, (teacher_id, class_name, academic_year, class_id))
            
            conn.commit()
            flash("Class updated successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating class: {str(e)}")
            flash("Failed to update class. Please try again.", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin.manage_classes'))

@admin_routes.route('/delete_class', methods=['POST'])
@admin_login_required
def delete_class():
    """Handle class deletion"""
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if class has students enrolled
            cursor.execute("""
                SELECT COUNT(*) FROM class_students
                WHERE classid = %s
            """, (class_id,))
            student_count = cursor.fetchone()[0]
            
            if student_count > 0:
                flash("Cannot delete class with enrolled students", "warning")
                return redirect(url_for('admin.manage_classes'))
                
            # Delete the class
            cursor.execute("""
                DELETE FROM classes
                WHERE classid = %s
            """, (class_id,))
            
            conn.commit()
            flash("Class deleted successfully!", "success")
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting class: {str(e)}")
            flash("Failed to delete class. Please try again.", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin.manage_classes'))



@admin_routes.route('/manage_class_students/<int:class_id>')
@admin_login_required
def manage_class_students(class_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get current class info
        cursor.execute("""
            SELECT c.classid, c.classname, c.academicyear
            FROM classes c
            WHERE c.classid = %s
        """, (class_id,))
        class_info = cursor.fetchone()
        
        # Get enrolled students
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname, s.studentnumber
            FROM class_students cs
            JOIN students s ON cs.studentid = s.studentid
            JOIN users u ON s.userid = u.userid
            WHERE cs.classid = %s
            ORDER BY u.lastname
        """, (class_id,))
        enrolled_students = cursor.fetchall()
        
        # Get available students (not in any class this academic year)
        cursor.execute("""
            SELECT s.studentid, u.firstname, u.lastname, s.studentnumber
            FROM students s
            JOIN users u ON s.userid = u.userid
            WHERE s.studentid NOT IN (
                SELECT cs.studentid 
                FROM class_students cs
                JOIN classes c ON cs.classid = c.classid
                WHERE c.academicyear = %s
            )
            ORDER BY u.lastname
        """, (class_info[2],))  # class_info[2] is academicyear
        available_students = cursor.fetchall()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        flash("Error loading student data", "danger")
        class_info, enrolled_students, available_students = None, [], []
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        'admin/manage_class_students.html',
        class_info=class_info,
        enrolled_students=enrolled_students,
        available_students=available_students
    )


@admin_routes.route('/add_student_to_class', methods=['POST'])
@admin_login_required
def add_student_to_class():
    class_id = request.form.get('class_id')
    student_id = request.form.get('student_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Step 1: Get the academic year of the target class
        cursor.execute("""
            SELECT academicyear FROM classes 
            WHERE classid = %s
        """, (class_id,))
        target_year = cursor.fetchone()[0]
        
        # Step 2: Check if student is already in any class this year
        cursor.execute("""
            SELECT c.classname 
            FROM class_students cs
            JOIN classes c ON cs.classid = c.classid
            WHERE cs.studentid = %s AND c.academicyear = %s
        """, (student_id, target_year))
        
        existing_enrollment = cursor.fetchone()
        
        if existing_enrollment:
            flash(
                f"Student is already enrolled in {existing_enrollment[0]} for {target_year}",
                "warning"
            )
            return redirect(url_for('admin.manage_class_students', class_id=class_id))
        
        # Step 3: Add to class if checks pass
        cursor.execute("""
            INSERT INTO class_students (classid, studentid, enrollmentdate)
            VALUES (%s, %s, CURRENT_DATE)
        """, (class_id, student_id))
        
        conn.commit()
        flash("Student added to class successfully!", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin.manage_class_students', class_id=class_id))

@admin_routes.route('/remove_student_from_class', methods=['POST'])
@admin_login_required
def remove_student_from_class():
    """Remove student from class"""
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        student_id = request.form.get('student_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM class_students
                WHERE classid = %s AND studentid = %s
            """, (class_id, student_id))
            conn.commit()
            flash("Student removed from class successfully", "success")
        except Exception as e:
            conn.rollback()
            print(f"Error removing student from class: {str(e)}")
            flash("Failed to remove student from class", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return redirect(url_for('admin.manage_class_students', class_id=class_id))




#===================================================================
#MANAGE PERFORMANCE LEVELS
#======================================================================

# Add these queries to your queries file (e.g., admin_queries.py or performance_queries.py)
GET_ALL_PERFORMANCE_LEVELS_QUERY = """
    SELECT PerformanceLevelID, LevelName, LevelDescription, ScoreValue 
    FROM Performance 
    ORDER BY ScoreValue DESC;
"""

INSERT_PERFORMANCE_LEVEL_QUERY = """
    INSERT INTO Performance (LevelName, LevelDescription, ScoreValue)
    VALUES (%s, %s, %s);
"""

GET_PERFORMANCE_LEVEL_BY_ID_QUERY = """
    SELECT PerformanceLevelID, LevelName, LevelDescription, ScoreValue
    FROM Performance
    WHERE PerformanceLevelID = %s;
"""

UPDATE_PERFORMANCE_LEVEL_QUERY = """
    UPDATE Performance
    SET LevelName = %s, LevelDescription = %s, ScoreValue = %s
    WHERE PerformanceLevelID = %s;
"""

DELETE_PERFORMANCE_LEVEL_QUERY = """
    DELETE FROM Performance
    WHERE PerformanceLevelID = %s;
"""

# Then add these routes to your admin_routes.py

@admin_routes.route('/manage_performance_levels')
@admin_login_required
def manage_performance_levels():
    """Display all performance levels"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_ALL_PERFORMANCE_LEVELS_QUERY)
        performance_levels = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching performance levels: {e}")
        performance_levels = []
        flash("An error occurred while fetching performance levels.", "danger")
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/manage_performance_levels.html', 
                         performance_levels=performance_levels)

@admin_routes.route('/add_performance_level', methods=['POST'])
@admin_login_required
def add_performance_level():
    """Handle adding a new performance level"""
    if request.method == 'POST':
        level_name = request.form['level-name']
        level_description = request.form['level-description']
        score_value = request.form['score-value']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(INSERT_PERFORMANCE_LEVEL_QUERY, 
                         (level_name, level_description, score_value))
            conn.commit()
            flash("Performance level added successfully!", "success")
        except Exception as e:
            print(f"Error adding performance level: {e}")
            conn.rollback()
            flash("An error occurred while adding the performance level.", "danger")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('admin.manage_performance_levels'))                                                                                                               

@admin_routes.route('/get_performance_level/<int:level_id>', methods=['GET'])
@admin_login_required
def get_performance_level(level_id):
    """Fetch performance level details for editing"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(GET_PERFORMANCE_LEVEL_BY_ID_QUERY, (level_id,))
        level = cursor.fetchone()

        if level:
            return {
                'PerformanceLevelID': level[0],
                'LevelName': level[1],
                'LevelDescription': level[2],
                'ScoreValue': level[3]
            }
        else:
            return {'error': 'Performance level not found'}, 404
    finally:
        cursor.close()
        conn.close()

@admin_routes.route('/edit_performance_level', methods=['POST'])
@admin_login_required
def edit_performance_level():
    """Handle performance level edit form submission"""
    if request.method == 'POST':
        level_id = request.form['level_id']
        level_name = request.form['level-name']
        level_description = request.form['level-description']
        score_value = request.form['score-value']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(UPDATE_PERFORMANCE_LEVEL_QUERY, 
                         (level_name, level_description, score_value, level_id))
            conn.commit()
            flash("Performance level updated successfully!", "success")
        except Exception as e:
            print(f"Error updating performance level: {e}")
            conn.rollback()
            flash("An error occurred while updating the performance level.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_performance_levels'))

@admin_routes.route('/delete_performance_level', methods=['POST'])
@admin_login_required
def delete_performance_level():
    """Handle performance level deletion"""
    if request.method == 'POST':
        level_id = request.form['level_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the performance level is used in any rubrics
            cursor.execute("""
                SELECT COUNT(*) FROM RubricPerformanceLevels
                WHERE PerformanceLevelID = %s
            """, (level_id,))
            usage_count = cursor.fetchone()[0]

            if usage_count > 0:
                flash("Cannot delete performance level that is used in rubrics.", "warning")
            else:
                cursor.execute(DELETE_PERFORMANCE_LEVEL_QUERY, (level_id,))
                conn.commit()
                flash("Performance level deleted successfully!", "success")
        except Exception as e:
            print(f"Error deleting performance level: {e}")
            conn.rollback()
            flash("An error occurred while deleting the performance level.", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('admin.manage_performance_levels'))