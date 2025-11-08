import sqlite3
import hashlib

def connect_db():
    return sqlite3.connect("users.db")

def encrypt_password(password):
    # Hash password for secure storage
    return hashlib.sha256(password.encode()).hexdigest()

def create_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            weight REAL,
            dob DATE,
            volume_of_lifts REAL
        )
    """)
    db.commit()
    db.close()

def create_lifts_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lift_name TEXT NOT NULL,
            weight REAL NOT NULL,
            reps INTEGER NOT NULL,
            rpe REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()

def log_lift(user_id, lift_name, weight, reps, rpe=None):
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cur.fetchone():
        db.close()
        raise ValueError("User not found")
    cur.execute(
        "INSERT INTO lifts (user_id, lift_name, weight, reps, rpe) VALUES (?, ?, ?, ?, ?)",
        (user_id, lift_name, float(weight), int(reps), float(rpe) if rpe is not None else None),
    )
    db.commit()
    db.close()

# categorize lifts, by selection, e.g., bench press, squat, deadlift and other exercises
def categorize_lift(lift_name):
    categories = {
        "bench press": "upper body",
        "squat": "lower body",
        "deadlift": "lower body",
        "overhead press": "upper body",
        "bicep curl": "arms",
        "tricep extension": "arms",
        "pull up": "back",
        "row": "back",
        "leg press": "lower body",
        "lunges": "lower body", 
        "shoulder press": "upper body",
        "lat pulldown": "back",
        "chest fly": "upper body",
        "leg curl": "lower body",
        "leg extension": "lower body",
        "calf raise": "lower body",
        #create custom lift
        "custom": "other"
    }
    return categories.get(lift_name.lower(), "other")

#when logging, the user should be able to select the name of the lift, within a menu of categories
def select_lift():
    print("Select a lift from the following categories:")
    lifts = [
        "Bench Press", "Squat", "Deadlift", "Overhead Press", "Bicep Curl",
        "Tricep Extension", "Pull Up", "Row", "Leg Press", "Lunges",
        "Shoulder Press", "Lat Pulldown", "Chest Fly", "Leg Curl",
        "Leg Extension", "Calf Raise", "Custom"
    ]
    for i, lift in enumerate(lifts, 1):
        print(f"{i}. {lift}")
    choice = int(input("Enter the number of your choice: "))
    if 1 <= choice <= len(lifts):
        return lifts[choice - 1]
    else:
        raise ValueError("Invalid choice")
    


# new: retrieve lifts for a user
def get_lifts_for_user(user_id, limit=100):
    db = connect_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, lift_name, weight, reps, rpe, created_at FROM lifts WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    db.close()
    return rows


def register_user():
    username = input("Please enter your new username: ")
    password = input("Please enter your new password: ")
    encrypted_pw = encrypt_password(password)
    name = input("Please enter your name: ")
    weight = float(input("Please enter your weight in kg: "))
    dob = input("Please enter your date of birth (YYYY-MM-DD): ")

    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, name, weight, dob)
            VALUES (?, ?, ?, ?, ?)
        """, (username, encrypted_pw, name, weight, dob))
        db.commit()
        print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists. Try a different one.")
    finally:
        db.close()

def login_user():
    #login user with original password (not hashed)
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? AND password = ?
    """, (username, encrypt_password(password)))
    user = cursor.fetchone()
    db.close()

    if user:
        print(f"Welcome back, {user[3]}!")  # user[3] is the name
    else:
        print("Invalid username or password.")


def main():
    create_table()
    print("1. Register")
    print("2. Login")
    choice = input("Select an option: ")
    if choice == "1":
        register_user()
    elif choice == "2":
        login_user()
    elif choice == "3":
        try:
            user = int(input("Enter your user id: "))
            lift_name = input("Lift name: ")
            weight = input("Weight (kg): ")
            reps = input("Reps: ")
            rpe = input("RPE (optional): ") or None
            log_lift(user, lift_name, weight, reps, rpe)
            print("Lift logged.")
        except Exception as e:
            print("Error:", e)
    elif choice == "4":
        try:
            user = int(input("Enter your user id: "))
            rows = get_lifts_for_user(user)
            if not rows:
                print("No lifts found for this user.")
            else:
                print("\nYour logged lifts:")
                for row in rows:
                    lid, name, weight, reps, rpe, created_at = row
                    print(f"Lift: {name}, Weight: {weight}kg, Reps: {reps}, RPE: {rpe}, Date: {created_at}")
        except Exception as e:
            print("Error:", e)
    else:
        print("Invalid selection.")
# run the categorized lift selection
        try:
            lift_name = select_lift()
            print(f"You selected: {lift_name}")
            category = categorize_lift(lift_name)
            print(f"Category: {category}")
        except Exception as e:
            print("Error:", e)
            print("Failed to select lift.")
            print("Please try again.")
            select_lift()
            

if __name__ == "__main__":
    main()
# Main.py

# This is a simple user registration and login system using SQLite for storage.
# Passwords are hashed using SHA-256 for security.
# The system allows users to register with a username, password, name, weight, and date of birth.

#i dont know how the fuck this worked, but when i deleted entry date, it just randomly made it so it actually puts the exact date, without me having to specify it.
# i guess it just uses the created_at timestamp then
