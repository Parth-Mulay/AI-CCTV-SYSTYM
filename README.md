ThreatSys – AI-Based Smart Surveillance System

ThreatSys is an intelligent real-time surveillance and threat detection platform powered by Artificial Intelligence, Computer Vision, and Web Technologies. It provides automated monitoring, anomaly detection, and alert generation through live camera streams and recorded videos.

This system is designed for smart security solutions in homes, offices, campuses, and restricted areas.

📌 Features

✅ Real-time camera streaming (Webcam / IP Camera)

✅ Motion-based anomaly detection

✅ Face recognition with watchlist monitoring

✅ Secure user authentication system

✅ Role-based AI model selection

✅ Automated alert generation

✅ Image-based evidence storage

✅ Background video processing

✅ Multi-user dashboard

✅ Low-latency optimized streaming

✅ Database-backed user management

🧠 Tech Stack
Category	Technologies
Backend	Python, Flask
AI / CV	OpenCV, Custom ML Models
Frontend	HTML, CSS, JavaScript, Bootstrap
Database	SQLite / MySQL
Security	Werkzeug Password Hashing, Sessions
Others	Multithreading, Background Processing
📁 Project Structure
ThreatSys/
│
├── app.py
├── utils/
│   ├── camera.py
│   ├── detector.py
│   ├── motion.py
│   ├── alert.py
│   └── db.py
│
├── templates/
├── static/
├── uploads/
├── watchlist/
├── models/
└── logs/

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/Parth-Mulay/ThreatSys.git
cd ThreatSys

2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python app.py


Open your browser:

http://127.0.0.1:5000

📸 How It Works

User registers and logs in

Camera/IP stream is connected

Video frames are captured in real time

AI models analyze motion and faces

Threats are detected automatically

Alerts are triggered with evidence

User monitors activity via dashboard

🎯 Use Cases

🏠 Smart Home Surveillance

🏢 Office & Corporate Security

🎓 Campus Monitoring

🚧 Restricted Area Protection

🚓 Law Enforcement Support

📹 AI-Based CCTV Analysis

🚀 Performance Optimization

Background threaded camera capture

Frame buffer minimization

Resolution & FPS tuning

JPEG compression optimization

Reduced network overhead

These optimizations ensure low-latency real-time streaming.

📈 Future Enhancements

Cloud deployment (AWS / Azure / GCP)

Mobile app integration

SMS / Email alert system

Deep Learning-based anomaly detection

Distributed multi-camera network

Edge AI implementation

Facial emotion analysis

👨‍💻 Author

Parth Mulay
AI & Data Science Developer

📧 Email: (mulayparth8@gmail.com)
💼 LinkedIn: (https://www.linkedin.com/in/parthmulay)
🌐 GitHub: https://github.com/Parth-Mulay
