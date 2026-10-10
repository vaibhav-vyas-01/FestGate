/**
 * FestGate — Client Controller
 * Connects frontend interactions with Python Flask backend and Firebase Realtime Database
 */

const FestGate = {
  apiBase: '/api',

  async getEvents() {
    try {
      const res = await fetch(`${this.apiBase}/events`);
      return await res.json();
    } catch (err) {
      console.error("Error loading events:", err);
      return [];
    }
  },

  async getAttendees() {
    try {
      const res = await fetch(`${this.apiBase}/attendees`);
      return await res.json();
    } catch (err) {
      console.error("Error loading attendees:", err);
      return [];
    }
  },

  async registerStudent(data) {
    try {
      const res = await fetch(`${this.apiBase}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      return await res.json();
    } catch (err) {
      console.error("Error registering student:", err);
      return { error: 'Network or server error' };
    }
  },

  async verifyTicket(ticketCode, gateStaff = 'Gate 1 - Lead') {
    try {
      const res = await fetch(`${this.apiBase}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticketCode, gateStaff })
      });
      return await res.json();
    } catch (err) {
      console.error("Error verifying ticket:", err);
      return { success: false, reason: 'ERROR', message: 'Verification server error' };
    }
  },

  async exportCSV() {
    window.location.href = `${this.apiBase}/export-csv`;
  }
};

window.FestGate = FestGate;
