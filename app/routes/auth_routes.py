from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from app.database import get_db_connection
from app.queries.auth_queries import (
    GET_USER_BY_EMAIL_QUERY, GET_USER_BY_PHONE_QUERY, INSERT_NEW_USER_QUERY,
    VERIFY_EMAIL_QUERY, CHECK_TOKEN_EXPIRY_QUERY, UPDATE_PASSWORD_QUERY,
    GET_TEACHER_BY_EMAIL_QUERY, GET_TEACHER_BY_PHONE_QUERY ,GET_USER_BY_RESET_TOKEN_QUERY, UPDATE_PASSWORD_QUERY,
    UPDATE_RESET_TOKEN_QUERY,GET_STUDENT_BY_EMAIL_OR_NUMBER_QUERY
)
from app.config import Config
import random
import string
from datetime import datetime, timedelta

# Define constants for parents route names
PARENT_LOGIN_ROUTE = 'auth.parent_login'
RESEND_VERIFICATION_ROUTE = 'auth.resend_verification'
PARENT_FORGOT_PASSWORD_ROUTE = 'auth.parent_forgot_password'
PARENT_SIGNUP_ROUTE = 'auth.parent_signup'
VERIFY_EMAIL_ROUTE = 'auth.verify_email'


# Define constants for admin route names
ADMIN_LOGIN_ROUTE = 'auth.admin_login'
ADMIN_DASHBOARD_ROUTE = 'admin.admin_dashboard'
ADMIN_REQUEST_RESET_ROUTE = 'auth.admin_request_reset'
ADMIN_RESET_PASSWORD_ROUTE = 'auth.admin_reset_password'

# Define constants for teacher route names
TEACHER_LOGIN_ROUTE = 'auth.teacher_login' 
TEACHER_DASHBOARD_ROUTE = 'teacher.teachers_dashboard'
TEACHER_FORGOT_PASSWORD_ROUTE = 'auth.teacher_forgot_password'
TEACHER_RESET_PASSWORD_ROUTE = 'auth.teacher_reset_password' 



# Define constants for role IDs
ADMIN_ROLE_ID = 4  # RoleID for admins

auth_routes = Blueprint('auth', __name__)
mail = Mail()

# Function to generate a random email verification token
def generate_token(length=50):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to set token expiry time (e.g., 3 minutes)
def get_token_expiry():
    return datetime.now() + timedelta(minutes=3)
# Parent Signup Route
@auth_routes.route('/parent_signup', methods=['GET', 'POST'])
def parent_signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        # Define role_id for parent users
        role_id = 3  # RoleID=3 is for parents

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for(PARENT_SIGNUP_ROUTE))

        # Generate email verification token
        token = generate_token()
        token_expiry = get_token_expiry()

        try:
            # Insert new user as a parent using the imported query
            cursor.execute(INSERT_NEW_USER_QUERY, (first_name, last_name, email, phone, password_hash, role_id, False, token, token_expiry))
            conn.commit()

            # Get the newly created user's ID
            cursor.execute("SELECT UserID FROM Users WHERE Email = %s;", (email,))
            user_id = cursor.fetchone()[0]

            # Insert into Parents table
            cursor.execute("INSERT INTO Parents (UserID) VALUES (%s);", (user_id,))
            conn.commit()

            # Send verification email with clickable link
            verification_link = url_for('auth.verify_email_token', token=token, _external=True)
            msg = Message("Email Verification", sender=Config.MAIL_USERNAME, recipients=[email])
            msg.html = f"""
            <p>Click the link below to verify your email:</p>
            <p><a href="{verification_link}">Verify Your Email</a></p>
            """
            mail.send(msg)

            flash("Your account has been created. Please check your email for verification.", "success")
            return redirect(url_for(VERIFY_EMAIL_ROUTE))

        except Exception as e:
            print(f"Error inserting user: {e}")
            conn.rollback()
            flash("An error occurred while creating your account.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/parent_signup.html')

# Email verification route
@auth_routes.route('/verify_email/<token>')
def verify_email_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(CHECK_TOKEN_EXPIRY_QUERY, (token,))
        user = cursor.fetchone()

        if user:
            token_expiry = user[1]  # Access token_expiry from tuple
            if datetime.now() > token_expiry:
                flash("The verification link has expired. Please request a new one.", "danger")
                return redirect(url_for(RESEND_VERIFICATION_ROUTE))

            cursor.execute(VERIFY_EMAIL_QUERY, (token,))
            conn.commit()
            flash("Your email has been successfully verified. Please log in.", "success")

        else:
            flash("Invalid or expired verification link.", "danger")

        return redirect(url_for(PARENT_LOGIN_ROUTE))

    finally:
        cursor.close()
        conn.close()

# Route for handling the resend verification request
@auth_routes.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database
            cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
            user = cursor.fetchone()

            if user:
                # Generate a new token and set its expiry
                new_token = generate_token()
                new_token_expiry = get_token_expiry()

                # Update the user's token and token expiry in the database
                cursor.execute("""
                    UPDATE Users 
                    SET email_token = %s, token_expiry = %s 
                    WHERE Email = %s;
                """, (new_token, new_token_expiry, email))
                conn.commit()

                # Send the new verification email with clickable link
                verification_link = url_for('auth.verify_email_token', token=new_token, _external=True)
                msg = Message("Email Verification", sender=Config.MAIL_USERNAME, recipients=[email])
                msg.html = f"""
                <p>Click the link below to verify your email:</p>
                <p><a href="{verification_link}">Verify Your Email</a></p>
                """
                mail.send(msg)

                flash("A new verification link has been sent to your email.", "success")
                return redirect(url_for(VERIFY_EMAIL_ROUTE))

            else:
                flash("No account found with this email address.", "danger")
                return redirect(url_for(RESEND_VERIFICATION_ROUTE))

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/resend_verification.html')


# Parent Login Route
# Define constants for role IDs
PARENT_ROLE_ID = 3  # RoleID=3 is for parents

@auth_routes.route('/parent_login', methods=['GET', 'POST'])
def parent_login():
    if request.method == 'POST':
        email_or_phone = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Determine if input is email or phone
            if '@' in email_or_phone:
                cursor.execute("""
                    SELECT u.userid, u.firstname, u.lastname, u.email, u.passwordhash, 
                           u.roleid, u.is_active, p.parentid
                    FROM users u
                    JOIN parents p ON u.userid = p.userid
                    WHERE u.email = %s AND u.roleid = %s
                """, (email_or_phone, PARENT_ROLE_ID))
            else:
                cursor.execute("""
                    SELECT u.userid, u.firstname, u.lastname, u.email, u.passwordhash, 
                           u.roleid, u.is_active, p.parentid
                    FROM users u
                    JOIN parents p ON u.userid = p.userid
                    WHERE u.phone = %s AND u.roleid = %s
                """, (email_or_phone, PARENT_ROLE_ID))

            user = cursor.fetchone()

            if user:
                if not user[6]:  # Check if email is verified (index 6 is is_active)
                    flash("Your account is not verified. Please verify your email to log in.", "danger")
                    return redirect(url_for('auth.resend_verification'))

                if check_password_hash(user[4], password):  # index 4 is passwordhash
                    # Store user_id, parent_id, and role in session
                    session['user_id'] = user[0]  # From users table
                    session['parent_id'] = user[7]  # From parents table
                    session['role'] = 'parent'
                    session['parent_name'] = f"{user[1]} {user[2]}"  # Optional: Store name
                    flash("Logged in!", "success")
                    return redirect(url_for('parent.parents_dashboard'))
                else:
                    flash("Incorrect password!.", "danger")
            else:
                flash("No parent account found with the provided credentials.", "danger")

        except Exception as e:
            print(f"Login error: {str(e)}")  # Simple error logging
            flash("An error occurred during login", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/parent_login.html')
                                                  


# Parent Forgot Password Route
@auth_routes.route('/parent_request_reset', methods=['GET', 'POST'])
def parent_forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database
            cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
            user = cursor.fetchone()

            if user:
                # Generate a reset token and set its expiry
                reset_token = generate_token()
                reset_token_expiry = get_token_expiry()

                # Update the user's reset token and expiry in the database
                cursor.execute(UPDATE_RESET_TOKEN_QUERY, (reset_token, reset_token_expiry, email))
                conn.commit()

                # Send the reset password email
                reset_link = url_for('auth.parent_reset_password', token=reset_token, _external=True)
                msg = Message("Reset Your Password-", sender=Config.MAIL_USERNAME, recipients=[email])
                msg.body = f"Click the link to reset your password: {reset_link}"
                mail.send(msg)

                flash("A password reset link has been sent to your email!.", "success")
                return redirect(url_for(PARENT_LOGIN_ROUTE))
            else:
                flash("No account found with this email address.", "danger")
                return redirect(url_for(PARENT_FORGOT_PASSWORD_ROUTE))

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/parent_request_reset.html')

# Reset Password Route
@auth_routes.route('/parent_reset_password/<token>', methods=['GET', 'POST'])
def parent_reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the token is valid and not expired
        cursor.execute(GET_USER_BY_RESET_TOKEN_QUERY, (token,))
        user = cursor.fetchone()

        if user:
            reset_expiry = user[1]  # Access reset_expiry from tuple
            if datetime.now() > reset_expiry:
                flash("The reset link has expired. Kindly request a new one.", "danger")
                return redirect(url_for(PARENT_FORGOT_PASSWORD_ROUTE))

            if request.method == 'POST':
                password = request.form['password']
                confirm_password = request.form['confirm_password']

                if password != confirm_password:
                    flash("Passwords do not match!!.", "danger")
                    return redirect(url_for('auth.parent_reset_password', token=token))

                # Hash the new password
                password_hash = generate_password_hash(password)

                # Update the user's password in the database
                cursor.execute(UPDATE_PASSWORD_QUERY, (password_hash, user[0]))
                conn.commit()

                flash("Your password has been reset successfully!. Please log in.", "success")
                return redirect(url_for(PARENT_LOGIN_ROUTE))

            return render_template('auth/parent_reset_password.html', token=token)
        else:
            flash("Invalid or expired reset link!.", "danger")
            return redirect(url_for(PARENT_FORGOT_PASSWORD_ROUTE))

    finally:
        cursor.close()
        conn.close()

# Parent Logout Route
@auth_routes.route('/logout')
def parent_logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for(PARENT_LOGIN_ROUTE))



# Admin Login Route
@auth_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Fetch admin by email
            cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
            admin = cursor.fetchone()

            if admin:
                
                # Check if the account is active and the role is Admin (RoleID = 4)
                if admin[6] == ADMIN_ROLE_ID and admin[7] == True:  
                    if check_password_hash(admin[5], password):  # Check password
                        session['admin_id'] = admin[0]  # Store admin ID in session
                        flash("Login successful!!", "success")
                        return redirect(url_for(ADMIN_DASHBOARD_ROUTE))
                    else:
                        flash("Incorrect password!!.", "danger")
                else:
                    flash("You do not have permission to access this page.", "danger")
            else:
                flash("No admin account found with this email address.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('admin/admin_login.html')

# Admin Forgot Password Route
@auth_routes.route('/admin_request_reset', methods=['GET', 'POST'])
def admin_request_reset():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database
            cursor.execute(GET_USER_BY_EMAIL_QUERY, (email,))
            admin = cursor.fetchone()

            if admin and admin[6] == ADMIN_ROLE_ID: 
                # Generate a reset token and set its expiry
                reset_token = generate_token()
                reset_token_expiry = get_token_expiry()

                # Update the admin's reset token and expiry in the database
                cursor.execute(""" 
                    UPDATE Users 
                    SET reset_token = %s, reset_expiry = %s 
                    WHERE Email = %s;
                """, (reset_token, reset_token_expiry, email))
                conn.commit()

                # Send the reset password email with clickable link
                reset_link = url_for(ADMIN_RESET_PASSWORD_ROUTE, token=reset_token, _external=True)
                msg = Message("Reset Your Password", sender=Config.MAIL_USERNAME, recipients=[email])
                msg.html = f"""
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Your Password</a></p>
                """
                mail.send(msg)

                flash("A password reset link has been sent to your email.", "success")
                return redirect(url_for(ADMIN_LOGIN_ROUTE))
            else:
                flash("No admin account found with this email address.", "danger")
                return redirect(url_for(ADMIN_REQUEST_RESET_ROUTE))

        finally:
            cursor.close()
            conn.close()

    return render_template('admin/admin_request_reset.html')

# Admin Reset Password Route
@auth_routes.route('/admin_reset_password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the token is valid and not expired
        cursor.execute("""
            SELECT UserID, reset_expiry 
            FROM Users 
            WHERE reset_token = %s;
        """, (token,))
        admin = cursor.fetchone()

        if admin:
            reset_expiry = admin[1]  # Access reset_expiry from tuple
            if datetime.now() > reset_expiry:
                flash("The reset link has expired. Please request a new one.", "danger")
                return redirect(url_for(ADMIN_REQUEST_RESET_ROUTE))

            if request.method == 'POST':
                password = request.form['password']
                confirm_password = request.form['confirm_password']

                if password != confirm_password:
                    flash("Passwords do not match.", "danger")
                    return redirect(url_for(ADMIN_RESET_PASSWORD_ROUTE, token=token))

                # Hash the new password
                password_hash = generate_password_hash(password)

                # Update the admin's password in the database
                cursor.execute(UPDATE_PASSWORD_QUERY, (password_hash, admin[0]))
                conn.commit()

                # Clear the reset token and expiry
                cursor.execute("""
                    UPDATE Users 
                    SET reset_token = NULL, reset_expiry = NULL 
                    WHERE UserID = %s;
                """, (admin[0],))
                conn.commit()

                flash("Your password has been reset successfully. Please log in.", "success")
                return redirect(url_for(ADMIN_LOGIN_ROUTE))

            return render_template('admin/admin_reset_password.html', token=token)
        else:
            flash("Invalid or expired reset link.", "danger")
            return redirect(url_for(ADMIN_REQUEST_RESET_ROUTE))

    finally:
        cursor.close()
        conn.close()


# Admin Logout Route
@auth_routes.route('/admin_logout')
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for(ADMIN_LOGIN_ROUTE))


#TEACHER LOGIN ROUTES

# Define constants for role IDs
TEACHER_ROLE_ID = 2  # RoleID=2 is for teachers

# TEACHER LOGIN ROUTES
@auth_routes.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email_or_phone = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Determine if input is email or phone
            if '@' in email_or_phone:
                cursor.execute("""
                    SELECT u.userid, u.firstname, u.lastname, u.email, u.passwordhash, 
                           u.roleid, u.is_active, t.teacherid
                    FROM users u
                    JOIN teachers t ON u.userid = t.userid
                    WHERE u.email = %s AND u.roleid = %s
                """, (email_or_phone, TEACHER_ROLE_ID))
            else:
                cursor.execute("""
                    SELECT u.userid, u.firstname, u.lastname, u.email, u.passwordhash, 
                           u.roleid, u.is_active, t.teacherid
                    FROM users u
                    JOIN teachers t ON u.userid = t.userid
                    WHERE u.phone = %s AND u.roleid = %s
                """, (email_or_phone, TEACHER_ROLE_ID))

            user = cursor.fetchone()

            if user:
                if not user[6]:  # Check if email is verified (index 6 is is_active)
                    flash("Your account is not verified. Please verify your email to log in.", "danger")
                    return redirect(url_for('auth.resend_verification'))

                if check_password_hash(user[4], password):  # index 4 is passwordhash
                    # Store both user_id and teacher_id in session
                    session['user_id'] = user[0]  # From users table
                    session['teacher_id'] = user[7]  # From teachers table
                    session['role'] = 'teacher'
                    session['teacher_name'] = f"{user[1]} {user[2]}"
                    flash("Login successful!", "success")
                    return redirect(url_for('teacher.teachers_dashboard'))
                else:
                    flash("Incorrect password.", "danger")
            else:
                flash("No teacher account found with the provided credentials.", "danger")

        except Exception as e:
            print(f"Login error: {str(e)}")  # Simple print instead of logger
            flash("An error occurred during login", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/teacher_login.html')

# Teacher Forgot Password Route
@auth_routes.route('/teacher_forgot_password', methods=['GET', 'POST'])
def teacher_forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if the email exists in the database and belongs to a teacher
            cursor.execute(GET_TEACHER_BY_EMAIL_QUERY, (email, TEACHER_ROLE_ID))
            user = cursor.fetchone()

            if user:
                # Generate a reset token and set its expiry
                reset_token = generate_token()
                reset_token_expiry = get_token_expiry()

                # Update the user's reset token and expiry in the database
                cursor.execute("""
                    UPDATE Users 
                    SET reset_token = %s, reset_expiry = %s 
                    WHERE Email = %s;
                """, (reset_token, reset_token_expiry, email))
                conn.commit()

                # Send the reset password email with clickable link
                reset_link = url_for(TEACHER_RESET_PASSWORD_ROUTE, token=reset_token, _external=True)
                msg = Message("Reset Your Password", sender=Config.MAIL_USERNAME, recipients=[email])
                msg.html = f"""
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Your Password</a></p>
                """
                mail.send(msg)

                flash("A password reset link has been sent to your email.", "success")
                return redirect(url_for(TEACHER_LOGIN_ROUTE))
            else:
                flash("No teacher account found with this email address.", "danger")
                return redirect(url_for(TEACHER_FORGOT_PASSWORD_ROUTE))

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/teacher_forgot_password.html')

# Teacher Reset Password Route
@auth_routes.route('/teacher_reset_password/<token>', methods=['GET', 'POST'])
def teacher_reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the token is valid and not expired
        cursor.execute("""
            SELECT UserID, reset_expiry 
            FROM Users 
            WHERE reset_token = %s;
        """, (token,))
        user = cursor.fetchone()

        if user:
            reset_expiry = user[1]  # Access reset_expiry from tuple
            if datetime.now() > reset_expiry:
                flash("The reset link has expired. Please request a new one.", "danger")
                return redirect(url_for(TEACHER_FORGOT_PASSWORD_ROUTE))

            if request.method == 'POST':
                password = request.form['password']
                confirm_password = request.form['confirm_password']

                if password != confirm_password:
                    flash("Passwords do not match.", "danger")
                    return redirect(url_for(TEACHER_RESET_PASSWORD_ROUTE, token=token))

                # Hash the new password
                password_hash = generate_password_hash(password)

                # Update the user's password in the database
                cursor.execute(UPDATE_PASSWORD_QUERY, (password_hash, user[0]))
                conn.commit()

                # Clear the reset token and expiry
                cursor.execute("""
                    UPDATE Users 
                    SET reset_token = NULL, reset_expiry = NULL 
                    WHERE UserID = %s;
                """, (user[0],))
                conn.commit()

                flash("Your password has been reset successfully. Please log in.", "success")
                return redirect(url_for(TEACHER_LOGIN_ROUTE))

            return render_template('auth/teacher_reset_password.html', token=token)
        else:
            flash("Invalid or expired reset link.", "danger")
            return redirect(url_for(TEACHER_FORGOT_PASSWORD_ROUTE))

    finally:
        cursor.close()
        conn.close()


# Teacher Logout Route
@auth_routes.route('/teacher_logout')
def teacher_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for(TEACHER_LOGIN_ROUTE))


# Student Login Route
# Student Login Route
@auth_routes.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email_or_student_number = request.form['email_or_student_number']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Updated query joins Users and Students to get names
            cursor.execute("""
                SELECT u.UserID, u.PasswordHash, u.is_active, u.FirstName, u.LastName
                FROM Users u
                JOIN Students s ON s.UserID = u.UserID
                WHERE u.Email = %s OR s.StudentNumber = %s
            """, (email_or_student_number, email_or_student_number))
            
            student = cursor.fetchone()

            if student:
                if not student[2]:  # is_active
                    flash("Your account is not active. Please contact support.", "danger")
                    return redirect(url_for('auth.student_login'))

                if check_password_hash(student[1], password):  # PasswordHash
                    # Get StudentID from Students table
                    cursor.execute("""
                        SELECT StudentID FROM Students 
                        WHERE UserID = %s
                    """, (student[0],))  # UserID

                    student_id_result = cursor.fetchone()

                    if student_id_result:
                        session['user_id'] = student[0]
                        session['student_id'] = student_id_result[0]
                        session['student_name'] = f"{student[3]} {student[4]}"  # FirstName + LastName

                        flash("Login successful!", "success")
                        return redirect(url_for('student.student_dashboard'))
                    else:
                        flash("Student record not found.", "danger")
                else:
                    flash("Incorrect password.", "danger")
            else:
                flash("No account found with the provided email or student number.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('auth/student_login.html')


 #student logout
@auth_routes.route("/student_logout")
def student_logout():
    flash("You have been logged out..", "success")
    return redirect(url_for('auth.student_login'))  


#student forgot password

    
