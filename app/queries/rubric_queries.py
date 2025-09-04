# Rubric Queries
GET_ALL_RUBRICS_QUERY = """
    SELECT r.RubricID, c.CriteriaName, p.LevelName, r.Description
    FROM Rubric r
    JOIN Criteria c ON r.CriteriaID = c.CriteriaID
    JOIN Performance p ON r.PerformanceLevelID = p.PerformanceLevelID
    ORDER BY r.RubricID;
"""

GET_CRITERIA_FOR_DROPDOWN_QUERY = """
    SELECT c.CriteriaID, c.CriteriaName, comp.CompetencyName 
    FROM Criteria c
    JOIN Competencies comp ON c.CompetencyID = comp.CompetencyID;
"""

GET_PERFORMANCE_LEVELS_QUERY = "SELECT * FROM Performance;"

INSERT_RUBRIC_QUERY = """
    INSERT INTO Rubric (CriteriaID, PerformanceLevelID, Description)
    VALUES (%s, %s, %s);
"""

GET_RUBRIC_BY_ID_QUERY = """
    SELECT RubricID, CriteriaID, PerformanceLevelID, Description
    FROM Rubric
    WHERE RubricID = %s;
"""

UPDATE_RUBRIC_QUERY = """
    UPDATE Rubric
    SET CriteriaID = %s, PerformanceLevelID = %s, Description = %s
    WHERE RubricID = %s;
"""

DELETE_RUBRIC_QUERY = "DELETE FROM Rubric WHERE RubricID = %s;"