# LAB-ONLY: Flask Server (V-FINAL with Nikto & DB)

import sys
import os
import json
import datetime

from flask import Flask, render_template, request, jsonify, send_file, url_for
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import recon_local, feature_extractor  # type: ignore
from model import predict  # type: ignore

app = Flask(__name__, template_folder="../templates", static_folder="../static")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "../data/autopenta.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_ip = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    scan_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# In-memory store of last scan for dashboard + PDF
last_scan_data: dict = {}
last_prediction: dict = {}
last_nikto_count: int = 0


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    try:
        scans = Scan.query.order_by(Scan.timestamp.desc()).all()
    except Exception:
        # First run: DB might not exist yet
        db.create_all()
        scans = []
    return render_template("history.html", scans=scans)


@app.route("/scan", methods=["POST"])
def scan():
    global last_scan_data, last_prediction, last_nikto_count

    try:
        data = request.json
        target = data.get("target")

        # Lab-only safety: only allow local / host-only ranges
        if not (
            target in ["127.0.0.1", "localhost"] or target.startswith("192.168.56.")
        ):
            return jsonify({"error": "Invalid Target"}), 400

        # Run recon (Nmap + Nikto)
        scan_data, nikto_ran = recon_local.scan_local(target)
        if scan_data is None:
            return (
                jsonify(
                    {
                        "error": "Scan Failed",
                        "message": "Nmap failed. Check terminal for details.",
                    }
                ),
                500,
            )

        last_scan_data = scan_data

        # Extract ML features
        feature_df = feature_extractor.extract_features(scan_data, nikto_ran)
        if feature_df is None:
            return (
                jsonify(
                    {
                        "error": "Feature Extraction Failed",
                        "message": "Could not extract features from scan data. Check logs.",
                    }
                ),
                500,
            )

        # ML prediction
        label, confidence = predict.get_prediction(feature_df)
        if label == "Error":
            return (
                jsonify(
                    {
                        "error": "Prediction Failed",
                        "message": "ML model prediction failed. Check model file.",
                    }
                ),
                500,
            )

        last_prediction = {"label": label, "confidence": f"{confidence:.2f}%"}

        # Basic scan info for UI
        target_ip = list(scan_data["scan"].keys())[0]
        scan_report = scan_data["scan"][target_ip]

        # Nikto summary
        nikto_count = 0
        if "nikto_vuln_count" in feature_df.columns and not feature_df.empty:
            nikto_count = int(feature_df["nikto_vuln_count"].iloc[0])
        last_nikto_count = nikto_count

        # Store in DB for history view
        try:
            new_scan = Scan(
                target_ip=target_ip,
                label=label,
                confidence=float(confidence),
                scan_json=json.dumps(scan_data),
            )
            db.session.add(new_scan)
            db.session.commit()
            print(f"Scan result saved (Nikto found: {nikto_count}).")
        except Exception as e:
            print(f"DB save error: {e}")
            db.session.rollback()

        return jsonify(
            {
                "success": True,
                "target": target_ip,
                "prediction": last_prediction,
                "scan_report": scan_report,
                "nikto_vuln_count": int(nikto_count),
            }
        )
    except Exception as e:
        print(f"Error in /scan endpoint: {e}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": f"An unexpected error occurred: {str(e)}",
                }
            ),
            500,
        )


@app.route("/report")
def generate_report():
    global last_scan_data, last_prediction, last_nikto_count

    if not last_scan_data or not last_prediction:
        return "No scan data available.", 404

    try:
        pdf = FPDF()
        pdf.add_page()

        # Header
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="AutoPentAI Lab Scan Report", ln=True, align="C")

        # Meta info
        pdf.set_font("Arial", size=10)
        now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        pdf.cell(200, 6, txt=f"Generated at: {now_str}", ln=True)

        target_ip = list(last_scan_data["scan"].keys())[0]
        pdf.cell(200, 6, txt=f"Target: {target_ip}", ln=True)
        pdf.ln(4)

        # Prediction summary
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 8, txt="--- Prediction ---", ln=True, align="L")

        pdf.set_font("Arial", size=11)
        pdf.cell(
            200,
            6,
            txt=f"Classification: {last_prediction.get('label')}",
            ln=True,
        )
        pdf.cell(
            200,
            6,
            txt=f"Confidence: {last_prediction.get('confidence')}",
            ln=True,
        )
        pdf.cell(
            200,
            6,
            txt=f"Nikto web vulns detected: {last_nikto_count}",
            ln=True,
        )
        pdf.ln(6)

        # Port table
        pdf.set_font("Arial", size=12)
        pdf.cell(
            200,
            8,
            txt="--- Scan Details (TCP Ports) ---",
            ln=True,
            align="L",
        )
        pdf.ln(2)

        pdf.set_font("Arial", "B", size=10)
        pdf.cell(20, 8, txt="Port", border=1)
        pdf.cell(20, 8, txt="State", border=1)
        pdf.cell(50, 8, txt="Service", border=1)
        pdf.cell(100, 8, txt="Product/Version", border=1, ln=True)

        pdf.set_font("Arial", size=10)

        tcp_data = last_scan_data["scan"].get(target_ip, {}).get("tcp", {})
        for port, data in tcp_data.items():
            pdf.cell(20, 8, txt=str(port), border=1)
            pdf.cell(20, 8, txt=data.get("state", "N/A"), border=1)
            pdf.cell(50, 8, txt=data.get("name", "N/A"), border=1)
            version = f"{data.get('product', '')} {data.get('version', '')}".strip()
            pdf.cell(100, 8, txt=version, border=1, ln=True)

        report_filename = os.path.join("data", "report.pdf")
        pdf.output(report_filename)

        return send_file(
            os.path.abspath(report_filename),
            as_attachment=True,
            download_name="AutoPentAI_Report.pdf",
        )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return "Error generating report", 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Starting Flask server (V-FINAL with Nikto)...")
    app.run(host="127.0.0.1", port=5001, debug=True)
