pipeline {
    agent any

    environment {
        PANDA_ADDR = '10.161.28.28'
        PANDA_IMAGES_DIR = 'rros_arch_jenkins'
    }

    stages{
        stage('Pre-Build') {
            steps {
                sh ''' #!/bin/bash
		            rustup override set beta-2021-06-23-x86_64-unknown-linux-gnu
                    rustup component add rust-src
                    make LLVM=1 rros_defconfig
                    touch compile.txt
                '''
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
                sh 'scp -rq ./arch/ yyx@${env.PANDA_ADDR}:~/images/${env.PANDA_IMAGES_DIR}'
            }
        }
        
    }
}
