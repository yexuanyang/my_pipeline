import xmlrpc.client
import sys
import os
import time
from robot import post_rbot

lava_rpc_url = 'http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/'
server = xmlrpc.client.ServerProxy(lava_rpc_url)
job_id_dir_path = "/lava_jobs/rros/{}"

def polling_lava_result(jobs: list) -> dict:
    # TODO: 可以设置一个最长的等待时间
    jobs_results = {}
    jobs_set = {id for id in jobs}
    while len(jobs_set) != 0:
        time.sleep(10)
        next_set = jobs_set.copy()
        for id in jobs_set:
            state = server.scheduler.job_state(id)['job_state']
            if state == 'Finished':
                next_set.remove(id)
                result = server.scheduler.job_output(id).data.decode('utf-8')
                jobs_results['id'] = result
            else:
                break
        jobs_set = next_set
    return jobs_results

def cancel_jobs(pr_number: str, comment_id: int=None):
    job_id_file_path = job_id_dir_path.format(pr_number) + "/jobs.txt"
    if os.path.exists(job_id_file_path) == False:
        os.makedirs(job_id_dir_path.format(pr_number), exist_ok=True)
        return

    # 读取jobid文件, 并且请求lava删除
    with open(job_id_file_path.format(pr_number), mode="r", encoding="UTF8") as f:
        content = f.readlines()
    for jobid in content:
        server.scheduler.cancel_job(jobid.strip())

    if comment_id is not None:
        post_rbot("Test jobs clean successfully.", int(pr_number), comment_id)

if __name__ == "__main__":
    # 清除lava jobs
    cancel_jobs(str(sys.argv[1]), eval(sys.argv[2]))
