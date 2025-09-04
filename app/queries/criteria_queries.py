# Criteria Queries
GET_ALL_CRITERIA_QUERY = """
    SELECT c.CriteriaID, comp.CompetencyName, c.CriteriaName, c.CriteriaDescription
    FROM Criteria c
    JOIN Competencies comp ON c.CompetencyID = comp.CompetencyID
    ORDER BY c.CriteriaID;
"""

GET_COMPETENCIES_FOR_DROPDOWN_QUERY = "SELECT CompetencyID, CompetencyName FROM Competencies;"

INSERT_CRITERIA_QUERY = """
    INSERT INTO Criteria (CompetencyID, CriteriaName, CriteriaDescription)
    VALUES (%s, %s, %s);
"""

GET_CRITERIA_BY_ID_QUERY = """
    SELECT CriteriaID, CompetencyID, CriteriaName, CriteriaDescription
    FROM Criteria
    WHERE CriteriaID = %s;
"""

UPDATE_CRITERIA_QUERY = """
    UPDATE Criteria
    SET CompetencyID = %s, CriteriaName = %s, CriteriaDescription = %s
    WHERE CriteriaID = %s;
"""

CHECK_CRITERIA_USAGE_QUERY = "SELECT COUNT(*) FROM Rubric WHERE CriteriaID = %s;"

DELETE_CRITERIA_QUERY = "DELETE FROM Criteria WHERE CriteriaID = %s;"