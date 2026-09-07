from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

# AI assistance was used during development.
# The code was reviewed, tested, and customized by the project author.


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    tasks = db.execute("""
        SELECT tasks.*, subjects.name AS subject_name
        FROM tasks
        LEFT JOIN subjects ON tasks.subject_id = subjects.id
        WHERE tasks.user_id = ?
        ORDER BY tasks.completed ASC,
                 CASE tasks.priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                 END,
                 tasks.due_date ASC
    """, user_id)

    total = len(tasks)
    completed = sum(task["completed"] for task in tasks)
    progress = round((completed / total) * 100) if total else 0

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        progress=progress
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username:
            return "Username required", 400

        if not password:
            return "Password required", 400

        if password != confirmation:
            return "Passwords do not match", 400

        existing = db.execute(
            "SELECT id FROM users WHERE username = ?",
            username
        )

        if existing:
            return "Username already exists", 400

        password_hash = generate_password_hash(password)

        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            password_hash
        )

        session["user_id"] = user_id

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"],
            password
        ):
            return "Invalid username or password", 403

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/subjects")
@login_required
def subjects():
    subjects = db.execute("""
        SELECT subjects.*,
               COUNT(tasks.id) AS task_count
        FROM subjects
        LEFT JOIN tasks ON subjects.id = tasks.subject_id
        WHERE subjects.user_id = ?
        GROUP BY subjects.id
        ORDER BY subjects.name
    """, session["user_id"])

    return render_template("subjects.html", subjects=subjects)


@app.route("/add_subject", methods=["POST"])
@login_required
def add_subject():
    name = request.form.get("name", "").strip()

    if not name:
        return "Subject name required", 400

    db.execute(
        "INSERT INTO subjects (user_id, name) VALUES (?, ?)",
        session["user_id"],
        name
    )

    return redirect("/subjects")


@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
@login_required
def delete_subject(subject_id):
    subject = db.execute(
        "SELECT id FROM subjects WHERE id = ? AND user_id = ?",
        subject_id,
        session["user_id"])

    if not subject:
        return "Subject not found", 404

    db.execute(
        "UPDATE tasks SET subject_id = NULL WHERE subject_id = ? AND user_id = ?",
        subject_id,
        session["user_id"]
    )

    db.execute(
        "DELETE FROM subjects WHERE id = ? AND user_id = ?",
        subject_id,
        session["user_id"]
    )

    return redirect("/subjects")


@app.route("/tasks")
@login_required
def tasks():
    priority = request.args.get("priority", "")
    status = request.args.get("status", "")
    sort = request.args.get("sort", "due")

    query = """
        SELECT tasks.*, subjects.name AS subject_name
        FROM tasks
        LEFT JOIN subjects ON tasks.subject_id = subjects.id
        WHERE tasks.user_id = ?
    """

    params = [session["user_id"]]

    if priority in ["High", "Medium", "Low"]:
        query += " AND tasks.priority = ?"
        params.append(priority)

    if status == "completed":
        query += " AND tasks.completed = 1"

    elif status == "pending":
        query += " AND tasks.completed = 0"

    if sort == "priority":
        query += """
            ORDER BY
            CASE tasks.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            tasks.due_date ASC
        """

    elif sort == "title":
        query += " ORDER BY tasks.title COLLATE NOCASE ASC"

    elif sort == "newest":
        query += " ORDER BY tasks.id DESC"

    else:
        query += " ORDER BY tasks.completed ASC, tasks.due_date ASC"

    tasks = db.execute(query, *params)

    return render_template(
        "tasks.html",
        tasks=tasks,
        selected_priority=priority,
        selected_status=status,
        selected_sort=sort
    )


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    subjects = db.execute(
        "SELECT * FROM subjects WHERE user_id = ? ORDER BY name",
        session["user_id"]
    )

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        subject_id = request.form.get("subject_id")
        due_date = request.form.get("due_date")
        priority = request.form.get("priority", "Medium")

        if not title:
            return "Task title required", 400

        if priority not in ["High", "Medium", "Low"]:
            priority = "Medium"

        if not subject_id:
            subject_id = None

        db.execute("""
            INSERT INTO tasks
            (user_id, subject_id, title, description, due_date, priority, completed)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
            session["user_id"],
            subject_id,
            title,
            description,
            due_date,
            priority
        )

        return redirect("/tasks")

    return render_template("add_task.html", subjects=subjects)


@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = db.execute("""
        SELECT *
        FROM tasks
        WHERE id = ? AND user_id = ?
    """, task_id, session["user_id"])

    if not task:
        return "Task not found", 404

    subjects = db.execute(
        "SELECT * FROM subjects WHERE user_id = ? ORDER BY name",
        session["user_id"]
    )

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        subject_id = request.form.get("subject_id")
        due_date = request.form.get("due_date")
        priority = request.form.get("priority", "Medium")

        if not title:
            return "Task title required", 400

        if priority not in ["High", "Medium", "Low"]:
            priority = "Medium"

        if not subject_id:
            subject_id = None

        db.execute("""
            UPDATE tasks
            SET title = ?,
                description = ?,
                subject_id = ?,
                due_date = ?,
                priority = ?
            WHERE id = ? AND user_id = ?
        """,
            title,
            description,
            subject_id,
            due_date,
            priority,
            task_id,
            session["user_id"]
        )

        return redirect("/tasks")

    return render_template(
        "edit_task.html",
        task=task[0],
        subjects=subjects
    )


@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete(task_id):
    task = db.execute(
        "SELECT id, completed FROM tasks WHERE id = ? AND user_id = ?",
        task_id,
        session["user_id"]
    )

    if not task:
        return "Task not found", 404

    new_status = 0 if task[0]["completed"] else 1

    db.execute(
        "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
        new_status,
        task_id,
        session["user_id"]
    )

    return redirect(request.referrer or "/")


@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        task_id,
        session["user_id"]
    )

    return redirect(request.referrer or "/tasks")


@app.route("/statistics")
@login_required
def statistics():
    user_id = session["user_id"]

    total = db.execute(
        "SELECT COUNT(*) AS count FROM tasks WHERE user_id = ?",
        user_id
    )[0]["count"]

    completed = db.execute(
        "SELECT COUNT(*) AS count FROM tasks WHERE user_id = ? AND completed = 1",
        user_id
    )[0]["count"]

    pending = total - completed

    high = db.execute(
        "SELECT COUNT(*) AS count FROM tasks WHERE user_id = ? AND priority = 'High' AND completed = 0",
        user_id
    )[0]["count"]

    subjects = db.execute("""
        SELECT subjects.name,
               COUNT(tasks.id) AS total,
               SUM(CASE WHEN tasks.completed = 1 THEN 1 ELSE 0 END) AS completed
        FROM subjects
        LEFT JOIN tasks ON subjects.id = tasks.subject_id
        WHERE subjects.user_id = ?
        GROUP BY subjects.id
        ORDER BY total DESC
    """, user_id)

    progress = round((completed / total) * 100) if total else 0

    return render_template(
        "statistics.html",
        total=total,
        completed=completed,
        pending=pending,
        high=high,
        progress=progress,
        subjects=subjects
    )


@app.route("/planner")
@login_required
def planner():
    tasks = db.execute("""
        SELECT tasks.*, subjects.name AS subject_name
        FROM tasks
        LEFT JOIN subjects ON tasks.subject_id = subjects.id
        WHERE tasks.user_id = ? AND tasks.completed = 0
        ORDER BY
            CASE tasks.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            tasks.due_date ASC
    """, session["user_id"])

    return render_template("planner.html", tasks=tasks)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
