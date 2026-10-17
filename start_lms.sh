#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x "./venv/bin/python" ]; then
  echo "Creating venv..."
  python3 -m venv venv
fi
./venv/bin/python -m pip install -q -r requirements.txt
# Debugger is OFF unless FLASK_DEBUG=1 is set explicitly (it then binds to 127.0.0.1 only).
if [ "${FLASK_DEBUG:-0}" = "1" ]; then
  echo "Starting CIWT LMS on http://127.0.0.1:${PORT:-5050} (FLASK_DEBUG=1: debugger ON, local only)"
else
  echo "Starting CIWT LMS on port ${PORT:-5050} (debugger off; set FLASK_DEBUG=1 for local debugging)"
fi
PORT="${PORT:-5050}" ./venv/bin/python app.py
