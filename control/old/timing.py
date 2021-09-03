#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_d

Docs:
https://docs.python.org/3/library/asyncio.html
https://docs.python.org/3/library/asyncio-task.html
"""

import aioserial
import asyncio
import sys
import time

sys.path.append('.')
sys.path.append('lib/hvsys')
#x# import config2
#x# import hvsys
from hv_supply import HVsysSupply
from hv_led import HVsysLED
#x# import message

reader = None
writer = None
aioserial_instance = None

start = time.time()
last = start

async def recv():
    global last
    while True:
        print('recv')
        response = await reader.readline()
        #response = (await aioserial_instance.readline_async()).decode(errors='ignore').strip()
        print('response %s: %f : %d' % (response, time.time()-start, 1000*(time.time()-last)))
        

async def send():
    global last
    global aioserial_instance
    print('Explicit context to send')
    while True:
        await asyncio.sleep(1)
        last = time.time()
        print('send start: %f : %d' % (time.time() - start, 1000*(time.time()-last)) )
#        await aioserial_instance.write_async(b'r0000x\n')
#        aioserial_instance.flush()
#        await aioserial_instance.write_async(b'r6500x\n')
#        await aioserial_instance.write_async(b'r6500x\n')
#        writer.write(b'r6500x\n')
        writer.write(b'r0000x\n')
        writer.write(b'r0000x\n')
#        writer.write(b'r6500x\n')
#        writer.write(b'r6600x\n')
#        writer.write(b'r6600x\n')
#        writer.write(b'r6600x\n')

        print('  complete: %f : %d' % (time.time() - start, 1000*(time.time()-last)) )


async def main(address, port):
    global reader
    global writer
    global aioserial_instance

    try:
        reader, writer = await asyncio.open_connection(address, port)
        #aioserial_instance = aioserial.AioSerial(port='/dev/ttyr00', baudrate=57600, parity='N', stopbits=1)
        #aioserial_instance = aioserial.AioSerial(port='/dev/ttyUSB0', baudrate=57600, parity='N', stopbits=1)
    except OSError as e:
        print("Cannot connect to system module")  
        return
    task1 = asyncio.get_event_loop().create_task(send())
    task2 = asyncio.get_event_loop().create_task(recv())
    await task1
    await task2


if __name__ == '__main__':
    address = '192.168.69.204'
    port = 4001

    if len(sys.argv) > 1:
        address = sys.argv[1]
        if address == '0':
            address == '127.0.0.1'
        if len(sys.argv) > 2:
            port = int(sys.argv[2])

    try:
        asyncio.run(main(address, port))
    except KeyboardInterrupt:
        print('\nTerminated by Ctrl-C')
