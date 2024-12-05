import base64
import requests
import json
import sys

def stop_build(pr_number: int, build_id: int):
    # 要编码的字符串
    credentials = "yyx:11cda8db826dcba7cb9adb579e50738f75"

    # 使用base64进行编码
    base64Credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    url = "http://10.161.28.28:8989/crumbIssuer/api/json"

    # 构建headers，添加Authorization头部
    headers = {
        'Authorization': f'Basic {base64Credentials}'
    }

    # 发送POST请求
    response = requests.post(url, headers=headers)

    res_dict = json.loads(response.text)

    crumb = res_dict.get("crumb", "")

    form_data = {
        "Submit" : "",
        "Jenkins-Crumb" : crumb,
    }

    # 这里只需要删除PR的正确性测试就可以了, 对于其他分支上的可以不删除
    # stop_url = "http://10.161.28.28:8989/job/build_rros/job/PR-{}/{}/stop".format(build_id)
    stop_url = "http://10.161.28.28:8989/job/build_rros/job/PR-{}/{}/stop".format(pr_number, build_id-1)
    print(f"stop PR-{pr_number}, build_id: {build_id - 1}")

    response = requests.post(stop_url, headers=headers, data=form_data)

if __name__ == "__main__":
    stop_build(*map(int, sys.argv[1:]))
