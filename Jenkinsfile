activatevenv="~/team-henrique/.venv/bin/activate"
python="/usr/bin/python3.11"

def runShellBuildStage(){
    sh """
        $python -m venv .venv
        . $activatevenv
        pip install -r requirements.txt
    """  
}
def runtests(){
    sh """
        . $activatevenv
        $python -m unittest
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
                SSH_KEY_DEV_BUCKET_NAME = "testing-bucket-team-henrique"
            }
            steps {
                runtests()
            }
        }
    }
}