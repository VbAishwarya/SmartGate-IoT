#!/usr/bin/env python3
"""Standalone Dashboard Runner - Run this to start just the web dashboard."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template, jsonify
from src.database import VehicleDB

app = Flask(__name__, template_folder='templates')
db = VehicleDB("smartgate.db")

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html', 
                         events=db.get_recent_events(limit=50),
                         vehicles=db.get_all_vehicles())

@app.route('/api/events')
def api_events():
    """API endpoint for events."""
    return jsonify(db.get_recent_events(limit=50))

@app.route('/api/vehicles')
def api_vehicles():
    """API endpoint for vehicles."""
    return jsonify(db.get_all_vehicles())

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SmartGate-IoT Web Dashboard")
    print("="*70)
    print("\n✅ Dashboard starting...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("📊 Dashboard will auto-refresh every 5 seconds")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
