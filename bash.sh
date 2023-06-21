#!/usr/bin/bash

set -u 
set -e
set -x
set -o pipefail


git_base_dir=$(git rev-parse --show-toplevel)
venv="$git_base_dir/.venv"
venv_py="$git_base_dir/.venv/bin/python3.11"


if [ -d $venv ]; then
    source "$git_base_dir/.venv/bin/activate"
    
    if cmp -s requirements.txt $git_base_dir/.venv/bin/requirements.txt; then
        echo "venv is up to date"
    else 
       pip install -r requirements.txt
    fi
else
    python3.11 -m venv .venv
    source "$git_base_dir/.venv/bin/activate"
    pip install -r requirements.txt
    cp requirements.txt $git_base_dir/.venv/bin/
    # Perform your logic here for the non-existing directory
fi
#find current directory, and git-hooks
repo_dir="$git_base_dir/tools/git_hooks/pre-commit"
system_dir="$git_base_dir/.git/hooks/pre-commit"

#copy python interpeter path to pre-commit file
echo "#!$venv_py" > "$system_dir"

#copy our manual git-hook to .git/hook/pre-commit
cat "$repo_dir" >> "$system_dir"

#make pre-commit file executable
chmod +x "$system_dir"

#$(pip install -r requirements.txt)

