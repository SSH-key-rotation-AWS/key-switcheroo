#!/usr/bin/bash

# Courtesy of ChatGPT (checked over)

# Get the current directory
current_dir="$(pwd)"

# Go up one level until reaching the root folder
while [ ! -f "$current_dir/tests" ]; do
    current_dir="$(dirname "$current_dir")"
done

source "$current_dir/.venv/bin/activate"
python3.11 ssh_key_rotator/server/retrieve_public_keys.py $1 $2

# Output the path to the root folder
echo "Path to root folder: $current_dir"