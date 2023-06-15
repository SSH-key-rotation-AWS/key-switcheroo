#!/usr/bin/bash


venv_py=".venv/bin/python"

if [ -d "$venv_py" ]; then
    echo "Directory exists."
    # Perform your logic here for the existing directory
else
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    # Perform your logic here for the non-existing directory
fi
#find current directory, and git-hooks
current_dir=$(pwd)
repo_dir="$current_dir/tools/git_hooks/pre-commit"
system_dir="$current_dir/.git/hooks/pre-commit"

#copy python interpeter path to pre-commit file
echo "#!$venv_py" > $system_dir

#copy our manual git-hook to .git/hook/pre-commit
cat $repo_dir >> $system_dir

#make pre-commit file executable
chmod +x $system_dir

#$(pip install -r requirements.txt)


