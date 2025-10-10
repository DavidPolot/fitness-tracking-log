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
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()
# Main.py

# This is a simple user registration and login system using SQLite for storage.
# Passwords are hashed using SHA-256 for security.
# The system allows users to register with a username, password, name, weight, and date of birth.


