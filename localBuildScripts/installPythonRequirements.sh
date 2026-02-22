#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_JSON="$SCRIPT_DIR/localData/scriptData.json"

echo "📦 Checking dependencies..."

# Install requirements globally from scriptData.json
if [[ -f "$LOCAL_JSON" ]]; then
  # Extract requirements list from JSON
  REQS=$(python3 -c "import json; data=json.load(open('$LOCAL_JSON')); print(' '.join(data['dependencies']['requirements']))")
  
  if [[ -n "$REQS" ]]; then
    # Use --break-system-packages for modern Linux/Mac environments
    pip3 install --upgrade pip --break-system-packages || pip3 install --upgrade pip 
    pip3 install $REQS --break-system-packages || pip3 install $REQS
  else
    echo "⚠️ No requirements found in $LOCAL_JSON."
  fi
else
  echo "❌ Error: $LOCAL_JSON not found."
  exit 1
fi

echo "✅ Dependencies ready. Running extraction..."

# Run the Python script automatically
python3 "$SCRIPT_DIR/getDeviceData.py"