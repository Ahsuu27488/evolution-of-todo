#!/bin/bash
# Keep Neon database warm to prevent cold starts
# Run this in background: ./scripts/keep_warm.sh &

while true; do
    curl -s http://localhost:8000/api/health > /dev/null 2>&1
    sleep 120  # Ping every 2 minutes
done
