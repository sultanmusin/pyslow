#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"


import asyncio
import logging
import os
import sys
import getopt

sys.path.append('.')
sys.path.append('control')
sys.path.append('lib/hvsys')
sys.path.append('../lib/hvsys')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply
from hvsysled import HVsysLED


configuration = None
detector = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def print_usage():
    print('Usage: mapper.py -c <configfile> [-b bus] -f <from_address> -t <to_address>')
    print('E.g. : mapper.py -c config.xml -f 0 -t 100\n')

    sys.exit()


def handler(loop, context):
    print(context)


def on_complete(value):
    print('Response = %d (0x%04x)'%(value, value))
    device = HVsys.find_device_by_cell_id(value)
    print("FOUND!\n")
    print(device.DESCRIPTION if device is not None else 'na61ps10c')


async def main(argv):
    opts, args = getopt.getopt(argv,"hc:b:f:t:",["config=","bus=","from=","to="])

    bus_id = None
    address = None
    config_file = '../config/MapperConfig.xml'
    config_file = 'config/MapperConfig.xml'
    from_address = 0
    to_address = 255

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
        elif opt in ("-b", "--bus"):
            bus_id = arg
        elif opt in ("-c", "--config"):
            config_file = arg
        elif opt in ("-f", "--from"):
            from_address = int(arg, 0)
        elif opt in ("-t", "--to"):
            to_address = int(arg, 0)

    print('Config file path =', config_file)

    if config_file is None and bus_id is not None:
        print_usage()

    configuration = config.load(config_file)
    detector = Detector(configuration)

    if bus_id is None and len(detector.buses) == 1:
        bus_id = list(detector.buses)[0]
        print("Selecting the bus from configuration = %s"%(bus_id))
    else:
        print("Bus =", bus_id)

    if bus_id is None:
        print_usage()

    bus = detector.buses[bus_id]
 #   part = bus.getPart(address)

 #   print('Address =', address)
 #   print('Part =', part.DESCRIPTION)
 
    # ask for reg 0 (cell id)
    register = 0

    print('Register =', register)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)

    try:
        await loop.create_task(bus.connect())
        loop.create_task(bus.send())
    except OSError as e:
        print("Cannot connect to system module")  
        sys.exit()

    print("Module link ok")

    for address in range(from_address, to_address+1):
        command = Message(Message.READ_SHORT, address, HVsysLED(None), 'CELL_ID', 0)

        print("Request: %s"%(str(command).rstrip()))
        loop.create_task(detector.add_task(bus_id, command, HVsysLED(None), on_complete))

    await asyncio.sleep(10)

if __name__ == '__main__':
    #asyncio.run(main(), debug=True)
    print("Staring main loop...")
    try: 
        logging.info("Go!")
        asyncio.get_event_loop().run_until_complete(asyncio.wait([main(sys.argv[1:])]))
    except asyncio.TimeoutError as e:
        logging.warning("Timeout.")
