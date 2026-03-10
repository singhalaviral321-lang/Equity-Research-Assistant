import os
import json
import subprocess
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 8050))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Ensure reports directory exists
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

@app.route("/")
def serve_dashboard():
    return send_from_directory(BASE_DIR, "dashboard.html")

@app.route("/api/latest", methods=["GET"])
def get_latest_report():
    try:
        # Search in reports/ folder
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
        
        # Fallback: check root folder
        if not files:
            files = [f for f in os.listdir(BASE_DIR) if f.startswith("analysis_") and f.endswith(".json")]
            search_dir = BASE_DIR
        else:
            search_dir = REPORTS_DIR

        if not files:
            return jsonify({
                "error": "no_reports",
                "message": "Analysis not yet run",
                "all_results": [],
                "summary": {"strong_buys":0,"buys":0,"neutrals":0,"sells":0}
            }), 200
        
        # Prioritize 'enriched' files if multiple exist for the same period
        enriched_files = [f for f in files if "_enriched.json" in f]
        if enriched_files:
            latest_file = sorted(enriched_files, reverse=True)[0]
        else:
            latest_file = sorted(files, reverse=True)[0]
        
        with open(os.path.join(search_dir, latest_file), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/run", methods=["POST"])
def run_analysis():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"reports/analysis_{timestamp}.json"
        
        # Run indicator_engine.py as a subprocess
        # We use sys.executable to ensure we use the same python interpreter
        import sys
        result = subprocess.run(
            [sys.executable, "indicator_engine.py", "--output", output_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({"error": f"Analysis failed: {result.stderr}"}), 500
            
        return jsonify({"status": "ok", "file": output_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    if request.method == "GET":
        try:
            if not os.path.exists(CONFIG_FILE):
                return jsonify({"error": "config.json not found"}), 404
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            return jsonify(config)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == "POST":
        try:
            new_config = request.json
            with open(CONFIG_FILE, "w") as f:
                json.dump(new_config, f, indent=2)
            return jsonify({"status": "saved"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
        # Return last 30 report filenames
        history = sorted(files, reverse=True)[:30]
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import threading
    import sys

    # Startup Check: If no reports, run an initial one in background
    report_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
    if not report_files:
        print("🔍 No reports found - running initial analysis in background...")
        def run_initial():
            try:
                subprocess.run([sys.executable, "indicator_engine.py"], capture_output=True)
                print("✅ Initial analysis complete.")
            except Exception as e:
                print(f"❌ Initial analysis failed: {e}")
        
        threading.Thread(target=run_initial, daemon=True).start()

    print(f"🚀 Equity Research Assistant Server starting...")
    print(f"📂 Reports Folder: {os.path.abspath(REPORTS_DIR)}")
    print(f"📍 Local URL: http://localhost:{PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/")
    app.run(host="0.0.0.0", port=PORT, debug=False)
