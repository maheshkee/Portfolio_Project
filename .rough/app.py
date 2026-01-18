from flask import Flask, render_template, abort

app = Flask(__name__)


# -------------------------
# Fake data (temporary)
# -------------------------

FAKE_STUDENTS = {
    "23CS045": {
        "student_name": "Mahesh Kumar",
        "about_text": (
            "Computer Science student passionate about backend engineering, "
            "system design, and building things from scratch."
        ),
        "profile_image_url": "/static/images/Mahadev.jpg",
        "github_url": "https://github.com/maheshkee",
        "linkedin_url": "https://linkedin.com/in/maheshkee",
        "email": "mahesh@example.com",
        "skills": ["Python", "Flask", "SQL"],
        "projects": ["Exam Preparation Tracker", "QR Code Generator"],
        "current_learning": ["System Design", "Networking"]
    }
}


# -------------------------
# Route 1: Root / Health
# -------------------------

@app.route("/")
def health():
    return "Aikaryashala server is running."


# -------------------------
# Route 2: Student Home Page
# -------------------------

@app.route("/Aikaryashala/Vidhyarthi/<student_id>")
def student_home(student_id):
    student = FAKE_STUDENTS.get(student_id)

    if not student:
        abort(404)

    return render_template(
        "home.html",
        student_name=student["student_name"],
        about_text=student["about_text"],
        profile_image_url=student["profile_image_url"],
        github_url=student["github_url"],
        linkedin_url=student["linkedin_url"],
        email=student["email"],
        capabilities_url=f"/Aikaryashala/Vidhyarthi/{student_id}/capabilities"
    )


# -------------------------
# Route 3: Student Capabilities Page
# -------------------------

@app.route("/Aikaryashala/Vidhyarthi/<student_id>/capabilities")
def student_capabilities(student_id):
    student = FAKE_STUDENTS.get(student_id)

    if not student:
        abort(404)

    return render_template(
        "capabilities.html",
        student_name=student["student_name"],
        skills=student["skills"],
        projects=student["projects"],
        current_learning=student["current_learning"]
    )


# -------------------------
# App Entry Point
# -------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
