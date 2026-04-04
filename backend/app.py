from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from groq import Groq

from config import UPLOAD_FOLDER, SECRET_KEY
from analyzer import analyze_log

app = Flask(__name__)

# ✅ FIX 1: Proper CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY

client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # 🔐 Replace with your key safely

LAST_RESULT = {}

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                  (data["name"], data["email"], data["password"]))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "User already exists"})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE (email=? OR name=?) AND password=?",
              (data["username"], data["username"], data["password"]))

    user = c.fetchone()
    conn.close()

    return jsonify({"status": "success" if user else "error"})

# ---------------- AI FUNCTION ----------------
def ai_explain(log_text):
    prompt = f"""
You are a cloud security expert.

Analyze this log:
{log_text}

Give output in this format:

Attack Type:
Severity: (LOW / MEDIUM / HIGH)
Risk Score: (1 to 10)
What Happened:
Cause:
Fix:
Prevention Tips:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ---------------- UPLOAD ----------------
@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    return jsonify({"path": filepath})

# ---------------- ANALYZE (🔥 FULL FIX) ----------------
@app.route("/api/analyze", methods=["POST"])
def analyze():
    print("🔵 Analyze API called")

    data = request.get_json(silent=True)
    print("📥 Incoming:", data)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    filepath = data.get("path")
    log_text = data.get("logs")

    try:
        # ✅ FILE CASE
        if filepath:
            if not os.path.exists(filepath):
                return jsonify({"error": "File not found"}), 404

            with open(filepath, "r", errors="ignore") as f:
                content = f.read()

        # ✅ PASTE LOG CASE
        elif log_text:
            content = log_text

        else:
            return jsonify({"error": "No input provided"}), 400

        print("📄 Content length:", len(content))

        # 🔥 ANALYSIS
        result = analyze_log(content)

        # 🔥 REQUIRED FOR FRONTEND
        result["raw_logs"] = content.split("\n")

        # 🔥 AI ANALYSIS
        ai_result = ai_explain(content[:2000])
        result["ai_explanation"] = ai_result

        global LAST_RESULT
        LAST_RESULT = result

        print("✅ Analysis success")

        return jsonify({"message": "Analysis complete"})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ---------------- RESULT ----------------
@app.route("/api/result", methods=["GET"])
def result():
    return jsonify(LAST_RESULT)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "Cloud Log Analyzer Backend Running ✅"

# ---------------- RUN ----------------
if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)