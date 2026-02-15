import os
import uuid
import threading
import secrets
from flask import Flask, render_template, Response, request, redirect, url_for, flash, session
from utils.camera import VideoCamera
from utils.detector import get_model_for_role
from utils.user import register_user, get_user_by_username_or_id, get_user
from utils.db import init_db
from utils.alert import trigger_alert
from utils.face_watchlist import load_watchlist_encodings, check_face_watchlist
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from utils.db import init_db


app = Flask(__name__)


# Secret key for session management
if not os.path.exists("secret.key"):
    with open("secret.key", "w") as f:
        f.write(secrets.token_hex(16))

with open("secret.key", "r") as f:
    app.secret_key = f.read().strip()

# Create necessary folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs(os.path.join("static", "alert_sounds"), exist_ok=True)
os.makedirs("watchlist", exist_ok=True)

# Initialize database and load watchlist
init_db()
WATCHLIST = load_watchlist_encodings("watchlist")

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")

        if not username or not role or not password:
            flash("Please provide username, role, and password")
            return redirect(url_for("register"))

        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(password)
        register_user(user_id, username, email, role, hashed_password)
        flash(f"Registered successfully. Your user id is {user_id}")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_id = request.form.get("username_or_id")
        password = request.form.get("password")
        user = get_user_by_username_or_id(username_or_id)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            flash(f"Welcome, {user['username']}!")
            return redirect(url_for("dashboard", user_id=user["user_id"]))
        else:
            flash("Invalid username/user id or password")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!")
    return redirect(url_for("login"))

@app.route("/start_stream", methods=["POST"])
def start_stream():
    user_id = request.form.get("user_id")
    source = request.form.get("source", 0)  # default webcam
    ipurl = request.form.get("ipurl", "").strip()
    if ipurl:
        source = ipurl
    else:
        # Convert to int if possible for webcam index
        try:
            source = int(source)
        except ValueError:
            pass

    user = get_user(user_id)
    if not user:
        flash("User not found")
        return redirect(url_for("index"))

    model_path = get_model_for_role(user['role'])
    cam = VideoCamera(source, model_path, user_id, WATCHLIST)
    CAMERAS[user_id] = cam  # store the camera instance
    flash("Stream started")
    return redirect(url_for("dashboard", user_id=user_id))


@app.route("/stream/<user_id>")
def stream(user_id):
    print("STREAM REQUEST for:", user_id)
    if user_id not in CAMERAS:
        print("CAMERA NOT FOUND")
        flash("Please start stream first")
        return redirect(url_for("dashboard", user_id=user_id))
    else:
        print("CAMERA FOUND:", CAMERAS[user_id])
    return Response(gen_frames(CAMERAS[user_id]), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/dashboard/<user_id>")
@login_required
def dashboard(user_id):
    user = get_user(user_id)
    if not user:
        flash("User not found")
        return redirect(url_for("index"))
    return render_template("dashboard.html", user_id=user_id, user=user)


# Live feed handling
CAMERAS = {}  # user_id -> VideoCamera instance

def gen_frames(camera: VideoCamera):
    while True:
        success, jpg_bytes, anomaly_flag, face_flag = camera.get_frame_bytes(WATCHLIST)
        if not success:
            break
        if anomaly_flag or face_flag:
            trigger_alert(camera.user_id, camera.last_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n')

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    user_id = request.form.get("user_id")
    file = request.files.get("file")
    if not user_id or not file or file.filename == '':
        flash("Missing user ID or file")
        return redirect(request.referrer or url_for('index'))

    user = get_user(user_id)
    if not user:
        flash("User not found")
        return redirect(url_for("index"))

    path = os.path.join("uploads", f"{uuid.uuid4()}.mp4")
    file.save(path)

    model_path = get_model_for_role(user['role'])
    from utils.camera import process_video_file
    thread = threading.Thread(target=process_video_file, args=(path, model_path, user_id, WATCHLIST))
    thread.start()
    flash(f"Video '{file.filename}' is being processed in the background.")
    return redirect(url_for("dashboard", user_id=user_id))

@app.route("/refresh_watchlist")
@login_required
def refresh_watchlist():
    global WATCHLIST
    WATCHLIST = load_watchlist_encodings("watchlist")
    return "Watchlist refreshed", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
