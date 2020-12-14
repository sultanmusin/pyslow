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
sys.path.append('lib/hvsys')
sys.path.append('../lib/hvsys')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply


configuration = None
detector = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

def print_usage():
    print('Usage: poller.py -c <configfile> [-b bus] -a <address> -r <register>')
    print('E.g. : poller.py -c config.xml -a 102 -r 24\n')
    print('Specify parameters as decimal or start with 0x for hex:')
    print('       poller.py -c config.xml -a 0x66 -r 0x18\n')
    print('To see the register list without polling: ')
    print('       poller.py -c <configfile> [-b bus] -a <address> -l')
    sys.exit()

def handler(loop, context):
    print(context)

def on_complete(value):
    print('Response = %d (0x%04x)'%(value, value))

async def main(argv):
    opts, args = getopt.getopt(argv,"hb:c:a:r:l",["bus=","config=","address=","register=","list"])

    bus_id = None
    address = None
    config_file = None
    register = None
    print_list = None

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
        elif opt in ("-b", "--bus"):
            bus_id = arg
        elif opt in ("-a", "--address"):
            address = int(arg, 0)
        elif opt in ("-c", "--config"):
            config_file = arg
        elif opt in ("-r", "--register"):
            register = arg
        elif opt in ("-l", "--list"):
            print_list = True

    print('Config file path =', config_file)

    if config_file is None:
        print_usage()

    configuration = config.load(config_file)
    detector = Detector(configuration)

    if bus_id is None and len(detector.buses) == 1:
        bus_id = list(detector.buses)[0]
        print("Selecting the bus from configuration = %s"%(bus_id))
    else:
        print("Bus =", bus_id)

    if bus_id is None or address is None:
        print_usage()

    bus = detector.buses[bus_id]
    part = bus.getPart(address)

    print('Address =', address)
    print('Part =', part.DESCRIPTION)
 
    if print_list:
        print(part.capabilities)
        sys.exit()

    caps = []

    if register is None:
        caps = list(part.capabilities.keys())
    elif register in part.capabilities:
        caps = register
    else:
        try: 
            register = int(register, 0)
            caps = [part.capabilities_by_subaddress[register]]
        except ValueError:
            print('Invalid register request, use int or capability name: %s'%(register))
            print('Available capabilities: ', part.capabilities)
            sys.exit(0)
        except IndexError:
            print('No such register in %s: %s'%(part.DESCRIPTION, register))
            sys.exit(0)


    print('Register =', register)
    print('Capabilities =', caps)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)

    try:
        await asyncio.create_task(bus.connect(), name="Connect to system module")
        asyncio.create_task(bus.send(), name="System module sending loop")
    except OSError as e:
        print("Cannot connect to system module")  
        sys.exit()

    print("Module link ok")

    for cap in caps:
        command = Message(Message.READ_SHORT, address, part, cap, 0)
        print("Request: %s"%(str(command).rstrip()))
        asyncio.create_task(detector.add_task(bus_id, command, part, on_complete))

    await asyncio.sleep(2)



if __name__ == "__main__":
   asyncio.run(main(sys.argv[1:]))
