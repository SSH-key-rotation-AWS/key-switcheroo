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
  $sed_path -i "s/username/${JENKINS_USERNAME}/g" /setup.groovy
  $sed_path -i "s/password/${JENKINS_PASSWORD}/g" /setup.groovy
  $java_path -jar jenkins-cli.jar -s $url groovy = < /setup.groovy

  # set up plugin update center, put it in correct location, download necessary plugins, and restart to apply changes
  $wget_path -O default.js http://updates.jenkins-ci.org/update-center.json
  $sed_path "1d;\$d" default.js > ~/default.json
  /bin/mkdir /root/.jenkins/updates
  /bin/mv ~/default.json /root/.jenkins/updates
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" install-plugin github-branch-source workflow-multibranch branch-api cloudbees-folder credentials workflow-aggregator -restart

  # add secrets to credential files
  $sed_path -i "s/usernameplaceholder/${GITHUB_USERNAME}/g" /github_credentials.xml
  $sed_path -i "s/passwordplaceholder/${GITHUB_PAT}/g" /github_credentials.xml
  $sed_path -i "s/keyplaceholder/${AWS_ACCESS_KEY}/g" /aws-access-key.xml
  $sed_path -i "s/keyplaceholder/${AWS_SECRET_ACCESS_KEY}/g" /aws-secret-access-key.xml
  $sed_path -i "s/keyplaceholder/${PYPI_API_TOKEN}/g" /pypi_api_token.xml
  $sed_path -i "s/keyplaceholder/${GITHUB_PAT}/g" /github_pat.xml

  # wait for jenkins to be running after restart
  while [ "$($curl_path -s -o /dev/null -w "%%{http_code}" $url/login\?from=%2F)" != "200" ];
  do 
    /bin/sleep 1;
  done

  # send xmls to jenkins and make credentials
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /github_credentials.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /aws-secret-access-key.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /aws-access-key.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /pypi_api_token.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-credentials-by-xml  system::system::jenkins _ < /github_pat.xml

  # make webhook in github
  $curl_path -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GITHUB_PAT}"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/SSH-key-rotation-AWS/team-henrique/hooks \
  -d "{\"name\":\"web\",\"active\":true,\"events\":[\"push\",\"pull_request\"],\"config\":{\"url\":\"http://$public_ip:8080/github-webhook/\",\"content_type\":\"json\",\"insecure_ssl\":\"0\"}}"

  # send pipeline xml to jenkins
#   $echo_path "<?xml version='1.1' encoding='UTF-8'?>
# <org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject plugin=\"workflow-multibranch@756.v891d88f2cd46\">
#   <actions/>
#   <description></description>
#   <displayName>MultiBranch</displayName>
#   <properties>
#     <org.jenkinsci.plugins.configfiles.folder.FolderConfigFileProperty plugin=\"config-file-provider@951.v0461b_87b_721b_\">
#       <configs class=\"sorted-set\">
#         <comparator class=\"org.jenkinsci.plugins.configfiles.ConfigByIdComparator\"/>
#       </configs>
#     </org.jenkinsci.plugins.configfiles.folder.FolderConfigFileProperty>
#     <org.jenkinsci.plugins.workflow.multibranch.PipelineTriggerProperty plugin=\"multibranch-action-triggers@1.8.6\">
#       <createActionJobsToTrigger></createActionJobsToTrigger>
#       <deleteActionJobsToTrigger></deleteActionJobsToTrigger>
#       <actionJobsToTriggerOnRunDelete></actionJobsToTriggerOnRunDelete>
#       <quitePeriod>0</quitePeriod>
#       <branchIncludeFilter>*</branchIncludeFilter>
#       <branchExcludeFilter></branchExcludeFilter>
#       <additionalParameters/>
#     </org.jenkinsci.plugins.workflow.multibranch.PipelineTriggerProperty>
#   </properties>
#   <folderViews class=\"jenkins.branch.MultiBranchProjectViewHolder\" plugin=\"branch-api@2.1122.v09cb_8ea_8a_724\">
#     <owner class=\"org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject\" reference=\"../..\"/>
#   </folderViews>
#   <healthMetrics/>
#   <icon class=\"jenkins.branch.MetadataActionFolderIcon\" plugin=\"branch-api@2.1122.v09cb_8ea_8a_724\">
#     <owner class=\"org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject\" reference=\"../..\"/>
#   </icon>
#   <orphanedItemStrategy class=\"com.cloudbees.hudson.plugins.folder.computed.DefaultOrphanedItemStrategy\" plugin=\"cloudbees-folder@6.815.v0dd5a_cb_40e0e\">
#     <pruneDeadBranches>false</pruneDeadBranches>
#     <daysToKeep>-1</daysToKeep>
#     <numToKeep>-1</numToKeep>
#     <abortBuilds>false</abortBuilds>
#   </orphanedItemStrategy>
#   <triggers/>
#   <disabled>false</disabled>
#   <sources class=\"jenkins.branch.MultiBranchProject\$BranchSourceList\" plugin=\"branch-api@2.1122.v09cb_8ea_8a_724\">
#     <data>
#       <jenkins.branch.BranchSource>
#         <source class=\"org.jenkinsci.plugins.github_branch_source.GitHubSCMSource\" plugin=\"github-branch-source@1728.v859147241f49\">
#           <id>d6f1f5bc-bbf7-4241-ada7-a8aa7a8877e9</id>
#           <apiUri>https://api.github.com</apiUri>
#           <credentialsId>github_login</credentialsId>
#           <repoOwner>SSH-key-rotation-AWS</repoOwner>
#           <repository>key-switcheroo</repository>
#           <repositoryUrl>https://github.com/SSH-key-rotation-AWS/key-switcheroo</repositoryUrl>
#           <traits>
#             <org.jenkinsci.plugins.github__branch__source.BranchDiscoveryTrait>
#               <strategyId>3</strategyId>
#             </org.jenkinsci.plugins.github__branch__source.BranchDiscoveryTrait>
#             <org.jenkinsci.plugins.github__branch__source.OriginPullRequestDiscoveryTrait>
#               <strategyId>3</strategyId>
#             </org.jenkinsci.plugins.github__branch__source.OriginPullRequestDiscoveryTrait>
#           </traits>
#         </source>
#         <strategy class=\"jenkins.branch.DefaultBranchPropertyStrategy\">
#           <properties class=\"java.util.Arrays\$ArrayList\">
#             <a class=\"jenkins.branch.BranchProperty-array\">
#               <jenkins.branch.NoTriggerBranchProperty>
#                 <triggeredBranchesRegex>main|PR-\d+-head</triggeredBranchesRegex>
#                 <strategy>NONE</strategy>
#               </jenkins.branch.NoTriggerBranchProperty>
#             </a>
#           </properties>
#         </strategy>
#       </jenkins.branch.BranchSource>
#     </data>
#     <owner class=\"org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject\" reference=\"../..\"/>
#   </sources>
#   <factory class=\"org.jenkinsci.plugins.workflow.multibranch.WorkflowBranchProjectFactory\">
#     <owner class=\"org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject\" reference=\"../..\"/>
#     <scriptPath>Jenkinsfile</scriptPath>
#   </factory>
# </org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject>" >> config.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" create-job MultiBranch < /config.xml
  $sed_path -i "s/ThrottleForNormalize/NoThrottle/g" /root/.jenkins/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml
  $java_path -jar jenkins-cli.jar -s $url -auth "$JENKINS_LOGIN" restart