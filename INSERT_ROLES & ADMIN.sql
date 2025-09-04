--Initially insert roles
INSERT INTO Roles (RoleName) VALUES
('student'),
('teacher'),
('parent'),
('admin');

--INSERT THE ADMIN
INSERT INTO Users (
    FirstName, 
    LastName, 
    Email, 
    Phone, 
    PasswordHash, 
    RoleID, 
    is_active, 
    created_at
)
VALUES (
    'Wamilimo',                -- FirstName
    'Hillary',                 -- LastName
    'youremail@gmail.com',    -- Email
    '0710578788',           -- Phone
    'scrypt:32768:8:1$gNzx5oJ93OFcsLSj$51057e14ed0165cfe7d7823511a387184092a65eb01d5dce1f6ce2325f33f2b2e4761ffef95ea59692822be9d0d314e3fe05d654deee8c700eb09cd07fdf8a18',    -- PasswordHash (replace with the hashed password from Step 2)
    4,                      -- RoleID (4 for Admin)
    TRUE,                   -- is_active (set to TRUE for active account)
    NOW()                   -- created_at (current timestamp)
);




