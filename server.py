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
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".json")]
        if not files:
            return jsonify({"error": "No reports found. Please run the analysis first."}), 404
        
        # Sort by filename (analysis_YYYYMMDD_HHMM.json)
        latest_file = sorted(files, reverse=True)[0]
        
        with open(os.path.join(REPORTS_DIR, latest_file), "r") as f:
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
    print(f"🚀 Equity Research Assistant Server starting...")
    print(f"📂 Reports Folder: {os.path.abspath(REPORTS_DIR)}")
    print(f"📍 Local URL: http://localhost:{PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/")
    app.run(host="0.0.0.0", port=PORT, debug=False)
