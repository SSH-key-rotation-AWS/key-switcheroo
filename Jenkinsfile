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

//updates the github tag so the PYPI package version's tag is bumped
def updatePackageVersion(){
    sh """
        $python github_api_tag_manager.py
    """
}

//fetch pypi API token from AWS secrets manager
def fetchPYPI(){
     
}


//The pipeline that Jenkins will look to on how to complete the build/test
pipeline {
    agent any 
    stages {
        stage("Build") { 
            environment{
                POETRY_PYPI_TOKEN_PYPI = fetchPYPI()
            }
            steps {
                updatePackageVersion()
                runShellBuildStage()
            }
        }
        stage("Test"){
            //Tells Jenkins which S3 bucket we are using
            environment{
                SSH_KEY_DEV_BUCKET_NAME = "testing-bucket-key-switcheroo"
            }
            steps {
                runTests()
            }
        }
    }
}