import os
import json
import csv
import io
import time
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory, session, Response

app = Flask(__name__, static_folder='dist', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'festgate_super_secret_gatekeeper_token_2026')

# Persistent Data Storage File (Fallback for Firebase Realtime Database)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'festgate_db.json')

# Firebase Admin SDK Initialization (Optional / Configurable via Env)
FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', '')
FIREBASE_CREDENTIALS = os.environ.get('FIREBASE_CREDENTIALS', '')

firebase_db = None
try:
    if FIREBASE_DATABASE_URL and FIREBASE_CREDENTIALS and os.path.exists(FIREBASE_CREDENTIALS):
        import firebase_admin
        from firebase_admin import credentials, db
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DATABASE_URL})
        firebase_db = db
        print("[FestGate] Connected to Firebase Realtime Database successfully!")
except Exception as e:
    print(f"[FestGate] Firebase initialization skipped ({e}). Using persistent JSON database.")

# Seed Data
DEFAULT_DATABASE = {
    "events": [
        {
            "id": "evt-1",
            "title": "National Hackathon 2026: Code & Innovate",
            "category": "TECH",
            "categoryColor": "#0284C7",
            "date": "Oct 15, 2026",
            "time": "09:00 AM - 09:00 PM",
            "venue": "Innovation Hub Hall A",
            "capacity": 250,
            "registeredCount": 198,
            "checkedInCount": 142,
            "description": "36-hour sprint bringing student developers together to build AI and Cloud solutions.",
            "coordinator": {
                "name": "Dr. Leonardo Samsul",
                "role": "Fest Lead Mentor",
                "initials": "LS",
                "avatarBg": "bg-indigo-500"
            },
            "imageGradient": "from-amber-700 via-amber-800 to-slate-900",
            "imageSrc": "/static/images/event1.jpg"
        },
        {
            "id": "evt-2",
            "title": "UI/UX Design Masterclass & Sprint",
            "category": "DESIGN",
            "categoryColor": "#7C3AED",
            "date": "Oct 16, 2026",
            "time": "11:00 AM - 04:00 PM",
            "venue": "Design Studio Lab 3",
            "capacity": 150,
            "registeredCount": 120,
            "checkedInCount": 88,
            "description": "Master human-centric interface design, design systems, and rapid interactive prototyping.",
            "coordinator": {
                "name": "Bayu Saito",
                "role": "Creative Lead",
                "initials": "BS",
                "avatarBg": "bg-emerald-500"
            },
            "imageGradient": "from-slate-800 via-purple-950 to-slate-900",
            "imageSrc": "/static/images/event2.jpg"
        },
        {
            "id": "evt-3",
            "title": "Grand Cultural Gala & Band Fest",
            "category": "CULTURAL",
            "categoryColor": "#E11D48",
            "date": "Oct 18, 2026",
            "time": "05:00 PM - 11:00 PM",
            "venue": "Main University Amphitheatre",
            "capacity": 800,
            "registeredCount": 650,
            "checkedInCount": 420,
            "description": "Live stage performances, battle of the bands, dance crew championships, and street food fest.",
            "coordinator": {
                "name": "Padhang Satrio",
                "role": "Cultural Advisor",
                "initials": "PS",
                "avatarBg": "bg-amber-600"
            },
            "imageGradient": "from-purple-900 via-indigo-900 to-black",
            "imageSrc": "/static/images/event3.jpg"
        }
    ],
    "attendees": [
        {
            "id": "att-1",
            "ticketCode": "FG-8291-TX",
            "name": "Padhang Satrio",
            "rollNo": "CS-2023-049",
            "email": "padhang.satrio@festgate.edu",
            "department": "Computer Science",
            "eventId": "evt-2",
            "eventTitle": "UI/UX Design Masterclass & Sprint",
            "eventCategory": "DESIGN",
            "registeredAt": "2026-10-09 10:14 AM",
            "status": "CHECKED_IN",
            "checkedInAt": "2026-10-10 08:30 AM",
            "checkedInBy": "Gate 1 - Lead",
            "initials": "PS",
            "avatarBg": "bg-purple-600"
        },
        {
            "id": "att-2",
            "ticketCode": "FG-4412-NB",
            "name": "Bagas Mahpie",
            "rollNo": "IT-2024-118",
            "email": "bagas.mahpie@festgate.edu",
            "department": "Information Tech",
            "eventId": "evt-1",
            "eventTitle": "National Hackathon 2026: Code & Innovate",
            "eventCategory": "TECH",
            "registeredAt": "2026-10-09 11:45 AM",
            "status": "REGISTERED",
            "initials": "BM",
            "avatarBg": "bg-blue-600"
        },
        {
            "id": "att-3",
            "ticketCode": "FG-9021-CL",
            "name": "Sir Dandy",
            "rollNo": "EC-2023-012",
            "email": "sir.dandy@festgate.edu",
            "department": "Electronics",
            "eventId": "evt-3",
            "eventTitle": "Grand Cultural Gala & Band Fest",
            "eventCategory": "CULTURAL",
            "registeredAt": "2026-10-09 01:20 PM",
            "status": "CHECKED_IN",
            "checkedInAt": "2026-10-10 09:12 AM",
            "checkedInBy": "Gate 2 - East Wing",
            "initials": "SD",
            "avatarBg": "bg-emerald-600"
        }
    ],
    "gate_logs": []
}

def load_db():
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATABASE)
        return DEFAULT_DATABASE
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATABASE

def save_db(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Admin Auth Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            # Allow development testing or return 401
            auth_header = request.headers.get('Authorization')
            if auth_header != 'Bearer festgate2026':
                return jsonify({"error": "Unauthorized. Admin privileges required."}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== API ROUTES ====================

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "system": "FestGate Live Gateway v2.4",
        "cloud_sync": "Firebase Realtime DB" if firebase_db else "Persistent Local DB",
        "tagline": "Every Event. One Smart Gate."
    })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()

    if username == 'admin' and (password == 'festgate2026' or password == 'admin123'):
        session['is_admin'] = True
        return jsonify({"success": True, "message": "Admin authenticated successfully", "role": "superadmin"})
    return jsonify({"success": False, "error": "Invalid username or password"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.pop('is_admin', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/auth/me', methods=['GET'])
def api_auth_me():
    return jsonify({"is_admin": bool(session.get('is_admin'))})

@app.route('/api/events', methods=['GET'])
def get_events():
    db_data = load_db()
    return jsonify(db_data.get("events", []))

@app.route('/api/events', methods=['POST'])
@admin_required
def create_event():
    payload = request.json or {}
    title = payload.get('title')
    if not title:
        return jsonify({"error": "Event title is required"}), 400

    db_data = load_db()
    new_event = {
        "id": f"evt-{int(time.time() * 1000)}",
        "title": title,
        "category": payload.get('category', 'TECH'),
        "categoryColor": payload.get('categoryColor', '#0284C7'),
        "date": payload.get('date', 'Oct 20, 2026'),
        "time": payload.get('time', '10:00 AM - 04:00 PM'),
        "venue": payload.get('venue', 'Auditorium Hall 1'),
        "capacity": int(payload.get('capacity', 200)),
        "registeredCount": 0,
        "checkedInCount": 0,
        "description": payload.get('description', ''),
        "coordinator": payload.get('coordinator', {
            "name": "Prof. Alex Turner",
            "role": "Gate Lead",
            "initials": "AT",
            "avatarBg": "bg-indigo-600"
        }),
        "imageGradient": payload.get('imageGradient', 'from-purple-900 via-indigo-900 to-black')
    }

    db_data["events"].insert(0, new_event)
    save_db(db_data)

    if firebase_db:
        try:
            firebase_db.reference(f'events/{new_event["id"]}').set(new_event)
        except Exception as e:
            print(f"Firebase sync error: {e}")

    return jsonify(new_event), 201

@app.route('/api/attendees', methods=['GET'])
def get_attendees():
    db_data = load_db()
    return jsonify(db_data.get("attendees", []))

@app.route('/api/register', methods=['POST'])
def register_student():
    payload = request.json or {}
    name = payload.get('name', '').strip()
    roll_no = payload.get('rollNo', '').strip()
    email = payload.get('email', '').strip()
    event_id = payload.get('eventId', '')
    department = payload.get('department', 'Engineering')

    if not name or not roll_no or not email or not event_id:
        return jsonify({"error": "Missing required fields (name, rollNo, email, eventId)"}), 400

    db_data = load_db()
    events = db_data.get("events", [])
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Target event not found"}), 404

    # Check for existing duplicate registration for this student and event
    existing = next((a for a in db_data["attendees"] if a["eventId"] == event_id and (a["rollNo"].lower() == roll_no.lower() or a["email"].lower() == email.lower())), None)
    if existing:
        return jsonify({
            "error": "Duplicate registration: Student already registered for this event.",
            "existingTicket": existing
        }), 409

    # Generate unique ticket ID: FG-XXXX-YY
    import random
    import string
    rand_num = random.randint(1000, 9999)
    rand_chars = ''.join(random.choices(string.ascii_uppercase, k=2))
    ticket_code = f"FG-{rand_num}-{rand_chars}"

    name_parts = name.split()
    initials = (name_parts[0][0] + (name_parts[-1][0] if len(name_parts) > 1 else '')).upper()

    colors = ['bg-purple-600', 'bg-blue-600', 'bg-emerald-600', 'bg-rose-600', 'bg-amber-600']
    avatar_bg = random.choice(colors)

    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    new_attendee = {
        "id": f"att-{int(time.time() * 1000)}",
        "ticketCode": ticket_code,
        "name": name,
        "rollNo": roll_no,
        "email": email,
        "department": department,
        "eventId": event["id"],
        "eventTitle": event["title"],
        "eventCategory": event["category"],
        "registeredAt": now_str,
        "status": "REGISTERED",
        "initials": initials,
        "avatarBg": avatar_bg
    }

    db_data["attendees"].insert(0, new_attendee)
    event["registeredCount"] = event.get("registeredCount", 0) + 1
    save_db(db_data)

    if firebase_db:
        try:
            firebase_db.reference(f'attendees/{ticket_code}').set(new_attendee)
            firebase_db.reference(f'events/{event["id"]}/registeredCount').set(event["registeredCount"])
        except Exception as e:
            print(f"Firebase sync error: {e}")

    return jsonify(new_attendee), 201

@app.route('/api/verify', methods=['POST'])
def verify_gate_pass():
    """
    CRITICAL GATE PASS VERIFICATION WITH FRAUD & DUPLICATE PREVENTION:
    1. Checks if ticket exists.
    2. If status is already CHECKED_IN -> Rejects with DUPLICATE ATTENDANCE DETECTED!
    3. If status is REGISTERED -> Admits student, records timestamp and gate staff.
    """
    payload = request.json or {}
    ticket_code = payload.get('ticketCode', '').strip().upper()
    gate_staff = payload.get('gateStaff', 'Gate 1 - Lead')

    if not ticket_code:
        return jsonify({"success": False, "reason": "INVALID", "message": "Please provide a valid ticket code."}), 400

    db_data = load_db()
    attendees = db_data.get("attendees", [])
    attendee = next((a for a in attendees if a["ticketCode"].upper() == ticket_code), None)

    if not attendee:
        return jsonify({
            "success": False,
            "reason": "INVALID",
            "message": f"Ticket '{ticket_code}' was not found in the FestGate database."
        }), 404

    # DUPLICATE ATTENDANCE DETECTION
    if attendee.get("status") == "CHECKED_IN":
        return jsonify({
            "success": False,
            "reason": "DUPLICATE",
            "message": f"DUPLICATE ATTENDANCE DETECTED! Pass was already scanned at {attendee.get('checkedInAt')} by {attendee.get('checkedInBy', 'Gate Staff')}. Re-entry denied.",
            "attendee": attendee
        }), 409

    # ADMISSION APPROVED
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    attendee["status"] = "CHECKED_IN"
    attendee["checkedInAt"] = now_str
    attendee["checkedInBy"] = gate_staff

    # Update event attendance
    events = db_data.get("events", [])
    event = next((e for e in events if e["id"] == attendee["eventId"]), None)
    if event:
        event["checkedInCount"] = event.get("checkedInCount", 0) + 1

    # Log to gate log
    db_data.setdefault("gate_logs", []).insert(0, {
        "ticketCode": ticket_code,
        "student": attendee["name"],
        "event": attendee["eventTitle"],
        "timestamp": now_str,
        "gateStaff": gate_staff,
        "result": "SUCCESS"
    })

    save_db(db_data)

    if firebase_db:
        try:
            firebase_db.reference(f'attendees/{ticket_code}').update({
                "status": "CHECKED_IN",
                "checkedInAt": now_str,
                "checkedInBy": gate_staff
            })
            if event:
                firebase_db.reference(f'events/{event["id"]}/checkedInCount').set(event["checkedInCount"])
        except Exception as e:
            print(f"Firebase sync error: {e}")

    return jsonify({
        "success": True,
        "reason": "SUCCESS",
        "message": f"Access Granted! Welcome {attendee['name']} to {attendee['eventTitle']}.",
        "attendee": attendee
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    db_data = load_db()
    attendees = db_data.get("attendees", [])
    events = db_data.get("events", [])
    total_reg = len(attendees)
    total_checked = sum(1 for a in attendees if a.get("status") == "CHECKED_IN")
    rate = round((total_checked / total_reg * 100)) if total_reg > 0 else 0

    return jsonify({
        "totalRegistered": total_reg,
        "totalCheckedIn": total_checked,
        "verificationRate": rate,
        "activeEventsCount": len(events)
    })

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    db_data = load_db()
    attendees = db_data.get("attendees", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Student Name", "Roll Number", "Email", 
        "Department", "Event Title", "Registration Date", 
        "Gate Status", "Check-In Timestamp", "Gate Staff"
    ])

    for a in attendees:
        writer.writerow([
            a.get("ticketCode", ""),
            a.get("name", ""),
            a.get("rollNo", ""),
            a.get("email", ""),
            a.get("department", ""),
            a.get("eventTitle", ""),
            a.get("registeredAt", ""),
            a.get("status", ""),
            a.get("checkedInAt", "N/A"),
            a.get("checkedInBy", "N/A")
        ])

    csv_data = output.getvalue()
    today_str = datetime.now().strftime("%Y-%m-%d")
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=FestGate_Attendance_Report_{today_str}.csv"}
    )

# Static Frontend Serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    if os.path.exists(dist_dir) and os.path.isfile(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    if os.path.exists(os.path.join(dist_dir, 'index.html')):
        return send_from_directory(dist_dir, 'index.html')
    return "FestGate backend is running. Build frontend with 'npm run build'."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==========================================")
    print(f"  FestGate — Every Event. One Smart Gate.  ")
    print(f"  Listening on http://localhost:{port}     ")
    print(f"==========================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
