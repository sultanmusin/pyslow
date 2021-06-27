#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2021, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"


import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


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

        self.button_start_run = wx.Button(self.panel_1, wx.ID_ANY, "Start run")
        self.button_start_run.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_2.Add(self.button_start_run, 0, 0, 0)

        self.button_stop_run = wx.Button(self.panel_1, wx.ID_ANY, "Stop run")
        self.button_stop_run.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_2.Add(self.button_stop_run, 0, 0, 0)

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

        label_run_number = wx.StaticText(self.panel_1, wx.ID_ANY, "12345")
        label_run_number.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(label_run_number, 0, wx.ALIGN_RIGHT, 0)

        label_is_run_started = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        label_is_run_started.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(label_is_run_started, 0, wx.ALIGN_RIGHT, 0)

        label_num_events = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        label_num_events.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(label_num_events, 0, wx.ALIGN_RIGHT, 0)

        label_event_rate = wx.StaticText(self.panel_1, wx.ID_ANY, "0")
        label_event_rate.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(label_event_rate, 0, wx.ALIGN_RIGHT, 0)

        label_elapsed_time = wx.StaticText(self.panel_1, wx.ID_ANY, "00:00:00")
        label_elapsed_time.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        grid_sizer_2.Add(label_elapsed_time, 0, wx.ALIGN_RIGHT, 0)

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

# end of class MainFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
