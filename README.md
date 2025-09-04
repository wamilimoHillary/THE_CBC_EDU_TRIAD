CBC EDU TRIAD README

1. Clone the project.
        https://github.com/wamilimoHillary/cbc_edu_triad modularized

2. Navigate to the project location using your favorite IDE (e.g., VS Code).
Create your environment file:
   - Copy `.env.example` to `.env`
   - Update it with your own values (database password, mail credentials, secret key, etc.)
3. Install requirements:
        pip install -r requirements.txt

4. In PgAdmin4/Postgres, create a database Set your password for it.:
        CREATE DATABASE "cbc_edu_triad";

5. Run the CREATE TABLES SQL file.
NB: If creating the tables one after the other, they must appear in the order they are due to constraints.

6. Insert roles in the Roles table.
Run the query in the insert roles file:
    --Initially insert roles
        INSERT INTO Roles (RoleName) VALUES
        ('student'),
        ('teacher'),
        ('parent'),
        ('admin');


7. Insert Admin. Run the insert admin query.
Put your actual credentials in the query (i.e., same email, number, and name you’ll use in Step 8).

                
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

8. Signup and login in Mailtrap.io using the email in Step 7.

    > In Inbox → Sandbox, select your project.

       > Go to My Sandbox → click the three dots (⋮) → Edit Project.

       >  Rename the project to cbc_edu_triad.

       > Under Settings → SMTP credentials, copy the username and mail password of your created project.

       > Paste them into your .env file.



9. Go to .env file:

Under DB configuration, edit by putting your DB username & password created in Step 4.

Under Mail configuration, edit your Mailtrap username and mail password from Step 8.


Run the project:

python run.py

Then open: http://127.0.0.1:5000

10. If it ran successfully:

Under Menu button, triple-tap the link "am the admin" to get the Admin login form.

Now reset your password there.

Login to Mailtrap (set in Step 8), open your inbox, and get the reset link.

Reset your password, set a new one, and login as admin.



11. It’s your time to enjoy by populating dummy data in each set THE DATA IN IN THE REPORT.

Sample dummy data is in tables.



12. New users like Teachers and Students are added by Admin in the Admin Panel.

Classes, link a Parent to a Student etc.