import sqlite3
import os

DB_PATH = "db/aikaryashala.db"


def init_db():
    # 1️⃣ Ensure db folder exists
    os.makedirs("db", exist_ok=True)

    # 2️⃣ Check if DB file already exists
    if os.path.exists(DB_PATH):
        print("Database already exists. Skipping creation.")
        return

    # 3️⃣ Create database connection (this creates the file)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 4️⃣ Enable foreign key constraints (IMPORTANT in SQLite)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 5️⃣ Create users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            github_url TEXT,
            linkedin_url TEXT,
            profile_photo_path TEXT,
            about_text TEXT
        );
    """)

    # 6️⃣ Create skills table
    cursor.execute("""
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # 7️⃣ Create projects table
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # 8️⃣ Create current_learning table
    cursor.execute("""
        CREATE TABLE current_learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # 9️⃣ Commit and close
    conn.commit()
    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    init_db()
