#!/bin/bash

# Account creation
echo "Create a username"
read username
sudo adduser $username

# Service setup
sudo apt-get update
sudo apt-get install -y ssh python3.11 python3-pip

# Install Python package
sudo pip3 install pycryptome
