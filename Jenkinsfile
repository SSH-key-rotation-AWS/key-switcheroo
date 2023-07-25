python = '/bin/python3.11'
poetry = "/root/.local/bin/poetry"

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
        /bin/git pull
        $poetry build
        $poetry publish
    """
}

//The pipeline that Jenkins will look to on how to complete the build/test
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                runShellBuildStage()
            }
        }

        stage('Test') {
            //Tells Jenkins which S3 bucket we are using
            environment {
                SSH_KEY_DEV_BUCKET_NAME = 'testing-bucket-key-switcheroo'
                AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
                AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
            }
            steps {
                script {
                    sh """
                        $poetry run switcheroo_configure add --access-key ${AWS_ACCESS_KEY_ID} --secret-access-key ${AWS_SECRET_ACCESS_KEY} --region us-east-1
                    """
                }
                runTests()
            }
        }

        stage('Publish') {
            when {
                branch 'main'
            }
            environment {
                GITHUB_PAT = credentials('github_pat')
                POETRY_PYPI_TOKEN_PYPI = credentials('pypi_api_token')
            }
            steps {
                publishToPYPI()
            }
        }
    }
}
