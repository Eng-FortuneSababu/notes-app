import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
DB_FILE = "notes.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/notes", methods=["GET"])
def get_notes():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, content, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    content = (data or {}).get("content", "").strip()
    if not content:
        return jsonify({"error": "Note content is required"}), 400

    with get_db() as conn:
        cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        note_id = cursor.lastrowid

    return jsonify({"id": note_id, "content": content}), 201

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    if cursor.rowcount == 0:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({"deleted": note_id}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)