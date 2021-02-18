import asyncio
from wxasync import WxAsyncApp

import gui
import config
from detector import Detector
from remotecmd import RemoteCmd, Action, RemoteQueue

gui.configuration = config.load("config/PsdSlowControlConfig.xml", schema="config/PsdSlowControlConfig.xsd")
gui.detector = Detector(gui.configuration)
remote_queue = None

class ChildWindow(gui.MainWindow):
    def poll_cb(self, cap:str, val:str):
        if cap in gui.hv_grid_coords:
            self.m_gridHV.SetCellValue(gui.hv_grid_coords[cap], val)

def _pollModule(self, moduleId):
    remote_queue.put_nowait( RemoteCmd(Action.POLL, moduleId, cb=self.poll_cb) )

def _OnPollTimer(self, event):
    self.pollModule(self.activeModuleId)

def _OnCheckBoxHVChange(self, event):
    action = Action.HV_ON if self.m_checkBoxHvOn.GetValue() > 0 else Action.HV_OFF
    remote_queue.put_nowait( RemoteCmd(action, self.activeModuleId) )

def _OnHVGridChange(self, event):
    cap = gui.capability_by_hv_grid_coords[(event.Row, event.Col)]
    new_val = self.m_gridHV.GetCellValue(event.Row, event.Col)
    if cap[2:] == 'REF_VOLTAGE':
        remote_queue.put_nowait( RemoteCmd(Action.SET_CH, self.activeModuleId, cap[:1], new_val) )

ChildWindow.pollModule = _pollModule
ChildWindow.OnCheckBoxHVChange = _OnCheckBoxHVChange
ChildWindow.OnPollTimer = _OnPollTimer
ChildWindow.OnHVGridChange = _OnHVGridChange

async def main():
    global remote_queue
    remote_queue = RemoteQueue()

    app = WxAsyncApp(False)
    frame = ChildWindow(None, 'HVsys GUI')
    await app.MainLoop()

asyncio.run(main())