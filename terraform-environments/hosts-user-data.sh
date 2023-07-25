#!/usr/bin/bash


# set variables
  sudo_path=/bin/sudo
  apt_path=/bin/apt
  curl_path=/bin/curl
  sed_path=/bin/sed

# store script encoded in base64 so the ec2 has access to it
  encoded_python_script="IyBVc2UgdGhpcyBjb2RlIHNuaXBwZXQgaW4geW91ciBhcHAuCiMgSWYgeW91IG5lZWQgbW9yZSBpbmZvcm1hdGlvbiBhYm91dCBjb25maWd1cmF0aW9ucwojIG9yIGltcGxlbWVudGluZyB0aGUgc2FtcGxlIGNvZGUsIHZpc2l0IHRoZSBBV1MgZG9jczoKIyBodHRwczovL2F3cy5hbWF6b24uY29tL2RldmVsb3Blci9sYW5ndWFnZS9weXRob24vCgppbXBvcnQgYm90bzMKZnJvbSBib3RvY29yZS5leGNlcHRpb25zIGltcG9ydCBDbGllbnRFcnJvcgoKCmRlZiBnZXRfc2VjcmV0KCk6CgogICAgc2VjcmV0X25hbWUgPSAicHJvZC9ob3N0cy9zZWNyZXRzIgogICAgcmVnaW9uX25hbWUgPSAidXMtZWFzdC0xIgoKICAgICMgQ3JlYXRlIGEgU2VjcmV0cyBNYW5hZ2VyIGNsaWVudAogICAgc2Vzc2lvbiA9IGJvdG8zLnNlc3Npb24uU2Vzc2lvbigpCiAgICBjbGllbnQgPSBzZXNzaW9uLmNsaWVudCgKICAgICAgICBzZXJ2aWNlX25hbWU9J3NlY3JldHNtYW5hZ2VyJywKICAgICAgICByZWdpb25fbmFtZT1yZWdpb25fbmFtZQogICAgKQoKICAgIHRyeToKICAgICAgICBnZXRfc2VjcmV0X3ZhbHVlX3Jlc3BvbnNlID0gY2xpZW50LmdldF9zZWNyZXRfdmFsdWUoCiAgICAgICAgICAgIFNlY3JldElkPXNlY3JldF9uYW1lCiAgICAgICAgKQogICAgZXhjZXB0IENsaWVudEVycm9yIGFzIGU6CiAgICAgICAgIyBGb3IgYSBsaXN0IG9mIGV4Y2VwdGlvbnMgdGhyb3duLCBzZWUKICAgICAgICAjIGh0dHBzOi8vZG9jcy5hd3MuYW1hem9uLmNvbS9zZWNyZXRzbWFuYWdlci9sYXRlc3QvYXBpcmVmZXJlbmNlL0FQSV9HZXRTZWNyZXRWYWx1ZS5odG1sCiAgICAgICAgcmFpc2UgZQoKICAgICMgRGVjcnlwdHMgc2VjcmV0IHVzaW5nIHRoZSBhc3NvY2lhdGVkIEtNUyBrZXkuCiAgICBzZWNyZXQgPSBnZXRfc2VjcmV0X3ZhbHVlX3Jlc3BvbnNlWydTZWNyZXRTdHJpbmcnXQoKICAgICMgY3JlYXRlIGEganNvbiBvYmplY3QgdXNpbmYgdGhlIHJldHVybmVkIHNlY3JldAogICAgZGF0YSA9IGpzb24ubG9hZHMoc2VjcmV0KQoKICAgICMgR2V0IHRoZSB2YWx1ZSBvZiBlYWNoIGtleQogICAgcHVibGljX2tleSA9IGRhdGFbJ3B1YmxpYyddCiAgICBwcml2YXRlX2tleSA9IGRhdGFbJ3ByaXZhdGUnXQoKICAgICMgWW91ciBjb2RlIGdvZXMgaGVyZS4KICAgIHByaW50KHB1YmxpY19rZXkpCiAgICBwcmludChwcml2YXRlX2tleSkKCmdldF9zZWNyZXQoKQo"

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

#install pip3
$sudo_path $apt_path install python3.11-dev python3.11-distutils -y
$sudo_path $curl_path -O https://bootstrap.pypa.io/get-pip.py
$sudo_path python3.11 get-pip.py


cd /
# $sudo_path mkdir pre-aws
# #for more below, but want to install it in venv
# $sudo_path $apt_path install unzip
# $curl_path "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# unzip awscliv2.zip
# ./aws/install
# aws_path=$(which aws)


# deactivate
cd /
cd home
# $sudo_path mkdir startoff
$sudo_path useradd -m ${USERNAME}
cd ${USERNAME}

$sudo_path mkdir atleasthere
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

#create aws user - doesn't do anything since ec2 itself already has admin access
$sudo_path useradd -m aws_user 
$sudo_path chown aws_user:aws_user /home/aws_user
$sudo_path chmod 755 /home/aws_user


#install and set up venv to run python script
$sudo_path $apt_path install python3.11-venv -y
$sudo_path mkdir switcheroo_venv
cd switcheroo_venv
$sudo_path python3.11 -m venv .venv
source .venv/bin/activate
pip3 install boto3


# Decode and save the Python script to a file
cd /home
$sudo_path mkdir python-script
cd python-script
python_script_decoded="$(echo "$encoded_python_script" | base64 -d)"
$sudo_path touch /home/python-script/get-creds.py
$sudo_path chmod 777 /home/python-script/get-creds.py
echo "$python_script_decoded" > /home/python-script/get-creds.py

# call script to get the keys, and store them in a temp file to access them
cd /
$sudo_path touch temp_output.txt
$sudo_path chmod 777 temp_output.txt
python3.11 /home/python-script/get-creds.py > temp_output.txt
access_key=$($sudo_path $sed_path '1!d' temp_output.txt)
secret_key=$($sudo_path $sed_path '2!d' temp_output.txt)
$sudo_path touch tempAcc.txt
$sudo_path touch tempSec.txt
echo "access_key=$access_key" > tempAcc.txt
echo "secret_key=$secret_key" >  tempSec.txt
# Remove the temporary file
$sudo_path rm temp_output.txt


# install switcheroo
$sudo_path pip3 install key-switcheroo
echo "1"
switcheroo_configure_path=$(which switcheroo_configure)
echo "2"
$sudo_path su - aws_user -c "$switcheroo_configure_path add --access-key $access_key --secret-access-key $secret_key --region us-east-1"
echo "3"
$sudo_path mkdir -p /etc/ssh/sshd_config.d
cd /etc/ssh/sshd_config.d
$sudo_path touch switcheroo.conf
switcheroo_retrieve_path=$(which switcheroo_retrieve)
$sudo_path echo -e "AuthorizedKeysCommand $switcheroo_retrieve_path %u -ds s3 --bucket production-bucket-team-henrique \nAuthorizedKeysCommandUser aws_user"> switcheroo.conf

cd / 
cd home
#confirms that all the code has run

$sudo_path apt remove ec2-instance-connect -y
$sudo_path mkdir iamdone
