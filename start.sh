#!/bin/bash
# LAB-ONLY: This script starts the entire lab environment.

echo "--- Starting AutoPentAI Lab Environment ---"

echo "[1/5] Activating Python virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: 'venv' directory not found. Did you run Step C?"
    exit 1
fi

echo "[2/5] Starting vulnerable target (Juice Shop) with Docker..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Error: docker-compose failed. Is Docker running?"
    exit 1
fi

echo "[3/5] Waiting 15s for container to boot..."
sleep 15

echo "[4/5] Training ML model..."
python model/train_model.py
if [ $? -ne 0 ]; then
    echo "Error: Model training failed. Check 'data/dataset.csv'."
    exit 1
fi

echo "[5/5] Launching Flask Web UI..."
echo "----------------------------------------------------"
echo "  Access the UI at: http://127.0.0.1:5001"
echo "  Press CTRL+C in this terminal to stop the web app."
echo "----------------------------------------------------"

# --- THIS IS THE FIX ---
# We now run the app.py script directly using python.
# This forces it to use the "debug=True" setting inside the file
# and load the newest code every time.
python app/app.py

# When user presses Ctrl+C, this will run:
echo "Flask app stopped."
echo "Run './stop.sh' to shut down the Docker container."
