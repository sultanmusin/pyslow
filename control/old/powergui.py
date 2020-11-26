#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import asyncio
import sys
import time

import wx
import wx.richtext
import os


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500,400))
        self.CreateLayout()
        self.Show()

        self.loop = asyncio.get_event_loop()

        self.OpenConnection()
        self.loop.run_until_complete(self.CheckState())


    def CreateLayout(self):
        self.channels = ['1','2','3','4','5','6','7','8']
        self.state = {}
        HEIGHT = 2
        self.miniGridSizer = wx.FlexGridSizer(HEIGHT, (len(self.channels) + HEIGHT - 1)/HEIGHT, 3, 3)
        self.moduleMiniButtons = {}


        for m in self.channels:
            self.moduleMiniButtons[m] = wx.Button(self, -1, m, size=(72,72), style=wx.BU_EXACTFIT)
            self.moduleMiniButtons[m].myname = m
            self.Bind(wx.EVT_BUTTON, self.OnClickButton, self.moduleMiniButtons[m])
            self.moduleMiniButtons[m].SetBackgroundColour((255, 255, 0))
            self.miniGridSizer.Add(self.moduleMiniButtons[m])
            self.state[m] = 1

#        self.mainSizer.Add(self.leftPaneSizer, 0, wx.EXPAND)
#        self.mainSizer.Add(self.rightPaneSizer, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.miniGridSizer)



    def OnClickButton(self,e):
        theButton = e.GetEventObject()
        channel = theButton.myname
        print("OnClickButton: %s" % channel)
        
        self.state[channel] = 1 - self.state[channel]
        if self.state[channel] == 0:
            self.moduleMiniButtons[channel].SetBackgroundColour((255, 0, 0))
        else:
            self.moduleMiniButtons[channel].SetBackgroundColour((0, 255, 0))

        #print(self.state)        
        cmd = "wFE%02d%04d_\n" % (int(channel), self.state[channel])
        print(cmd)




    def OpenConnection(self):
        address = "127.0.0.1"
        port = 4001

        loop = asyncio.get_event_loop()
        coro = asyncio.open_connection(address, port, loop=loop)
        try:
            self.reader, self.writer = loop.run_until_complete(coro)
        except OSError as e:
            print("Cannot connect to system module")  



    async def CheckState(self):
        pass
        #for ch in self.channels:
        #    cmd = "rFE%02d_\n" % (int(ch))
        #    self.writer.write(cmd.encode())
        #    data = await self.reader.read(100)
            



app = wx.App(False)
frame = MainWindow(None, "FHcal Power Supply Control")
app.MainLoop()
