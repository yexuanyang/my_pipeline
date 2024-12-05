import xmlrpc.client
import sys
import os
import time
import requests
from lxml import html
from robot import post_rbot

lava_rpc_url = 'http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/'
server = xmlrpc.client.ServerProxy(lava_rpc_url)
job_id_dir_path = "/lava_jobs/rros/{}"

def scrape_data(url, xpath):
    try:
        # 获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 使用 lxml.html 解析 HTML 内容
        tree = html.fromstring(response.content)

        # 使用 XPath 提取所需的元素
        elements = tree.xpath(xpath)
        
        # 提取元素内容并返回
        data = [element.text_content() for element in elements]
        return data
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"Parse error: {e}")

def has_fail(job_id: str):
    # 示例URL和XPath
    url = "http://10.161.28.28:9999/results/{}".format(job_id)
    xpath = '//*[@id="table"]/tbody/tr/td[6]'
    extracted_data = scrape_data(url, xpath)
    fail_number = 0

    if extracted_data:
        for item in extracted_data:
            fail_number += int(item)
            print("has_fail: fail_item {}".format(item))
    else:
        print("Access {} with {} error, content is not found".format(url, xpath))
    return fail_number != 0

def polling_lava_result(jobs: list) -> dict:
    jobs_results = {}
    jobs_set = {id for id in jobs}
    while len(jobs_set) != 0:
        time.sleep(10)
        next_set = jobs_set.copy()
        for id in jobs_set:
            state = server.scheduler.job_state(id)['job_state']
            health = server.scheduler.job_health(id)['job_health']

            if health == 'Complete' and not has_fail(id):
                # `result` type is `str`
                result = server.scheduler.job_output(id).data.decode('utf-8')
                jobs_results[id] = result
            elif state == 'Finished':
                jobs_results[id] = 'fail'
            
            if state == "Finished":
                next_set.remove(id)
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
