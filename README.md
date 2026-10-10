# FestGate — Every Event. One Smart Gate.

> **FestGate** is a premium university festival event management & gatekeeper web application built with React, TypeScript, Tailwind CSS, Python Flask, and Firebase Realtime Database cloud storage.

---

## 🌟 Visual UI/UX Design

The dashboard recreates the reference layout:
- **Left Sidebar**: FestGate brand logo with sparkle motif, Overview menu (`Dashboard`, `Events`, `Gate Scanner`, `Registrations`), Active Gate Crew list with circular avatars, and Admin Settings & Logout.
- **Top Bar**: Search bar with real-time filtering, fast action buttons (`Scan Gate Pass`, `Register Student`, `New Event`), notification badge, and admin profile pill.
- **Purple Hero Banner**: High-contrast purple gradient banner (`#6246EA` to `#7B61FF`) with subtle star vectors, category pill badge, and the headline *"Every Event. One Smart Gate."* with quick action buttons.
- **Three Metric / Stat Cards**: Horizontal stat cards with soft tinted badges (`Total Registered`, `Gate Attendance / Checked In`, and `Verification Rate %`).
- **Upcoming Events Carousel**: Event cards featuring category badges (`TECH`, `DESIGN`, `CULTURAL`), event title, organizer info, bookmark button, and instant registration trigger.
- **Recent Registrations & Gate Logs Table**: Clean table with Attendee initials badge, Event Type pill badge, Ticket Code, status badge (`Admitted` / `Registered`), and action button `↗` to inspect digital pass.
- **Right Analytics Panel**: Circular progress ring gauge with percentage badge, greeting *"Good Morning Jason 🔥"*, bar chart showing hourly gate traffic flow, Gate Coordinators list with `+ Follow` buttons, and `Export CSV Report` button.

---

## 🚀 Key Features

1. **Smart Event Creation**:
   - Modal to create events with title, category, date, time, venue, seats capacity, and description.
2. **Student Event Registration**:
   - Register students by Name, Roll No, Email, Department, and Event.
   - Prevents duplicate registration for the same student on the same event.
3. **Tamper-Proof QR Gate Pass**:
   - Instantly generates a unique Ticket ID (`FG-XXXX-YY`) and high-resolution QR code.
   - Digital pass modal displays attendee details, verified status, and printable ticket layout.
4. **Gate Scanner & Verification**:
   - Integrated camera scanner (WebRTC / HTML5 QR Scanner).
   - Fast manual ticket code entry.
   - 1-click test buttons for testing fresh, duplicate, and invalid tickets.
5. **Duplicate Attendance Prevention**:
   - When a ticket is scanned for the first time, it is verified, admitted, and marked as `CHECKED_IN` with timestamp and gate staff name.
   - Any subsequent scan of the same ticket will immediately trigger:
     > ⚠️ **DUPLICATE ATTENDANCE DETECTED! Pass was already scanned at [Time] by [Gate Staff]. Re-entry denied!**
6. **Live Attendance Analytics & CSV Reports**:
   - Dynamic check-in rate calculations, live traffic distribution.
   - 1-click CSV export with all registration and gate timestamps.
7. **Protected Admin Access**:
   - Session-based admin login protection.
   - Default credentials:
     - **Username:** `admin`
     - **Password:** `festgate2026`

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide Icons, QRCode.js, Html5Qrcode, Canvas Confetti.
- **Backend**: Python 3, Flask, Firebase Realtime Database SDK, REST API.
- **Storage**: Firebase Realtime Database (with automatic fallback to persistent JSON storage `festgate_db.json` for zero-configuration local runs).

---

## 💻 How to Run Locally

### Option 1: Run Full-Stack with Python Flask (Recommended)
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the backend:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Option 2: Run Frontend Development Server (Vite)
1. Start the Vite dev server:
   ```bash
   npm run dev
   ```
2. Open your browser at:
   ```
   http://localhost:3000
   ```

---

## 🔐 Firebase Realtime Database Setup (Optional Cloud Sync)
FestGate runs **100% out of the box** using its local persistent database `festgate_db.json`. To connect your own Firebase Realtime Database:
1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com).
2. Enable **Realtime Database**.
3. Copy `.env.example` to `.env` and fill in:
   ```env
   FIREBASE_DATABASE_URL=https://<your-project>-default-rtdb.firebaseio.com/
   FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json
   ```
