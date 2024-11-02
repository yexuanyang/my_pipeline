import xmlrpc.client
import sys
import os

lava_rpc_url = 'http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/'
job_id_dir_path = "/data/user_home/yyx/lava_jobs/rros/{}"

def cancel(pr_number: str):
    job_id_file_path = job_id_dir_path.format(pr_number) + "/jobs.txt"
    if os.path.exists(job_id_file_path) == False:
        os.makedirs(job_id_dir_path)
        return

    server = xmlrpc.client.ServerProxy(lava_rpc_url)

    # 读取jobid文件, 并且请求lava删除
    with open(job_id_file_path.format(pr_number), mode="r", encoding="UTF8") as f:
        content = f.readlines()
    for jobid in content:
        server.scheduler.cancel_job(jobid.strip())

if __name__ == "__main__":
    cancel(sys.argv[1])