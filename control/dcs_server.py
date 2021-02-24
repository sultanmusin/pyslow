from asyncio import create_task, sleep, start_server, run
from functools import partial
import sys
import logging

from config import load
from detector import Detector
sys.path.append('lib/hvsys')
from message import Message
sys.path.append('lib/workers')
from tcontrol import TmpControl
from vpoller import VolatPoller 
from remotecmd import RemoteCmd

# logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
cfg = load('config/PsdSlowControlConfig.xml', schema='config/PsdSlowControlConfig.xsd')
det = Detector(cfg)
polled_flags = {}
pedestal_flags = {}

def get_hv_part(mod_id:str):
    mod_cfg = cfg.modules[mod_id]
    return det.buses[mod_cfg.bus_id].getPart(mod_cfg.address('hv'))

for mod_id, mod_cfg in cfg.modules.items():
    if mod_cfg.online:
        pedestal_flags[mod_id] = False
        for cap in get_hv_part(mod_id).capabilities:
            polled_flags[f'{mod_id}_{cap}'] = False

def polling_cb(mod_id:str, part, cap:str, val:int):
    polled_flags[f'{mod_id}_{cap}'] = True

def set_pedestal_cb(mod_id:str, val:int):
    pedestal_flags[mod_id] = True

async def handle_connection(reader, writer):
    print('CLIENT CONNECTED')
    req = await reader.readline()
    while req:
        remote_cmd = RemoteCmd.parse(req)
        writer.write(await remote_cmd.do(det))

        req = await reader.readline()
    print('CLIENT DISCONNECTED')

async def main():
    # Подключиться к коробкам и запустить обработчики
    for sm in det.buses.values():
        await create_task(sm.connect())
        create_task(sm.send())
    
    # Опросить 'важные' регистры
    for mod_id, mod_cfg in cfg.modules.items():
        if mod_cfg.online:
            await det.poll_module_important(mod_id, partial(polling_cb, mod_id))
    while not all(flag == True for flag in polled_flags.values()):
        await sleep(1)
    print('IMPORTANT POLLED')
    
    # Выставить пьедесталы по конфигу
    for mod_id, mod_cfg in cfg.modules.items():
        if mod_cfg.online:
            sm = det.buses[mod_cfg.bus_id]
            hv_addr = mod_cfg.address('hv')
            hv_part = sm.getPart(hv_addr)

            val = hv_part.valueFromString('SET_PEDESTAL_VOLTAGE', mod_cfg.hvPedestal)
            msg = Message(Message.WRITE_SHORT, hv_addr, hv_part, 'SET_PEDESTAL_VOLTAGE', val)
            await sm.add_task(msg, hv_part, partial(set_pedestal_cb, mod_id))
    while not all(flag == True for flag in pedestal_flags.values()):
        await sleep(1)
    print('PEDESTALS SETTED')

    # Запустить TmpControl
    tmp_control = TmpControl(det)
    tmp_control.start()

    # Запустить VolatPoller
    volat_poller = VolatPoller(det)
    volat_poller.start()

    # Запустить сервер 
    server = await start_server(handle_connection, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

try:
    run(main())
except KeyboardInterrupt:
    pass