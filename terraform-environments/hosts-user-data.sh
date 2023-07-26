#!/usr/bin/bash


# set variables
  # sudo_path=$(which sudo)
  # apt_path=$(which apt)
  # curl_path=$(which curl)
  # sed_path=$(which sed)
  sudo_path=/bin/sudo
  apt_path=/bin/apt
  curl_path=/bin/curl
  sed_path=/bin/sed


set -u
set -e
set +x
set -o pipefail

cd /

# install python3.11
$sudo_path "$sed_path" -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
$sudo_path "$sed_path" -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
$sudo_path "$apt_path" update && $sudo_path "$apt_path" -y upgrade
$sudo_path "$apt_path" install python3.11 -y

$sudo_path "$apt_path" install ssh -y

#install pip3
$sudo_path "$apt_path" install python3.11-dev python3.11-distutils -y
$sudo_path "$curl_path" -O https://bootstrap.pypa.io/get-pip.py
$sudo_path python3.11 get-pip.py



cd /
cd home

$sudo_path useradd -m ${USERNAME}
cd ${USERNAME}


# Set the ownership and permissions for the user's home directory
$sudo_path chown ${USERNAME}:${USERNAME} /home/${USERNAME}
$sudo_path chmod 755 /home/${USERNAME}

cd /
# copy the existing .ssh directory to the new user 
$sudo_path cp -r /home/ubuntu/.ssh /home/${USERNAME}
$sudo_path chmod 705 /home/${USERNAME}/.ssh


# Set the ownership and permissions for the authorized_keys file (in case it was overwritten)
$sudo_path chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh/authorized_keys
$sudo_path chmod 600 /home/${USERNAME}/.ssh/authorized_keys


# Update the SSH server configuration
$sudo_path systemctl reload sshd

#create aws user - doesn't do anything since ec2 itself already has admin access
$sudo_path useradd -m aws_user 
$sudo_path chown aws_user:aws_user /home/aws_user
$sudo_path chmod 755 /home/aws_user


#install and set up venv to run python script
$sudo_path "$apt_path" install python3.11-venv -y
$sudo_path mkdir switcheroo_venv
cd switcheroo_venv
$sudo_path python3.11 -m venv .venv
source .venv/bin/activate
pip3 install boto3


# Decode and save the Python script to a file
cd /home
$sudo_path mkdir python-script
cd python-script

python_code=$(cat <<'EOL'
import boto3
from botocore.exceptions import ClientError
import json


def get_secret():

    secret_name = "prod/hosts/keys"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    # create a json object using the returned secret
    data = json.loads(secret)

    # Get the value of each key
    public_key = data['public']
    private_key = data['private']

    # Your code goes here.
    print(public_key)
    print(private_key)

get_secret()
EOL
)


$sudo_path touch /home/python-script/get-creds-plain.py
$sudo_path chmod 777 /home/python-script/get-creds-plain.py
echo "$python_code" > /home/python-script/get-creds-plain.py

# call script to get the keys, and store them in a temp file to access them
cd /
$sudo_path touch temp_output.txt
$sudo_path chmod 777 temp_output.txt
python3.11 /home/python-script/get-creds-plain.py > temp_output.txt
access_key=$($sudo_path "$sed_path" '1!d' temp_output.txt)
secret_key=$($sudo_path "$sed_path" '2!d' temp_output.txt)
# Remove the temporary file
$sudo_path rm temp_output.txt


# install switcheroo
$sudo_path pip3 install key-switcheroo
switcheroo_configure_path=$(which switcheroo_configure)
$sudo_path su - aws_user -c "$switcheroo_configure_path add --access-key $access_key --secret-access-key $secret_key --region us-east-1"
$sudo_path mkdir -p /etc/ssh/sshd_config.d
cd /etc/ssh/sshd_config.d
$sudo_path touch switcheroo.conf
switcheroo_retrieve_path=$(which switcheroo_retrieve)
$sudo_path echo -e "AuthorizedKeysCommand $switcheroo_retrieve_path %u -ds s3 --bucket production-bucket-team-henrique \nAuthorizedKeysCommandUser aws_user"> switcheroo.conf

$sudo_path apt remove ec2-instance-connect -y
