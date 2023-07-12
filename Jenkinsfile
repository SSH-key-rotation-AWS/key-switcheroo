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
        poetry run pytest tests
    """   
}
def updatePackageVersion(){
    
}

pipeline {
    agent any 
    stages {
        stage("Build") { 
            steps {
                runShellBuildStage()
            }
        }
        stage("Test"){
            environment{
                SSH_KEY_DEV_BUCKET_NAME = "testing-bucket-team-henrique"
            }
            steps {
                runTests()
            }
        }
    }
}