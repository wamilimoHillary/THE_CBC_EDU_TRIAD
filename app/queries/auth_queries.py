# Query to fetch a user by their email address
# Returns: UserID, FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry
GET_USER_BY_EMAIL_QUERY = """
    SELECT UserID, FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry 
    FROM Users 
    WHERE Email = %s;
"""

# Query to fetch a user by their phone number
# Returns: UserID, FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry
GET_USER_BY_PHONE_QUERY = """
    SELECT UserID, FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry 
    FROM Users 
    WHERE Phone = %s;
"""

# Query to insert a new user into the Users table
# Fields: FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry, created_at
INSERT_NEW_USER_QUERY = """
    INSERT INTO Users 
    (FirstName, LastName, Email, Phone, PasswordHash, RoleID, is_active, email_token, token_expiry, created_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
"""

# Query to verify a user's email by setting is_active to TRUE
# Requires: email_token
VERIFY_EMAIL_QUERY = """
    UPDATE Users 
    SET is_active = TRUE 
    WHERE email_token = %s;
"""
# Query to check if a token is valid and not expired
# Returns: UserID, token_expiry
CHECK_TOKEN_EXPIRY_QUERY = """
    SELECT UserID, token_expiry 
    FROM Users 
    WHERE email_token = %s;
"""

# Query to update a user's password
# Requires: New PasswordHash, UserID
UPDATE_PASSWORD_QUERY = """
    UPDATE Users 
    SET PasswordHash = %s 
    WHERE UserID = %s;
""" 

# Teacher Queries
GET_TEACHER_BY_EMAIL_QUERY = "SELECT * FROM Users WHERE Email = %s AND RoleID = %s;"
GET_TEACHER_BY_PHONE_QUERY = "SELECT * FROM Users WHERE Phone = %s AND RoleID = %s;"

# Parent Forgot Password Queries
GET_USER_BY_EMAIL_QUERY = "SELECT * FROM Users WHERE Email = %s;"
UPDATE_RESET_TOKEN_QUERY = """
    UPDATE Users 
    SET reset_token = %s, reset_expiry = %s 
    WHERE Email = %s;
"""
GET_USER_BY_RESET_TOKEN_QUERY = """
    SELECT UserID, reset_expiry 
    FROM Users 
    WHERE reset_token = %s;
"""
UPDATE_PASSWORD_QUERY = """
    UPDATE Users 
    SET PasswordHash = %s, reset_token = NULL, reset_expiry = NULL 
    WHERE UserID = %s;
"""

# Query to fetch student by email or student number
GET_STUDENT_BY_EMAIL_OR_NUMBER_QUERY = """
    SELECT u.UserID, u.PasswordHash, u.is_active
    FROM Users u
    JOIN Students s ON u.UserID = s.UserID
    WHERE u.Email = %s OR s.StudentNumber = %s;
"""

