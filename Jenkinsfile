pipeline {
    agent any
    stages{
        stage('Build') {
            steps {
                sh ''' #!/bin/bash
		            ls -la
                    echo "webhook is working!"
                    make LLVM=1 rros_defconfig
                    touch compile.txt
                    make LLVM=1 -j40 &> compile.txt | tail -10 < compile.txt
                '''
            }
        }
    }
}
