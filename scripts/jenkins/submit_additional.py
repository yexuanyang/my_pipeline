"""
@rros-rbot test clean
@rros-rbot test perf ...
@rros-rbot首先解析test后第一个参数:
    1. 如果是clean, 则向jenkins发送POST请求, 触发一个pre-clean pipeline(后续略)
    2. 如果是perf/SEU/posix, 则向jenkins发送POST请求(传递pr number和pr comment body),
       触发一个test_jobs pipeline, pipeline中调用本python脚本, 并且传入pr_number和pr_comment_body作为参数

本python脚本:
    1. 解析pr_comment_body参数内容:
    2. 如果参数不正确, 则向@rros-rbot一个路由发送POST请求, @rros-rbot以pr comment的形式反馈给maintainer
    3. 如果参数正确:
        a. 读取@prefix/pr-number/test-latest/jobs文件中的lava job id, 向lava发送请求, cancel这些job
        b. 向lava提交任务, 并且把job id保存在文件中
        c. 向lava发送job yaml的时候需要指定image路径、fs路径、架构、notify.token
    4. 直接结束流水线

@rros-rbot test perf ...
1. -n --name: test name
2. -c --compare: compare to (这个需要通过notify.token传到@rros-rbot)
3. -a --arch: architecture and boards
4. -s --stress: stress加压  (默认会进行不加压测试, 如果指定了加压, 就需要同时再对比加压和不加压的数据)
5. --prNumber: pr_number(需要传递给notify.token TODO: 如何引用一个issue comment)

notify.token里面需要prNumber、--commentNumber
"""
import argparse
import sys
import xmlrpc.client
import os
import yaml
import requests
import json
import cancel

tests = ['perf']    # 后续可以添加其他test类型

arch_board_mapping = {
    "x86"       :   "qemu",
    "arm64"     :   "qemu",    # 等到lava支持实板部署后, 更换"raspi4b"
    "riscv"     :   "qemu",
    "loongarch" :   "qemu",
}

# 对于一些测试来说, 只能跑在特定的RTOS上
test_rtos_mapping = {
    "QNX"           : ["RROS", "EVL"],
    "cyclictest"    : ["preempt-rt"],
}

rbot_error_arg_url = 'http://10.161.28.28:30000/lava-callback/error-arg'
lava_rpc_url = 'http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/'
perf_jos_defination_prefix = '/root/my_pipeline/tests/jobs_defination/additional_job/perf'
perf_test_defination_prefix = '/root/my_pipeline/tests/test_defination/additional_job/perf'
job_id_file_path = "/data/user_home/yyx/lava_jobs/rros/{}/jobs.txt"
rros_image_path = "/data/user_home/yyx/jenkins_images/rros/{}/{}/archive/arch/{}/boot/Image"

def post_rbot_error_arg(info: str):
    post_data = {
        'info': info,
    }
    headers = {
        'Content-Type': 'application/json',
    }
    requests.post(url=rbot_error_arg_url, headers=headers, data=json.dumps(post_data))
    

def perf_test(raw_args: list):
    parser = argparse.ArgumentParser(
        description="Parsing performance test parameters",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # -n QNX cyclictest
    parser.add_argument(
        "-n", "--name",
        nargs='+',
        default=['QNX'],
        required=False,
        help="Specify the name of the test set to be tested",
    )
    
    # -c preempt-rt EVL
    parser.add_argument(
        "-c", "--compare",
        nargs='+',
        default=['RROS'],
        required=False,
        help="Specify the RTOS name and version number that RROS needs to compare",
    )
    
    # -a arm64 riscv
    parser.add_argument(
        "-a", "--arch",
        nargs='+',
        default=["arm64"],
        required=False,
        help="Specify the architecture and board type",
    )
    
    # --prNumber 60
    parser.add_argument(
        "--prNumber",
        type=int,
        required=True,
        help="PR number passed in from Jenkinsfile",
    )
    
    # --buildNumber 6
    parser.add_argument(
        "--buildNumber",
        type=int,
        required=True,
        help="build number passed in from Jenkinsfile",
    )

    try:
        args = parser.parse_args(raw_args)
    except:
        post_rbot_error_arg("The passed parameters were not parsed successfully.")
        return

    server = xmlrpc.client.ServerProxy(lava_rpc_url)

    job_id_file_path = job_id_file_path.format(args.prNumber)
    # 取消未完成的lava job
    cancel.cancel(str(args.prNumber))

    # 向lava提交测试任务
    new_job_ids = []
    for test_name in args.name:
        jobs_defination_path = os.path.join(perf_jos_defination_prefix, test_name + ".yaml")
        with open(jobs_defination_path) as f:
            # 修改config: arch, token, fs, image
            config = yaml.load(f, yaml.FullLoader)
            config["notify"]["callbacks"][0]["token"] = args.prNumber
            config["actions"][0]["deploy"]["images"]["kernel"]["url"] = rros_image_path.format(args.prNumber, args.buildNumber, "arm64")
            config = yaml.dump(config)
            server = xmlrpc.client.ServerProxy(lava_rpc_url)
            jobid = server.scheduler.submit_job(config)
            new_job_ids.append(str(jobid))
    
    # 写入jobid文件
    with open(job_id_file_path, mode="w", encoding="UTF8") as f:
        f.write('\n'.join(new_job_ids))

# def SEU_test():
    # pass

#def posix_test():
    # pass

def main():
    # @rros-rbot test perf ... --pr_number 61 --issue_comment_number 1
    if sys.argv.__len__() < 2 or sys.argv[1] not in tests:
        post_rbot_error_arg("You should specify the correct test type: perf (or SEU...).")
        return

    args = sys.argv[2:]
    # 根据测试的类型来调用相应的测试函数来处理参数
    eval("{}_test({})".format(sys.argv[1], args))

if __name__ == "__main__":
    main()
