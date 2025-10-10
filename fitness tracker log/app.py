from flask import Flask, request, redirect, session
from markupsafe import escape
import sqlite3
from Main import connect_db, encrypt_password, create_table

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # change for production

create_table()

@app.route("/")
def index():
    if session.get("username"):
        return f"Hello {escape(session['username'])} — <a href='/profile'>Profile</a> | <a href='/logout'>Logout</a>"
    return "<a href='/login'>Login</a> | <a href='/register'>Register</a>"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        name = request.form.get("name", "")
        weight = request.form.get("weight") or None
        dob = request.form.get("dob") or None
        encrypted = encrypt_password(password)

        db = connect_db()
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password, name, weight, dob) VALUES (?, ?, ?, ?, ?)",
                (username, encrypted, name, weight, dob),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            return "Username already exists", 400
        db.close()
        return redirect("/login")

    return '''
    <h2>Register</h2>
    <form method="post">
      Username: <input name="username"><br>
      Password: <input name="password" type="password"><br>
      Name: <input name="name"><br>
      Weight (kg): <input name="weight" type="number" step="any"><br>
      DOB (YYYY-MM-DD): <input name="dob"><br>
      <button type="submit">Register</button>
    </form>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = connect_db()
        cur = db.cursor()
        cur.execute("SELECT id, username, name FROM users WHERE username = ? AND password = ?",
                    (username, encrypt_password(password)))
        user = cur.fetchone()
        db.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/profile")
        return "Invalid credentials", 401

    return '''
    <h2>Login</h2>
    <form method="post">
      Username: <input name="username"><br>
      Password: <input name="password" type="password"><br>
      <button type="submit">Login</button>
    </form>
    '''

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect("/login")
    db = connect_db()
    cur = db.cursor()
    cur.execute("SELECT username, name, weight, dob, volume_of_lifts FROM users WHERE id = ?", (session["user_id"],))
    user = cur.fetchone()
    db.close()
    if not user:
        return "User not found", 404
    return f"<h2>Profile</h2>Username: {escape(user[0])}<br>Name: {escape(user[1] or '')}<br>Weight: {escape(str(user[2] or ''))}<br>DOB: {escape(user[3] or '')}<br><a href='/'>Home</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)