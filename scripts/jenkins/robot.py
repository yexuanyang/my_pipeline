import requests

rbot_reply_comment_url = 'http://10.161.28.28:30000/action/reply-comment'

def post_rbot(info: str, prNumber: int, originComment: int):
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
