pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make LLVM=1 defconfig'
                sh 'make LLVM=1 -j80 > /tmp/compile.txt'
                sh 'tail -10 < /tmp/compile.txt'
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'arch/**/Image,compile.txt', fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
                sh 'scp -r ${JENKINS_HOME}/jobs/${JOB_NAME}/builds/${BUILD_NUMBER}/archive/ root@192.168.2.11:/var/lib/shared_images/${BRANCH_NAME}/${BUILD_NUMBER}/'
            }
        }
        stage('Post') {
            steps {
                dir('${WORKSPACE}/../workspace\@script/')
                echo 'All done!'
                sh 'ls -lh'
            }
        }
    }
}