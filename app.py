from flask import Flask, request, redirect, session
from markupsafe import escape
import sqlite3
from Main import connect_db, encrypt_password, create_table, create_lifts_table, log_lift as db_log_lift, get_lifts_for_user

app = Flask(__name__)
import os

app.secret_key = os.environ.get("APP_SECRET", "dev-secret")
 # change for production

# ensure DB tables exist
create_table()
create_lifts_table()

LIFT_CATEGORIES = {
    "upper body": ["Bench Press", "Overhead Press", "Shoulder Press", "Chest Fly"],
    "lower body": ["Squat", "Deadlift", "Leg Press", "Lunges", "Leg Curl", "Leg Extension", "Calf Raise"],
    "back": ["Pull Up", "Row", "Lat Pulldown"],
    "arms": ["Bicep Curl", "Tricep Extension"],
    "other": ["Custom"]
}


@app.route("/")
def index():
    if session.get("username"):
        return f"Hello {escape(session['username'])} — <a href='/profile'>Profile</a> | <a href='/log_lift'>Log Lift</a> | <a href='/lifts'>My Lifts</a> | <a href='/logout'>Logout</a>"
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
    return f"<h2>Profile</h2>Username: {escape(user[0])}<br>Name: {escape(user[1] or '')}<br>Weight: {escape(str(user[2] or ''))}<br>DOB: {escape(user[3] or '')}<br><a href='/'>Home</a> | <a href='/log_lift'>Log Lift</a> | <a href='/lifts'>My Lifts</a>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# new: log a lift (form + save)
@app.route("/log_lift", methods=["GET", "POST"])
def log_lift():
    if not session.get("user_id"):
        return redirect("/login")

    if request.method == "POST":
        lift_name = request.form.get("lift_name", "").strip()
        weight_raw = request.form.get("weight", "").strip()
        reps_raw = request.form.get("reps", "").strip()
        rpe_raw = request.form.get("rpe", "").strip()

        if not lift_name or not weight_raw or not reps_raw:
            return "Lift name, weight and reps are required", 400

        try:
            weight = float(weight_raw)
            reps = int(reps_raw)
            rpe = float(rpe_raw) if rpe_raw != "" else None
        except ValueError:
            return "Invalid numeric input", 400

        try:
            db_log_lift(session["user_id"], lift_name, weight, reps, rpe)
            return redirect("/lifts")
        except Exception as e:
            return f"Error logging lift: {escape(str(e))}", 500

    # Create list of all lifts for the dropdown
    all_lifts = []
    for category, lifts in LIFT_CATEGORIES.items():
        all_lifts.extend(lifts)
    all_lifts.sort()

    return f'''
    <h2>Log Lift</h2>
    <form method="post">
      <label for="lift_name">Select Exercise:</label><br>
      <select name="lift_name" id="lift_name" required>
        <option value="">Choose a lift...</option>
        {generate_lift_options()}
      </select><br>
      <label for="weight">Weight (kg):</label><br>
      <input name="weight" type="number" step="0.25" min="0" required><br>
      <label for="reps">Reps:</label><br>
      <input name="reps" type="number" min="1" required><br>
      <label for="rpe">RPE (optional):</label><br>
      <input name="rpe" type="number" step="0.5" min="1" max="10"><br>
      <button type="submit">Save</button>
    </form>
    <a href="/lifts">View your lifts</a> | <a href="/profile">Profile</a>
    '''

def generate_lift_options():
    options = []
    for category, lifts in LIFT_CATEGORIES.items():
        options.append(f'<optgroup label="{category.title()}">')
        for lift in sorted(lifts):
            options.append(f'<option value="{lift}">{lift}</option>')
        options.append('</optgroup>')
    return '\n'.join(options)

# Update the view_lifts route
@app.route("/lifts")
def view_lifts():
    if not session.get("user_id"):
        return redirect("/login")

    try:
        rows = get_lifts_for_user(session["user_id"], limit=500)
    except Exception as e:
        return f"Error retrieving lifts: {escape(str(e))}", 500

    html = """
    <h2>Your Lifts</h2>
    <a href='/log_lift'>Log new lift</a> | <a href='/profile'>Profile</a><br><br>
    """
    
    if not rows:
        return html + "No lifts logged yet."

    html += """
    <table border='1' cellpadding='4'>
    <tr>
        <th>Exercise</th>
        <th>Category</th>
        <th>Weight (kg)</th>
        <th>Reps</th>
        <th>RPE</th>
        <th>Date</th>
    </tr>
    """

    for r in rows:
        lid, name, weight, reps, rpe, created_at = r
        category = get_lift_category(name)
        html += f"""
        <tr>
            <td>{escape(name)}</td>
            <td>{escape(category)}</td>
            <td>{escape(str(weight))}</td>
            <td>{escape(str(reps))}</td>
            <td>{escape(str(rpe) if rpe is not None else '-')}</td>
            <td>{escape(str(created_at))}</td>
        </tr>
        """
    html += "</table>"
    return html

def get_lift_category(lift_name):
    for category, lifts in LIFT_CATEGORIES.items():
        if lift_name in lifts:
            return category.title()
    return "Other"


if __name__ == "__main__":
    app.run(debug=True)