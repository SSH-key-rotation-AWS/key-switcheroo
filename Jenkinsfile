python="/bin/python3.11"

def runShellBuildStage(){
    sh """
        poetry env use $python
        poetry install
        poetry build
    """  
}
def runTests(){
    sh """
        poetry env use $python
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
                runTests()
            }
        }
        stage('Publish'){
            when {
                branch 'main'
            }
            steps{
                script{
                    sh 'gh workflow run main.yml -R SSH-key-rotation-AWS/team-henrique'
                }
            }
        }
    }
}