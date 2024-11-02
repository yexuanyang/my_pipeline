pipeline {
    agent any
    
    environment {
    	ARCH = 'arm64'
	    CROSS_COMPILE = 'aarch64-linux-gnu-'
    }

    stages{
        stage('Pre-Build') {
            steps {
                echo "base brach ${CHANGE_TARGET}"
                echo "current branch ${GIT_BRANCH}"
                script {
                    def current_branch = env.GIT_BRANCH
                    def base_branch = env.CHANGE_TARGET
                    if (current_branch == 'linux-v6.6-dev' || base_branch == 'linux-v6.6-dev') {
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
                    def base_branch = env.CHANGE_TARGET
                    if (current_branch == 'linux-v6.6-dev' || base_branch == 'linux-v6.6-dev') {
                        sh 'make ARCH=loongarch CROSS_COMPILE=/root/loongson-gnu-toolchain-8.3-x86_64-loongarch64-linux-gnu-rc1.5/bin/loongarch64-linux-gnu- -j80 > /tmp/compile.txt'
                    } else {
                        sh 'make LLVM=1 -j80 > /tmp/compile.txt'
                    }
                }
                sh 'tail -10 < /tmp/compile.txt'
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'arch/**/Image,compile.txt,arch/**/vmlinux.efi', fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
                sh 'ssh yyx@10.161.28.28 mkdir -p /data/jenkins_images/rros/${BRANCH_NAME}/${BUILD_NUMBER}'
                sh 'rsync -avz --del ../builds/${BUILD_NUMBER}/archive yyx@10.161.28.28:/data/jenkins_images/rros/${BRANCH_NAME}/${BUILD_NUMBER}/archive'
            }
        }
        stage('Post') {
            steps {
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
