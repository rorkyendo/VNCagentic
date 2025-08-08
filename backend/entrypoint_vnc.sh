#!/bin/bash
set -e

# Start the original computer use demo services
./start_all.sh
./novnc_startup.sh

# Start our backend integration service (if needed)
# This would run a service that bridges our FastAPI backend with the computer use agent

echo "✨ VNC Computer Use Agent is ready!"
echo "➡️  VNC available on port 5900"
echo "➡️  noVNC web interface on port 6080"

# Keep the container running
tail -f /dev/null
