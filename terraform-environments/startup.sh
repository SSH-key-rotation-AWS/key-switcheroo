#!/bin/bash
  # set up bash settings
  set -eux
  set -o pipefail

  # set variables
  ubuntu_user="/bin/sudo -u ubuntu"
  apt_path=/bin/apt
  curl_path=/bin/curl
  java_path=/bin/java
  sed_path=/bin/sed
  wget_path=/bin/wget
  python_path=/bin/python3.11
  poetry_path=~/.local/bin/poetry
  url=http://localhost:8080
  public_ip=$($curl_path ifconfig.me)
  JENKINS_LOGIN=${JENKINS_USERNAME}:${JENKINS_PASSWORD}

  # disable prompts that make the script hang
  $sed_path -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
  $sed_path -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/g" /etc/needrestart/needrestart.conf

  # download neccesary programs
  $apt_path update && $apt_path upgrade -y
  $apt_path install python3.11 -y
  $apt_path install openjdk-11-jdk -y
  cd /home/ubuntu
  $curl_path -sSL https://install.python-poetry.org | $python_path -
  $poetry_path self add poetry-git-version-plugin
  $curl_path -OL http://mirrors.jenkins-ci.org/war/latest/jenkins.war

  # run jenkins in background and send output to file
  $ubuntu_user /bin/nohup $java_path -jar -Djenkins.install.runSetupWizard=false jenkins.war &

  # wait for jenkins page to be up
  while [ "$($curl_path -s -o /dev/null -w "%%{http_code}" $url)" != "200" ];
  do
    /bin/sleep 1;
  done

  # download cli client
  $wget_path $url/jnlpJars/jenkins-cli.jar

  # send jenkins login script to jenkins
  $sed_path -i "s/username/${JENKINS_USERNAME}/g" /home/ubuntu/setup.groovy
  $sed_path -i "s/password/${JENKINS_PASSWORD}/g" /home/ubuntu/setup.groovy
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url groovy = < /home/ubuntu/setup.groovy

  # set up plugin update center, put it in correct location, download necessary plugins, and restart to apply changes
  $wget_path -O default.js http://updates.jenkins-ci.org/update-center.json
  $sed_path "1d;\$d" default.js > /home/ubuntu/default.json
  /bin/mkdir /home/ubuntu/.jenkins/updates
  /bin/mv /home/ubuntu/default.json /home/ubuntu/.jenkins/updates
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" install-plugin github-branch-source workflow-multibranch branch-api cloudbees-folder credentials workflow-aggregator -restart
  
  # add secrets to credential files
  $sed_path -i "s/usernameplaceholder/${GITHUB_USERNAME}/g" /home/ubuntu/github_credentials.xml
  $sed_path -i "s/passwordplaceholder/${GITHUB_PAT}/g" /home/ubuntu/github_credentials.xml
  $sed_path -i "s/keyplaceholder/${AWS_ACCESS_KEY}/g" /home/ubuntu/aws-access-key.xml
  $sed_path -i "s/keyplaceholder/${AWS_SECRET_ACCESS_KEY}/g" /home/ubuntu/aws-secret-access-key.xml
  $sed_path -i "s/keyplaceholder/${PYPI_API_TOKEN}/g" /home/ubuntu/pypi_api_token.xml
  $sed_path -i "s/keyplaceholder/${GITHUB_PAT}/g" /home/ubuntu/github_pat.xml

  # wait for jenkins to be running after restart
  while [ "$($curl_path -s -o /dev/null -w "%%{http_code}" $url/login\?from=%2F)" != "200" ];
  do 
    /bin/sleep 1;
  done

  # send xmls to jenkins and make credentials
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml system::system::jenkins _ < /home/ubuntu/github_credentials.xml
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml system::system::jenkins _ < /home/ubuntu/aws-secret-access-key.xml
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml system::system::jenkins _ < /home/ubuntu/aws-access-key.xml
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml system::system::jenkins _ < /home/ubuntu/pypi_api_token.xml
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml system::system::jenkins _ < /home/ubuntu/github_pat.xml

  # make webhook in github
  $curl_path -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/SSH-key-rotation-AWS/team-henrique/hooks \
  -d "{\"name\":\"web\",\"active\":true,\"events\":[\"push\",\"pull_request\"],\"config\":{\"url\":\"http://$public_ip:8080/github-webhook/\",\"content_type\":\"json\",\"insecure_ssl\":\"0\"}}"

  #disable throttling
  $sed_path "s/ThrottleForNormalize/NoThrottle/g" /home/ubuntu/.jenkins/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml

  # send pipeline xml to jenkins
  $ubuntu_user $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-job MultiBranch < /home/ubuntu/config.xml