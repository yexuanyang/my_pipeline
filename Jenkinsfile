pipeline {
    agent any
    
    environment {
    	ARCH = 'arm64'
	    CROSS_COMPILE = 'aarch64-linux-gnu-'
    }

    stages{
        stage('Pre-Clean') {
            steps {
                dir('/root/my_pipeline') {
                    sh '''
                    if [[ $s == PR-* ]]; then
                        export comment_id="None"
                        export pr_number=$(echo ${BRANCH_NAME} | awk -F'-' '{print $2}')
                        export last_build=${BUILD_NUMBER}
                        export multi="true"
                        bash /root/my_pipeline/scripts/jenkins/clean.sh
                    fi
                    '''
                }
            }
        }
        stage('Pre-Build') {
            // when {
            //     allOf {
            //         expression { env.CHANGE_ID != null }
            //         expression { env.CHANGE_TARGET != null }
            //     }
            // }
            // steps {
            //     echo "Build PR #${CHANGE_ID}"
            // }
            steps {
                script {
                    def current_branch = env.GIT_BRANCH
                    echo "current branch ${GIT_BRANCH}"
                    def base_branch = ""
                    if (env.CHANGE_TARGET != null && env.CHANGE_ID != null) {
                        base_branch = env.CHANGE_TARGET
                        echo "Build PR #${CHANGE_ID}"
                        echo "Base branch ${CHANGE_TARGET}"
                    }
                    if (current_branch == 'linux-v6.6-dev' || base_branch == 'linux-v6.6-dev') {
                        sh 'cd /root/my_pipeline;git reset --hard origin/HEAD;git pull;chmod +x /root/my_pipeline/scripts/jenkins/6.6pre_build.sh'
                        sh '/root/my_pipeline/scripts/jenkins/6.6pre_build.sh'
                    } else {
                        sh 'cd /root/my_pipeline;git reset --hard origin/HEAD;git pull;chmod +x /root/my_pipeline/scripts/jenkins/pre_build.sh'
                        sh '/root/my_pipeline/scripts/jenkins/pre_build.sh'
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    def current_branch = env.GIT_BRANCH
                    def base_branch = ""
                    if (env.CHANGE_TARGET != null) {
                        base_branch = env.CHANGE_TARGET
                    }
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
                sh 'ssh yyx@10.161.28.28 mkdir -p /data/user_home/yyx/jenkins_images/rros/${BRANCH_NAME}/${BUILD_NUMBER}'
                sh 'rsync -avz --del ../builds/${BUILD_NUMBER}/archive yyx@10.161.28.28:/data/user_home/yyx/jenkins_images/rros/${BRANCH_NAME}/${BUILD_NUMBER}/'
            }
        }
        stage('Post') {
            steps {
                dir('/root/my_pipeline') {
                    sh '''
                        git reset --hard origin/HEAD
                        git pull
                        python3 scripts/jenkins/submit_job.py
                    '''
                }
            }
        }
    }
}
