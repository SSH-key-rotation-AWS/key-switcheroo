#!/usr/bin/bash


# set variables
  sudo_path=/bin/sudo
  apt_path=/bin/apt
  curl_path=/bin/curl
  sed_path=/bin/sed

# USERNAME=$username
set -u
set -e
set +x
set -o pipefail

cd /

# install python3.11
$sudo_path $sed_path -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
$sudo_path $sed_path -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
$sudo_path $apt_path update && $sudo_path $apt_path -y upgrade
$sudo_path $apt_path install python3.11 -y

$sudo_path $apt_path install ssh -y

# #install and start up venv
# $sudo_path $apt_path install python3.11-venv -y
# $sudo_path mkdir switcheroo_venv
# cd switcheroo_venv
# $sudo_path python3.11 -m venv .venv
# source .venv/bin/activate

# #install pip into venv - don't need its already there
$sudo_path $apt_path install python3.11-dev python3.11-distutils -y
$sudo_path $curl_path -O https://bootstrap.pypa.io/get-pip.py
$sudo_path python3.11 get-pip.py



# test installation of pylint to ensure pip is installed 
$sudo_path pip3.11 install pylint
#for more below, but want to install it in venv
$sudo_path pip3.11 install awscli

# check if it is downloaded, if yes: pip works
# python3.11 -m pylint --version

# deactivate
cd /
cd home
# $sudo_path mkdir startoff
$sudo_path useradd -m ${USERNAME}
# $sudo_path mkdir atleasthere
# Set the ownership and permissions for the user's home directory
$sudo_path chown ${USERNAME}:${USERNAME} /home/${USERNAME}
$sudo_path chmod 755 /home/${USERNAME}

cd /
$sudo_path mkdir iamhere1
# copy the existing .ssh directory to the new user 
$sudo_path cp -r /home/ubuntu/.ssh /home/${USERNAME}
$sudo_path chmod 705 /home/${USERNAME}/.ssh

$sudo_path mkdir iamhere2

# Set the ownership and permissions for the authorized_keys file (in case it was overwritten)
$sudo_path chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys
$sudo_path chmod 600 /home/${USERNAME}/.ssh/authorized_keys

# Update the SSH server configuration
$sudo_path systemctl reload sshd

$sudo_path mkdir iamhere3

#create aws user
$sudo_path useradd -m aws_user 
$sudo_path chown aws_user:aws_user /home/aws_user
$sudo_path chmod 755 /home/aws_user
# set variables
export AWS_DEFAULT_REGION="us-east-1"
cd / 
cd home
#confirms that all the code has run
$sudo_path mkdir iamdone

########### Need to figure out
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

