#!/bin/bash
  # set up bash settings
  set -eux
  set -o pipefail

  # set variables
  apt_path=/bin/apt
  curl_path=/bin/curl
  java_path=/bin/java
  sed_path=/bin/sed
  wget_path=/bin/wget
  python_path=/bin/python3.11
  poetry_path=/root/.local/bin/poetry
  url=http://localhost:8080
  public_ip=$($curl_path ifconfig.me)
  JENKINS_LOGIN=${JENKINS_USERNAME}:${JENKINS_PASSWORD}
  PRIVATE_KEY_ENV=${PRIVATE_KEY}
  PRIVATE_KEY_TRIMMED=$${PRIVATE_KEY_ENV::-1}

  # disable prompts that make the script hang
  $sed_path -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
  $sed_path -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/g" /etc/needrestart/needrestart.conf

  # download neccesary programs
  $apt_path update && $apt_path upgrade -y
  $apt_path install python3.11 -y
  $apt_path install python3-pip -y
  $curl_path -sSL https://install.python-poetry.org | $python_path -
  $poetry_path self add poetry-git-version-plugin
  $apt_path install openjdk-11-jdk -y
  $apt_path install awscli -y
  $curl_path -OL http://mirrors.jenkins-ci.org/war/latest/jenkins.war

  # run jenkins in background and send output to file
  /bin/nohup $java_path -jar -Djenkins.install.runSetupWizard=false jenkins.war &

  # wait for jenkins page to be up
  while [ "$($curl_path -s -o /dev/null -w "%%{http_code}" $url)" != "200" ];
  do
    /bin/sleep 1;
  done

  # download cli client
  $wget_path $url/jnlpJars/jenkins-cli.jar

  # send jenkins login script to jenkins
  $sed_path -i "s/username/${JENKINS_USERNAME}/g" /files/setup.groovy
  $sed_path -i "s/password/${JENKINS_PASSWORD}/g" /files/setup.groovy
  $java_path -jar jenkins-cli.jar -s $url groovy = < /files/setup.groovy

  # move file to disable throttling
  /bin/mv /files/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml /root/.jenkins/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml
  
  # set up plugin update center, put it in correct location, download necessary plugins, and restart to apply changes
  $wget_path -O default.js http://updates.jenkins-ci.org/update-center.json
  $sed_path "1d;\$d" default.js > /root/default.json
  /bin/mkdir /root/.jenkins/updates
  /bin/mv /root/default.json /root/.jenkins/updates
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" install-plugin github-branch-source workflow-multibranch branch-api cloudbees-folder ssh-steps credentials workflow-aggregator -restart

  # add secrets to credential files
  $sed_path -i "s/usernameplaceholder/${GITHUB_USERNAME}/g" /files/github_credentials.xml
  $sed_path -i "s/passwordplaceholder/${GITHUB_PAT}/g" /files/github_credentials.xml
  $sed_path -i "s/keyplaceholder/${AWS_ACCESS_KEY}/g" /files/aws_access_key.xml
  $sed_path -i "s/keyplaceholder/${AWS_SECRET_ACCESS_KEY}/g" /files/aws_secret_access_key.xml
  $sed_path -i "s/keyplaceholder/${PYPI_API_TOKEN}/g" /files/pypi_api_token.xml
  $sed_path -i "s/keyplaceholder/${GITHUB_PAT}/g" /files/github_pat.xml
  $sed_path -i "s/keyplaceholder/${HOST_1_IP}/g" /files/host_1_ip.xml
  $sed_path -i "s/keyplaceholder/${HOST_2_IP}/g" /files/host_2_ip.xml
  $sed_path -i "s/keyplaceholder/$PRIVATE_KEY_TRIMMED/g" /files/private_key.xml

  # wait for jenkins to be running after restart
  while [ "$($curl_path -s -o /dev/null -w "%%{http_code}" $url/login\?from=%2F)" != "200" ];
  do 
    /bin/sleep 1;
  done

  # send xmls to jenkins and make credentials
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/github_credentials.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/aws_secret_access_key.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/aws_access_key.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/pypi_api_token.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/github_pat.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/host_1_ip.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/host_2_ip.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /files/private_key.xml

  # make webhook in github
  $curl_path -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/SSH-key-rotation-AWS/key-switcheroo/hooks \
  -d "{\"name\":\"web\",\"active\":true,\"events\":[\"push\",\"pull_request\"],\"config\":{\"url\":\"http://$public_ip:8080/github-webhook/\",\"content_type\":\"json\",\"insecure_ssl\":\"0\"}}"
  
  # send pipeline xml to jenkins
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-job MultiBranch < /files/config.xml

  #delete files
  /bin/rm -r /files

  #delete output with sensitive info
  #/bin/rm /var/log/cloud-init-input.log