"""Web dashboard launcher."""

from .colors import print_success, print_info, print_error


def start_dashboard(db):
    """Start the web dashboard."""
    try:
        from flask import Flask, render_template, jsonify
        import threading
        
        app = Flask(__name__, template_folder='templates')
        
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
