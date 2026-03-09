"""Web dashboard launcher."""

import os

from .colors import print_success, print_info, print_error

# Project root (parent of src/) so Flask finds templates/
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_TEMPLATES = os.path.join(_ROOT, 'templates')

# Scenario list for future "Simulate scenario" feature (see docs/TESTING.md)
SCENARIOS = [
    {"id": "quick_pass", "name": "Quick vehicle pass", "description": "Fast vehicle passing through"},
    {"id": "slow_approach", "name": "Slow vehicle approach", "description": "Gradual vehicle approach"},
    {"id": "stop_and_go", "name": "Vehicle stops at gate", "description": "Vehicle stops and waits"},
    {"id": "multiple_vehicles", "name": "Multiple vehicles sequence", "description": "Multiple vehicles in sequence"},
    {"id": "false_alarm", "name": "False alarm test", "description": "Near-threshold readings test"},
    {"id": "full_flow_authorized", "name": "Full flow - Authorized vehicle", "description": "Complete flow with authorized plate"},
    {"id": "full_flow_denied", "name": "Full flow - Unauthorized vehicle", "description": "Complete flow with denied plate"},
    {"id": "full_flow_custom", "name": "Full flow - Custom plate number", "description": "Enter your own plate number"},
    {"id": "full_flow_multiple", "name": "Full flow - Multiple vehicles", "description": "Multiple vehicles with different plates"},
]


def run_scenario(db, scenario_id: str):
    """Run a scenario (mock sensor + detector), log events to db. Returns (success, message)."""
    from src.vehicle_detection import MockSensor, VehicleDetector
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)

    def log_event(event):
        db.log_detection_event(event["type"], event["data"].get("distance"))

    detector.on_vehicle_detected(log_event)
    detector.on_no_vehicle(log_event)

    if scenario_id == "full_flow_custom":
        scenario = [
            {"distance": 50, "delay": 0.3}, {"distance": 30, "delay": 0.3},
            {"distance": 15, "delay": 0.3}, {"distance": 8, "delay": 0.5},
            {"distance": 5, "delay": 1.0}, {"distance": 12, "delay": 0.3},
            {"distance": 30, "delay": 0.3}, {"distance": 50, "delay": 0.3},
        ]
    else:
        scenario = sensor.get_predefined_scenario(scenario_id)

    if not scenario:
        return False, f"Unknown scenario: {scenario_id}"

    for step in scenario:
        sensor.set_distance(step["distance"])
        detector.check()

    return True, f"Scenario '{scenario_id}' completed"


def start_dashboard(db):
    """Start the web dashboard."""
    try:
        from flask import Flask, render_template, jsonify, request
        import threading
        
        app = Flask(__name__, template_folder=_TEMPLATES)
        
        @app.route('/')
        def dashboard():
            return render_template('dashboard.html', 
                                 events=db.get_recent_events(limit=50),
                                 vehicles=db.get_all_vehicles())
        
        @app.route('/api/events')
        def api_events():
            return jsonify(db.get_recent_events(limit=50))
        
        @app.route('/api/vehicles')
        def api_vehicles():
            return jsonify(db.get_all_vehicles())

        @app.route('/api/scenarios')
        def api_scenarios():
            return jsonify(SCENARIOS)

        @app.route('/api/scenarios/<scenario_id>/run', methods=['POST'])
        def run_scenario_route(scenario_id):
            success, message = run_scenario(db, scenario_id)
            return jsonify({'success': success, 'message': message})

        @app.route('/api/vision/check', methods=['POST'])
        def api_vision_check():
            """Run plate OCR on uploaded image and check authorization."""
            from src.vision import ocr_from_bytes, ocr_available
            from src.fuzzy_logic import check_plate_authorization
            if not ocr_available():
                return jsonify({'success': False, 'error': 'OCR not available (install pytesseract and Tesseract)'}), 503
            file = request.files.get('image')
            if not file or file.filename == '':
                return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
            data = file.read()
            plate_text, err = ocr_from_bytes(data)
            if err is not None:
                return jsonify({'success': False, 'error': err}), 200
            authorized_plates = [v['plate_number'] for v in db.get_all_vehicles()]
            authorized_direct = db.is_authorized(plate_text)
            if authorized_direct:
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

        def run_flask():
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
        thread = threading.Thread(target=run_flask, daemon=True)
        thread.start()
        print_success("Dashboard started! Open http://localhost:5000 in your browser")
        print_info("Press Enter to return to main menu...")
        input()
    except ImportError:
        print_error("Flask not installed. Install with: pip install flask")
    except Exception as e:
        print_error(f"Failed to start dashboard: {e}")
