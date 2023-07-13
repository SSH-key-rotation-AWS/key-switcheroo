#!/usr/bin/bash

USERNAME=${username}

set -u
set -e
set -x
set -o pipefail

cd /

# install python3.11
sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
sudo sed -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
sudo apt update && sudo apt -y upgrade
sudo apt install python3.11 -y

sudo apt install ssh -y

#install and start up venv
sudo apt install python3.11-venv -y
sudo mkdir switcheroo_venv
cd switcheroo_venv
sudo python3.11 -m venv .venv
source .venv/bin/activate

# #install pip into venv - don't need its already there
sudo apt install python3.11-dev python3.11-distutils -y
sudo curl -O https://bootstrap.pypa.io/get-pip.py
sudo python3.11 get-pip.py

# test installation of pylint to ensure pip is installed 
sudo pip3.11 install pylint

# check if it is downloaded, if yes: pip works
# python3.11 -m pylint --version

deactivate
cd /

sudo useradd -m ${USERNAME}
sudo mkdir home/test/${USERNAME}
# Set the ownership and permissions for the user's home directory
sudo chown ${USERNAME}:${USERNAME} /home/${USERNAME}
sudo chmod 755 /home/${USERNAME}

# copy the existing .ssh directory to the new user 
sudo cp -r /home/ubuntu/.ssh /home/${USERNAME}
sudo chmod 705 /home/${USERNAME}/.ssh

# Set the ownership and permissions for the authorized_keys file (in case it was overwritten)
sudo chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys
sudo chmod 600 /home/${USERNAME}/.ssh/authorized_keys

# Update the SSH server configuration
sudo systemctl reload sshd


#create aws user
sudo useradd -m aws_user 
sudo chown aws_user:aws_user /home/aws_user
sudo chmod 755 /home/aws_user
# make sure in the venv
sudo pip3.11 install awscli
# set variables
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

