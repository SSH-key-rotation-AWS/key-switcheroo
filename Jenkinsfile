python="/bin/python3.11"

def runShellBuildStage(){
    sh """
        #pip install poetry-git-version-plugin (maybe already have in terraform)
        poetry env use $python
        poetry install
    """  
}
def runtests(){
    sh """
        poetry run $python -m unittest
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