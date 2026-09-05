#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x "./venv/bin/python" ]; then
  echo "Creating venv..."
  python3 -m venv venv
fi
./venv/bin/python -m pip install -q -r requirements.txt
echo "Starting CIWT LMS on port ${PORT:-5050}"
PORT="${PORT:-5050}" ./venv/bin/python app.py
