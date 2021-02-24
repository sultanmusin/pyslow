import sys
from asyncio import sleep

from worker import Worker
sys.path.append('control')
from detector import Detector
sys.path.append('lib/hvsys')
from message import Message

class VolatPoller(Worker):
    TIMEOUT = 10 #sec

    def __init__(self, det:Detector):
        super().__init__(det)
    
    async def poll(self):
        while True:
            print('VOLATILE POLLING...')
            
            for mod_id, mod_cfg in self.detector.config.modules.items():
                if mod_cfg.online:
                    sm = self.detector.buses[mod_cfg.bus_id]
                    hv_addr = mod_cfg.address('hv')
                    hv_part = sm.getPart(hv_addr)
                    
                    for cap in hv_part.volatile: 
                        msg = Message(Message.READ_SHORT, hv_addr, hv_part, cap, 0)
                        await sm.add_task(msg, hv_part, lambda new_val: None)

            await sleep(VolatPoller.TIMEOUT)
    
    def start(self):
        super().start(self.poll)