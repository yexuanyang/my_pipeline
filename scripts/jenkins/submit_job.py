# Python3
import yaml
import xmlrpc.client
import os
from lava import polling_lava_result
from dotenv import load_dotenv
import argparse
load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
job_dir = os.path.join(script_dir, '../../tests/jobs_definition')
rpc_url = os.getenv("LAVA_RPC_URL")

def submit_single_job(job_path, rpc_url, kernel):
    with open(job_path) as f:
        config = yaml.dump(yaml.load(f, yaml.FullLoader))
    config = config.replace("{{kernel}}", kernel)
    server=xmlrpc.client.ServerProxy(rpc_url)
    jobid=server.scheduler.submit_job(config)
    print("submit job " + str(jobid))
    return str(jobid)

def submit_all_jobs_in_directory(directory, rpc_url, kernel):
    jobs = []
    for root, dirs, files in os.walk(directory):
        for file_name in files: 
            file_path = os.path.join(root, file_name)
            jobs.append(submit_single_job(file_path, rpc_url, kernel))
    return jobs

def submit_all_jobs_in_dir_list(dir_list, rpc_url, kernel):
    jobs = []
    for dir in dir_list:
        jobs.extend(submit_all_jobs_in_directory(dir, rpc_url, kernel))
    return jobs

if __name__ == "__main__":
    print("Start to submit")
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", "-k", help="kernel location", required=True)
    args = parser.parse_args()
    kernel = args.kernel
    jobs = submit_all_jobs_in_dir_list([job_dir+'/basic_job'], rpc_url, kernel)
    jobs_results = polling_lava_result(jobs)
    pipeline_is_fail = "fail" in jobs_results.values()
    if pipeline_is_fail:
        exit(1)
