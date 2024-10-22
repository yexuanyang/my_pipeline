pipeline {
    agent any

    environment {
    	ARCH = 'arm64'
	    CROSS_COMPILE = 'aarch64-linux-gnu-'
    }

    stages{
        stage('Pre-Build') {
            steps {
                echo "current branch ${GIT_BRANCH}"
                script {
                    def current_branch = env.GIT_BRANCH
                    if (current_branch == 'linux-v6.6-dev') {
                        sh '/root/my_pipeline/scripts/6.6pre_build.sh'
                    } else {
                        sh '/root/my_pipeline/scripts/pre_build.sh'
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    def current_branch = env.GIT_BRANCH
                    if (current_branch == 'linux-v6.6-dev') {
                        sh 'make ARCH=loongarch CROSS_COMPILE=/root/loongson-gnu-toolchain-8.3-x86_64-loongarch64-linux-gnu-rc1.5/bin/loongarch64-linux-gnu- -j80 > /tmp/compile.txt'
                    } else {
                        sh 'make LLVM=1 -j80 > /tmp/compile.txt'
                    }
                }
                sh 'tail -10 < /tmp/compile.txt'
                archiveArtifacts artifacts: 'arch/**/Image,compile.txt,arch/**/vmlinux.efi', fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
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
