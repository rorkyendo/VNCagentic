#!/bin/bash
set -e

# Start the original computer use demo services
cd /home/computeruse
./start_all.sh &
./novnc_startup.sh &

# Wait a bit for the services to start
sleep 5

# Start our VNC API server
echo "Starting VNC API Server on port 8090..."
python3 vnc_api.py &

echo "✨ VNC Computer Use Agent is ready!"
echo "➡️  VNC available on port 5900"
echo "➡️  noVNC web interface on port 6080"
echo "➡️  VNC API server on port 8090"

# Keep the container running
tail -f /dev/null
