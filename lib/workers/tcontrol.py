import sys
from asyncio import sleep

from worker import Worker
sys.path.append('control')
from detector import Detector
sys.path.append('lib/hvsys')
from message import Message

class TmpControl(Worker):
    TIMEOUT = 10 #sec

    def __init__(self, det:Detector):
        super().__init__(det)
    
    async def set_ch_hv(self):
        while True:
            print('TEMPERATURE CORR...')
            
            for mod_id, mod_cfg in self.detector.config.modules.items():
                if mod_cfg.online:
                    sm = self.detector.buses[mod_cfg.bus_id]
                    hv_addr = mod_cfg.address('hv')
                    hv_part = sm.getPart(hv_addr)
                    
                    for ch, hv_str in mod_cfg.hv.items(): 
                        hv = hv_part.valueFromString(f'{ch}/SET_VOLTAGE', hv_str)
                        msg = Message(Message.WRITE_SHORT, hv_addr, hv_part, f'{ch}/SET_VOLTAGE', hv)
                        await sm.add_task(msg, hv_part, lambda new_val: None)

            await sleep(TmpControl.TIMEOUT)
    
    def start(self):
        super().start(self.set_ch_hv)