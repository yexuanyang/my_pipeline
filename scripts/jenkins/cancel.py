import xmlrpc.client
import sys

lava_rpc_url = 'http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/'
job_id_file_path = "/data/user_home/yyx/lava_jobs/rros/{}/jobs.txt"

def cancel(pr_number: str):
    server = xmlrpc.client.ServerProxy(lava_rpc_url)

    # 读取jobid文件, 并且请求lava删除
    with open(job_id_file_path.format(pr_number), mode="r", encoding="UTF8") as f:
        content = f.readlines()
    for jobid in content:
        server.scheduler.cancel_job(jobid.strip())

if __name__ == "__main__":
    cancel(sys.argv[1])