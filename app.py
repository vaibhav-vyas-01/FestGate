import streamlit as st
import pandas as pd
import hashlib
import os
import uuid
import random
import io
import re
from datetime import datetime
import QRcode

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="EventEase", page_icon="🎪", layout="centered")

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — single CSS block
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Design tokens ──────────────────────────────────────────────── */
:root{
  --pri-s:#6366f1;--pri-e:#8b5cf6;
  --gradient:linear-gradient(135deg,var(--pri-s),var(--pri-e));
  --card-bg:rgba(255,255,255,.92);--card-b:rgba(99,102,241,.12);
  --t1:#1e1b4b;--t2:#6b7280;
  --r:16px;
  --sh:0 4px 24px rgba(0,0,0,.07);
  --sh-up:0 8px 32px rgba(99,102,241,.16);
  --ok:#10b981;--ok-bg:#ecfdf5;
  --err:#ef4444;--err-bg:#fef2f2;
}
@media(prefers-color-scheme:dark){:root{
  --card-bg:rgba(30,30,46,.88);--card-b:rgba(139,92,246,.2);
  --t1:#e2e8f0;--t2:#94a3b8;
  --sh:0 4px 24px rgba(0,0,0,.25);--sh-up:0 8px 32px rgba(139,92,246,.22);
  --ok-bg:rgba(16,185,129,.12);--err-bg:rgba(239,68,68,.12);
}}

/* ── Hide Streamlit chrome ──────────────────────────────────────── */
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.block-container{padding-top:1.5rem!important}

/* ── Typography ─────────────────────────────────────────────────── */
html,body,[class*="css"],.stMarkdown,.stTextInput label,
.stSelectbox label,.stDateInput label,.stTextArea label,
.stNumberInput label{
  font-family:'Inter',system-ui,-apple-system,sans-serif!important;
}

/* ── Keyframes ──────────────────────────────────────────────────── */
@keyframes fadeInUp{
  from{opacity:0;transform:translateY(24px)}
  to{opacity:1;transform:translateY(0)}
}
@keyframes gradientShift{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}
}
@keyframes pulse{
  0%,100%{transform:scale(1)}
  50%{transform:scale(1.018)}
}
@keyframes barFill{from{width:0}}

@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;
    animation-iteration-count:1!important;
    transition-duration:.01ms!important;
  }
}

/* ── Hero ───────────────────────────────────────────────────────── */
.hero{
  background:linear-gradient(135deg,var(--pri-s),var(--pri-e),#a78bfa,var(--pri-s));
  background-size:300% 300%;
  animation:fadeInUp .6s ease-out,gradientShift 8s ease infinite;
  border-radius:var(--r);padding:2.5rem 1.5rem;
  text-align:center;margin-bottom:1.5rem;
}
.hero h1,.hero h2{color:#fff!important;margin:0;font-weight:800}
.hero h1{font-size:2.4rem}
.hero h2{font-size:1.6rem}
.hero p{color:rgba(255,255,255,.88);margin:.4rem 0 0;font-size:1.05rem}
.hero-sm{padding:1.8rem 1.2rem}

/* ── Role cards ─────────────────────────────────────────────────── */
.role-card{
  background:var(--card-bg);border:1.5px solid var(--card-b);
  border-radius:var(--r);padding:2rem 1.2rem;text-align:center;
  box-shadow:var(--sh);
  transition:transform .25s ease,box-shadow .25s ease;
  animation:fadeInUp .5s ease-out both;cursor:default;
}
.role-card:hover{transform:translateY(-4px);box-shadow:var(--sh-up)}
.role-icon{font-size:2.8rem;margin-bottom:.6rem}
.role-card h3{color:var(--t1);margin:0 0 .4rem;font-weight:700;font-size:1.2rem}
.role-card p{color:var(--t2);margin:0;font-size:.92rem;line-height:1.4}
.role-card-delay{animation-delay:.15s}

/* ── Generic ee-card ────────────────────────────────────────────── */
.ee-card{
  background:var(--card-bg);border:1px solid var(--card-b);
  border-radius:var(--r);padding:1.5rem;box-shadow:var(--sh);
  transition:transform .25s ease,box-shadow .25s ease;
  animation:fadeInUp .5s ease-out both;
}
.ee-card:hover{transform:translateY(-4px);box-shadow:var(--sh-up)}

/* ── Success / Error ────────────────────────────────────────────── */
.success-card{
  background:var(--ok-bg);border-left:4px solid var(--ok);
  border-radius:var(--r);padding:1.2rem 1.5rem;
  color:var(--t1);font-weight:600;font-size:1.05rem;
  margin:1rem 0;animation:fadeInUp .4s ease-out;
}
.error-card{
  background:var(--err-bg);border-left:4px solid var(--err);
  border-radius:var(--r);padding:1.2rem 1.5rem;
  color:var(--t1);font-weight:600;font-size:1.05rem;
  margin:1rem 0;animation:fadeInUp .4s ease-out;
}

/* Large success card for check-in */
.success-card-lg{
  background:var(--ok-bg);border:2px solid var(--ok);
  border-radius:var(--r);padding:2rem;text-align:center;
  animation:fadeInUp .4s ease-out,pulse 2s ease-in-out infinite;
  margin:1rem 0;
}
.success-card-lg .card-icon{font-size:3rem}
.success-card-lg .card-title{
  color:var(--ok);font-size:1.4rem;font-weight:700;margin:.5rem 0 .2rem;
}
.success-card-lg .card-detail{color:var(--t1);font-size:1.1rem;font-weight:500}

.error-card-lg{
  background:var(--err-bg);border:2px solid var(--err);
  border-radius:var(--r);padding:2rem;text-align:center;
  animation:fadeInUp .4s ease-out;margin:1rem 0;
}
.error-card-lg .card-icon{font-size:3rem}
.error-card-lg .card-title{
  color:var(--err);font-size:1.4rem;font-weight:700;margin:.5rem 0 .2rem;
}
.error-card-lg .card-detail{color:var(--t1);font-size:1.05rem;font-weight:500}

/* ── Metric cards ───────────────────────────────────────────────── */
.metric-card{
  background:var(--card-bg);border:1.5px solid var(--card-b);
  border-radius:var(--r);padding:1.2rem;text-align:center;
  box-shadow:var(--sh);animation:fadeInUp .5s ease-out both;
}
.metric-val{
  font-size:2rem;font-weight:800;
  background:var(--gradient);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;
}
.metric-label{color:var(--t2);font-size:.85rem;font-weight:500;margin-top:.2rem}

/* ── Progress bar ───────────────────────────────────────────────── */
.progress-track{
  background:var(--card-b);border-radius:99px;height:12px;
  overflow:hidden;margin:.5rem 0 1rem;
}
.progress-fill{
  height:100%;border-radius:99px;background:var(--gradient);
  animation:barFill 1s ease-out;
}

/* ── Pass card ──────────────────────────────────────────────────── */
.pass-card{
  position:relative;
  background:var(--card-bg);
  border-radius:var(--r);padding:2rem 1.5rem;text-align:center;
  box-shadow:var(--sh);overflow:hidden;
  animation:pulse 2.5s ease-in-out infinite,fadeInUp .5s ease-out;
}
.pass-card::before{
  content:'';position:absolute;inset:-2px;
  background:var(--gradient);border-radius:calc(var(--r) + 2px);z-index:-1;
}
.pass-card h3{color:var(--t1);font-weight:700;margin:0 0 .3rem}
.pass-detail{color:var(--t2);font-size:.92rem;margin:.15rem 0}
.pass-code{
  font-size:1.8rem;font-weight:800;letter-spacing:.25em;
  background:var(--gradient);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;
  margin:.8rem 0;
}
.pass-divider{
  border:none;border-top:2px dashed var(--card-b);margin:1rem 0;
}

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton>button{
  border-radius:12px!important;
  font-family:'Inter',system-ui,sans-serif!important;
  font-weight:600!important;
  transition:transform .2s ease,box-shadow .2s ease!important;
}
.stButton>button:hover{
  transform:translateY(-2px)!important;box-shadow:var(--sh-up)!important;
}
.stFormSubmitButton>button{
  background:var(--gradient)!important;color:#fff!important;
  border:none!important;padding:.6rem 1.5rem!important;
}

/* ── Tabs ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"]{gap:.5rem}
.stTabs [data-baseweb="tab"]{
  border-radius:10px;
  font-family:'Inter',system-ui,sans-serif!important;
  font-weight:500;
}

/* ── Helpers ────────────────────────────────────────────────────── */
.subtitle{text-align:center;color:var(--t2);font-size:1.1rem;font-weight:500;margin-bottom:1.2rem}
.section-head{color:var(--t1);font-size:1.15rem;font-weight:700;margin:1.2rem 0 .6rem}

/* ── Responsive ─────────────────────────────────────────────────── */
@media(max-width:600px){
  .hero h1{font-size:1.8rem}
  .hero h2{font-size:1.3rem}
  .hero{padding:1.8rem 1rem}
  .role-card{padding:1.4rem 1rem}
  .role-icon{font-size:2.2rem}
  .metric-val{font-size:1.5rem}
  .pass-code{font-size:1.4rem}
}

/* ── Verification Email Simulation Card ─────────────────────────── */
.verify-email-box{
  background:var(--card-bg);
  border:2px dashed var(--pri-s);
  border-radius:var(--r);
  padding:1.6rem;
  margin:1.2rem 0;
  box-shadow:var(--sh-up);
  animation:fadeInUp .4s ease-out;
}
.verify-email-meta{
  border-bottom:1px solid var(--card-b);
  padding-bottom:.8rem;margin-bottom:1rem;
  font-size:.88rem;color:var(--t2);line-height:1.6;
}
.verify-email-meta strong{color:var(--t1)}
.verify-email-subject{
  color:var(--t1);font-weight:700;font-size:1.15rem;margin:.4rem 0 .2rem;
}
.verify-email-body{
  color:var(--t1);font-size:.98rem;line-height:1.6;margin-bottom:1.2rem;
  background:rgba(99,102,241,.06);padding:1rem 1.2rem;border-radius:12px;
}
.verify-pill{
  display:inline-block;padding:.2rem .6rem;border-radius:99px;
  background:var(--ok-bg);color:var(--ok);font-size:.8rem;font-weight:700;
}
</style>""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ═══════════════════════════════════════════════════════════════════════════════
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

_SCHEMAS = {
    "organizers.csv": ["organizer_id", "name", "email", "salt", "password_hash"],
    "events.csv": [
        "event_id", "organizer_id", "title", "date", "venue",
        "description", "capacity",
    ],
    "registrations.csv": [
        "reg_id", "event_id", "name", "email", "ticket_code",
        "checked_in", "registered_at",
    ],
}


def _path(fn):
    return os.path.join(DATA_DIR, fn)


def ensure_csv(fn):
    p = _path(fn)
    if not os.path.exists(p):
        pd.DataFrame(columns=_SCHEMAS[fn]).to_csv(p, index=False)
    return p


def read_csv(fn):
    p = ensure_csv(fn)
    try:
        df = pd.read_csv(p, dtype=str)
        if df.empty or len(df.columns) == 0:
            return pd.DataFrame(columns=_SCHEMAS[fn])
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=_SCHEMAS[fn])


def write_csv(df, fn):
    df.to_csv(_path(fn), index=False)


# ═══════════════════════════════════════════════════════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════════════════════════════════════════════════════
def _salt():
    return os.urandom(16).hex()


def _hash_pw(pw, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", pw.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET CODE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
def _new_ticket_code():
    """Return a unique 6-digit zero-padded code."""
    regs = read_csv("registrations.csv")
    existing = set(regs["ticket_code"]) if not regs.empty else set()
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if code not in existing:
            return code


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════
def register_organizer(name, email, pw):
    if not is_valid_email(email):
        return False, "Please provide a valid email address (e.g. you@college.edu)."
    df = read_csv("organizers.csv")
    if not df.empty and email.strip().lower() in df["email"].str.lower().values:
        return False, "An account with this email already exists."
    salt = _salt()
    row = pd.DataFrame([{
        "organizer_id": str(uuid.uuid4()),
        "name": name.strip(),
        "email": email.strip().lower(),
        "salt": salt,
        "password_hash": _hash_pw(pw, salt),
    }])
    write_csv(pd.concat([df, row], ignore_index=True), "organizers.csv")
    return True, "Account created successfully!"


def login_organizer(email, pw):
    if not is_valid_email(email):
        return False, None, None
    df = read_csv("organizers.csv")
    if df.empty:
        return False, None, None
    match = df[df["email"].str.lower() == email.strip().lower()]
    if match.empty:
        return False, None, None
    r = match.iloc[0]
    if _hash_pw(pw, r["salt"]) == r["password_hash"]:
        return True, r["organizer_id"], r["name"]
    return False, None, None


# ═══════════════════════════════════════════════════════════════════════════════
# EVENT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def create_event(org_id, title, date, venue, description, capacity):
    df = read_csv("events.csv")
    row = pd.DataFrame([{
        "event_id": str(uuid.uuid4()),
        "organizer_id": org_id,
        "title": title.strip(),
        "date": date,
        "venue": venue.strip(),
        "description": description.strip(),
        "capacity": str(int(capacity)),
    }])
    write_csv(pd.concat([df, row], ignore_index=True), "events.csv")


def get_my_events(org_id):
    df = read_csv("events.csv")
    if df.empty:
        return df
    return df[df["organizer_id"] == org_id].reset_index(drop=True)


def get_event_regs(event_id):
    df = read_csv("registrations.csv")
    if df.empty:
        return df
    return df[df["event_id"] == event_id].reset_index(drop=True)


def check_in_ticket(code, event_id):
    """Return (status, name).  status: 'ok' | 'already' | 'invalid'."""
    code = code.strip()
    if len(code) != 6 or not code.isdigit():
        return "invalid", ""
    df = read_csv("registrations.csv")
    if df.empty:
        return "invalid", ""
    mask = (df["ticket_code"] == code) & (df["event_id"] == event_id)
    if not mask.any():
        return "invalid", ""
    idx = df.index[mask][0]
    if df.loc[idx, "checked_in"] == "1":
        return "already", df.loc[idx, "name"]
    df.loc[idx, "checked_in"] = "1"
    write_csv(df, "registrations.csv")
    return "ok", df.loc[idx, "name"]


def get_open_events():
    """Events with remaining capacity > 0."""
    evts = read_csv("events.csv")
    regs = read_csv("registrations.csv")
    if evts.empty:
        return evts
    counts = regs.groupby("event_id").size() if not regs.empty else pd.Series(dtype=int)
    rows = []
    for _, e in evts.iterrows():
        cap = int(e["capacity"])
        used = counts.get(e["event_id"], 0)
        if used < cap:
            rows.append(e)
    if not rows:
        return pd.DataFrame(columns=evts.columns)
    return pd.DataFrame(rows).reset_index(drop=True)


def register_participant(event_id, name, email):
    if not is_valid_email(email):
        return False, "Please provide a valid email address.", ""
    regs = read_csv("registrations.csv")
    evts = read_csv("events.csv")
    # duplicate check
    if not regs.empty:
        dup = regs[(regs["event_id"] == event_id) & (regs["email"].str.lower() == email.strip().lower())]
        if not dup.empty:
            return False, "You are already registered for this event.", ""
    # capacity check
    evt = evts[evts["event_id"] == event_id]
    if evt.empty:
        return False, "Event not found.", ""
    cap = int(evt.iloc[0]["capacity"])
    used = len(regs[regs["event_id"] == event_id]) if not regs.empty else 0
    if used >= cap:
        return False, "This event is full.", ""
    code = _new_ticket_code()
    row = pd.DataFrame([{
        "reg_id": str(uuid.uuid4()),
        "event_id": event_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "ticket_code": code,
        "checked_in": "0",
        "registered_at": datetime.now().isoformat(timespec="seconds"),
    }])
    write_csv(pd.concat([regs, row], ignore_index=True), "registrations.csv")
    return True, "Registered!", code


def lookup_pass(email, code):
    regs = read_csv("registrations.csv")
    if regs.empty:
        return None
    match = regs[
        (regs["email"].str.lower() == email.strip().lower())
        & (regs["ticket_code"] == code.strip())
    ]
    if match.empty:
        return None
    r = match.iloc[0]
    evts = read_csv("events.csv")
    evt = evts[evts["event_id"] == r["event_id"]]
    if evt.empty:
        return None
    e = evt.iloc[0]
    return {
        "name": r["name"], "email": r["email"], "ticket_code": r["ticket_code"],
        "title": e["title"], "date": e["date"], "venue": e["venue"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# QR CODE HELPER
# ═══════════════════════════════════════════════════════════════════════════════
def make_qr_png(data_str):
    """Return PNG bytes for a QR code encoding *data_str*."""
    import qrcode
    img = qrcode.make(data_str, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "page": "welcome",
    "org_id": None,
    "org_name": None,
    "selected_event": None,
    "org_pending_verify": None,
    "part_pending_verify": None,
    "part_last_pass": None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _nav(p):
    st.session_state.page = p


def _logout():
    st.session_state.update({
        "org_id": None,
        "org_name": None,
        "selected_event": None,
        "org_pending_verify": None,
        "page": "welcome",
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

# ── Welcome ──────────────────────────────────────────────────────────────────
def page_welcome():
    st.markdown(
        """<div class="hero">
            <h1>🎪 EventEase</h1>
            <p>College Event Check-In, Simplified</p>
        </div>
        <p class="subtitle">What do you want to do?</p>""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            """<div class="role-card">
                <div class="role-icon">🎯</div>
                <h3>Event Organizer</h3>
                <p>Create &amp; manage events, check in attendees</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("I'm an Organizer", key="go_org", use_container_width=True):
            _nav("org_auth"); st.rerun()
    with c2:
        st.markdown(
            """<div class="role-card role-card-delay">
                <div class="role-icon">🎫</div>
                <h3>Event Participant</h3>
                <p>Register for events &amp; get your digital pass</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("I'm a Participant", key="go_part", use_container_width=True):
            _nav("participant"); st.rerun()
    with c3:
        st.markdown(
            """<div class="role-card" style="animation-delay:.3s">
                <div class="role-icon">🎟️</div>
                <h3>FestGate QR</h3>
                <p>Firebase Realtime DB &amp; OpenCV QR Scanner</p>
            </div>""",
            unsafe_allow_html=True,
        )
        if st.button("Open FestGate QR", key="go_festgate", use_container_width=True):
            _nav("festgate"); st.rerun()


# ── Organizer Auth ───────────────────────────────────────────────────────────
def page_org_auth():
    if st.button("← Back", key="back_auth"):
        st.session_state.org_pending_verify = None
        _nav("welcome"); st.rerun()

    st.markdown(
        """<div class="hero hero-sm">
            <h2>🎯 Organizer Access</h2>
            <p>Log in or create your account</p>
        </div>""",
        unsafe_allow_html=True,
    )
    tab_in, tab_up = st.tabs(["🔑 Login", "📝 Register"])

    with tab_in:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@college.edu")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if not email or not pw:
                    st.markdown(
                        '<div class="error-card">❌ Please fill in all fields.</div>',
                        unsafe_allow_html=True,
                    )
                elif not is_valid_email(email):
                    st.markdown(
                        '<div class="error-card">❌ Please enter a valid email address (e.g. you@college.edu).</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    ok, oid, oname = login_organizer(email, pw)
                    if ok:
                        st.session_state.update(
                            {"org_id": oid, "org_name": oname, "page": "org_dashboard"}
                        )
                        st.rerun()
                    else:
                        st.markdown(
                            '<div class="error-card">❌ Invalid email or password.</div>',
                            unsafe_allow_html=True,
                        )

    with tab_up:
        pending = st.session_state.get("org_pending_verify")
        if pending:
            st.markdown(
                f"""<div class="verify-email-box">
                    <div class="verify-email-meta">
                        <span class="verify-pill">📬 Verification Email Sent</span><br>
                        <strong>To:</strong> {pending['email']}<br>
                        <strong>From:</strong> EventEase Security &lt;verify@eventease.edu&gt;
                    </div>
                    <div class="verify-email-subject">🎯 Verify your Organizer Account</div>
                    <div class="verify-email-body">
                        Hello <strong>{pending['name']}</strong>,<br>
                        Thank you for registering with EventEase! Click the verification button below to immediately verify your email and activate your organizer account.
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            v_col1, v_col2 = st.columns([2, 1])
            with v_col1:
                if st.button("✅ Click Here to Verify Email & Activate Account (તરત વેરિફાય કરો)", key="btn_verify_org", use_container_width=True):
                    ok, msg = register_organizer(pending["name"], pending["email"], pending["pw"])
                    if ok:
                        _, oid, oname = login_organizer(pending["email"], pending["pw"])
                        st.session_state.org_id = oid
                        st.session_state.org_name = oname
                        st.session_state.org_pending_verify = None
                        st.session_state.page = "org_dashboard"
                        st.balloons()
                        st.rerun()
                    else:
                        st.markdown(
                            f'<div class="error-card">❌ {msg}</div>',
                            unsafe_allow_html=True,
                        )
            with v_col2:
                if st.button("Edit Details", key="btn_cancel_org_verify", use_container_width=True):
                    st.session_state.org_pending_verify = None
                    st.rerun()
        else:
            with st.form("reg_form"):
                name = st.text_input("Full Name", placeholder="Jane Doe")
                r_email = st.text_input("Email", placeholder="you@college.edu")
                r_pw = st.text_input("Password", type="password", help="Min 6 characters")
                r_pw2 = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Send Verification Email", use_container_width=True):
                    if not name or not r_email or not r_pw:
                        st.markdown(
                            '<div class="error-card">❌ Please fill in all fields.</div>',
                            unsafe_allow_html=True,
                        )
                    elif not is_valid_email(r_email):
                        st.markdown(
                            '<div class="error-card">❌ Please enter a valid email address (e.g. you@college.edu).</div>',
                            unsafe_allow_html=True,
                        )
                    elif len(r_pw) < 6:
                        st.markdown(
                            '<div class="error-card">❌ Password must be at least 6 characters.</div>',
                            unsafe_allow_html=True,
                        )
                    elif r_pw != r_pw2:
                        st.markdown(
                            '<div class="error-card">❌ Passwords do not match.</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        df = read_csv("organizers.csv")
                        if not df.empty and r_email.strip().lower() in df["email"].str.lower().values:
                            st.markdown(
                                '<div class="error-card">❌ An account with this email already exists.</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.session_state.org_pending_verify = {
                                "name": name.strip(),
                                "email": r_email.strip().lower(),
                                "pw": r_pw
                            }
                            st.rerun()


# ── Organizer Dashboard ─────────────────────────────────────────────────────
def page_org_dashboard():
    # Header row
    hdr1, hdr2 = st.columns([4, 1])
    with hdr1:
        st.markdown(
            f"""<div class="hero hero-sm">
                <h2>🎯 Dashboard</h2>
                <p>Welcome back, {st.session_state.org_name}!</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with hdr2:
        st.write("")
        if st.button("🚪 Logout", key="logout"):
            _logout(); st.rerun()

    if st.button("← Switch Role", key="switch"):
        _logout(); st.rerun()

    # ── Tabs ──
    t_create, t_stats, t_checkin, t_export = st.tabs(
        ["➕ Create Event", "📊 My Events & Stats", "✅ Check-In", "📥 Export"]
    )

    org_id = st.session_state.org_id
    my_events = get_my_events(org_id)

    # ── Tab 1: Create Event ──
    with t_create:
        with st.form("create_event"):
            title = st.text_input("Event Title", placeholder="Hackathon 2026")
            date = st.date_input("Date")
            venue = st.text_input("Venue", placeholder="Main Auditorium")
            desc = st.text_area("Description", placeholder="A brief description…",
                                max_chars=500)
            cap = st.number_input("Capacity", min_value=1, value=100, step=1)
            if st.form_submit_button("Create Event", use_container_width=True):
                if not title or not venue:
                    st.markdown(
                        '<div class="error-card">❌ Title and venue are required.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    create_event(org_id, title, str(date), venue, desc, cap)
                    st.markdown(
                        '<div class="success-card">✅ Event created!</div>',
                        unsafe_allow_html=True,
                    )
                    st.rerun()

    # ── Helper: event selector (shared by stats, check-in, export) ──
    def _pick_event(key):
        if my_events.empty:
            st.info("You haven't created any events yet.")
            return None
        opts = {f"{r['title']}  ({r['date']})": r["event_id"]
                for _, r in my_events.iterrows()}
        sel = st.selectbox("Select event", list(opts.keys()), key=key)
        return opts[sel]

    # ── Tab 2: My Events & Live Stats ──
    with t_stats:
        eid = _pick_event("stats_ev")
        if eid:
            regs = get_event_regs(eid)
            evt_row = my_events[my_events["event_id"] == eid].iloc[0]
            cap = int(evt_row["capacity"])
            total = len(regs)
            checked = int(regs["checked_in"].astype(int).sum()) if total else 0
            remaining = max(cap - total, 0)
            rate = (checked / total * 100) if total else 0

            m1, m2, m3 = st.columns(3, gap="small")
            with m1:
                st.markdown(
                    f"""<div class="metric-card">
                        <div class="metric-val">{total}</div>
                        <div class="metric-label">Registrations</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""<div class="metric-card" style="animation-delay:.1s">
                        <div class="metric-val">{checked}</div>
                        <div class="metric-label">Checked In</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f"""<div class="metric-card" style="animation-delay:.2s">
                        <div class="metric-val">{remaining}</div>
                        <div class="metric-label">Remaining</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            # Progress bar
            st.markdown(
                f"""<div style="margin-top:.8rem">
                    <span style="color:var(--t2);font-size:.9rem;font-weight:500">
                        Check-in rate: {rate:.0f}%
                    </span>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{rate}%"></div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Participant table
            if total:
                display = regs[["name", "email", "ticket_code", "checked_in",
                                "registered_at"]].copy()
                display["checked_in"] = display["checked_in"].map(
                    {"1": "✅ Yes", "0": "❌ No"}
                )
                display.columns = ["Name", "Email", "Ticket Code",
                                   "Checked In", "Registered"]
                st.dataframe(display, use_container_width=True, hide_index=True)
            else:
                st.info("No registrations yet.")

    # ── Tab 3: Check-In ──
    with t_checkin:
        eid2 = _pick_event("checkin_ev")
        if eid2:
            checkin_mode = st.radio("Check-In Method", ["🔢 Enter 6-Digit Code", "📷 Upload / Scan QR Image"], horizontal=True, key="ci_mode")

            if checkin_mode == "🔢 Enter 6-Digit Code":
                code_in = st.text_input(
                    "Enter 6-digit ticket code",
                    max_chars=6,
                    placeholder="004821",
                    key="checkin_code",
                )
                if st.button("Check In", key="do_checkin", use_container_width=True):
                    status, pname = check_in_ticket(code_in, eid2)
                    if status == "ok":
                        st.markdown(
                            f"""<div class="success-card-lg">
                                <div class="card-icon">🎉</div>
                                <div class="card-title">Checked In!</div>
                                <div class="card-detail">{pname}</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        st.balloons()
                    elif status == "already":
                        st.markdown(
                            f"""<div class="error-card-lg">
                                <div class="card-icon">⚠️</div>
                                <div class="card-title">Already Checked In</div>
                                <div class="card-detail">{pname}</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """<div class="error-card-lg">
                                <div class="card-icon">🚫</div>
                                <div class="card-title">Invalid Code</div>
                                <div class="card-detail">No matching ticket found for this event.</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
            else:
                st.caption("Upload participant's QR pass image to verify automatically using OpenCV detector:")
                qr_file = st.file_uploader("Upload QR Pass Image", type=["png", "jpg", "jpeg"], key="checkin_qr_file")
                if qr_file and st.button("📷 Scan QR & Check In", key="do_qr_checkin", use_container_width=True):
                    scanned_code = QRcode.scan_qr(qr_file)
                    if not scanned_code:
                        st.markdown(
                            """<div class="error-card-lg">
                                <div class="card-icon">🚫</div>
                                <div class="card-title">QR Not Detected</div>
                                <div class="card-detail">Could not read a valid QR code from this image.</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                    else:
                        status, pname = check_in_ticket(str(scanned_code), eid2)
                        if status == "ok":
                            st.markdown(
                                f"""<div class="success-card-lg">
                                    <div class="card-icon">🎉</div>
                                    <div class="card-title">Checked In via QR!</div>
                                    <div class="card-detail">{pname} (Code: {scanned_code})</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                            st.balloons()
                        elif status == "already":
                            st.markdown(
                                f"""<div class="error-card-lg">
                                    <div class="card-icon">⚠️</div>
                                    <div class="card-title">Already Checked In</div>
                                    <div class="card-detail">{pname} (Code: {scanned_code})</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""<div class="error-card-lg">
                                    <div class="card-icon">🚫</div>
                                    <div class="card-title">Ticket Not Found</div>
                                    <div class="card-detail">Decoded value '{scanned_code}' does not match this event.</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )

    # ── Tab 4: Export ──
    with t_export:
        eid3 = _pick_event("export_ev")
        if eid3:
            regs3 = get_event_regs(eid3)
            evt3 = my_events[my_events["event_id"] == eid3].iloc[0]
            if regs3.empty:
                st.info("No registrations to export.")
            else:
                export_df = regs3[["name", "email", "ticket_code",
                                   "checked_in", "registered_at"]].copy()
                export_df.columns = ["Name", "Email", "Ticket Code",
                                     "Checked In", "Registered At"]
                csv_bytes = export_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Attendance CSV",
                    csv_bytes,
                    file_name=f"{evt3['title']}_attendance.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.dataframe(export_df, use_container_width=True, hide_index=True)


# ── Participant ──────────────────────────────────────────────────────────────
def _render_pass(info, show_download=True):
    """Render the digital pass card with QR code."""
    qr_bytes = make_qr_png(info["ticket_code"])
    st.markdown(
        f"""<div class="pass-card">
            <h3>{info['title']}</h3>
            <p class="pass-detail">📅 {info['date']}</p>
            <p class="pass-detail">📍 {info['venue']}</p>
            <hr class="pass-divider">
            <p class="pass-detail" style="font-weight:600">{info['name']}</p>
            <p class="pass-detail">{info['email']}</p>
            <div class="pass-code">{info['ticket_code']}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    # QR image (centered)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(qr_bytes, caption="Scan this QR at check-in", use_container_width=True)
        if show_download:
            st.download_button(
                "📥 Download QR Code",
                qr_bytes,
                file_name=f"eventease_pass_{info['ticket_code']}.png",
                mime="image/png",
                use_container_width=True,
            )


def page_participant():
    if st.button("← Back", key="back_part"):
        st.session_state.part_pending_verify = None
        st.session_state.part_last_pass = None
        _nav("welcome"); st.rerun()

    st.markdown(
        """<div class="hero hero-sm">
            <h2>🎫 Participant Portal</h2>
            <p>Register for events or look up your pass</p>
        </div>""",
        unsafe_allow_html=True,
    )

    tab_reg, tab_pass = st.tabs(["📝 Register", "🔍 My Pass"])

    # ── Register ──
    with tab_reg:
        last_pass = st.session_state.get("part_last_pass")
        pending = st.session_state.get("part_pending_verify")

        if last_pass:
            st.markdown(
                '<div class="success-card">🎉 Email verified! Your official entry pass is ready:</div>',
                unsafe_allow_html=True,
            )
            _render_pass(last_pass)
            if st.button("➕ Register for Another Event", key="part_reg_another", use_container_width=True):
                st.session_state.part_last_pass = None
                st.session_state.part_pending_verify = None
                st.rerun()

        elif pending:
            st.markdown(
                f"""<div class="verify-email-box">
                    <div class="verify-email-meta">
                        <span class="verify-pill">📬 Verification Email Sent</span><br>
                        <strong>To:</strong> {pending['email']}<br>
                        <strong>From:</strong> EventEase Passes &lt;verify@eventease.edu&gt;
                    </div>
                    <div class="verify-email-subject">🎫 Confirm Registration for {pending['title']}</div>
                    <div class="verify-email-body">
                        Hello <strong>{pending['name']}</strong>,<br>
                        Click the verification button below to immediately verify your email and generate your digital entry pass for <strong>{pending['title']}</strong> (Date: {pending['date']}, Venue: {pending['venue']}).
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            pv_col1, pv_col2 = st.columns([2, 1])
            with pv_col1:
                if st.button("✅ Click Here to Verify Email & Get Pass (તરત વેરિફાય કરો)", key="btn_verify_part", use_container_width=True):
                    ok, msg, code = register_participant(pending["event_id"], pending["name"], pending["email"])
                    if ok:
                        st.balloons()
                        st.session_state.part_last_pass = {
                            "title": pending["title"],
                            "date": pending["date"],
                            "venue": pending["venue"],
                            "name": pending["name"],
                            "email": pending["email"],
                            "ticket_code": code,
                        }
                        st.session_state.part_pending_verify = None
                        st.rerun()
                    else:
                        st.markdown(
                            f'<div class="error-card">❌ {msg}</div>',
                            unsafe_allow_html=True,
                        )
            with pv_col2:
                if st.button("Edit Details", key="btn_cancel_part_verify", use_container_width=True):
                    st.session_state.part_pending_verify = None
                    st.rerun()

        else:
            open_evts = get_open_events()
            if open_evts.empty:
                st.info("No events with available capacity right now.")
            else:
                opts = {f"{r['title']}  ({r['date']}, {r['venue']})": r["event_id"]
                        for _, r in open_evts.iterrows()}
                with st.form("part_reg"):
                    sel = st.selectbox("Choose an event", list(opts.keys()))
                    pname = st.text_input("Your Name", placeholder="Alex Smith")
                    pemail = st.text_input("Your Email", placeholder="alex@university.edu")
                    if st.form_submit_button("Send Verification Email & Register", use_container_width=True):
                        if not pname or not pemail:
                            st.markdown(
                                '<div class="error-card">❌ Please fill in all fields.</div>',
                                unsafe_allow_html=True,
                            )
                        elif not is_valid_email(pemail):
                            st.markdown(
                                '<div class="error-card">❌ Please enter a valid email address (e.g. name@university.edu).</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            eid = opts[sel]
                            regs = read_csv("registrations.csv")
                            if not regs.empty:
                                dup = regs[(regs["event_id"] == eid) & (regs["email"].str.lower() == pemail.strip().lower())]
                                if not dup.empty:
                                    st.markdown(
                                        '<div class="error-card">❌ You are already registered for this event.</div>',
                                        unsafe_allow_html=True,
                                    )
                                    st.stop()
                            evt_row = open_evts[open_evts["event_id"] == eid].iloc[0]
                            st.session_state.part_pending_verify = {
                                "event_id": eid,
                                "title": evt_row["title"],
                                "date": evt_row["date"],
                                "venue": evt_row["venue"],
                                "name": pname.strip(),
                                "email": pemail.strip().lower(),
                            }
                            st.rerun()

    # ── My Pass ──
    with tab_pass:
        with st.form("lookup_form"):
            lu_email = st.text_input("Your Email", placeholder="alex@university.edu")
            lu_code = st.text_input("Ticket Code (6 digits)", placeholder="004821",
                                    max_chars=6)
            if st.form_submit_button("Look Up My Pass", use_container_width=True):
                if not lu_email or not lu_code:
                    st.markdown(
                        '<div class="error-card">❌ Please fill in both fields.</div>',
                        unsafe_allow_html=True,
                    )
                elif not is_valid_email(lu_email):
                    st.markdown(
                        '<div class="error-card">❌ Please enter a valid email address.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    info = lookup_pass(lu_email, lu_code)
                    if info:
                        _render_pass(info)
                    else:
                        st.markdown(
                            '<div class="error-card">❌ No pass found. Check your email and code.</div>',
                            unsafe_allow_html=True,
                        )


# ── FestGate QR System (Teammate Module) ────────────────────────────────────
def page_festgate():
    QRcode.render_festgate_app(show_back_button=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "org_dashboard" and st.session_state.org_id is None:
    _nav("welcome"); st.rerun()

{"welcome": page_welcome,
 "org_auth": page_org_auth,
 "org_dashboard": page_org_dashboard,
 "participant": page_participant,
 "festgate": page_festgate,
}[st.session_state.page]()
