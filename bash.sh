#!/usr/bin/bash
current_dir=$(pwd)
system_dir="$current_dir/.git/hooks/pre-commit"
repo_dir="$current_dir/tools/git_hooks/pre-commit"
cp "$repo_dir" "$system_dir"






