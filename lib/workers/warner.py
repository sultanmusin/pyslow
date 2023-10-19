import requests
import time


WARNING_SERVERS = ['http://127.0.0.1:9009/warning',
                   'http://192.168.69.1:9009']


def warn(msg: str):
    current_time = time.ctime(time.time())
    data = {
        'MSG': f'{current_time}: {msg}'
    }
    print(msg)
    for server in WARNING_SERVERS:
        r = requests.get(server, params=data)
