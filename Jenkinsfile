pipeline {
    agent any
    stages{
        stage('Build') {
            steps {
                sh ''' #!/bin/bash
		            ls -la
                    echo "webhook is working!"
                    make LLVM=1 rros_defconfig
                    make LLVM=1 -j40
                '''
            }
        }
    }
}
