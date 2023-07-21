python = '/bin/python3.11'
poetry = "~/.local/bin/poetry"

//Builds all the code
def runShellBuildStage() {
    sh """
        $poetry env use $python
        $poetry install
        $poetry build
    """
}

//runs all the tests and spits out errors if any
def runTests() {
    sh """
        $poetry env use $python
        $poetry run pytest tests
    """
}

//updates the github tag so the PYPI package version's tag is bumped
def publishToPYPI() {
    sh """
        $poetry run python jenkins_pipeline/github_api_tag_manager.py
        $poetry publish
    """
}

def pythonAPIOutput

//The pipeline that Jenkins will look to on how to complete the build/test
pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
    }
    stages {
        stage('Retrieve PYPI api token and docker') {
            steps {
                script {
                    // Run the Python script and capture its output
                    sh """
                        $poetry env use $python
                        $poetry install
                        chmod +x -R jenkins_pipeline/pypi_api_secret.py
                    """
                    pythonAPIOutput = sh(returnStdout: true, script: ".venv/bin/python3.11 jenkins_pipeline/pypi_api_secret.py").trim()
                }
            }
        }

        stage('Build') {
            steps {
                runShellBuildStage()
            }
        }

        stage('Test') {
            //Tells Jenkins which S3 bucket we are using
            environment {
                SSH_KEY_DEV_BUCKET_NAME = 'testing-bucket-key-switcheroo2'
            }
            steps {
                script {
                    sh """
                        $poetry run switcheroo_configure add --access-key $AWS_ACCESS_KEY_ID --secret-access-key $AWS_SECRET_ACCESS_KEY --region us-east-1
                    """
                }
                runTests()
            }
        }

        stage('Publish') {
            environment {
                POETRY_PYPI_TOKEN_PYPI = "${pythonAPIOutput}"
            }
            steps {
                publishToPYPI()
            }
        }
    }
}
