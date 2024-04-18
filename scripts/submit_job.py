# Python3
import yaml
import xmlrpc.client

path = '/root/my_pipeline/tests/basic.yaml'

with open(path) as f:
    config = yaml.dump(yaml.load(f, yaml.FullLoader))
    server=xmlrpc.client.ServerProxy("http://admin:longrandomtokenadmin@10.161.28.28:9999/RPC2/")
    jobid=server.scheduler.submit_job(config)
