# Project Submission Queries
GET_TASK_DETAILS_QUERY = """
    SELECT t.*, u.firstname, u.lastname 
    FROM tasks t
    JOIN teachers te ON t.teacherid = te.teacherid
    JOIN users u ON te.userid = u.userid
    WHERE t.taskid = %s
"""

GET_TASK_GROUP_QUERY = """
    SELECT sg.groupid, sg.groupname 
    FROM taskassignments ta
    JOIN studentgroups sg ON ta.groupid = sg.groupid
    WHERE ta.taskid = %s 
    LIMIT 1
"""

INSERT_PROJECT_QUERY = """
    INSERT INTO projects (
        taskid, studentid, groupid, submitter_id, 
        file_name, projectfilepath, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""