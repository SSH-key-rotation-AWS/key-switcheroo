#!/usr/bin/bash


# set variables
  sudo_path=/bin/sudo
  apt_path=/bin/apt
  curl_path=/bin/curl
  sed_path=/bin/sed

# store script encoded in base64 so the ec2 has access to it
  encoded_python_script="aW1wb3J0IGJvdG8zCmZyb20gYm90b2NvcmUuZXhjZXB0aW9ucyBpbXBvcnQgQ2xpZW50RXJyb3IKaW1wb3J0IGpzb24KCgoKZGVmIGdldF9zZWNyZXQoKToKCiAgICBzZWNyZXRfbmFtZSA9ICJwcm9kL2hvc3Qva2V5cyIKICAgIHJlZ2lvbl9uYW1lID0gInVzLWVhc3QtMSIKCiAgICAjIENyZWF0ZSBhIFNlY3JldHMgTWFuYWdlciBjbGllbnQKICAgIHNlc3Npb24gPSBib3RvMy5zZXNzaW9uLlNlc3Npb24oKQogICAgY2xpZW50ID0gc2Vzc2lvbi5jbGllbnQoCiAgICAgICAgc2VydmljZV9uYW1lPSdzZWNyZXRzbWFuYWdlcicsCiAgICAgICAgcmVnaW9uX25hbWU9cmVnaW9uX25hbWUKICAgICkKCiAgICB0cnk6CiAgICAgICAgZ2V0X3NlY3JldF92YWx1ZV9yZXNwb25zZSA9IGNsaWVudC5nZXRfc2VjcmV0X3ZhbHVlKAogICAgICAgICAgICBTZWNyZXRJZD1zZWNyZXRfbmFtZQogICAgICAgICkKICAgIGV4Y2VwdCBDbGllbnRFcnJvciBhcyBlOgogICAgICAgICMgRm9yIGEgbGlzdCBvZiBleGNlcHRpb25zIHRocm93biwgc2VlCiAgICAgICAgIyBodHRwczovL2RvY3MuYXdzLmFtYXpvbi5jb20vc2VjcmV0c21hbmFnZXIvbGF0ZXN0L2FwaXJlZmVyZW5jZS9BUElfR2V0U2VjcmV0VmFsdWUuaHRtbAogICAgICAgIHJhaXNlIGUKCiAgICAjIERlY3J5cHRzIHNlY3JldCB1c2luZyB0aGUgYXNzb2NpYXRlZCBLTVMga2V5LgogICAgc2VjcmV0ID0gZ2V0X3NlY3JldF92YWx1ZV9yZXNwb25zZVsnU2VjcmV0U3RyaW5nJ10KCiAgICAjIGNyZWF0ZSBhIGpzb24gb2JqZWN0IHVzaW5mIHRoZSByZXR1cm5lZCBzZWNyZXQKICAgIGRhdGEgPSBqc29uLmxvYWRzKHNlY3JldCkKCiAgICAjIEdldCB0aGUgdmFsdWUgb2YgZWFjaCBrZXkKICAgIHB1YmxpY19rZXkgPSBkYXRhWydwdWJsaWMnXQogICAgcHJpdmF0ZV9rZXkgPSBkYXRhWydwcml2YXRlJ10KCiAgICAjIFlvdXIgY29kZSBnb2VzIGhlcmUuCiAgICBwcmludChwdWJsaWNfa2V5KQogICAgcHJpbnQocHJpdmF0ZV9rZXkpCgpnZXRfc2VjcmV0KCkKCgoK"

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

# # #install pip into venv - don't need its already there
# $sudo_path $apt_path install python3.11-dev python3.11-distutils -y
# $sudo_path $curl_path -O https://bootstrap.pypa.io/get-pip.py
# $sudo_path python3.11 get-pip.py



cd /
$sudo_path mkdir pre-aws
#for more below, but want to install it in venv
$sudo_path $apt_path install unzip
$curl_path "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
$sudo_path ./aws/install

# check if it is downloaded, if yes: pip works
# python3.11 -m pylint --version

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

#create aws user
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
# $sudo_path rm temp_output.txt


# uncomment removal
# /////////////////////////////
# ////////////////////
# ///////////////////////////////
# ////////////////////////////
# ///////////////\\\






# set variables
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCESS_KEY_ID=$access_key
export AWS_SECRET_ACCESS_KEY=$secret_key


# # install switcheroo
# $sudo_path pip3 install key-switcheroo
# switcheroo_path=(which switcheroo_retrieve)

# $sudo_path mkdir -p /etc/ssh/sshd_config.d
# cd /etc/ssh/sshd_config.d
# $sudo_path touch your_conf.conf
# $sudo_path echo "AuthorizedKeysCommand "$switcheroo_path" %u -ds s3 --bucket [production-bucket-team-henrique]"> your_conf.conf
# $sudo_path echo "AuthorizedKeysCommandUser [aws_user]"> your_conf.conf

cd / 
cd home
#confirms that all the code has run
$sudo_path mkdir iamdone


