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

// def publishToPyPi(){
//     //needs api key
//     sh """
//         poetry env use $python
//         poetry publish
//     """
// }

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
        // stage('Publish'){
        //     steps {
        //         publishToPyPi()
        //     }
        // }
    }
}