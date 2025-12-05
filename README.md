




# AutoPentAI – AI Powered Vulnerability Assessment Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge">
  <img src="https://img.shields.io/badge/Category-VAPT-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Tech-ML%20%7C%20Nmap%20%7C%20Nikto-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Backend-Flask-lightgrey?style=for-the-badge">
</p>

AutoPentAI is a **full-stack AI-driven vulnerability scanning tool** that automates:
- Nmap Port & Service Scanning  
- Nikto Web Vulnerability Scanning  
- AI-Based Risk Prediction (RandomForest)  
- Real-time Dashboard Visualization  
- One-click PDF Reporting  
- Scan History Logging  

Designed for **virtual lab environments** such as Metasploitable2, DVWA, Juice Shop, and private networks.

---

## 📸 Screenshots

### 🔹 Dashboard (Idle)
![Dashboard](static/preview/dashboard_idle.png)

### 🔹 Scanning (Nmap + Nikto Running)
![Scanning](static/preview/scanning.png)

### 🔹 Result Summary
![Result](static/preview/result.png)

### 🔹 PDF Export
![PDF](static/preview/pdf_export.png)

---

## 🚀 Features

- **Automated Recon** → Nmap + Nikto in a single click  
- **AI Risk Prediction** → RandomForest classifier  
- **Dark Themed Dashboard** → Live progress + charts  
- **PDF Reporting** → Clean professional summary  
- **Scan History (SQLite)** → Stores all previous scans  
- **Modular Backend** → Flask + Python + ML pipeline  
- **Safe Lab Mode** → Only internal / virtual networks allowed  

---

## 🧠 System Architecture

```mermaid
flowchart TD
    A["User Input (Target IP)"] --> B["Flask Backend API"]
    B --> C["Nmap Scan (Ports / Services)"]
    B --> D["Nikto Scan (Web Vulns)"]
    C --> E["Feature Extractor (Parse Nmap Output)"]
    D --> E
    E --> F["RandomForest Model (Risk + Confidence)"]
    F --> G["Dashboard View (Risk + Nmap + Nikto)"]
    G --> H["PDF Export + SQLite History"]
```


🛠 Installation (Kali/Ubuntu)
1. Clone the repository
git clone https://github.com/KreeeDox/AutoPentAI-Scanner.git
cd AutoPentAI-Scanner


2. Install dependencies
sudo apt update
sudo apt install -y python3-venv nmap nikto docker.io docker-compose

3. Environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

4. Start the tool
./start.sh


Open browser:

http://127.0.0.1:5001


🖥️ Usage

1️⃣ Start the tool
2️⃣ Enter target IP (example: 192.168.56.101 for Metasploitable2)
3️⃣ Click Start Scan
4️⃣ View:

Risk Level

Confidence %

Nmap scan

Nikto findings
5️⃣ Export PDF
6️⃣ Check previous scans in Scan History


📂 Recommended Lab Setup

Use virtual lab machines:

Metasploitable 2

Metasploitable 3

DVWA (Docker)

Juice Shop (Docker)

Network mode:

Scanner VM → NAT + Host-Only

Target VM → Host-Only



👨‍💻 Author

Krishna (KreeeDox)

A cybersecurity enthusiast building AI-powered tools for research and learning.












































