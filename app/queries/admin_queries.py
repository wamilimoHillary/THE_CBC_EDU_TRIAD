# Queries for Admin Dashboard
COUNT_TEACHERS_QUERY = "SELECT COUNT(*) FROM Teachers;"
COUNT_PARENTS_QUERY = "SELECT COUNT(*) FROM Parents;"
COUNT_STUDENTS_QUERY = "SELECT COUNT(*) FROM Students;"
COUNT_COMPETENCIES_QUERY = "SELECT COUNT(*) FROM competencies;"


# Queries for Managing Students
INSERT_NEW_STUDENT_QUERY = """
    INSERT INTO Students (UserID, ParentID, StudentNumber, RegistrationDate)
    VALUES (%s, %s, %s, %s);
"""

# Query to fetch all students
GET_ALL_STUDENTS_QUERY = """
    SELECT u.UserID, u.FirstName, u.LastName, u.Email, s.StudentNumber, s.RegistrationDate
    FROM Users u
    JOIN Students s ON u.UserID = s.UserID
    ORDER BY u.UserID ASC;
"""

GET_PARENT_BY_EMAIL_QUERY = """
    SELECT p.ParentID
    FROM Parents p
    JOIN Users u ON p.UserID = u.UserID
    WHERE u.Email = %s;
"""

# Query to fetch all parents
# Updated Query to fetch all parents
GET_ALL_PARENTS_QUERY = """
    SELECT u.UserID, u.FirstName, u.LastName, u.Email, u.Phone, u.created_at
    FROM Parents p
    JOIN Users u ON p.UserID = u.UserID
    ORDER BY u.UserID ASC;
"""

# Query to search teachers by name or email
SEARCH_TEACHERS_QUERY = """
    SELECT t.TeacherID, u.FirstName, u.LastName, u.Email, t.HireDate
    FROM Teachers t
    JOIN Users u ON t.UserID = u.UserID
    WHERE u.FirstName LIKE %s OR u.LastName LIKE %s OR u.Email LIKE %s;
"""

# Query to search students by name, email, or student number
SEARCH_STUDENTS_QUERY = """
    SELECT s.StudentID, u.FirstName, u.LastName, u.Email, s.StudentNumber, s.RegistrationDate
    FROM Students s
    JOIN Users u ON s.UserID = u.UserID
    WHERE u.FirstName LIKE %s OR u.LastName LIKE %s OR u.Email LIKE %s OR s.StudentNumber LIKE %s;
"""

# Query to search parents by name or email
SEARCH_PARENTS_QUERY = """
    SELECT p.ParentID, u.FirstName, u.LastName, u.Email, u.Phone, u.created_at
    FROM Parents p
    JOIN Users u ON p.UserID = u.UserID
    WHERE u.FirstName LIKE %s OR u.LastName LIKE %s OR u.Email LIKE %s;
"""



