#!/usr/bin/bash
# the above line, known as the "Shebang" is basically the path to bash

#sets the options for the whole script
set -u 
set -e
set -x
set -o pipefail

# setting variables
# Git base is team-henrique/
git_base_dir=$(git rev-parse --show-toplevel)
venv="$git_base_dir/.venv"
venv_py="$git_base_dir/.venv/bin/python3.11"

# if there exists a venv
if [ -d $venv ]; then
    # activate the venv
    source "$git_base_dir/.venv/bin/activate"
    
    # if the requirements have not changed since the last install
    if cmp -s pyproject.toml $git_base_dir/.venv/bin/pyproject.toml; then
        echo "venv is up to date"
    else # i.e. the requiremnts may have changed
       poetry install
       # save the newly used requirements in the venv, 
       # to test if they are missing anything next time the script is called
       cp requirements.txt $git_base_dir/.venv/bin/
    fi
else # i.e there is no venv
    # create the venv, activate it, install requirements.txt, and save a copy of them (see above why)
    poetry env use python3.11
    poetry install
    cp pyproject.toml $git_base_dir/.venv/bin/
fi

#find the directory of the git hook in the repo
repo_dir="$git_base_dir/tools/git_hooks/pre-commit"
# find the directory the hook should be stored in locally
system_dir="$git_base_dir/.git/hooks/pre-commit"

#copy python interpeter path to pre-commit file 1st line
echo "#!$venv_py" > "$system_dir"

#copy our manual git-hook to .git/hook/pre-commit
cat "$repo_dir" >> "$system_dir"

#make pre-commit file executable
chmod +x "$system_dir"


