def runShellBuildStage(){
    sh """
        cd ~/team-henrique
        python3.11 -m venv .venv
        . .venv/bin/activate
        pip3.11 install -r requirements.txt
    """  
}
def runtests(){
    sh """
        cd ~/team-henrique
        . .venv/bin/activate
        python3.11 -m unittest
    """   
}
pipeline {
    agent any 
    stages {
        stage('Build') { 
            steps {
                runShellBuildStage()
            }
        }
        stage('Test'){
            environment{
                SSH_KEY_DEV_BUCKET_NAME = "bigboom"
            }
            steps {
                runtests()
            }
        }
    }
}
