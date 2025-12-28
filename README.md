This project was built to demonstrate my knowledge of practical database design, normalization, query optimization, and data integrity in a real-world scenario.

**Database Schema Overview**
The database is structured around a one-to-many relationship between users and their logged lifts.

**Database structure:**
Users table:
CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            weight REAL,
            dob DATE,
            volume_of_lifts REAL
        );
        
Each user has their unique identifier and username
Constraints enable uniqueness and prevent false inputs


CREATE TABLE lifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lift_name TEXT NOT NULL,
            weight REAL NOT NULL,
            reps INTEGER NOT NULL,
            rpe REAL,
            entry_date TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
Implements a foreign key constraint to enforce integrity
supports the lift entries per user without data duplication
seperates logical entry date from record creation timestamp.

Users and lifts are separate to allow the correct use of the table joins
User_id is a foreign key to enable the tables to join together, either using a left, inner or a regular join



Password hashing is included within the project. This creates a unique hash for every password created with a valid salt for the password, SQL implementation for parameterized queries 

**Future Improvements:**
- Normalize lift data by separating exercises and workout sessions. 
- Add indexing on queried fields
- Remove aggregates

**Planned Features**
- make a secure two-factor authentication
- password reset functionality with token-based validation
- Role-based access considerations for expansions.
