#!/bin/bash
# LAB-ONLY: This script stops the lab environment.

echo "Stopping vulnerable target (Juice Shop)..."
docker-compose down

echo "Killing any stray Flask processes (just in case)..."
# This finds and kills the specific flask app process
pkill -f "flask --app app/app run"

echo "Lab environment stopped."
