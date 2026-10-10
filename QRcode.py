import streamlit as st
from pathlib import Path
from io import BytesIO
from datetime import datetime
from PIL import Image
import qrcode
import cv2
import numpy as np
import json
import uuid
import re

# Try importing firebase_admin
try:
    import firebase_admin
    from firebase_admin import credentials, db
    HAS_FIREBASE_LIB = True
except ImportError:
    HAS_FIREBASE_LIB = False

# ---------------- CONFIGURATION ----------------
DATABASE_URL = "https://festgate-66dc3-default-rtdb.firebaseio.com/"
KEY_FILE = Path(__file__).parent / "serviceaccount.json"

# In-memory local fallback store if Firebase service account is not yet provided
if "local_festgate_db" not in st.session_state:
    st.session_state["local_festgate_db"] = {}


# ---------------- LOCAL DB WRAPPER ----------------
class LocalFirebaseMock:
    """Provides the same child().set() / get() / update() API as Firebase RTDB when serviceaccount.json is not present."""
    def __init__(self, key=None):
        self.key = key

    def child(self, child_key):
        return LocalFirebaseMock(key=child_key)

    def set(self, data):
        if self.key:
            st.session_state["local_festgate_db"][self.key] = data

    def update(self, data):
        if self.key and self.key in st.session_state["local_festgate_db"]:
            st.session_state["local_festgate_db"][self.key].update(data)

    def get(self):
        if self.key is None:
            return st.session_state["local_festgate_db"]
        return st.session_state["local_festgate_db"].get(self.key)


# ---------------- FIREBASE CONNECTION ----------------
def connect_firebase():
    """Connect to Firebase RTDB or fallback to local mock with instructions."""
    if not KEY_FILE.exists():
        st.warning(
            "⚠️ **serviceaccount.json not found** in the project folder.\n\n"
            "To connect to live Firebase RTDB (`https://festgate-66dc3-default-rtdb.firebaseio.com/`), "
            "place your `serviceaccount.json` in the app directory. "
            "Running in **Local Simulation Mode** so you can test QR Generation & Scanning right now!"
        )
        return LocalFirebaseMock(), False

    if not HAS_FIREBASE_LIB:
        st.error("firebase-admin package is not installed.")
        return LocalFirebaseMock(), False

    try:
        if not firebase_admin._apps:
            credential = credentials.Certificate(str(KEY_FILE))
            firebase_admin.initialize_app(
                credential,
                {"databaseURL": DATABASE_URL}
            )
        return db.reference("registrations"), True
    except Exception as e:
        st.error(f"Firebase connection error: {e}")
        return LocalFirebaseMock(), False


# ---------------- QR GENERATION ----------------
def generate_qr(registration_id):
    qr_data = json.dumps({
        "registration_id": registration_id
    })
    image = qrcode.make(qr_data)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


# ---------------- EMAIL VALIDATION ----------------
def is_valid_email(email):
    """Validate email address format strictly."""
    if not email or not isinstance(email, str):
        return False
    email = email.strip()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False
    tld = domain.split(".")[-1]
    if len(tld) < 2 or not tld.isalpha():
        return False
    return True


# ---------------- REGISTER STUDENT ----------------
def register_student(database, name, email, event):
    if not is_valid_email(email):
        raise ValueError("Invalid email format.")
    registration_id = str(uuid.uuid4())
    student_data = {
        "student_name": name.strip(),
        "student_email": email.strip().lower(),
        "email_verified": True,
        "event_name": event,
        "created_at": datetime.now().astimezone().isoformat(),
        "attended": False,
        "attended_at": None
    }
    database.child(registration_id).set(student_data)
    return registration_id


# ---------------- READ QR IMAGE ----------------
def scan_qr(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image_array = np.array(image)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

    detector = cv2.QRCodeDetector()
    text, _, _ = detector.detectAndDecode(image_array)

    if not text:
        return None

    try:
        data = json.loads(text)
        return data.get("registration_id")
    except (json.JSONDecodeError, AttributeError):
        # Plain string support (e.g. 6-digit ticket code or raw UUID)
        return text.strip()


# ---------------- VERIFY ATTENDANCE ----------------
def mark_attendance(database, registration_id):
    if not registration_id:
        return "invalid", "QR code could not be read."

    student_ref = database.child(registration_id)
    student = student_ref.get()

    if not isinstance(student, dict):
        return "invalid", f"Registration '{registration_id}' not found."

    if student.get("attended") is True:
        return "duplicate", f"Attendance is already marked for {student.get('student_name', 'Student')}."

    checked_in = datetime.now().astimezone().isoformat()
    student_ref.update({
        "attended": True,
        "attended_at": checked_in
    })

    return "success", (
        f"Attendance marked for {student.get('student_name')} "
        f"— {student.get('event_name')}."
    )


# ---------------- UI DESIGN STYLING ----------------
def inject_festgate_styles():
    st.markdown(
        """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --pri-s:#6366f1;--pri-e:#8b5cf6;
  --gradient:linear-gradient(135deg,var(--pri-s),var(--pri-e));
  --card-bg:rgba(255,255,255,.92);--card-b:rgba(99,102,241,.14);
  --t1:#1e1b4b;--t2:#6b7280;
  --r:16px;
  --sh:0 4px 24px rgba(0,0,0,.08);
  --sh-up:0 8px 32px rgba(99,102,241,.18);
  --ok:#10b981;--ok-bg:#ecfdf5;
  --err:#ef4444;--err-bg:#fef2f2;
}
@media(prefers-color-scheme:dark){:root{
  --card-bg:rgba(30,30,46,.9);--card-b:rgba(139,92,246,.25);
  --t1:#e2e8f0;--t2:#94a3b8;
  --ok-bg:rgba(16,185,129,.14);--err-bg:rgba(239,68,68,.14);
}}
html,body,[class*="css"],.stMarkdown,.stTextInput label,.stSelectbox label{
  font-family:'Inter',system-ui,-apple-system,sans-serif!important;
}
.festgate-hero{
  background:linear-gradient(135deg,#6366f1,#8b5cf6,#a78bfa,#6366f1);
  background-size:300% 300%;animation:gradShift 8s ease infinite;
  border-radius:var(--r);padding:2.2rem 1.5rem;text-align:center;margin-bottom:1.4rem;
}
@keyframes gradShift{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}
.festgate-hero h1{color:#fff!important;margin:0;font-size:2.2rem;font-weight:800}
.festgate-hero p{color:rgba(255,255,255,.9);margin:.4rem 0 0;font-size:1.05rem}
.stTabs [data-baseweb="tab-list"]{gap:.5rem}
.stTabs [data-baseweb="tab"]{border-radius:10px;font-family:'Inter',sans-serif!important;font-weight:600}
.stButton>button,.stFormSubmitButton>button{
  border-radius:12px!important;font-family:'Inter',sans-serif!important;font-weight:600!important;
  transition:transform .2s ease,box-shadow .2s ease!important;
}
.stButton>button:hover{transform:translateY(-2px)!important}
.stFormSubmitButton>button{
  background:var(--gradient)!important;color:#fff!important;border:none!important;
}
</style>""",
        unsafe_allow_html=True,
    )


# ---------------- FESTGATE MAIN COMPONENT ----------------
def render_festgate_app(show_back_button=False):
    inject_festgate_styles()

    if show_back_button:
        if st.button("← Back to EventEase", key="festgate_back_btn"):
            st.session_state.page = "welcome"
            st.rerun()

    st.markdown(
        """<div class="festgate-hero">
            <h1>🎟️ FestGate QR System</h1>
            <p>Event Registration • Unique QR • Attendance Verification</p>
        </div>""",
        unsafe_allow_html=True,
    )

    database, is_live_firebase = connect_firebase()

    registration_tab, scanner_tab, dashboard_tab = st.tabs([
        "📝 Registration",
        "📷 QR Scanner",
        "📊 Dashboard"
    ])

    # ── REGISTRATION TAB ──
    with registration_tab:
        pending = st.session_state.get("festgate_pending_verify")

        if pending:
            st.markdown(
                f"""<div class="verify-email-box">
                    <div class="verify-email-meta">
                        <span class="verify-pill">📬 Verification Email Sent</span><br>
                        <strong>To:</strong> {pending['email']}<br>
                        <strong>From:</strong> FestGate Auth &lt;verify@festgate.edu&gt;
                    </div>
                    <div class="verify-email-subject">🎫 Confirm Registration for {pending['event']}</div>
                    <div class="verify-email-body">
                        Hello <strong>{pending['name']}</strong>,<br>
                        Click the verification button below to immediately verify your email and generate your unique QR entry pass for <strong>{pending['event']}</strong>.
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            v_col1, v_col2 = st.columns([2, 1])
            with v_col1:
                if st.button("✅ Click Here to Verify Email & Generate QR (તરત વેરિફાય કરો)", key="festgate_verify_btn", use_container_width=True):
                    try:
                        registration_id = register_student(database, pending["name"], pending["email"], pending["event"])
                        st.session_state["festgate_latest_id"] = registration_id
                        st.session_state["festgate_pending_verify"] = None
                        st.balloons()
                        st.success("🎉 Email verified immediately! QR pass generated.")
                        st.rerun()
                    except Exception as error:
                        st.error(f"Registration failed: {error}")
            with v_col2:
                if st.button("Edit Details", key="festgate_cancel_btn", use_container_width=True):
                    st.session_state["festgate_pending_verify"] = None
                    st.rerun()

        else:
            st.subheader("Student Registration")
            with st.form("festgate_reg_form"):
                student_name = st.text_input("Student Name", placeholder="e.g. John Doe")
                student_email = st.text_input("Student Email", placeholder="e.g. student@college.edu")
                event_name = st.selectbox(
                    "Select Event",
                    [
                        "Hackathon 2026",
                        "Coding Competition",
                        "Robotics",
                        "Code Carnival",
                        "Tech Symposium"
                    ]
                )
                submitted = st.form_submit_button("Send Verification Email & Register", use_container_width=True)

            if submitted:
                if not student_name.strip() or not student_email.strip():
                    st.error("❌ Please enter both your name and email address.")
                elif not is_valid_email(student_email):
                    st.error("❌ Invalid Email Format! Please enter a valid email address (e.g. student@college.edu).")
                else:
                    st.session_state["festgate_pending_verify"] = {
                        "name": student_name.strip(),
                        "email": student_email.strip().lower(),
                        "event": event_name
                    }
                    st.rerun()

        reg_id = st.session_state.get("festgate_latest_id")
        if reg_id:
            try:
                student = database.child(reg_id).get()
                if isinstance(student, dict):
                    qr_image = generate_qr(reg_id)
                    st.markdown("---")
                    st.subheader("Your Unique QR Code")

                    col1, col2 = st.columns([1, 1], gap="medium")
                    with col1:
                        st.image(qr_image, width=240, caption="Scan this at event entrance")
                    with col2:
                        st.markdown(f"**Student:** {student.get('student_name', '')}")
                        st.markdown(f"**Email:** {student.get('student_email', '—')} *(Verified ✅)*")
                        st.markdown(f"**Event:** {student.get('event_name', '')}")
                        st.markdown("**Registration ID:**")
                        st.code(reg_id)
                        st.download_button(
                            "📥 Download QR Code",
                            data=qr_image,
                            file_name=f"festgate_{reg_id}.png",
                            mime="image/png",
                            use_container_width=True
                        )
            except Exception as error:
                st.error(f"Could not load QR code: {error}")

    # ── QR SCANNER TAB ──
    with scanner_tab:
        st.subheader("Verify QR & Mark Attendance")
        st.info("Upload the participant's QR image or ticket pass to scan.")

        uploaded_file = st.file_uploader(
            "Choose QR image",
            type=["png", "jpg", "jpeg"],
            key="festgate_qr_upload"
        )

        if uploaded_file and st.button("Scan & Verify Attendance", use_container_width=True, key="festgate_scan_btn"):
            try:
                registration_id = scan_qr(uploaded_file)
                if not registration_id:
                    st.error("🚫 Could not detect or read a valid QR code in this image.")
                else:
                    status, message = mark_attendance(database, registration_id)
                    if status == "success":
                        st.balloons()
                        st.success(f"🎉 {message}")
                    elif status == "duplicate":
                        st.warning(f"⚠️ {message}")
                    else:
                        st.error(f"❌ {message}")
            except Exception as error:
                st.error(f"QR verification failed: {error}")

    # ── ATTENDANCE DASHBOARD TAB ──
    with dashboard_tab:
        st.subheader("Event Dashboard")

        if st.button("🔄 Refresh Data", key="festgate_refresh"):
            st.rerun()

        try:
            records = database.get() or {}
            if not isinstance(records, dict):
                records = {}

            rows = []
            for r_id, student in records.items():
                if not isinstance(student, dict):
                    continue
                rows.append({
                    "Student": student.get("student_name", ""),
                    "Email": student.get("student_email", "—"),
                    "Email Verified": "✅ Yes" if student.get("email_verified") else "⏳ Pending",
                    "Event": student.get("event_name", ""),
                    "Registration ID": r_id,
                    "Attendance": (
                        "✅ Present"
                        if student.get("attended") is True
                        else "⏳ Not checked in"
                    ),
                    "Registered At": student.get("created_at", "")[:19].replace("T", " ") if student.get("created_at") else "",
                    "Checked In At": student.get("attended_at", "")[:19].replace("T", " ") if student.get("attended_at") else ""
                })

            total = len(rows)
            present = sum(1 for row in rows if "Present" in row["Attendance"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Registrations", total)
            c2.metric("Checked In (Present)", present)
            c3.metric("Remaining", total - present)

            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("No registrations found yet.")
        except Exception as error:
            st.error(f"Dashboard failed: {error}")


# ---------------- STANDALONE EXECUTION ----------------
if __name__ == "__main__":
    st.set_page_config(
        page_title="FestGate QR System",
        page_icon="🎟️",
        layout="centered"
    )
    render_festgate_app(show_back_button=False)
