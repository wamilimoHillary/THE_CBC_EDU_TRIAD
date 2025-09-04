
-- Create Roles Table
CREATE TABLE Roles (
    RoleID SERIAL PRIMARY KEY,
    RoleName VARCHAR(50) NOT NULL UNIQUE
);

-- Create Users Table (Now includes Phone and reset functionality)
CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20) UNIQUE NOT NULL,  -- Added phone number column
    PasswordHash VARCHAR(255) NOT NULL,
    RoleID INT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    email_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    token_expiry TIMESTAMP,
    reset_token VARCHAR(255),          -- Added reset token column
    reset_expiry TIMESTAMP,           -- Added reset expiry column
    CONSTRAINT fk_users_role FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE CASCADE
);


-- Create Teachers Table
CREATE TABLE Teachers (
    TeacherID SERIAL PRIMARY KEY,
    UserID INT UNIQUE NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    HireDate DATE NOT NULL
);

-- Create Parents Table
CREATE TABLE Parents (
    ParentID SERIAL PRIMARY KEY,
    UserID INT UNIQUE NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE
);


-- Create Students Table 
CREATE TABLE Students (
    StudentID SERIAL PRIMARY KEY,
    UserID INT UNIQUE NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    ParentID INT REFERENCES Parents(ParentID) ON DELETE SET NULL,
    StudentNumber VARCHAR(20) UNIQUE NOT NULL, 
    RegistrationDate DATE NOT NULL
);

-- Create Tasks Table 
CREATE TABLE Tasks (
    TaskID SERIAL PRIMARY KEY,
    TeacherID INT NOT NULL REFERENCES Teachers(TeacherID) ON DELETE CASCADE,
    Title VARCHAR(255) NOT NULL,  -- Added Title column
    TaskDescription TEXT NOT NULL,
    DueDate DATE NOT NULL,
    createdat TIMESTAMP DEFAULT NOW()  -- Added createdat column
);

-- Create Feedback Table
CREATE TABLE Feedback (
    FeedbackID SERIAL PRIMARY KEY,
    ProjectID INT NOT NULL REFERENCES Projects(ProjectID) ON DELETE CASCADE,
    UserID INT NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    FeedbackText TEXT NOT NULL,
    FeedbackDate DATE NOT NULL
);

-- Create Competencies Table
CREATE TABLE Competencies (
    CompetencyID SERIAL PRIMARY KEY,
    CompetencyName VARCHAR(100) NOT NULL UNIQUE,
    CompetencyDescription TEXT
);


-- Create Criteria Table
CREATE TABLE Criteria (
    CriteriaID SERIAL PRIMARY KEY,
    CompetencyID INT NOT NULL REFERENCES Competencies(CompetencyID) ON DELETE CASCADE,
    CriteriaName VARCHAR(100) NOT NULL UNIQUE,
    CriteriaDescription TEXT
);

-- Create Performance Table
CREATE TABLE Performance (
    PerformanceLevelID SERIAL PRIMARY KEY,
    LevelName VARCHAR(50) NOT NULL UNIQUE,
    LevelDescription TEXT,
    ScoreValue INT NOT NULL CHECK (ScoreValue BETWEEN 0 AND 100)
);

-- Create Rubric Table
CREATE TABLE Rubric (
    RubricID SERIAL PRIMARY KEY,
    CriteriaID INT NOT NULL REFERENCES Criteria(CriteriaID) ON DELETE CASCADE,
    PerformanceLevelID INT NOT NULL REFERENCES Performance(PerformanceLevelID) ON DELETE CASCADE,
    Description TEXT
);

-- Create Competency Assessments Table
CREATE TABLE competency_assessments (
    assessment_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(studentid) ON DELETE CASCADE,
    task_id INT NOT NULL REFERENCES tasks(taskid) ON DELETE CASCADE,
    competency_id INT NOT NULL REFERENCES competencies(competencyid) ON DELETE CASCADE,
    overall_score DECIMAL(5,2),
    feedback TEXT,
    assessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, task_id, competency_id)
);

-- create criteria rating table
CREATE TABLE criteria_ratings (
    rating_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES competency_assessments(assessment_id) ON DELETE CASCADE,
    criteria_id INT NOT NULL REFERENCES criteria(criteriaid) ON DELETE CASCADE,
    performance_level_id INT NOT NULL REFERENCES performance(performancelevelid),
    feedback TEXT,
    UNIQUE(assessment_id, criteria_id)
);
-- Create Reports Table
CREATE TABLE Reports (
    ReportID SERIAL PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES Students(StudentID) ON DELETE CASCADE,
    TeacherID INT REFERENCES Teachers(TeacherID) ON DELETE SET NULL,
    ReportDate DATE NOT NULL,
    ReportFilePath VARCHAR(255) NOT NULL
);
CREATE TABLE classes (
    classid SERIAL PRIMARY KEY,
    teacherid INT NOT NULL REFERENCES teachers(teacherid) ON DELETE CASCADE,
    classname VARCHAR(100) NOT NULL,
    academicyear VARCHAR(20) NOT NULL,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE class_students (
    classid INT NOT NULL REFERENCES classes(classid) ON DELETE CASCADE,
    studentid INT NOT NULL REFERENCES students(studentid) ON DELETE CASCADE,
    enrollmentdate DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (classid, studentid)
);
-- Create Student Groups Table with teacherid column
CREATE TABLE StudentGroups (
    GroupID SERIAL PRIMARY KEY,             -- Auto-generated unique ID for each group
    GroupName VARCHAR(100) NOT NULL UNIQUE, -- Name of the group, must be unique
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the group is created
    teacherid INT REFERENCES Teachers(teacherid) -- Link to the teacher who oversees the group, references Teachers table
); 

-- Create Projects Table with additional columns for assessment status
CREATE TABLE Projects (
    projectid SERIAL PRIMARY KEY,                -- Auto-generated unique ID for each project
    taskid INT NOT NULL REFERENCES Tasks(taskid) ON DELETE CASCADE,  -- Link to the related task
    studentid INT REFERENCES Students(studentid) ON DELETE CASCADE,  -- Link to the student who submits the project
    groupid INT REFERENCES StudentGroups(groupid) ON DELETE CASCADE, -- Link to the student group (if any)
    submitter_id INT NOT NULL REFERENCES Students(studentid) ON DELETE CASCADE,  -- ID of the student submitting the project
    file_name VARCHAR(255) NOT NULL,              -- Name of the project file
    projectfilepath VARCHAR(512) NOT NULL,        -- Path where the project file is stored
    is_late BOOLEAN NOT NULL DEFAULT FALSE,       -- Whether the project is late or not
    file_size BIGINT NOT NULL,                    -- Size of the project file in bytes
    file_type VARCHAR(50) NOT NULL,               -- Type of file (e.g., pdf, docx, etc.)
    submission_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the project is submitted
    modified_at TIMESTAMP,                        -- Timestamp for any modifications made to the project
    is_assessed BOOLEAN DEFAULT FALSE,            -- Whether the project has been assessed or not
    assessment_time TIMESTAMP                     -- Timestamp when the project was assessed
);

-- Table for assigning tasks to individual students, whole classes, or groups
CREATE TABLE TaskAssignments (
    AssignmentID SERIAL PRIMARY KEY,
    TaskID INT NOT NULL REFERENCES Tasks(TaskID) ON DELETE CASCADE,
    StudentID INT REFERENCES Students(StudentID) ON DELETE CASCADE,  -- If assigned to a single student
    ClassID INT REFERENCES Classes(ClassID) ON DELETE CASCADE,      -- If assigned to a whole class
    GroupID INT REFERENCES StudentGroups(GroupID) ON DELETE CASCADE, -- If assigned to a student group
    AssignedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE GroupMembers (
    GroupID INT NOT NULL REFERENCES StudentGroups(GroupID) ON DELETE CASCADE,
    StudentID INT NOT NULL REFERENCES Students(StudentID) ON DELETE CASCADE,
    AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (GroupID, StudentID)
);




CREATE TABLE task_competencies (
    taskid INT NOT NULL REFERENCES tasks(taskid) ON DELETE CASCADE,
    competencyid INT NOT NULL REFERENCES competencies(competencyid) ON DELETE CASCADE,
    PRIMARY KEY (taskid, competencyid)
);



