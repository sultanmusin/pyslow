#!/usr/bin/env python3

"""emu.py: Emulate network presence of hvsys device(s)"""

__author__      = "Oleg Petukhov, INR RAS"
__copyright__   = "2020"
__email__       = "opetukhov@inr.ru"



import asyncio
import json
#import socket
from time import sleep



HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 4001         # Port to listen on (non-privileged ports are > 1023)
SAVEFILE = "device_state.json"
device_state = {}



def load_device_state(filename: str) -> dict:
    try:
        f = open(filename,"r")
        return json.load(f)
    except FileNotFoundError:
        print("Cannot read saved device state from %r" % filename)
        return {}

 
def save_device_state(filename: str, state: dict):
    print(state)
    data = json.dumps(state, indent=4, sort_keys=True)
    f = open(filename,"w")
    f.write(data)
    f.close()



def process_register_read(device_id, offset):
    print("process reg read ( %r, %r )" % (device_id, offset))
    global device_state

    resp = '0000_\n'

    if device_id not in device_state:
        resp = '0000_\n'
    elif offset not in device_state[device_id]:
        resp = '0000_\n'
    else:
        resp = '%s_\n' % device_state[device_id][offset]
    
    return resp.encode()


def process_register_write(device_id, offset, value):
    print("process reg write ( %r, %r, %r )" % (device_id, offset, value))

    if '' in (device_id, offset, value):
        print("Bad command or file name")
        return

    if device_id not in device_state:
        device_state[device_id] = {}

    device_state[device_id][offset] = value   

    # save_device_state(SAVEFILE, device_state)
     
    resp = '%s_\n' % device_state[device_id][offset]
    
    return resp.encode()



def process_command(cmd: str):
    if len(cmd) > 0 and cmd[0] == 'r':
        return process_register_read(cmd[1:3], cmd[3:5])
    elif len(cmd) > 0 and cmd[0] == 'w':
        return process_register_write(cmd[1:3], cmd[3:5], cmd[5:9])
    else:
        print("Bad command: %r", cmd)
        return b'0000_\n'   # wish this helps



async def handle_message(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))
    #print(type(message))
    resp = process_command(message)

    #resp = b"0000_\n"
    print("Send: %r" % resp)
    sleep(0.01)
    writer.write(resp)
    await writer.drain()

    #print("Close the client socket")


device_state = load_device_state(SAVEFILE)
loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_message, HOST, PORT, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

save_device_state(SAVEFILE, device_state)
