"""
FestGate - Campus Event Management & Passes
Backend Application (Flask)
Handles Participant Signup, Login, Session Management, and Dashboard Data API.
"""

import os
import csv
import re
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, session, redirect, send_file, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# ── Flask Application Configuration ──────────────────────────────────────────
app = Flask(__name__)
# Secret key loaded from environment variable with development fallback
app.secret_key = os.environ.get('FESTGATE_SECRET_KEY', 'festgate-dev-secret-key-change-in-prod')

# ── File Paths & Global Concurrency Lock ─────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARTICIPANTS_CSV = os.path.join(BASE_DIR, 'participants.csv')
EVENTS_CSV = os.path.join(BASE_DIR, 'events.csv')
REGISTRATIONS_CSV = os.path.join(BASE_DIR, 'registrations.csv')

PARTICIPANTS_HEADER = [
    'participant_id',
    'full_name',
    'college',
    'roll_number',
    'email',
    'phone',
    'password_hash',
    'created_at',
    'last_login'
]

# Shared threading.Lock wrapping EVERY read and write on participants.csv
csv_lock = threading.Lock()


# ── Storage Helper Functions ──────────────────────────────────────────────────
def ensure_participants_csv():
    """Ensure participants.csv exists with the correct exact header."""
    with csv_lock:
        if not os.path.exists(PARTICIPANTS_CSV) or os.path.getsize(PARTICIPANTS_CSV) == 0:
            with open(PARTICIPANTS_CSV, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(PARTICIPANTS_HEADER)


def _read_participants_unlocked():
    """Read all participant rows from CSV as dictionaries (must be called with csv_lock held)."""
    if not os.path.exists(PARTICIPANTS_CSV):
        return []
    with open(PARTICIPANTS_CSV, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def _write_participants_unlocked(rows):
    """Write participant rows back to CSV (must be called with csv_lock held)."""
    with open(PARTICIPANTS_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=PARTICIPANTS_HEADER)
        writer.writeheader()
        for r in rows:
            # Ensure every field is written as string
            writer.writerow({k: str(r.get(k, '')) for k in PARTICIPANTS_HEADER})


def get_next_participant_id(rows):
    """Generate next auto-incrementing participant_id (P001, P002, ...) based on the last row."""
    if not rows:
        return "P001"
    last_id = rows[-1].get('participant_id', '')
    match = re.match(r'^P(\d+)$', last_id)
    if match:
        next_num = int(match.group(1)) + 1
        return f"P{next_num:03d}"
    return f"P{len(rows) + 1:03d}"


def is_valid_email(email):
    """Validate email address format strictly."""
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email.strip()))


# ── Page & Static Asset Routes ────────────────────────────────────────────────
@app.route('/')
def route_home():
    """Serve index.html or redirect to /dashboard if participant already logged in."""
    if session.get('participant_id'):
        return redirect('/dashboard')
    return send_file(os.path.join(BASE_DIR, 'index.html'))


@app.route('/dashboard')
def route_dashboard():
    """Serve dashboard.html only if participant session exists; otherwise redirect to /."""
    if not session.get('participant_id'):
        return redirect('/')
    dashboard_file = os.path.join(BASE_DIR, 'dashboard.html')
    if os.path.exists(dashboard_file):
        return send_file(dashboard_file)
    # Temporary fallback if dashboard.html is created in Phase 3
    return send_file(os.path.join(BASE_DIR, 'index.html'))


@app.route('/<path:filename>')
def route_static(filename):
    """Safely serve frontend static assets (CSS, JS, images)."""
    allowed_extensions = ('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.woff', '.woff2', '.ttf')
    if any(filename.endswith(ext) for ext in allowed_extensions) or filename.startswith('assets/'):
        return send_from_directory(BASE_DIR, filename)
    return "Not Found", 404


# ── Participant Authentication API ───────────────────────────────────────────
@app.route('/api/participant/signup', methods=['POST'])
def api_participant_signup():
    """Register a new participant, validate inputs, prevent duplicates, and create session."""
    data = request.get_json(silent=True) or {}
    full_name = str(data.get('full_name', '')).strip()
    college = str(data.get('college', '')).strip()
    roll_number = str(data.get('roll_number', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    phone = str(data.get('phone', '')).strip()
    password = str(data.get('password', ''))
    confirm_password = str(data.get('confirm_password', ''))

    # Validate all fields required
    if not all([full_name, college, roll_number, email, phone, password, confirm_password]):
        return jsonify({'error': 'All fields are required.'}), 400

    # Validate email format
    if not is_valid_email(email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    # Validate phone exactly 10 digits
    if not re.match(r'^\d{10}$', phone):
        return jsonify({'error': 'Phone number must be exactly 10 digits.'}), 400

    # Validate password length (at least 6 characters)
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    # Validate passwords match
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400

    with csv_lock:
        rows = _read_participants_unlocked()

        # Reject signup if email OR roll number already exists (case-insensitively and trimmed)
        for r in rows:
            if r.get('email', '').strip().lower() == email:
                return jsonify({'error': 'An account with this email already exists.'}), 409
            if r.get('roll_number', '').strip().lower() == roll_number.lower():
                return jsonify({'error': 'An account with this roll number already exists.'}), 409

        # Generate auto-incremented ID and password hash
        new_id = get_next_participant_id(rows)
        password_hash = generate_password_hash(password)
        now_iso = datetime.now(timezone.utc).isoformat()

        new_row = {
            'participant_id': new_id,
            'full_name': full_name,
            'college': college,
            'roll_number': roll_number,
            'email': email,
            'phone': phone,
            'password_hash': password_hash,
            'created_at': now_iso,
            'last_login': now_iso
        }
        rows.append(new_row)
        _write_participants_unlocked(rows)

    # Establish Flask session
    session['participant_id'] = new_id
    return jsonify({'success': True, 'redirect': '/dashboard'}), 200


@app.route('/api/participant/login', methods=['POST'])
def api_participant_login():
    """Authenticate participant credentials, update last_login timestamp, and create session."""
    data = request.get_json(silent=True) or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({'error': 'Invalid email or password'}), 401

    with csv_lock:
        rows = _read_participants_unlocked()
        matched = None
        for r in rows:
            if r.get('email', '').strip().lower() == email:
                matched = r
                break

        # Same error message for unknown email and wrong password
        if not matched or not check_password_hash(matched.get('password_hash', ''), password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Update last_login timestamp
        now_iso = datetime.now(timezone.utc).isoformat()
        matched['last_login'] = now_iso
        _write_participants_unlocked(rows)
        participant_id = matched.get('participant_id')

    # Establish Flask session
    session['participant_id'] = participant_id
    return jsonify({'success': True, 'redirect': '/dashboard'}), 200


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Clear active session and return redirect to home page."""
    session.clear()
    return jsonify({'success': True, 'redirect': '/'}), 200


@app.route('/api/participant/me', methods=['GET'])
def api_participant_me():
    """Return logged-in participant's profile details. Return 401 if unauthorized."""
    pid = session.get('participant_id')
    if not pid:
        return jsonify({'error': 'Unauthorized'}), 401

    with csv_lock:
        rows = _read_participants_unlocked()
        matched = next((r for r in rows if r.get('participant_id') == pid), None)

    if not matched:
        session.clear()
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({
        'full_name': matched.get('full_name', ''),
        'college': matched.get('college', ''),
        'roll_number': matched.get('roll_number', ''),
        'email': matched.get('email', ''),
        'phone': matched.get('phone', ''),
        'participant_id': matched.get('participant_id', '')
    }), 200


@app.route('/api/participant/dashboard-data', methods=['GET'])
def api_participant_dashboard_data():
    """Return events from events.csv and participant statistics from registrations.csv."""
    pid = session.get('participant_id')
    if not pid:
        return jsonify({'error': 'Unauthorized'}), 401

    # Read events.csv safely
    events = []
    if os.path.exists(EVENTS_CSV):
        try:
            with open(EVENTS_CSV, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    events.append({
                        'event_id': r.get('event_id', ''),
                        'organizer_id': r.get('organizer_id', ''),
                        'title': r.get('title', ''),
                        'date': r.get('date', ''),
                        'venue': r.get('venue', ''),
                        'description': r.get('description', ''),
                        'capacity': r.get('capacity', '')
                    })
        except Exception:
            events = []

    # Read registrations.csv safely (do NOT modify registrations.csv)
    events_registered = 0
    passes = 0
    checked_in = 0
    if os.path.exists(REGISTRATIONS_CSV):
        try:
            with open(REGISTRATIONS_CSV, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                if 'participant_id' in fieldnames:
                    for r in reader:
                        if r.get('participant_id') == pid:
                            events_registered += 1
                            passes += 1
                            if str(r.get('checked_in', '0')) == '1':
                                checked_in += 1
        except Exception:
            pass

    return jsonify({
        'events': events,
        'stats': {
            'events_registered': events_registered,
            'passes': passes,
            'checked_in': checked_in
        }
    }), 200


# ── Startup Initialization ────────────────────────────────────────────────────
ensure_participants_csv()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
