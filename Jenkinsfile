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
def publishToPYPI(){
    sh """
        $python jenkins_pipeline/github_api_tag_manager.py
        $poetry publish
    """
}


//The pipeline that Jenkins will look to on how to complete the build/test
pipeline {
    agent any 
    stages {
        stage("Retrieve PYPI api token") {
            steps {
                script {
                    // Run the Python script and capture its output
                    def pythonAPIOutput
                    pythonAPIOutput = sh(returnStdout: true, script: 'jenkins_pipeline/pypi_api_secret.py').trim()
                }
            }
        }
        stage("Build") { 
            steps {
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
        stage("Publish"){
            environment{
                POETRY_PYPI_TOKEN_PYPI = pythonAPIOutput
            }
            steps {
                publishToPYPI()
            }
        }
    }
}