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
            }
        }
        stage('Post') {
            steps {
                sh 'scp -rq ./arch/ yyx@10.161.28.28:~/images/rros_arch_jenkins'
                sh '''
                    cd /root/my_pipeline
                    git pull
                    python3 submit_job.py
                '''
            }
        }

    }
}
