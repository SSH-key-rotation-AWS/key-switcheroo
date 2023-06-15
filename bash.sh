#!/usr/bin/bash


venv_py=".venv/bin/python"

if [ -d ".venv/bin/" ]; then
    source .venv/bin/activate 
    missing_packages=""
    while read -r line; do
        if ! grep -q "^$line" <<< "$installed_packages"; then
            missing_packages+=" $line"
        fi
    done < requirements.txt
    if [[ -z "$missing_packages" ]]; then
        echo "All packages are installed."
    else
        echo "Some packages are missing: $missing_packages"
        pip install $missing_packages
    fi
else
    echo "i am here"
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

