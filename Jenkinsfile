pipeline {
    agent any
    stages{
        stage('Build') {
            steps {
                sh ''' #!/bin/bash
		            rustup override set beta-2021-06-23-x86_64-unknown-linux-gnu
                    rustup component add rust-src
                    make LLVM=1 rros_defconfig
                    make LLVM=1 -j40
                '''
            }
        }
    }
}
