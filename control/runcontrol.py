#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2021, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"


import asyncio
import wx
from datetime import datetime
import os
from wxasync import WxAsyncApp

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


RAW_FILE_PATTERN = '/home/runna61/DataBuffer/run-%06dx000_%d.raw'     # %(run_number, card_number)
DATA_PATH_PATTERN = '/home/runna61/RunData/run-%06d'                  # %(run_number)
START_COMMAND_PATTERN = 'echo "START%05d" | nc -w 10 localhost 2345'  # %(run_number)
STOP_COMMAND = 'echo "STOP      " | nc -w 10 localhost 2345'          # %(run_number)
LOG_FILE='/home/runna61/RunData/log.txt'

run_number = 15



class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 600))
        self.SetTitle("RUNCONTROL")

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        label_3 = wx.StaticText(self.panel_1, wx.ID_ANY, "Run control:")
        label_3.SetForegroundColour(wx.Colour(50, 50, 204))
        label_3.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_1.Add(label_3, 0, wx.ALL, 3)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)

        self.button_quit = wx.Button(self.panel_1, wx.ID_ANY, "Quit")
        self.button_quit.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_2.Add(self.button_quit, 0, 0, 0)
        self.button_quit.Bind( wx.EVT_BUTTON, self.on_button_quit )

        self.button_start_run = wx.Button(self.panel_1, wx.ID_ANY, "Start run")
        self.button_start_run.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_2.Add(self.button_start_run, 0, 0, 0)
        self.button_start_run.Bind( wx.EVT_BUTTON, self.on_button_start_run )

        self.button_stop_run = wx.Button(self.panel_1, wx.ID_ANY, "Stop run")
        self.button_stop_run.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        self.button_stop_run.Disable()
        sizer_2.Add(self.button_stop_run, 0, 0, 0)
        self.button_stop_run.Bind( wx.EVT_BUTTON, self.on_button_stop_run )

        label_4 = wx.StaticText(self.panel_1, wx.ID_ANY, "Run sheet:")
        label_4.SetForegroundColour(wx.Colour(50, 50, 204))
        label_4.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_1.Add(label_4, 0, wx.ALL, 3)

        grid_sizer_1 = wx.GridSizer(2, 3, 0, 0)
        sizer_1.Add(grid_sizer_1, 0, wx.EXPAND, 0)

        label_1 = wx.StaticText(self.panel_1, wx.ID_ANY, "Shift crew:")
        label_1.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_1.Add(label_1, 0, 0, 0)

        self.text_shift_crew = wx.TextCtrl(self.panel_1, wx.ID_ANY, "A.Izvestniy, S.Morozov, O.Petukhov")
        grid_sizer_1.Add(self.text_shift_crew, 1, wx.EXPAND, 0)

        grid_sizer_1.Add((0, 0), 0, 0, 0)

        label_2 = wx.StaticText(self.panel_1, wx.ID_ANY, "Comment:")
        label_2.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_1.Add(label_2, 0, 0, 0)

        self.text_comment = wx.TextCtrl(self.panel_1, wx.ID_ANY, "ca va")
        grid_sizer_1.Add(self.text_comment, 1, wx.EXPAND, 0)

        grid_sizer_1.Add((0, 0), 0, 0, 0)

        label_5 = wx.StaticText(self.panel_1, wx.ID_ANY, "Run status:")
        label_5.SetForegroundColour(wx.Colour(50, 50, 204))
        label_5.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_1.Add(label_5, 0, wx.ALL, 3)

        grid_sizer_2 = wx.GridSizer(2, 5, 0, 0)
        sizer_1.Add(grid_sizer_2, 0, wx.EXPAND, 0)

        label_7 = wx.StaticText(self.panel_1, wx.ID_ANY, "runNumber")
        label_7.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_2.Add(label_7, 0, wx.ALIGN_RIGHT, 0)

        label_8 = wx.StaticText(self.panel_1, wx.ID_ANY, "isRunStarted")
        label_8.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_2.Add(label_8, 0, wx.ALIGN_RIGHT, 0)

        label_9 = wx.StaticText(self.panel_1, wx.ID_ANY, "numEvents")
        label_9.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_2.Add(label_9, 0, wx.ALIGN_RIGHT, 0)

        label_10 = wx.StaticText(self.panel_1, wx.ID_ANY, "eventRate")
        label_10.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_2.Add(label_10, 0, wx.ALIGN_RIGHT, 0)

        label_11 = wx.StaticText(self.panel_1, wx.ID_ANY, "elapsedTime")
        label_11.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        grid_sizer_2.Add(label_11, 0, wx.ALIGN_RIGHT, 0)

        self.label_run_number = wx.StaticText(self.panel_1, wx.ID_ANY, "12345")
        self.label_run_number.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(self.label_run_number, 0, wx.ALIGN_RIGHT, 0)

        self.label_is_run_started = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        self.label_is_run_started.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(self.label_is_run_started, 0, wx.ALIGN_RIGHT, 0)

        self.label_num_events = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        self.label_num_events.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(self.label_num_events, 0, wx.ALIGN_RIGHT, 0)

        self.label_event_rate = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        self.label_event_rate.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(self.label_event_rate, 0, wx.ALIGN_RIGHT, 0)

        self.label_elapsed_time = wx.StaticText(self.panel_1, wx.ID_ANY, "00:00:00")
        self.label_elapsed_time.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(self.label_elapsed_time, 0, wx.ALIGN_RIGHT, 0)

        label_6 = wx.StaticText(self.panel_1, wx.ID_ANY, "Messages:")
        label_6.SetForegroundColour(wx.Colour(50, 50, 204))
        label_6.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_1.Add(label_6, 0, wx.ALL, 3)

        self.text_console = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.HSCROLL | wx.TE_MULTILINE)
        self.text_console.SetFont(wx.Font(11, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        sizer_1.Add(self.text_console, 1, wx.EXPAND, 0)

        self.panel_1.SetSizer(sizer_1)

        self.Layout()
        # end wxGlade

        self.read_log()


    def on_button_quit(self, event):
        wx.CallAfter(self.Destroy)


    def on_button_start_run(self, event):
        self.start_run()


    def on_button_stop_run(self, event):
        self.stop_run()


    def start_run(self):
        self.button_start_run.Disable()
        self.write_to_log('START')
        run_number = int(self.label_run_number.GetLabelText())
        start_command = START_COMMAND_PATTERN%(run_number)
        os.system(start_command)
        self.is_run_started = True
        self.button_stop_run.Enable()


    def stop_run(self):
        self.button_stop_run.Disable()
        self.write_to_log('STOP')
        os.system(STOP_COMMAND)
        run_number = int(self.label_run_number.GetLabelText())
        self.label_run_number.SetLabelText(str(run_number+1))
        self.is_run_started = False
        self.button_start_run.Enable()


    def read_log(self):
        try:
            f = open(LOG_FILE, "r")
            lines = f.readlines()
            (run_number, action, datetime, crew, comment) = lines[-1].split(';')
        except (IOError, FileNotFoundError, IndexError) as e:
            (run_number, action, datetime, crew, comment) = (0, 'none', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '-', '-')

        self.label_run_number.SetLabelText(str(int(run_number)+1))
        self.text_shift_crew.SetLabelText(crew)
        self.text_comment.SetLabelText(comment)


    def write_to_log(self, action=''):
        f = open(LOG_FILE, "a+")


        # (run_number; datetime; crew; comment)

        logline = '%s;%s;%s;%s;%s\n' % (
            self.label_run_number.GetLabelText(),
            action,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            self.text_shift_crew.GetValue(),
            self.text_comment.GetValue()
        )

        f.write(logline)
        print(logline)

        f.close()
    


# end of class MainFrame

def handler(loop, context):
    print(context)

async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)
        
    app = WxAsyncApp(False)
    frame = MainFrame(None)
    await app.MainLoop()

if __name__ == '__main__':
    #asyncio.run(main(), debug=True)
    print("Staring main loop...")
    asyncio.get_event_loop().run_until_complete(asyncio.wait([main()]))
