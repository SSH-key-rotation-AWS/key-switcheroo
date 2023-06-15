#!/usr/bin/bash


#find python interpeter to run the git-hook
python_path=$(which python)

if [ -z "$python_path" ]; then
    echo "Python interpreter not found"
    exit 1
fi

#find current directory, and git-hooks
current_dir=$(pwd)
repo_dir="$current_dir/tools/git_hooks/pre-commit"
system_dir="$current_dir/.git/hooks/pre-commit"

#copy python interpeter path to pre-commit file
echo "#!$python_path" > $system_dir

#copy our manual git-hook to .git/hook/pre-commit
cat $repo_dir >> $system_dir

#make pre-commit file executable
$(chmod +x $system_dir)

#$(pip install -r requirements.txt)


