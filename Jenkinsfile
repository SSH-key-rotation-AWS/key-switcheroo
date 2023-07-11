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
        stage('Trigger Github Versioning action'){
            steps{
                sh 'curl -X POST https://api.github.com/repos/SSH-key-rotation-AWS/team-henrique/actions/workflows/https://github.com/SSH-key-rotation-AWS/team-henrique/blob/5b7136f1d1c17ccaf9af69cc402400230320cbf8/.github/workflows/main.yml/dispatches \
                    -H "Accept: application/vnd.github.v3+json" \
                    -H "Authorization: Bearer Team_Henrique" \
                    -d \'{"ref": "main"}\''
            }
        }
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
    }
}