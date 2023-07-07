#!/usr/bin/bash
  sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
  sudo sed -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
  sudo apt update && sudo apt -y upgrade
  sudo apt install python3.11 -y
  # sudo apt install python3-pip -y
  # sudo apt install python3.11-venv -y
  curl -sSL https://install.python-poetry.org | python3.11 -
  poetry self add poetry-git-version-plugin
  sudo apt -y install openjdk-11-jdk
  curl -OL http://mirrors.jenkins-ci.org/war/latest/jenkins.war
  nohup java -jar -Djenkins.install.runSetupWizard=false jenkins.war &
  # sudo apt install wget build-essential libncursesw5-dev libssl-dev \
  #   libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev -y
  url="http://localhost:8080"
  while [ "$(curl -s -o /dev/null -w "%{http_code}" $url)" != "200" ]; do sleep 1; done
  wget $url/jnlpJars/jenkins-cli.jar
  touch setup.groovy
  echo "import jenkins.model.*
  import hudson.security.*

  def instance = Jenkins.getInstance()

  def hudsonRealm = new HudsonPrivateSecurityRealm(false)
  hudsonRealm.createAccount(\"TeamHenrique\", \"AWS_SSH\")
  instance.setSecurityRealm(hudsonRealm)
  instance.save()

  def strategy = new hudson.security.FullControlOnceLoggedInAuthorizationStrategy()
  strategy.setAllowAnonymousRead(false)
  instance.setAuthorizationStrategy(strategy)" >> setup.groovy
  java -jar jenkins-cli.jar -s $url/ groovy = < setup.groovy
  java -jar jenkins-cli.jar -s $url -auth "TeamHenrique":"AWS_SSH" install-plugin github-branch-source