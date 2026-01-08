import qrcode
import sqlite3
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, abort, request, redirect, url_for

# configuration for photo path
UPLOAD_FOLDER = "static/uploads/profile_photos"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# configuration for db
DB_PATH = "db/aikaryashala.db"

# configuration for qr code
QR_FOLDER = "static/qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)


app = Flask(__name__)

# helper function to make sure correct file upload
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS




# -------------------------------------------------
# Helper: get a database connection (READ ONLY)
# -------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows row["column_name"]
    return conn


# -------------------------------------------------
# Route 1: Health check
# -------------------------------------------------
@app.route("/")
def health():
    return "Aikaryashala server is running."


# -------------------------------------------------
# Route 2: Student Home Page
# -------------------------------------------------
@app.route("/Aikaryashala/Vidhyarthi/<student_id>")
def student_home(student_id):
    conn = get_db_connection()

    # 1️⃣ Fetch user by student_id
    user = conn.execute(
        "SELECT * FROM users WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    qr_code_path = user["qr_code_path"]
    
    if user is None:
        conn.close()
        abort(404)

    conn.close()

    return render_template(
        "home.html",
        student_name=user["name"],
        about_text=user["about_text"],
        profile_image_url=user["profile_photo_path"],
        github_url=user["github_url"],
        linkedin_url=user["linkedin_url"],
        email=user["email"],
        capabilities_url=f"/Aikaryashala/Vidhyarthi/{student_id}/capabilities",
        qr_code_path=qr_code_path
    )


# -------------------------------------------------
# Route 3: Student Capabilities Page
# -------------------------------------------------
@app.route("/Aikaryashala/Vidhyarthi/<student_id>/capabilities")
def student_capabilities(student_id):
    conn = get_db_connection()

    # 1️⃣ Fetch user
    user = conn.execute(
        "SELECT * FROM users WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    if user is None:
        conn.close()
        abort(404)

    user_id = user["id"]

    # 2️⃣ Fetch skills
    skills_rows = conn.execute(
        "SELECT skill_name FROM skills WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    # 3️⃣ Fetch projects
    projects_rows = conn.execute(
        "SELECT project_name FROM projects WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    # 4️⃣ Fetch current learning
    learning_rows = conn.execute(
        "SELECT topic_name FROM current_learning WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    conn.close()

    # Convert rows → simple lists
    skills = [row["skill_name"] for row in skills_rows]
    projects = [row["project_name"] for row in projects_rows]
    current_learning = [row["topic_name"] for row in learning_rows]

    return render_template(
        "capabilities.html",
        student_name=user["name"],
        skills=skills,
        projects=projects,
        current_learning=current_learning
    )

# -------------------------------------------------
# Route 4: Show Registration Form
# -------------------------------------------------
@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")

# -------------------------------------------------
# Route 4: Handle Submission
# -------------------------------------------------
@app.route("/register", methods=["POST"])
def register_submit():
    student_id = request.form.get("student_id")
    name = request.form.get("name")
    email = request.form.get("email")
    github_url = request.form.get("github_url")
    linkedin_url = request.form.get("linkedin_url")
    about_text = request.form.get("about_text")

    photo = request.files.get("profile_photo")
    
    # Default image
    profile_photo_path = "/static/images/Mahadev.jpg"
    
    if photo and photo.filename != "":
        if allowed_file(photo.filename):
            original_filename = secure_filename(photo.filename)
            ext = original_filename.rsplit(".", 1)[1].lower()
            filename = f"{student_id}.{ext}"
            
    
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(save_path)
    
            profile_photo_path = f"/static/uploads/profile_photos/{filename}"
    # for debugging purposes if photo uploaded properly
    print("FILES RECEIVED:", request.files)
    print("PROFILE PHOTO:", request.files.get("profile_photo"))
    

    # 1️⃣ Basic validation
    if not student_id or not name or not email:
        return "Student ID, Name, and Email are required", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("FINAL PHOTO PATH BEFORE INSERT:", profile_photo_path)
        # 2️⃣ Insert into users table
        cursor.execute(
            """
            INSERT INTO users (
                student_id, name, email,
                github_url, linkedin_url,
                profile_photo_path, about_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                name,
                email,
                github_url,
                linkedin_url,
                profile_photo_path,
                about_text,
            ),
        )

        conn.commit()

# BUILD portfolio URL
        portfolio_url = request.url_root.rstrip("/") + f"/Aikaryashala/Vidhyarthi/{student_id}"
# GENERATE QR image
        qr_img = qrcode.make(portfolio_url)
        
        qr_filename = f"{student_id}.png"
        qr_save_path = os.path.join(QR_FOLDER, qr_filename)
        
        qr_img.save(qr_save_path)
# BUILD QR URL PATH (browser path)
        qr_code_path = f"/static/qr_codes/{qr_filename}"

# STORE QR PATH IN DB
        cursor.execute(
            "UPDATE users SET qr_code_path = ? WHERE student_id = ?",
            (qr_code_path, student_id),
        )
        conn.commit()
        
        

    except sqlite3.IntegrityError as e:
        conn.close()
        return "Student ID or Email already exists", 400

    conn.close()

    # 3️⃣ Redirect to portfolio page
    return redirect(
        f"/Aikaryashala/Vidhyarthi/{student_id}"
    )

# -------------------------------------------------
# Route 6 : to see db for debuggingprocess
# -------------------------------------------------
@app.route("/debug/users")
def debug_users():
    conn = get_db_connection()

    users = conn.execute(
        """
        SELECT id, student_id, name, email, github_url, linkedin_url
        FROM users
        """
    ).fetchall()

    conn.close()

    return {
        "users": [dict(user) for user in users]
    }


# -------------------------------------------------
# App entry point
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
