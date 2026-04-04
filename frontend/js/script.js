const API = "http://localhost:5000";

function showMessage(msg, type) {
    const el = document.getElementById("msg");
    el.innerText = msg;
    el.className = "message " + type;
}

/* LOGIN */
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        showMessage("Fill all fields", "error");
        return;
    }

    try {
        const res = await fetch(API + "/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({email, password})
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("token", data.token);
            showMessage("Login success", "success");
            setTimeout(() => window.location = "dashboard.html", 1000);
        } else {
            showMessage(data.message || "Login failed", "error");
        }
    } catch {
        showMessage("Server error", "error");
    }
}

/* REGISTER */
async function register() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
        showMessage("Fill all fields", "error");
        return;
    }

    try {
        const res = await fetch(API + "/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name, email, password})
        });

        const data = await res.json();

        if (res.ok) {
            showMessage("Registered successfully", "success");
            setTimeout(() => window.location = "login.html", 1200);
        } else {
            showMessage(data.message || "Registration failed", "error");
        }
    } catch {
        showMessage("Server error", "error");
    }
}

// ---------------- FILE UPLOAD + ANALYZE ----------------

let uploadedPath = "";

// UPLOAD FILE
async function uploadFile() {
    const fileInput = document.getElementById("fileInput");

    if (!fileInput.files.length) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch(API + "/api/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    uploadedPath = data.path;  // 🔥 SAVE PATH

    console.log("Uploaded path:", uploadedPath);
    alert("File uploaded successfully");
}

// ANALYZE FILE
async function analyzeFile() {
    if (!uploadedPath) {
        alert("Upload file first!");
        return;
    }

    const res = await fetch(API + "/api/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            path: uploadedPath   // 🔥 THIS FIXES YOUR ISSUE
        })
    });

    const data = await res.json();

    console.log("Analyze response:", data);
    alert("Analysis complete");

    // OPTIONAL: fetch result
    getResult();
}

// GET RESULT
async function getResult() {
    const res = await fetch(API + "/api/result");
    const data = await res.json();

    console.log("Final Result:", data);

    // Display AI explanation
    document.getElementById("aiResult").innerText =
        data.ai_explanation || "No AI result";
}