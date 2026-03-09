#!/usr/bin/env python3
"""Standalone Dashboard Runner - Run this to start just the web dashboard."""

import sys
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, 'src'))

# Templates path: project_root/templates (works regardless of CWD)
_TEMPLATES = os.path.join(_SCRIPT_DIR, 'templates')

from flask import Flask, render_template, jsonify, request
from src.database import VehicleDB
from src.common.dashboard import SCENARIOS, run_scenario

app = Flask(__name__, template_folder=_TEMPLATES)
db = VehicleDB("smartgate.db")

# Use SCENARIOS from common.dashboard (no duplicate list)

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

@app.route('/api/scenarios')
def api_scenarios():
    """API endpoint for scenario list (for future scenario simulation with real imagery)."""
    return jsonify(SCENARIOS)

@app.route('/api/scenarios/<scenario_id>/run', methods=['POST'])
def run_scenario_route(scenario_id):
    """Run a scenario and log events to the database."""
    success, message = run_scenario(db, scenario_id)
    return jsonify({'success': success, 'message': message})

@app.route('/api/vision/check', methods=['POST'])
def api_vision_check():
    """Run plate OCR on uploaded image and check authorization.
    Optional form field 'backend': 'tesseract' (default) or 'easyocr'.
    """
    from src.vision import ocr_from_bytes, ocr_available
    from src.fuzzy_logic import check_plate_authorization

    backend = (request.form.get('backend') or request.args.get('backend') or 'tesseract').strip().lower()
    if backend == 'easyocr':
        try:
            import easyocr  # noqa: F401
        except ImportError:
            return jsonify({'success': False, 'error': 'EasyOCR not installed (pip install easyocr)'}), 503
        prev = os.environ.get('SMARTGATE_OCR_BACKEND')
        os.environ['SMARTGATE_OCR_BACKEND'] = 'easyocr'
    else:
        prev = None

    if not ocr_available():
        if prev is not None:
            os.environ.pop('SMARTGATE_OCR_BACKEND', None)
            if prev:
                os.environ['SMARTGATE_OCR_BACKEND'] = prev
        return jsonify({'success': False, 'error': 'OCR not available (install pytesseract and Tesseract)'}), 503

    try:
        file = request.files.get('image')
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        data = file.read()
        plate_text, err = ocr_from_bytes(data)
    finally:
        if backend == 'easyocr' and prev is not None:
            os.environ.pop('SMARTGATE_OCR_BACKEND', None)
            if prev:
                os.environ['SMARTGATE_OCR_BACKEND'] = prev

    if err is not None:
        return jsonify({'success': False, 'error': err}), 200
    authorized_plates = [v['plate_number'] for v in db.get_all_vehicles()]
    if db.is_authorized(plate_text):
        return jsonify({
            'success': True, 'plate': plate_text, 'authorized': True,
            'match': plate_text, 'score': 1.0, 'similar': []
        })
    ok, match, score = check_plate_authorization(plate_text, authorized_plates or None, threshold=0.85)
    similar = db.find_similar_plates(plate_text, threshold=0.5)
    similar_list = [{'plate': p, 'score': s} for p, s in similar[:5]]
    return jsonify({
        'success': True, 'plate': plate_text, 'authorized': ok,
        'match': match or '', 'score': round(score, 2), 'similar': similar_list
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SmartGate-IoT Web Dashboard")
    print("="*70)
    print("\n✅ Dashboard starting...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("📊 Dashboard will auto-refresh periodically (you can pause from the UI)")
    print("\nPress Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
