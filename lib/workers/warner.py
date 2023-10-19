import time
import threading

import requests


WARNING_SERVERS = ['http://127.0.0.1:9009/warning',
                   'http://192.168.69.1:9009']


def send_message(params: dict[str,str]):
    for server in WARNING_SERVERS:
        print(server)
        try:
            r = requests.get(server, params=params, timeout=5)
        except:
            print(f'Cannot connect to the {server}')


def warn(msg: str):
    current_time = time.ctime(time.time())
    data = {
        'MSG': f'{current_time}: {msg}'
    }
    th = threading.Thread(target=send_message, args=(data,))
    th.start()
