#!/bin/bash

# Get the directory path of the running script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check the provided argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <yaml-file>"
fi

# pass the script directory along with the filename argument
poetry run python "$SCRIPT_DIR/output_local_env_vars.py" "$1" | source /dev/stdin
