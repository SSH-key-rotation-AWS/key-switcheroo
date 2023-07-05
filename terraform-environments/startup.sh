#!/usr/bin/bash
  sudo sed -i "s/#\$nrconf{kernelhints} = -1;/\$nrconf{kernelhints} = -1;/g" /etc/needrestart/needrestart.conf
  sudo sed -i 's/#$nrconf{restart} = '"'"'i'"'"';/$nrconf{restart} = '"'"'a'"'"';/g' /etc/needrestart/needrestart.conf
  sudo apt update && sudo apt -y upgrade
  sudo apt install python3.11 -y
  sudo apt install python3-pip -y
  pip install virtualenv
  sudo apt -y install openjdk-11-jdk
  curl -OL http://mirrors.jenkins-ci.org/war/latest/jenkins.war
  nohup java -jar -Djenkins.install.runSetupWizard=false jenkins.war & sudo apt install wget build-essential libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev -y
  sudo chmod 755 /root/
  sudo chmod 755 /root/.jenkins/secrets/initialAdminPassword
  url=http://localhost:8080
  password=$(sudo cat /root/.jenkins/secrets/initialAdminPassword)

  # NEW ADMIN CREDENTIALS URL ENCODED USING PYTHON
  python_path="/bin/python3.11"
  username=$($python_path -c "import urllib;print urllib.quote(raw_input(), safe='')" <<< "TeamHenrique")
  new_password=$($python_path -c "import urllib;print urllib.quote(raw_input(), safe='')" <<< "AWS_SSH")
  fullname=$($python_path -c "import urllib;print urllib.quote(raw_input(), safe='')" <<< "Ari Krakauer")
  email=$($python_path -c "import urllib;print urllib.quote(raw_input(), safe='')" <<< "krakauer@mail.yu.edu")

  # GET THE CRUMB AND COOKIE
  cookie_jar="$(mktemp)"
  full_crumb=$(curl -u "admin:$password" --cookie-jar "$cookie_jar" $url/crumbIssuer/api/xml?xpath=concat\(//crumbRequestField,%22:%22,//crumb\))
  arr_crumb=(${full_crumb//:/ })
  only_crumb=$(echo ${arr_crumb[1]})

  # MAKE THE REQUEST TO CREATE AN ADMIN USER
  curl "$url/j_spring_security_check" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Cache-Control: max-age=0" \
  -H "Connection: keep-alive" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Cookie: $cookie_jar" \
  -H "DNT: 1" \
  -H "Origin: $url" \
  -H "Referer: $url/login?from=%2F" \
  -H "Upgrade-Insecure-Requests: 1" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36" \
  --data-raw "from=%2F&j_username=admin&j_password=$password&json=%7B%22from%22%3A+%22%2F%22%2C+%22j_username%22%3A+%22admin%22%2C+%22j_password%22%3A+%$password%22%2C+%22%24redact%22%3A+%22j_password%22%7D" \
  --compressed \
  --insecure

  # GET for next page
  # curl 'http://18.212.26.209:8080/' \
  # -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  # -H 'Accept-Language: en-US,en;q=0.9' \
  # -H 'Cache-Control: max-age=0' \
  # -H 'Connection: keep-alive' \
  # -H 'Cookie: JSESSIONID.dcb48f34=node0m3p12kij0pfaezvyz6q477o6.node0' \
  # -H 'DNT: 1' \
  # -H 'Referer: http://18.212.26.209:8080/login?from=%2F' \
  # -H 'Upgrade-Insecure-Requests: 1' \
  # -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  # --compressed \
  # --insecure

curl "$url/pluginManager/installPlugins" \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H "Cookie: $cookie_jar" \
  -H 'DNT: 1' \
  -H "Jenkins-Crumb: $only_crumb" \
  -H "Origin: $url" \
  -H "Referer: $url/" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw "{\"dynamicLoad\":true,\"plugins\":[\"cloudbees-folder\",\"antisamy-markup-formatter\",\"build-timeout\",\"credentials-binding\",\"timestamper\",\"ws-cleanup\",\"ant\",\"gradle\",\"workflow-aggregator\",\"github-branch-source\",\"pipeline-github-lib\",\"pipeline-stage-view\",\"git\",\"ssh-slaves\",\"matrix-auth\",\"pam-auth\",\"ldap\",\"email-ext\",\"mailer\"],\"Jenkins-Crumb\":\"$only_crumb\"}" \
  --compressed \
  --insecure

  # GET for next page
  # curl 'http://18.212.26.209:8080/setupWizard/setupWizardFirstUser' \
  # -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  # -H 'Accept-Language: en-US,en;q=0.9' \
  # -H 'Connection: keep-alive' \
  # -H 'Cookie: JSESSIONID.dcb48f34=node0m3p12kij0pfaezvyz6q477o6.node0' \
  # -H 'DNT: 1' \
  # -H 'Referer: http://18.212.26.209:8080/' \
  # -H 'Upgrade-Insecure-Requests: 1' \
  # -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  # --compressed \
  # --insecure

  curl "$url/setupWizard/createAdminUser" \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H "Cookie: $cookie_jar" \
  -H 'DNT: 1' \
  -H "Jenkins-Crumb: $only_crumb" \
  -H "Origin: $url" \
  -H "Referer: $url/" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw "username=$username&password1=$password&password2=AWS_SSH&fullname=Ari%20Krakauer&email=krakauer%40mail.yu.edu&Jenkins-Crumb=$only_crumb&json=%7B%22username%22%3A%20%22TeamHenrique%22%2C%20%22password1%22%3A%20%22AWS_SSH%22%2C%20%22%24redact%22%3A%20%5B%22password1%22%2C%20%22password2%22%5D%2C%20%22password2%22%3A%20%22AWS_SSH%22%2C%20%22fullname%22%3A%20%22Ari%20Krakauer%22%2C%20%22email%22%3A%20%22krakauer%40mail.yu.edu%22%2C%20%22Jenkins-Crumb%22%3A%20%$only_crumb%22%7D&core%3Aapply=&Submit=Save&json=%7B%22username%22%3A%20%22TeamHenrique%22%2C%20%22password1%22%3A%20%22AWS_SSH%22%2C%20%22%24redact%22%3A%20%5B%22password1%22%2C%20%22password2%22%5D%2C%20%22password2%22%3A%20%22AWS_SSH%22%2C%20%22fullname%22%3A%20%22Ari%20Krakauer%22%2C%20%22email%22%3A%20%22krakauer%40mail.yu.edu%22%2C%20%22Jenkins-Crumb%22%3A%20%$only_crumb%22%7D" \
  --compressed \
  --insecure

  curl "$url/setupWizard/configureInstance" \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H "Cookie: $cookie_jar" \
  -H 'DNT: 1' \
  -H "Jenkins-Crumb: $only_crumb" \
  -H "Origin: $url" \
  -H "Referer: $url/" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw "rootUrl=$url%2F&Jenkins-Crumb=$only_crumb&json=%7B%22rootUrl%22%3A%20%22$url%2F%22%2C%20%22Jenkins-Crumb%22%3A%20%$only_crumb%22%7D&core%3Aapply=&Submit=Save&json=%7B%22rootUrl%22%3A%20%22$url%2F%22%2C%20%22Jenkins-Crumb%22%3A%20%$only_crumb%22%7D" \
  --compressed \
  --insecure

  curl "$url/setupWizard/completeInstall" \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H "Cookie: $cookie_jar" \
  -H 'DNT: 1' \
  -H "Jenkins-Crumb: $only_crumb" \
  -H "Origin: $url" \
  -H "Referer: $url/" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw "{\"Jenkins-Crumb\":\"$only_crumb\"}" \
  --compressed \
  --insecure

  export SSH_KEY_DEV_BUCKET_NAME="testing-bucket-team-henrique"