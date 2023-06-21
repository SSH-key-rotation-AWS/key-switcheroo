#!/usr/bin/bash

set -u 
set -e
set -x
set -o pipefail
venv_py=".venv/bin/python"
venv_pip=".venv/bin/pip"

if [ -d ".venv/bin/" ]; then
    source .venv/bin/activate 
    if cmp -s requirements.txt .venv/bin/requirements.txt; then
        echo "venv is up to date"
    else 
       pip install -r requirements.txt
    fi
else
    python3.11 -m venv .venv
    source .venv/bin/activate 
    pip install -r requirements.txt
    cp requirements.txt .venv/bin/
    # Perform your logic here for the non-existing directory
fi
#find current directory, and git-hooks
current_dir=$(pwd)
repo_dir="$current_dir/tools/git_hooks/pre-commit"
system_dir="$current_dir/.git/hooks/pre-commit"

#copy python interpeter path to pre-commit file
echo "#!$venv_py" > "$system_dir"

#copy our manual git-hook to .git/hook/pre-commit
cat "$repo_dir" >> "$system_dir"

#make pre-commit file executable
chmod +x "$system_dir"

#$(pip install -r requirements.txt)

