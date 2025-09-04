# Competency Queries
GET_ALL_COMPETENCIES_QUERY = "SELECT CompetencyID, CompetencyName, CompetencyDescription FROM Competencies;"

INSERT_COMPETENCY_QUERY = """
    INSERT INTO Competencies (CompetencyName, CompetencyDescription)
    VALUES (%s, %s);
"""

GET_COMPETENCY_BY_ID_QUERY = """
    SELECT CompetencyID, CompetencyName, CompetencyDescription
    FROM Competencies
    WHERE CompetencyID = %s;
"""

UPDATE_COMPETENCY_QUERY = """
    UPDATE Competencies
    SET CompetencyName = %s, CompetencyDescription = %s
    WHERE CompetencyID = %s;
"""

DELETE_COMPETENCY_QUERY = "DELETE FROM Competencies WHERE CompetencyID = %s;"