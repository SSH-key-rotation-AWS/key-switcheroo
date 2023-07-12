python="/bin/python3.11"
poetry="~/.local/bin/poetry"

//Builds all the code
def runShellBuildStage(){
    sh """
        $poetry env use $python
        $poetry install
        $poetry build
    """  
}

//runs all the tests and spits out errors if any
def runTests(){
    sh """
        $poetry env use $python
        $poetry run pytest tests
    """   
}
def updatePackageVersion(){

}

//The pipeline that Jenkins will look to on how to complete the build/test
pipeline {
    agent any 
    stages {
        stage("Build") { 
            steps {
                runShellBuildStage()
            }
        }
        stage("Test"){
            //Tells Jenkins which S3 bucket we are using
            environment{
                SSH_KEY_DEV_BUCKET_NAME = "testing-bucket-team-henrique"
            }
            steps {
                runTests()
            }
        }
    }
}