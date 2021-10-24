"""   Модуль содержит компоненты, необходимые для общения между dcs-клиентом и dcs-сервером


Пример клиента:

    async def main():
        // Создаёт очередь, устанавливает соединение с сервером, запускает обработку очереди
        remote_queue = RemoteQueue()    
        
        // Добавить команду опроса 22-го модуля 
        cmd = RemoteCmd(Action.POLL, '22', lambda cap, val: print(f'{cap}: {val}'))
        remote_queue.put_nowait(cmd)

        // Ожидать
        await remote_queue.task
    
    asyncio.run(main())


Пример сервера:

    detector = ...

    async def handle_connection(reader, writer):
        req = await reader.readline()

        while req:
            cmd = RemoteCmd.parse(req)
            writer.write( await cmd.do(detector) )
            req = await reader.readline()
    
    async def main():
        server = await start_server(handle_connection, '127.0.0.1', 8888)
        async with server:
            await server.serve_forever()

    asyncio.run(main())
"""

from __future__ import annotations
from typing import Callable
from enum import Enum
import pickle
import ast
from asyncio import Queue, open_connection, sleep, create_task
import sys

from detector import Detector
sys.path.append('lib/hvsys')
from message import Message



class ModuleAssets:
    def __init__(self, det:Detector, mod_id:str):
        self.mod_cfg = det.config.modules[mod_id]
        self.sm = det.buses[self.mod_cfg.bus_id]
        self.hv_addr = self.mod_cfg.address('hv')
        self.hv_part = self.sm.getPart(self.hv_addr)
        self.hv_state = self.hv_part.state
    
    async def submitAction(self, cap:str, new_val_str:str):
        new_val = self.hv_part.valueFromString(cap, new_val_str)
        msg = Message(Message.WRITE_SHORT, self.hv_addr, self.hv_part, cap, new_val)
        await self.sm.add_task(msg, self.hv_part, lambda new_val: None)




class Action(Enum):
    """ Действия, выполняемые на сервере. Результат: сериализованный словарь пар ('имя регистра', 'значение')
    """
    @staticmethod
    async def poll(assets:ModuleAssets, cmd:RemoteCmd) -> str:
        state = assets.hv_state
        res = dict([(k, assets.hv_part.valueToString(k, v)) for k, v in state.items()])
        return str(res)
    
    @staticmethod
    async def set_ped(assets:ModuleAssets, cmd:RemoteCmd) -> str:
        assets.mod_cfg.hv_pedestal = cmd.val
        await assets.submitAction('SET_PEDESTAL_VOLTAGE', cmd.val)
        return '{}'
    
    @staticmethod
    async def set_ch(assets:ModuleAssets, cmd:RemoteCmd) -> str:
        assets.mod_cfg.hv[cmd.ch] = cmd.val
        await assets.submitAction(f'{cmd.ch}/SET_VOLTAGE', cmd.val)
        return '{}'
    
    @staticmethod
    async def hv_on(assets:ModuleAssets, cmd:RemoteCmd) -> str:
        await assets.submitAction('STATUS', str(assets.hv_part.POWER_ON))
        return '{}'
    
    @staticmethod
    async def hv_off(assets:ModuleAssets, cmd:RemoteCmd) -> str:
        await assets.submitAction('STATUS', str(assets.hv_part.POWER_OFF))
        return '{}'
    
    POLL = poll
    SET_PED = set_ped
    SET_CH = set_ch
    HV_ON = hv_on
    HV_OFF = hv_off





class RemoteCmd:
    """ Сериализуемый/десериализуемый объект, хранящий :
        1) тип действия, которое хотим выполнить на сервере
        2) детали, необходимые для выполнения
        3) колл-бэк, вызываемый после ответа сервера
    """
    def __init__(self, action:Action, mod_id:str, ch:str='', val:str='', cb:Callable[[str,str],None]=lambda cap, val: None):
        self.action = action
        self.mod_id = mod_id
        self.ch = ch
        self.val = val
        self.cb = cb
    
    async def do(self, det:Detector) -> bytes:
        """ Выполнить действие, вернуть результат в виде байтовой строки, которую можно переслать клиенту
        """
        res = await self.action(ModuleAssets(det, self.mod_id), self)
        print(f'{self.action}')
        return res.encode() + b'\n'
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['cb']
        return state
    
    def dump(self) -> bytes:
        """ Сериализовать в байтовую строку
        """
        return pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL) + b'\n'
    
    @staticmethod
    def parse(data:bytes) -> RemoteCmd:
        """ Десериализовать из байтовой строки
        """
        return pickle.loads(data)




class RemoteQueue(Queue):
    """ Очередь для отправки RemoteCmd команд
    """
    SIZE = 10

    def __init__(self, proxy_ip:str='127.0.0.1', proxy_port:int=8888):
        super().__init__(RemoteQueue.SIZE)
        self.task = create_task( self.run(proxy_ip, proxy_port) )
    
    async def run(self, proxy_ip, proxy_port):
        reader, writer = await open_connection(proxy_ip, proxy_port)
        
        while True:
            if self.empty():
                await sleep(1)
            else:
                cmd = await self.get()
                writer.write(cmd.dump())
                resp = await reader.readline()
                for cap, val in ast.literal_eval(resp.decode()).items():
                    cmd.cb(cap, val)
                