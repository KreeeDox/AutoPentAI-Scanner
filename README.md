# 🛡️ AutoPentAI: AI-Powered Vulnerability Assessment Dashboard (VAPT)

This project is a powerful, educational, full-stack application that automates the process of identifying security weaknesses in a controlled lab environment. It demonstrates the integration of multiple security tools with Machine Learning for risk classification.

**THIS TOOL IS STRICTLY FOR EDUCATIONAL AND LAB-ONLY USE. It is hardcoded to reject external network scans.**

---

## ✨ Advanced Features & Technologies

| Feature | Technologies Used | Description |
| :--- | :--- | :--- |
| **Intelligent Recon** | **Nmap, Nikto (Subprocess)** | Automatically performs port scanning (Nmap) and web vulnerability checks (Nikto) against the target IP. |
| **AI Risk Classification** | **Python, scikit-learn (RandomForest), Joblib** | A custom ML model trained on unique service features to classify the target's risk level (e.g., `Compromised_Host_Full`). **Accuracy is guaranteed at 100%** on the training dataset. |
| **Full-Stack Application** | **Flask, HTML/CSS/JS** | A unified, animated, dark-theme dashboard for real-time control and visualization. |
| **Actionable Advice** | **JSON DB, Python Logic** | Generates immediate, specific recommendations (e.g., "IMMEDIATELY patch vsftpd 2.3.4") based on the services found. |
| **Data Persistence** | **SQLAlchemy (SQLite)** | Saves every scan result, prediction, and confidence score to a persistent database for audit/history viewing. |
| **Visualization** | **Chart.js, CSS Animations** | Displays results using a confidence chart and features animated progress bars for a professional look. |

---

## 🏗️ Project Architecture & Data Flow

The project follows a standard M-L-O (Machine Learning Operations) pipeline adapted for security:

1.  **Request:** User inputs target IP (e.g., `192.168.56.101`) via the Flask UI.
2.  **Recon:** Python backend calls `recon_local.py` which runs **Nmap** (Port/Service Scan) and **Nikto** (Web Vulnerability Scan).
3.  **Feature Extraction:** `feature_extractor.py` reads Nmap/Nikto outputs and converts raw service strings (like "vsftpd 2.3.4") into numeric ML features (like `critical_risk_count: 2`).
4.  **Prediction:** `model/predict.py` loads the `autopenta_model.pkl` and predicts the **Risk Label** and **Confidence**.
5.  **Reporting:** The result is saved to the SQLite database and rendered on the dashboard with specific recommendations.

---

## ⚙️ How to Setup and Run (Kali/Ubuntu VM)

This setup requires Docker for the vulnerable target.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR-USERNAME/AutoPentAI-Scanner.git](https://github.com/YOUR-USERNAME/AutoPentAI-Scanner.git)
    cd AutoPentAI-Scanner
    ```

2.  **Install Dependencies:**
    ```bash
    # System Packages & Tools
    sudo apt update
    sudo apt install -y python3-venv nmap docker.io docker-compose nikto
    
    # Python Environment Setup
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the Project:**
    ```bash
    # This script starts the Docker container, trains the model, and launches the Flask server.
    ./start.sh
    ```

4.  **Access the Dashboard:**
    Open your browser to: `http://127.0.0.1:5001`

5.  **Test the Scan:**
    Enter your Metasploitable IP (`e.g., 192.168.56.101`) and click **"Start Scan"**.

---

## 🛑 Lab Target (Metasploitable)

The project uses **Metasploitable 2** as the vulnerable target. Ensure your Kali VM and Metasploitable VM are connected via a **Host-only Adapter** network for isolated, safe testing.


