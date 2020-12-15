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
import string
import sys
import wx
import wx.richtext
from wxasync import WxAsyncApp

sys.path.append('.')
sys.path.append('lib/hvsys')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply


configuration = None
detector = None


class CharValidator(wx.PyValidator):
    ''' Validates data as it is entered into the text controls. '''

    #----------------------------------------------------------------------
    def __init__(self, flag):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    #----------------------------------------------------------------------
    def Clone(self):
        '''Required Validator method'''
        return CharValidator(self.flag)

    #----------------------------------------------------------------------
    def Validate(self, win):
        return True

    #----------------------------------------------------------------------
    def TransferToWindow(self):
        return True

    #----------------------------------------------------------------------
    def TransferFromWindow(self):
        return True

    #----------------------------------------------------------------------
    def OnChar(self, event):
        keycode = int(event.GetKeyCode())
        controls = [wx.WXK_BACK, wx.WXK_TAB, wx.WXK_RETURN, wx.WXK_TAB]
        if keycode < 256:
            #print keycode
            key = chr(keycode)
            if keycode in controls: 
                return
            #print key
            if self.flag == 'no-alpha' and key in string.ascii_letters:
                return
            if self.flag == 'no-digit' and key in string.digits:
                return
            if self.flag == 'float' and key not in string.digits + '.':
                return
        event.Skip()
        
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname=''

        global configuration
        self.config = configuration


        wx.Frame.__init__(self, parent, title=title, size=(1500,1000))
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        self.CreateMenu()
        self.CreateLayout()
        self.Show()

        # select first online module (if any...)
        self.SelectFirstOnlineModule()

    def CreateLayout(self):

        self.moduleListTitle = wx.StaticBox(self, -1, "Modules")
        self.moduleListBox = wx.ListBox(self, choices=self.config.modulesOrderedById, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.OnSelectModuleFromList, self.moduleListBox)
        self.moduleListBox.SetSelection(0)
        
        self.miniGridSizer = wx.FlexGridSizer(self.config.geom_height, self.config.geom_width, 3, 3)

        self.moduleMiniButtons = {}
        for m in self.config.modulesOrderedByGeometry:
            if len(m) > 0:
                self.moduleMiniButtons[m] = wx.Button(self, -1, m, size=(36,40), style=wx.BU_EXACTFIT)
                self.moduleMiniButtons[m].myname = m
                if self.config.modules[m].online:
                    self.Bind(wx.EVT_BUTTON, self.OnSelectModuleFromGrid, self.moduleMiniButtons[m])
                    self.moduleMiniButtons[m].SetBackgroundColour((255, 255, 0))
                self.miniGridSizer.Add(self.moduleMiniButtons[m])
            else:
                self.miniGridSizer.Add(wx.StaticText(self, -1, ""))

        self.leftPaneSizer = wx.BoxSizer(wx.VERTICAL)
        self.leftPaneSizer.Add(self.moduleListTitle, 0, wx.EXPAND)
        self.leftPaneSizer.Add(self.moduleListBox, 1, wx.EXPAND)
        self.leftPaneSizer.Add(self.miniGridSizer, 0, wx.EXPAND)

        self.N_SECTIONS = 10

        self.hvControls = {}
        self.ledControls = {}

        self.gridSizer = wx.FlexGridSizer(self.N_SECTIONS+7, 5, 4, 4)
        self.gridSizer.Add(wx.StaticText(self, -1, "  Section"))
        self.gridSizer.Add(wx.StaticText(self, -1, "Set "))
        self.gridSizer.Add(wx.StaticText(self, -1, "Meas "))
        self.gridSizer.Add(wx.StaticText(self, -1, "Ref "))
        self.gridSizer.Add(wx.StaticText(self, -1, "Error"))
        for row in range(1,self.N_SECTIONS+1):
            self.gridSizer.Add(wx.StaticText(self, -1, "  "+str(row)))
            self.hvControls['%d/SET_VOLTAGE'%row] = wx.TextCtrl(self, -1, "0.0")#, validator=CharValidator('float'))
            self.gridSizer.Add(self.hvControls['%d/SET_VOLTAGE'%row])
            self.hvControls['%d/SET_VOLTAGE'%row].myname = '%d/SET_VOLTAGE'%row
            self.hvControls['%d/SET_VOLTAGE'%row].Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            self.hvControls['%d/MEAS_VOLTAGE'%row] = wx.TextCtrl(self, -1, "0.0")
            self.gridSizer.Add(self.hvControls['%d/MEAS_VOLTAGE'%row])
            self.hvControls['%d/REF_VOLTAGE'%row] = wx.TextCtrl(self, -1, "0.0")
            self.gridSizer.Add(self.hvControls['%d/REF_VOLTAGE'%row])
            self.hvControls['%d/ERROR'%row] = wx.TextCtrl(self, -1, "OK")
            self.gridSizer.Add(self.hvControls['%d/ERROR'%row])

        self.gridSizer.Add(wx.StaticText(self, -1, "  Pedestal"))
        self.hvControls['SET_PEDESTAL_VOLTAGE'] = wx.TextCtrl(self, -1, "0.0")
        self.gridSizer.Add(self.hvControls['SET_PEDESTAL_VOLTAGE'])
        self.hvControls['MEAS_PEDESTAL_VOLTAGE'] = wx.TextCtrl(self, -1, "0.0")
        self.gridSizer.Add(self.hvControls['MEAS_PEDESTAL_VOLTAGE'])
        self.hvControls['REF_PEDESTAL_VOLTAGE'] = wx.TextCtrl(self, -1, "0.0")
        self.gridSizer.Add(self.hvControls['REF_PEDESTAL_VOLTAGE'])
        self.gridSizer.Add(wx.StaticText(self, -1, ""))

        self.gridSizer.Add(wx.StaticText(self, -1, ""))
        self.hvControls['HV_ON'] = wx.Button(self, -1, "HV ON")
        self.gridSizer.Add(self.hvControls['HV_ON'])
        self.Bind(wx.EVT_BUTTON, self.OnSwitchOnHV, self.hvControls['HV_ON'])
        self.hvControls['HV_OFF'] = wx.Button(self, -1, "HV OFF")
        self.gridSizer.Add(self.hvControls['HV_OFF'])
        self.Bind(wx.EVT_BUTTON, self.OnSwitchOffHV, self.hvControls['HV_OFF'])
        self.gridSizer.Add(wx.StaticText(self, -1, ""))
        self.gridSizer.Add(wx.StaticText(self, -1, ""))

        self.gridSizer.Add(wx.StaticText(self, -1, "  LED Frequency"))
        self.ledControls['SET_FREQUENCY'] = wx.TextCtrl(self, -1, "0")
        self.gridSizer.Add(self.ledControls['SET_FREQUENCY'])
        self.ledControls['MEAS_FREQUENCY'] = wx.TextCtrl(self, -1, "0")
        self.gridSizer.Add(self.ledControls['MEAS_FREQUENCY'])
        self.ledControls['REF_FREQUENCY'] = wx.TextCtrl(self, -1, "100")
        self.gridSizer.Add(self.ledControls['REF_FREQUENCY'])
        self.gridSizer.Add(wx.StaticText(self, -1, ""))

        self.gridSizer.Add(wx.StaticText(self, -1, "  LED Amplitude"))
        self.ledControls['SET_AMPLITUDE'] = wx.TextCtrl(self, -1, "0")
        self.gridSizer.Add(self.ledControls['SET_AMPLITUDE'])
        self.ledControls['MEAS_AMPLITUDE'] = wx.TextCtrl(self, -1, "0")
        self.gridSizer.Add(self.ledControls['MEAS_AMPLITUDE'])
        self.ledControls['REF_AMPLITUDE'] = wx.TextCtrl(self, -1, "1000")
        self.gridSizer.Add(self.ledControls['REF_AMPLITUDE'])
        self.gridSizer.Add(wx.StaticText(self, -1, ""))

        self.controlSizer = wx.BoxSizer(wx.VERTICAL)
        self.controlLabel = wx.StaticBox(self, -1, "Control")
        self.controlSizer.Add(self.controlLabel, 0, wx.EXPAND)
        self.controlSizer.Add(self.gridSizer, 1, wx.EXPAND)

        self.debugLineSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.debugLineSizer.Add(wx.StaticText(self, -1, "Part:"), 0, wx.EXPAND)
        self.modulePartsBox = wx.Choice(self, -1, choices=["loading..."])
        self.Bind(wx.EVT_CHOICE, self.OnChoosePart, self.modulePartsBox)
        self.debugLineSizer.Add(self.modulePartsBox, 0, wx.EXPAND)

        self.debugLineSizer.Add(wx.StaticText(self, -1, "Capability:"), 0, wx.EXPAND)
        self.moduleCapabilitiesBox = wx.Choice(self, -1, choices=[])
        self.Bind(wx.EVT_CHOICE, self.OnChooseCapability, self.moduleCapabilitiesBox)
        self.debugLineSizer.Add(self.moduleCapabilitiesBox, 0, wx.EXPAND)

        self.SelectFirstOnlineModule()
        self.modulePartsBox.Select(0)   # now as we have second dropdown created we can use it
        self.OnChoosePart(None)

        self.buttonRead = wx.Button(self, -1, "Read")
        self.debugLineSizer.Add(self.buttonRead, 0, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnRead, self.buttonRead)

        self.buttonWrite = wx.Button(self, -1, "Write")
        self.debugLineSizer.Add(self.buttonWrite, 0, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.OnWrite, self.buttonWrite)

        self.debugLineSizer.Add(wx.StaticText(self, -1, "Command:"), 0, wx.EXPAND)
        self.commandText = wx.TextCtrl(self, -1, "...")
        self.debugLineSizer.Add(self.commandText, 1, wx.EXPAND)
        self.debugLineSizer.Add(wx.StaticText(self, -1, "Response:"), 0, wx.EXPAND)
        self.responseText = wx.TextCtrl(self, -1, "0")
        self.debugLineSizer.Add(self.responseText, 1, wx.EXPAND)
        self.debugLineSizer.Add(wx.StaticText(self, -1, "Value:"), 0, wx.EXPAND)
        self.valueText = wx.TextCtrl(self, -1, "0")
        self.debugLineSizer.Add(self.valueText, 1, wx.EXPAND)

        self.debugSizer = wx.BoxSizer(wx.VERTICAL)
        self.sb = wx.StaticBox(self, -1, "Debug")
        self.debugSizer.Add(self.sb, 1, wx.EXPAND)
        self.debugSizer.Add(self.debugLineSizer, 1, wx.EXPAND)
        #self.debugSizer.Add(self.btn4, 1, wx.EXPAND)

        self.rightPaneSizer = wx.BoxSizer(wx.VERTICAL)
        self.rightPaneSizer.Add(self.controlSizer, 1, wx.EXPAND)
        self.rightPaneSizer.Add(self.debugSizer, 0, wx.EXPAND)

        # Use some sizers to see layout options
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(self.leftPaneSizer, 0, wx.EXPAND)
        self.mainSizer.Add(self.rightPaneSizer, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.mainSizer)


    def SelectFirstOnlineModule(self):
        for m in self.config.modules.values():
            if m.online:
                self.SelectModule(m.id)
                break



    def CreateMenu(self):
        # Setting up the menu.
        filemenu= wx.Menu()
        helpmenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open configuration"," Open configuration file")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save configuration"," Save configuration file")
        menuPreferences = filemenu.Append(wx.ID_PREFERENCES, "&Preferences"," Open application preferences")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuAbout= helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the "helpmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Events
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnPreferences, menuPreferences)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)



    def OnChoosePart(self,e):
        part = self.modulePartsBox.GetStringSelection() # [self.moduleListBox.GetSelection()]
        print("OnChoosePart: %s" % part)

        part_type = HVsys.catalogus[part] # HVsysLED or HVsysModule
        capabilities = part_type.capabilities

        self.moduleCapabilitiesBox.Clear()
        for index, (capability, address) in enumerate(capabilities.items()):
            self.moduleCapabilitiesBox.Append(capability)
            self.moduleCapabilitiesBox.SetClientData(index, address)



    def OnChooseCapability(self,e):
        capability = self.moduleCapabilitiesBox.GetStringSelection() 
        index = self.moduleCapabilitiesBox.GetSelection()
        data = self.moduleCapabilitiesBox.GetClientData(index)
        print("OnChooseCapability: %s, %s" % (capability, data))



    def GetActivePartAddress(self):
        part = self.modulePartsBox.GetStringSelection() # [self.moduleListBox.GetSelection()]
        return self.config.modules[self.activeModuleId].address(part)



    def GetActivePartType(self):
        part = self.modulePartsBox.GetStringSelection() # [self.moduleListBox.GetSelection()]
        if part in HVsys.catalogus:
            return HVsys.catalogus[part]
        else:
            print("Unknown module part to interact with")
        


    def OnRead(self,e):
        global detector

        part_address = self.GetActivePartAddress()
        part_type = self.GetActivePartType()

        if part_address is None:
            print("No part address, cannot send cmd")
        else:
            command = Message(Message.READ_SHORT, part_address, part_type, self.moduleCapabilitiesBox.GetStringSelection(), 0)
            self.commandText.SetValue(str(command).rstrip())

            # find out which system module interacts with active module
            bus_id = self.config.modules[self.activeModuleId].bus_id
            part = detector.buses[bus_id].getPart(part_address) 
            asyncio.create_task(detector.add_task(bus_id, command, part, self.ShowQueryResult))



    def ShowQueryResult(self, data):
        self.responseText.SetValue(data.rstrip().decode('utf-8'))
        self.valueText.SetValue(str(int(data[0:4], 16)))



    def OnWrite(self,e):
        global detector

        part_address = self.GetActivePartAddress()
        part_type = self.GetActivePartType()

        value = int(self.valueText.GetValue())

        command = Message(Message.WRITE_SHORT, part_address, part_type, self.moduleCapabilitiesBox.GetStringSelection(), value)
        self.commandText.SetValue(command.rstrip())

        # TODO send (danger danger)


    def SwitchHV(self,state):
        global detector

        moduleId = self.activeModuleId
        moduleConfig = self.config.modules[moduleId]
        
        if moduleConfig.has('hv'): 
            bus_id = self.config.modules[self.activeModuleId].bus_id
            part_address = int(self.config.modules[self.activeModuleId].address('hv'))
            part = detector.buses[bus_id].getPart(part_address) 
            command = Message(Message.WRITE_SHORT, part_address, part, 'STATUS', state)
            logging.warning('HV switching!')
            asyncio.create_task(detector.add_task(bus_id, command, part, print))
        else:
            logging.warning('HV ON requested for module without HV part')

    def OnSwitchOnHV(self, e):
        self.SwitchHV(HVsysSupply.POWER_ON)

    def OnSwitchOffHV(self, e):
        self.SwitchHV(HVsysSupply.POWER_OFF)


    def OnSelectModuleFromGrid(self,e):
        theButton = e.GetEventObject()
        moduleId = theButton.myname
        print("OnSelectModule: %s" % moduleId)
        self.SelectModule(moduleId)
        
    def getPartNameByCap(self, cap:str):
        part_name = None
        if cap in self.hvControls:
            part_name = 'hv'
        elif cap in self.ledControls:
            part_name = 'led'
        else:
            raise ValueError('getPartNameByCap: unknown cap '+cap)


    def OnKillFocus(self,e):
        field = e.GetEventObject()
        cap = field.myname
        value = self.hvControls[cap].GetValue()
        print("OnKillFocus: requested %s = %s" % (cap, value))

        bus_id = self.config.modules[self.activeModuleId].bus_id
        part_name = self.getPartNameByCap(cap)
        part_address = int(self.config.modules[self.activeModuleId].address(part_name))
        part = detector.buses[bus_id].getPart(part_address) 
        command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
        logging.warning('HV switching!')
        asyncio.create_task(detector.add_task(bus_id, command, part, print))

        


    def OnSelectModuleFromList(self,e):
        moduleId = self.config.modulesOrderedById[self.moduleListBox.GetSelection()]
        print("OnSelectModuleFromList: %s" % moduleId)
        if self.config.modules[moduleId].online:
            self.SelectModule(moduleId)
        else:
            listIndex = self.config.modulesOrderedById.index(self.activeModuleId)
            self.moduleListBox.Select(listIndex)
        

    def SelectModule(self, moduleId):
        print("SelectModule: %s" % (moduleId))

        self.activeModuleId = moduleId

        listIndex = self.config.modulesOrderedById.index(moduleId)
        self.moduleListBox.Select(listIndex)

        for button in self.moduleMiniButtons.values():
            if button.myname == moduleId: 
                button.SetFont(wx.Font(wx.FontInfo(12).Bold()))
            else:
                button.SetFont(wx.Font(wx.FontInfo(12)))

        activeModule = self.config.modules[moduleId]
        partsText = ', '.join(
            ["%s=%d" % (p, activeModule.address(p)) for p in activeModule.parts]
        )
        self.controlLabel.SetLabelText("Module %s [%s]" % (activeModule.id, partsText))

        moduleConfig = self.config.modules[moduleId]

        for field in self.hvControls:
            self.hvControls[field].Enable(moduleConfig.has('hv'))   # enable or disable depending on whether this module has the HV part
        
        if moduleConfig.has('hv'): 
            pass #TODO
                
        if field in self.ledControls:
            self.ledControls[field].Enable(moduleConfig.has('led'))   # enable or disable depending on whether this module has the LED part

        if moduleConfig.has('led'): 
            pass #TODO

        #self.textLedFrequencyRef.SetValue(str(moduleConfig.ledFrequency))

        self.modulePartsBox.Clear() #AAA
        for part in moduleConfig.parts:
            self.modulePartsBox.Append(part)
            #self.modulePartsBox.SetClientData(index, address)

        self.pollModule(moduleId)


    def pollModule(self, moduleId):
        moduleConfig = self.config.modules[moduleId]
#        for part in moduleConfig.parts:
        asyncio.create_task(detector.poll_module_important(moduleId, self.DisplayValueOnComplete), name="poll_module_important")

    def DisplayValueOnComplete(self, part, capability, value):
        
        print("DisplayValueOnComplete: %s=%s"%(capability, value))
        if capability in self.hvControls: 
            str_value = part.valueToString(capability, value)
            self.hvControls[capability].SetValue(str_value)

    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, "FHcal DCS\n\nINR RAS, 2020\nOleg Petukhov", "About DCS", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.



    def OnSave(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

    def OnPreferences(self,e):
        prefFrame = PreferencesWindow(None, "Preferences")
        prefFrame.ShowModal() # Shows it
        prefFrame.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    def OnOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()

class PreferencesWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname=''

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(200,-1))

        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []
        for i in range(0, 6):
            self.buttons.append(wx.Button(self, -1, "Button &"+str(i)))
            self.sizer2.Add(self.buttons[i], 1, wx.EXPAND)

        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()


loop = None

def handler(loop, context):
    print(context)

async def main():
    global detector
    global loop
    global configuration

    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    configuration = config.load("config/PsdSlowControlConfig.xml", schema="config/PsdSlowControlConfig.xsd")

    detector = Detector(configuration)


    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)

    try:
        for id, sm in detector.buses.items():
            await asyncio.create_task(sm.connect(), name="Connect to system module")
            asyncio.create_task(sm.send(), name="System module sending loop")
    except OSError as e:
        print("Cannot connect to system module")  

    print("Module link ok")
    app = WxAsyncApp(False)
    frame = MainWindow(None, "FHcal DCS")
    await app.MainLoop()



asyncio.run(main(), debug=True)
