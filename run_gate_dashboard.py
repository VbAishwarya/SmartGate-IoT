#!/usr/bin/env python3
"""
Gate Live Dashboard — separate app for live display of Raspberry Pi ALPR events.

Run on a machine reachable from the Pi (e.g. laptop on same network):
  python run_gate_dashboard.py

Then on the Pi, set GATE_DASHBOARD_URL=http://<laptop-ip>:5001 and run:
  python alpr.py

Events from the Pi are POSTed to this app and shown in real time. The main
dashboard (run_dashboard.py on port 5000) is unchanged.
"""

import os
import sys
from collections import deque
from datetime import datetime
from threading import Lock

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, "src"))
_TEMPLATES = os.path.join(_SCRIPT_DIR, "templates")

from flask import Flask, render_template, jsonify, request

app = Flask(__name__, template_folder=_TEMPLATES)

# In-memory store: last N events + current state (mirrors alpr.py logic)
MAX_EVENTS = 200
_events: deque = deque(maxlen=MAX_EVENTS)
_state = {
    "plate": None,
    "distance": None,
    "decision": None,
    "match": None,
    "similarity": None,
    "gate_open": False,
    "last_updated": None,
}
_lock = Lock()


def _emit(event_type: str, **kwargs):
    with _lock:
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {"type": event_type, "timestamp": ts, **kwargs}
        _events.appendleft(entry)
        if event_type == "plate_decision":
            _state["plate"] = kwargs.get("plate")
            _state["distance"] = kwargs.get("distance")
            _state["decision"] = kwargs.get("decision")
            _state["match"] = kwargs.get("match")
            _state["similarity"] = kwargs.get("similarity")
            _state["last_updated"] = ts
        elif event_type == "gate_open":
            _state["gate_open"] = True
            _state["last_updated"] = ts
        elif event_type == "gate_closed":
            _state["gate_open"] = False
            _state["last_updated"] = ts


@app.route("/")
def index():
    return render_template("gate_dashboard.html")


@app.route("/api/gate/state")
def api_gate_state():
    with _lock:
        return jsonify(dict(_state))


@app.route("/api/gate/events")
def api_gate_events():
    limit = request.args.get("limit", type=int) or 50
    with _lock:
        out = list(_events)[:limit]
    return jsonify(out)


@app.route("/api/gate/event", methods=["POST"])
def api_gate_event():
    data = request.get_json(force=True, silent=True) or {}
    event_type = (data.get("type") or "").strip()
    if not event_type:
        return jsonify({"success": False, "error": "Missing 'type'"}), 400
    if event_type == "plate_decision":
        _emit(
            "plate_decision",
            plate=data.get("plate"),
            distance=data.get("distance"),
            decision=data.get("decision"),
            match=data.get("match"),
            similarity=data.get("similarity"),
        )
    elif event_type == "gate_open":
        _emit("gate_open")
    elif event_type == "gate_closed":
        _emit("gate_closed")
    else:
        _emit(event_type, **{k: v for k, v in data.items() if k != "type"})
    return jsonify({"success": True})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SmartGate Gate Live Dashboard")
    print("=" * 60)
    print("\nOpen in browser: http://0.0.0.0:5001")
    print("On the Pi, set: GATE_DASHBOARD_URL=http://<this-machine-ip>:5001")
    print("Then run: python alpr.py")
    print("\nPress Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
