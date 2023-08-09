import requests

WARNING_SERVERS = ['http://127.0.0.1:9009/warning']


def warn(msg: str):
    data = {
        'MSG': msg
    }
    for server in WARNING_SERVERS:
        r = requests.get(server, params=data)
