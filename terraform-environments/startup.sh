#!/usr/bin/bash
  set -x
  sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
  sudo sed -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
  sudo apt update && sudo apt -y upgrade
  sudo apt install python3.11 -y
  sudo apt -y install openjdk-11-jdk
  #commands past here need to be fixed
  curl -fsSL https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo tee \
    /usr/share/keyrings/jenkins-keyring.asc > /dev/null
  echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
    https://pkg.jenkins.io/debian binary/ | sudo tee \
    /etc/apt/sources.list.d/jenkins.list > /dev/null
  sudo apt -y install fontconfig openjdk-11-jre
  sudo apt install jenkins
  sudo systemctl start jenkins.service
  sudo apt install wget build-essential libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt install python3-pip
  pip install virtualenv
  echo 'export SSH_KEY_DEV_BUCKET_NAME="testing-bucket-team-henrique"' >> /etc/profile.d/custom_env.sh