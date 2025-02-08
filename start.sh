#!/bin/bash

set -e

OUTPUT_LOG='output.log'
install_bun() {
  pushd script/screenshotter &>/dev/null
  ./install.sh 1>/dev/null
  popd &>/dev/null
}
run_bun() {
  # FIXME could block indefinitely. eventually refactor signalling in main app.
  local project="$1"
  if tail -f "$OUTPUT_LOG" 2>/dev/null | grep -q 'App created successfully'; then
    pushd "projects/$project" &>/dev/null
    bun dev &>/dev/null
    popd &>/dev/null
  fi
}

source .venv/bin/activate
install_bun
pip install -r requirements.txt 1>/dev/null
echo "" > "$OUTPUT_LOG"

read -p "What would you like to name your project? " project

run_bun "$project" &
python script/create_next_app.py "$project" | tee "$OUTPUT_LOG"
deactivate
