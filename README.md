
# AutoPentAI (Lab-Only Version)

This is an educational project demonstrating a simple pipeline for:
1.  **Scanning** a local target (Dockerized Juice Shop) with Nmap.
2.  **Extracting** features from the scan results.
3.  **Classifying** the target using a simple Machine Learning model.
4.  **Presenting** the results in a Flask web UI.

**THIS TOOL IS STRICTLY FOR LOCALHOST LAB USE.**
It is hard-coded to reject any target other than `127.0.0.1` or `localhost`.

## How to Run

1.  Ensure Docker, Python3, and Nmap are installed.
2.  Install Python packages: `pip install -r requirements.txt`
3.  Run the one-click start script: `./start.sh`
4.  Access the UI at: `http://127.0.0.1:5001`

