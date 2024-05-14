pipeline {
    agent any

    stages{
        stage('Pre-Build') {
            steps {
                sh '/root/my_pipeline/scripts/pre_build.sh'
            }
        }
        stage('Build') {
            steps {
                sh 'make LLVM=1 -j80 > compile.txt'
                sh 'tail -10 < compile.txt'
                archiveArtifacts artifacts: 'arch/**/Image,compile.txt', fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
            }
        }
        stage('Post') {
            steps {
                sh 'rsync -avz --del ./arch/ yyx@10.161.28.28:~/images/rros_arch_jenkins'
                dir('/root/my_pipeline') {
                    sh '''
                        git pull
                        python3 scripts/submit_job.py
                    '''
                }
            }
        }

    }
}
