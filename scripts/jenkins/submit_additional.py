"""
本python脚本:
    1. 解析pr_comment_body参数内容:
    2. 如果参数不正确, 则向@rros-rbot一个路由发送POST请求, @rros-rbot以pr comment的形式反馈给maintainer
    3. 如果参数正确:
        a. 读取@prefix/pr-number/test-latest/jobs文件中的lava job id, 向lava发送请求, cancel这些job
        b. 向lava提交任务, 并且把job id保存在文件中
        c. 向lava发送job yaml的时候需要指定image路径、fs路径、架构、notify.token
    4. 轮询等待所有job结束
    5. 处理log、整理数据、向APP发送POST展示结果

@rros-rbot test perf ...
1. -n --name: test name
2. -c --compare: compare to (这个需要通过notify.token传到@rros-rbot)
3. -a --arch: architecture and boards
4. -s --stress: stress加压  (默认会进行不加压测试, 如果指定了加压, 就需要同时再对比加压和不加压的数据)
"""
import argparse
import sys
import os
import yaml
import requests
import json
import lava
import re

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

rbot_reply_comment_url = 'http://10.161.28.28:30000/action/reply-comment'
perf_jos_definition_prefix = './tests/jobs_definition/additional_job/perf'
perf_tests_definition_prefix = './tests/tests_definition/additional_job/perf'
job_id_file_path_tmplate = "/lava_jobs/rros/{}/jobs.txt"
rros_image_path = "file:///data/user_home/yyx/jenkins_images/rros/{}/{}/archive/arch/{}/boot/Image"

prNumber, originComment, buildNumber = None, None, None

def post_rbot(info: str):
    # TODO: 给一个APP的参数说明文档链接
    data = {
        'replyComment': info,
        'issueNumber': prNumber,
        'originComment': originComment,
    }
    headers = {
        'Content-Type': 'application/json',
    }

    # requests.post(url=rbot_reply_comment_url, headers=headers, data=json.dumps(post_data))
    requests.post(url=rbot_reply_comment_url, headers=headers, json=data)

def process_QNX_log(log: str) -> str:
    # TODO: 把所有的结果保存在json里
    # TODO: 需要规定所有test的log规则
    pattern = r"min: (\d+) avg: (\d+) max: (\d+)"
    datas = re.search(pattern, log)
    min_value = datas.group(1)
    avg_value = datas.group(2)
    max_value = datas.group(3)
    return "QNX: min: {}, avg: {}, max: {}".format(min_value, avg_value, max_value)
    
def compare_datas() -> str:
    # TODO: 根据json中的数据和其他的RTOS数据进行比较
    pass

def perf_test(raw_args: list):
    global prNumber
    global originComment
    global buildNumber

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

    try:
        args = parser.parse_args(raw_args)
    except:
        post_rbot("The passed parameters were not parsed successfully.")
        return

    job_id_file_path = job_id_file_path_tmplate.format(prNumber)
    # 取消未完成的lava job
    lava.cancel_jobs(str(prNumber))

    # 向lava提交测试任务
    new_job_ids = []
    for test_name in args.name:
        jobs_definition_path = os.path.join(perf_jos_definition_prefix, test_name + ".yaml")
        with open(jobs_definition_path) as f:
            # 修改config: arch, token, fs, image
            config = yaml.load(f, yaml.FullLoader)
            config["notify"]["callbacks"][0]["token"] = str(prNumber)
            # TODO: 先固定路径
            # config["actions"][0]["deploy"]["images"]["kernel"]["url"] = rros_image_path.format(prNumber, buildNumber, "arm64")
            config["actions"][0]["deploy"]["images"]["kernel"]["url"] = "file:///data/user_home/yyx/images/rros_arch_jenkins/arm64/boot"
            config = yaml.dump(config)
            jobid = lava.server.scheduler.submit_job(config)
            # TODO: 需要记录每个test job的测试类型, 比如QNX、cyclictest等等
            new_job_ids.append(str(jobid))

    # 写入jobid文件
    with open(job_id_file_path, mode="w", encoding="UTF8") as f:
        f.write('\n'.join(new_job_ids))

    # 轮询结果
    results = lava.polling_lava_result(new_job_ids)
    # TODO: 处理结果
    # TODO: 轮询提交的测试任务，全都完成之后，获得测试数据，进行数据分析，形成markdown格式文本之后向Github App的/action/reply-comment发送请求
    # json 格式
    # {
    #     replyComment: <string> (要发送的错误提示信息, markdown格式字符串, 建议从文件里面读取, 而不是硬编码到代码里面)
    #     issueNumber: <number> (要回复的comment所在的pr的pr number)
    #     originComment: <number> (要回复的comment id)
    # }

    # TODO: 需要给一个html的模板
    table = """
<table>
    <tr>
        <td></td>
        <td colspan="3">RROS</td>
    </tr>
    <tr>
        <td></td>
        <td>min</td>
        <td>avg</td>
        <td>max</td>
    </tr>
    <tr>
        <td>QNX</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
    </tr>
</table>
"""
    post_rbot(table.format(120, 121, 122))

# def SEU_test():
    # pass

#def posix_test():
    # pass

def main():
    global prNumber
    global originComment
    global buildNumber

    # --prNumber ${pr_number} --originComment ${comment_id} --buildNumber ${last_build} ${arg}
    prNumber, originComment, buildNumber = map(int, sys.argv[2:7:2])
    args = sys.argv[8:]

    if sys.argv[7] not in tests:
        post_rbot("You should specify the correct test type: perf (or SEU...).")
        return

    # 根据测试的类型来调用相应的测试函数来处理参数
    eval("{}_test({})".format(sys.argv[7], args))

if __name__ == "__main__":
    main()
