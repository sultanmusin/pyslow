#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Oleg Petukhov"
__copyright__ = "2020, INR RAS"
__license__ = "GPL"
__version__ = "0.5"
__email__ = "opetukhov@inr.ru"
__status__ = "Development"



import asyncio
import datetime
import logging
import os
import string
import sys
import wx
import wx.richtext
import wx.xrc
import wx.grid
from wxasync import WxAsyncApp

sys.path.append('.')
sys.path.append('lib/hvsys')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply
from hvsyssupply800c import HVsysSupply800c
from hvsysled import HVsysLED
from hvstatus import HVStatus

configuration = None
detector = None

COLOR_OFFLINE = wx.Colour(192,192,192)
COLOR_HV_OFF = wx.Colour(224,224,96)
COLOR_RAMP = wx.Colour(96,96,224)
COLOR_ERROR = wx.Colour(224,48,48)
COLOR_NOT_REFERENCE = wx.Colour(224,48,224)
COLOR_OK = wx.Colour(128,224,48)

GRID_COLUMN_ONLINE = 0
GRID_COLUMN_HV_ON = 1
GRID_COLUMN_LEFT_STATE = 2

# HV grid legend
N_SECTIONS = 10
GRID_ROW_PEDESTAL = N_SECTIONS
GRID_ROW_TEMPERATURE = N_SECTIONS + 1
GRID_ROW_SLOPE = N_SECTIONS + 2
GRID_ROWS_HV = N_SECTIONS + 3 # for pedestal, temperature, slope

# LED grid legend
GRID_ROW_FREQUENCY = 0
GRID_ROW_AMPLITUDE = 1
GRID_ROW_ADC_SET_POINT = 2
GRID_ROW_AVERAGE_POINTS = 3
GRID_ROW_AUTOREG = 4
GRID_ROW_AVERAGE_ADC = 5
GRID_ROWS_LED = 6

# All grids column legend
GRID_COLUMN_REFERENCE = 0
GRID_COLUMN_SET = 1
GRID_COLUMN_MEAS = 2
GRID_COLUMN_STATE = 3
GRID_COLUMNS = 4
GRID_COLUMNS_LED = 3

cc = wx.grid.GridCellCoords
hv_grid_coords = {
    "1/REF_VOLTAGE": cc(0,GRID_COLUMN_REFERENCE),
    "2/REF_VOLTAGE": cc(1,GRID_COLUMN_REFERENCE),
    "3/REF_VOLTAGE": cc(2,GRID_COLUMN_REFERENCE),
    "4/REF_VOLTAGE": cc(3,GRID_COLUMN_REFERENCE),
    "5/REF_VOLTAGE": cc(4,GRID_COLUMN_REFERENCE),
    "6/REF_VOLTAGE": cc(5,GRID_COLUMN_REFERENCE),
    "7/REF_VOLTAGE": cc(6,GRID_COLUMN_REFERENCE),
    "8/REF_VOLTAGE": cc(7,GRID_COLUMN_REFERENCE),
    "9/REF_VOLTAGE": cc(8,GRID_COLUMN_REFERENCE),
    "10/REF_VOLTAGE": cc(9,GRID_COLUMN_REFERENCE),

    "1/SET_VOLTAGE": cc(0,GRID_COLUMN_SET),
    "2/SET_VOLTAGE": cc(1,GRID_COLUMN_SET),
    "3/SET_VOLTAGE": cc(2,GRID_COLUMN_SET),
    "4/SET_VOLTAGE": cc(3,GRID_COLUMN_SET),
    "5/SET_VOLTAGE": cc(4,GRID_COLUMN_SET),
    "6/SET_VOLTAGE": cc(5,GRID_COLUMN_SET),
    "7/SET_VOLTAGE": cc(6,GRID_COLUMN_SET),
    "8/SET_VOLTAGE": cc(7,GRID_COLUMN_SET),
    "9/SET_VOLTAGE": cc(8,GRID_COLUMN_SET),
    "10/SET_VOLTAGE": cc(9,GRID_COLUMN_SET),
    "SET_PEDESTAL_VOLTAGE": cc(GRID_ROW_PEDESTAL,GRID_COLUMN_SET),
    "TEMPERATURE": cc(GRID_ROW_TEMPERATURE,GRID_COLUMN_MEAS),
    "1/MEAS_VOLTAGE": cc(0,GRID_COLUMN_MEAS),
    "2/MEAS_VOLTAGE": cc(1,GRID_COLUMN_MEAS),
    "3/MEAS_VOLTAGE": cc(2,GRID_COLUMN_MEAS),
    "4/MEAS_VOLTAGE": cc(3,GRID_COLUMN_MEAS),
    "5/MEAS_VOLTAGE": cc(4,GRID_COLUMN_MEAS),
    "6/MEAS_VOLTAGE": cc(5,GRID_COLUMN_MEAS),
    "7/MEAS_VOLTAGE": cc(6,GRID_COLUMN_MEAS),
    "8/MEAS_VOLTAGE": cc(7,GRID_COLUMN_MEAS),
    "9/MEAS_VOLTAGE": cc(8,GRID_COLUMN_MEAS),
    "10/MEAS_VOLTAGE": cc(9,GRID_COLUMN_MEAS),        
    "MEAS_PEDESTAL_VOLTAGE": cc(GRID_ROW_PEDESTAL,GRID_COLUMN_MEAS),
}

capability_by_hv_grid_coords = {val.Get() : key for key, val in hv_grid_coords.items()}

led_grid_coords = {
    "SET_FREQUENCY": cc(GRID_ROW_FREQUENCY,GRID_COLUMN_SET),
    "SET_AMPLITUDE": cc(GRID_ROW_AMPLITUDE,GRID_COLUMN_SET),
    "ADC_SET_POINT": cc(GRID_ROW_ADC_SET_POINT,GRID_COLUMN_SET),
    "AVERAGE_POINTS": cc(GRID_ROW_AVERAGE_POINTS,GRID_COLUMN_SET),
    "AUTOREG": cc(GRID_ROW_AUTOREG,GRID_COLUMN_SET),
    "AVERAGE_ADC": cc(GRID_ROW_AVERAGE_ADC,GRID_COLUMN_SET),
}

capability_by_led_grid_coords = {val.Get() : key for key, val in led_grid_coords.items()}

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        self.dirname=''

        global configuration
        self.config = configuration

        wx.Log().EnableLogging(False)

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"FHCal DCS", pos = wx.DefaultPosition, size = wx.Size( 1080,960 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.CreateLayout()
        self.Show()

        # select first online module (if any...)
        self.SelectFirstOnlineModule()
        self.ShowReferenceParameters()
        self.SetReferenceParameters()
        self.UpdateModuleGrid()


    def CreateLayout(self):
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_statusBar1 = self.CreateStatusBar( 5, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menuFile = wx.Menu()
        self.m_menuOpen = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Open", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuOpen )

        self.m_menuSave = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Save", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuSave )

        self.m_menuPreferences = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Preferences", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuPreferences )

        self.m_menuExit = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuExit )

        self.m_menubar1.Append( self.m_menuFile, u"&File" )

        self.m_menuHelp = wx.Menu()
        self.m_menuAbout = wx.MenuItem( self.m_menuHelp, wx.ID_ANY, u"A&bout", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuHelp.Append( self.m_menuAbout )

        self.m_menubar1.Append( self.m_menuHelp, u"&Help" )

        self.SetMenuBar( self.m_menubar1 )

        # Menu Events
        self.Bind(wx.EVT_MENU, self.OnOpen, self.m_menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, self.m_menuSave)
        self.Bind(wx.EVT_MENU, self.OnPreferences, self.m_menuPreferences)
        self.Bind(wx.EVT_MENU, self.OnExit, self.m_menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.m_menuAbout)

        bSizerMain = wx.BoxSizer( wx.HORIZONTAL )

        self.m_panelLeft = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_THEME|wx.TAB_TRAVERSAL )
        self.m_panelLeft.SetMaxSize( wx.Size( 400,-1 ) )

        bSizerLeft = wx.BoxSizer( wx.VERTICAL )

        self.m_staticTextLeftCaption = wx.StaticText( self.m_panelLeft, wx.ID_ANY, u"Detector Map", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextLeftCaption.Wrap( -1 )

        bSizerLeft.Add( self.m_staticTextLeftCaption, 0, wx.ALL, 5 )

        self.m_buttonSelectAllModules = wx.Button( self.m_panelLeft, wx.ID_ANY, u"Select All Modules", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerLeft.Add( self.m_buttonSelectAllModules, 0, wx.ALL, 5 )

        self.m_buttonSelectAllModules.Bind( wx.EVT_BUTTON, self.OnButtonSelectAllModulesClick )


        self.m_gridModules = wx.grid.Grid( self.m_panelLeft, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridModules.CreateGrid( len(self.config.modules), 3 )
        self.m_gridModules.EnableEditing( True )
        self.m_gridModules.EnableGridLines( True )
        self.m_gridModules.EnableDragGridSize( False )
        self.m_gridModules.SetMargins( 0, 0 )
        self.m_gridModules.SetMaxSize( wx.Size(-1, 500) )
        self.m_gridModules.SetSelectionMode(wx.grid.Grid.SelectRows)
        

        # Columns
        self.m_gridModules.EnableDragColMove( False )
        self.m_gridModules.EnableDragColSize( True )
        self.m_gridModules.SetColLabelValue( 0, u"Online" )
        self.m_gridModules.SetColLabelValue( 1, u"HV ON" )
        self.m_gridModules.SetColLabelValue( 2, u"State" )
        self.m_gridModules.SetColFormatBool( 0 )
        self.m_gridModules.SetColFormatBool( 1 )
        self.m_gridModules.SetColLabelSize( wx.grid.GRID_AUTOSIZE )
        self.m_gridModules.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.m_gridModules.EnableDragRowSize( False )
        self.m_gridModules.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.m_gridModules.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        #self.m_gridModules.SetDefaultEditor( wx.grid.GridCellBoolEditor )

        # Populate cells
        for index, (title, config) in enumerate(self.config.modules.items()):
            self.m_gridModules.SetRowLabelValue( index, "Module %s"%(title) )
            self.m_gridModules.SetCellEditor( index, GRID_COLUMN_ONLINE, wx.grid.GridCellBoolEditor() )
#            self.m_gridModules.SetCellValue( index, GRID_COLUMN_ONLINE, config.online )
            # hv on and state columns get filled later on detector poll procedure                 

        bSizerLeft.Add( self.m_gridModules, 1, wx.ALL, 5 )

        fgSizerModuleGrid = wx.FlexGridSizer(self.config.geom_height, self.config.geom_width, 3, 3)
        fgSizerModuleGrid.SetFlexibleDirection( wx.BOTH )
        fgSizerModuleGrid.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizerModuleGrid.SetMinSize( wx.Size( -1,400 ) )

        bSizerLeft.Add( fgSizerModuleGrid, 1, wx.EXPAND, 5 )
        bSizerLeft.Layout()

        self.m_panelLeft.SetSizer( bSizerLeft )
        self.m_panelLeft.Layout()
        bSizerLeft.Fit( self.m_panelLeft )
        bSizerMain.Add( self.m_panelLeft, 1, wx.EXPAND |wx.ALL, 5 )

        self.m_panelRight = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_THEME|wx.TAB_TRAVERSAL )
        bSizerRight = wx.BoxSizer( wx.VERTICAL )

        self.m_staticTextRightCaption = wx.StaticText( self.m_panelRight, wx.ID_ANY, u"Module #", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRightCaption.Wrap( -1 )

        bSizerRight.Add( self.m_staticTextRightCaption, 0, wx.ALL, 5 )

        self.m_panelMulti = wx.Panel( self.m_panelRight, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"Module Control")

        bSizerMulti = wx.WrapSizer( wx.HORIZONTAL )

        self.m_checkBoxOnline = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"Online", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxOnline, 0, wx.ALL, 5 )

        self.m_checkBoxHvOn = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"HV ON", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxHvOn, 0, wx.ALL, 5 )

        self.m_checkBoxLedAuto = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"LED Auto", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxLedAuto, 0, wx.ALL, 5 )

        self.m_checkBoxPoll = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"Poll", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxPoll, 0, wx.ALL, 5 )
        self.m_checkBoxPoll.SetValue( self.config.query_delay > 0 )

        self.m_checkBoxTemperatureControl = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"Temperature Control", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxTemperatureControl, 0, wx.ALL, 5 )
        self.m_checkBoxTemperatureControl.SetValue(True)
        self.m_checkBoxTemperatureControl.Disable()

        self.m_checkBoxAlertsEnabled = wx.CheckBox( self.m_panelMulti, wx.ID_ANY, u"Alerts Enabled", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_checkBoxAlertsEnabled, 0, wx.ALL, 5 )
        self.m_checkBoxAlertsEnabled.Disable()

        self.m_buttonApplyReference = wx.Button( self.m_panelMulti, wx.ID_ANY, u"Apply reference HV", wx.DefaultPosition, wx.DefaultSize, wx.CHK_3STATE )
        bSizerMulti.Add( self.m_buttonApplyReference, 0, wx.ALL, 5 )


        self.m_panelMulti.SetSizer( bSizerMulti )
        self.m_panelMulti.Layout()
        bSizerMulti.Fit( self.m_panelMulti )
        bSizerRight.Add( self.m_panelMulti, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_panelHV = wx.Panel( self.m_panelRight, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"High Voltage" )

        bSizerHV = wx.BoxSizer( wx.VERTICAL )

        self.m_gridHV = wx.grid.Grid( self.m_panelHV, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridHV.CreateGrid( GRID_ROWS_HV, GRID_COLUMNS )
        self.m_gridHV.EnableEditing( True )
        self.m_gridHV.SetDefaultEditor(wx.grid.GridCellFloatEditor(width=3, precision=1))
        self.m_gridHV.EnableGridLines( True )
        self.m_gridHV.EnableDragGridSize( False )
        self.m_gridHV.SetMargins( 0, 0 )

        # Columns
        self.m_gridHV.EnableDragColMove( False )
        self.m_gridHV.EnableDragColSize( True )
        self.m_gridHV.SetColLabelValue( GRID_COLUMN_REFERENCE, u"Reference" )
        self.m_gridHV.SetColLabelValue( GRID_COLUMN_SET, u"Set" )
        self.m_gridHV.SetColLabelValue( GRID_COLUMN_MEAS, u"Measured" )
        self.m_gridHV.SetColLabelValue( GRID_COLUMN_STATE, u"State" )
        self.m_gridHV.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        for row in range(GRID_ROWS_HV):
            self.m_gridHV.SetRowLabelValue(row, "Section %d"%(row+1))
            for col in range(GRID_COLUMNS):
                self.m_gridHV.SetReadOnly(row, col, True)
                self.m_gridHV.SetCellValue(row, col, "0.0")

            self.m_gridHV.SetReadOnly(row, 0, False)
            self.m_gridHV.SetReadOnly(row, 1, False)
            self.m_gridHV.SetCellValue(row, 3, "OK")

        self.m_gridHV.EnableDragRowSize( False )
        self.m_gridHV.SetRowLabelSize( 100 )
        self.m_gridHV.SetRowLabelValue( GRID_ROW_PEDESTAL, u"Pedestal" )
        self.m_gridHV.SetRowLabelValue( GRID_ROW_TEMPERATURE, u"Temperature" )
        self.m_gridHV.SetRowLabelValue( GRID_ROW_SLOPE, u"Slope" )
        self.m_gridHV.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTER )

        self.m_gridHV.SetCellValue(GRID_ROW_PEDESTAL, 3, "")
        self.m_gridHV.SetCellValue(GRID_ROW_TEMPERATURE, 3, "")
        self.m_gridHV.SetCellValue(GRID_ROW_SLOPE, 3, "")


        # Label Appearance

        # Cell Defaults
        self.m_gridHV.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizerHV.Add( self.m_gridHV, 0, wx.ALL, 5 )


        self.m_panelHV.SetSizer( bSizerHV )
        self.m_panelHV.Layout()
        bSizerHV.Fit( self.m_panelHV )
        bSizerRight.Add( self.m_panelHV, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_panelLED = wx.Panel( self.m_panelRight, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, u"LED Control")

        bSizerLED = wx.BoxSizer( wx.VERTICAL )

        self.m_gridLED = wx.grid.Grid( self.m_panelLED, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridLED.CreateGrid( GRID_ROWS_LED, GRID_COLUMNS_LED )
        self.m_gridLED.EnableEditing( True )
        self.m_gridLED.EnableGridLines( True )
        self.m_gridLED.EnableDragGridSize( False )
        self.m_gridLED.SetMargins( 0, 0 )

        # Columns
        self.m_gridLED.EnableDragColMove( False )
        self.m_gridLED.EnableDragColSize( True )
        self.m_gridLED.SetColLabelValue( GRID_COLUMN_REFERENCE, u"Reference" )
        self.m_gridLED.SetColLabelValue( GRID_COLUMN_SET, u"Set" )
        self.m_gridLED.SetColLabelValue( GRID_COLUMN_MEAS, u"Measured" )
        self.m_gridLED.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.m_gridLED.SetRowLabelSize( 100 )
        self.m_gridLED.EnableDragRowSize( False )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_AMPLITUDE, u"Amplitude" )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_FREQUENCY, u"Frequency" )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_ADC_SET_POINT, u"ADC Setpoint" )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_AVERAGE_POINTS, u"Average points" )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_AUTOREG, u"Autoregulation on/off" )
        self.m_gridLED.SetRowLabelValue( GRID_ROW_AVERAGE_ADC, u"Average ADC readout" )
        self.m_gridLED.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.m_gridLED.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizerLED.Add( self.m_gridLED, 0, wx.ALL, 5 )


        self.m_panelLED.SetSizer( bSizerLED )
        self.m_panelLED.Layout()
        bSizerLED.Fit( self.m_panelLED )
        bSizerRight.Add( self.m_panelLED, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_collapsiblePaneDebug = wx.CollapsiblePane( self.m_panelRight, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, wx.CP_NO_TLW_RESIZE )
        self.m_collapsiblePaneDebug.Collapse( True )

        bSizerDebug = wx.BoxSizer( wx.HORIZONTAL )

        self.m_listBoxParts = wx.ListBox( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [], 0 )
        bSizerDebug.Add( self.m_listBoxParts, 0, wx.ALL, 5 )

        self.m_listBoxCapabilities = wx.ListBox( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [], 0 )
        bSizerDebug.Add( self.m_listBoxCapabilities, 0, wx.ALL, 5 )

        self.m_textCtrl1 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

        self.m_button1 = wx.Button( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, u"Read", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_textCtrl2 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl2, 0, wx.ALL, 5 )

        self.m_button2 = wx.Button( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, u"Write", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_button2, 0, wx.ALL, 5 )

        self.m_textCtrl3 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl3, 0, wx.ALL, 5 )


        self.m_collapsiblePaneDebug.GetPane().SetSizer( bSizerDebug )
        self.m_collapsiblePaneDebug.GetPane().Layout()
        bSizerDebug.Fit( self.m_collapsiblePaneDebug.GetPane() )
        bSizerRight.Add( self.m_collapsiblePaneDebug, 0, wx.ALL|wx.EXPAND, 5 )


        self.m_panelRight.SetSizer( bSizerRight )
        self.m_panelRight.Layout()
        bSizerRight.Fit( self.m_panelRight )
        bSizerMain.Add( self.m_panelRight, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )

        # Module poll timer
        self.m_pollTimer = wx.Timer(self, 12345)
        self.Bind( wx.EVT_TIMER, self.OnPollTimer, self.m_pollTimer )
        if self.config.query_delay > 0: # means we should periodically query the module          
            self.m_pollTimer.Start(self.config.query_delay * 1000)
            logging.info("First poll timer start!")


        # Connect Events

        self.m_checkBoxOnline.Bind( wx.EVT_CHECKBOX, self.OnCheckBoxOnlineChange )
        self.m_checkBoxHvOn.Bind( wx.EVT_CHECKBOX, self.OnCheckBoxHVChange )
        self.m_checkBoxLedAuto.Bind( wx.EVT_CHECKBOX, self.OnCheckBoxLEDChange )
        self.m_checkBoxPoll.Bind( wx.EVT_CHECKBOX, self.OnCheckBoxPollChange )
        self.m_buttonApplyReference.Bind( wx.EVT_BUTTON, self.OnButtonApplyReferenceClick )

        self.m_gridHV.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.OnHVGridChange )
        self.m_gridLED.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.OnLEDGridChange )

        self.m_gridModules.Bind( wx.grid.EVT_GRID_RANGE_SELECT, self.OnModuleGridRangeSelect )   
        self.m_gridModules.Bind( wx.grid.EVT_GRID_CMD_SELECT_CELL, self.OnModuleGridSelectCell )   
        self.m_gridModules.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnModuleGridLabelLeftClick )   
        self.m_gridModules.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.OnModuleGridChange )   
        
        self.m_moduleMiniButtons = {}
        for m in self.config.modulesOrderedByGeometry:
            if len(m) > 0:
                self.m_moduleMiniButtons[m] = wx.Button(self.m_panelLeft, -1, m, size=(36,40), style=wx.BU_EXACTFIT)
                self.m_moduleMiniButtons[m].myname = m
                self.Bind(wx.EVT_BUTTON, self.OnSelectModuleFromGrid, self.m_moduleMiniButtons[m])
                if self.config.modules[m].online:
                    self.m_moduleMiniButtons[m].SetBackgroundColour((255, 255, 0))
                fgSizerModuleGrid.Add(self.m_moduleMiniButtons[m])
            else:
                fgSizerModuleGrid.Add(wx.StaticText(self.m_panelLeft, -1, ""))


    def __del__( self ):
        pass

    
    def UpdateModuleGrid(self):
        for index, (title, config) in enumerate(self.config.modules.items()):
            if config.online:
                self.m_gridModules.SetCellValue(index, GRID_COLUMN_ONLINE, "1")
            else:
                self.m_gridModules.SetCellValue(index, GRID_COLUMN_ONLINE, "0")
                self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_OFFLINE)    

            if config.has('hv'): 
                bus_id = config.bus_id
                part_address = int(config.address('hv'))
                part = detector.buses[bus_id].getPart(part_address) 

                self.m_gridModules.SetReadOnly(index, GRID_COLUMN_HV_ON, False)

                if 'STATUS' in part.state and part.state['STATUS'] is not None:
                    status = HVStatus(part.state['STATUS'])
                    self.m_gridModules.SetCellValue(index, GRID_COLUMN_LEFT_STATE, str(status))
                    if status.is_on():
                        self.m_gridModules.SetCellValue(index, GRID_COLUMN_HV_ON, "1")
                        self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_OK)    
                    else:
                        self.m_gridModules.SetCellValue(index, GRID_COLUMN_HV_ON, "0")
                        self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_HV_OFF)    
                    if status.is_error():
                        self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_ERROR)    
                    if not part.has_reference_voltage():
                        self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_NOT_REFERENCE)   
                    if status.is_ramp():
                        self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_RAMP)   

                else:
                    # not polled yet, strange
                    self.m_gridModules.SetCellValue(index, GRID_COLUMN_LEFT_STATE, "unknown" if config.online else "offline")
                    self.m_gridModules.SetCellValue(index, GRID_COLUMN_HV_ON, "0")
                    self.m_gridModules.SetCellBackgroundColour(index, GRID_COLUMN_LEFT_STATE, COLOR_OFFLINE)    
            else:
                self.m_gridModules.SetCellValue(index, GRID_COLUMN_HV_ON, "0")
                self.m_gridModules.SetReadOnly(index, GRID_COLUMN_HV_ON, True)
                self.m_gridModules.SetCellValue(index, GRID_COLUMN_LEFT_STATE, "unknown")


    def OnPollTimer(self, event):
        logging.info("Poll timer fired!")
        #print(event)
        #for module_id in self.activeModuleId:
        for module_id, config in self.config.modules.items():
            if config.online:
                self.pollModule(module_id)
        
        self.UpdateModuleGrid()


    def OnCheckBoxPollChange(self, event):
        if self.m_checkBoxPoll.GetValue() and self.config.query_delay > 0:
            self.m_pollTimer.Start(self.config.query_delay * 1000)
            logging.info("Poll timer started!")
        else: 
            self.m_pollTimer.Stop()
            logging.info("Poll timer stopped!")


    def OnModuleGridSelectCell( self, event ):
        global detector
        #self.OnModuleGridRangeSelect( event )
        self.m_gridModules.SelectRow( event.Row )
        logging.info("OnModuleGridSelect: %s"%(event.GetString()))
        


    def OnModuleGridRangeSelect( self, event ):
        global detector
        selectedRows = self.m_gridModules.GetSelectedRows()
        #        for index, (title, config) in enumerate(self.config.modules.items()):
        selected_modules = [list(self.config.modules.keys())[i] for i in selectedRows]

        logging.info("OnModuleGridRangeSelect: %s"%(selected_modules))
        logging.info("OnModuleGridRangeSelect: prev selected %s"%(self.activeModuleId))
        
        if len(selected_modules) > 0 and selected_modules != self.activeModuleId:
            self.SelectModule(selected_modules)

    def OnModuleGridLabelLeftClick( self, event ):
        # Disable clicking on column caption
        if event.Row > -1:
            event.Skip()
        

    def OnModuleGridChange( self, event ):
        global detector
        
        #cap = capability_by_hv_grid_coords[(event.Row, event.Col)]
        new_value = self.m_gridModules.GetCellValue(event.Row, event.Col)

        logging.info("OnModuleChange: %s %s %s"%(event.Row, event.Col, new_value))

        """
        moduleId = self.activeModuleId[0]
        moduleConfig = self.config.modules[moduleId]
        
        if moduleConfig.has('hv'): 
            bus_id = self.config.modules[moduleId].bus_id
            part_address = int(self.config.modules[moduleId].address('hv'))
            part = detector.buses[bus_id].getPart(part_address) 

            cap = capability_by_hv_grid_coords[(event.Row, event.Col)]
            new_value = self.m_gridHV.GetCellValue(event.Row, event.Col)
            value = part.valueFromString(cap, new_value)

            command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
            asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
        """

    def OnHVGridChange( self, event ):
        global detector
        logging.info("OnHVGridChange: %s"%(event.GetString()))

        moduleId = self.activeModuleId[0]
        moduleConfig = self.config.modules[moduleId]
        
        if moduleConfig.has('hv'): 
            bus_id = self.config.modules[moduleId].bus_id
            part_address = int(self.config.modules[moduleId].address('hv'))
            part = detector.buses[bus_id].getPart(part_address) 

            cap = capability_by_hv_grid_coords[(event.Row, event.Col)]
            new_value = self.m_gridHV.GetCellValue(event.Row, event.Col)
            value = part.valueFromString(cap, new_value)

            command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
            asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))

    def OnLEDGridChange( self, event ):
        global detector
        logging.info("OnLEDGridChange: %s"%(event.GetString()))

        for moduleId in self.activeModuleId:
            moduleConfig = self.config.modules[moduleId]
            
            if moduleConfig.has('led'): 
                bus_id = self.config.modules[moduleId].bus_id
                part_address = int(self.config.modules[moduleId].address('led'))
                part = detector.buses[bus_id].getPart(part_address) 

                cap = capability_by_led_grid_coords[(event.Row, event.Col)]
                new_value = self.m_gridLED.GetCellValue(event.Row, event.Col)
                value = part.valueFromString(cap, new_value)

                command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
                asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))


    def SelectFirstOnlineModule(self):
        for m in self.config.modules.values():
            if m.online:
                self.SelectModule([m.id])
                break

    def ShowReferenceParameters(self):
        if type(self.activeModuleId) is list and len(self.activeModuleId) == 1:
            active_module_config = configuration.modules[self.activeModuleId[0]]
            if active_module_config.has('hv'):
                for ch, hv in active_module_config.hv.items():
                    self.m_gridHV.SetCellValue(int(ch)-1, GRID_COLUMN_REFERENCE, str(hv))    

                self.m_gridHV.SetCellValue(GRID_ROW_PEDESTAL, GRID_COLUMN_REFERENCE, str(active_module_config.hvPedestal))
                self.m_gridHV.SetCellValue(GRID_ROW_TEMPERATURE, GRID_COLUMN_REFERENCE, str(configuration.reference_temperature))
                self.m_gridHV.SetCellValue(GRID_ROW_SLOPE, GRID_COLUMN_REFERENCE, str(-configuration.temperature_slope))

    def SetReferenceParameters(self):
        pass

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
            asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, self.ShowQueryResult))


    def ShowQueryResult(self, data):
        self.responseText.SetValue("0x%x" % (data))
        self.valueText.SetValue(str(data))


    def OnWrite(self,e):
        global detector

        part_address = self.GetActivePartAddress()
        part_type = self.GetActivePartType()

        value = int(self.valueText.GetValue())

        command = Message(Message.WRITE_SHORT, part_address, part_type, self.moduleCapabilitiesBox.GetStringSelection(), value)
        self.commandText.SetValue(command.rstrip())

        # TODO send (danger danger)


    async def pollOnlineModules(self):
        global detector
        
        last_task = None
        for module_id, module_config in self.config.modules.items():
            if module_config.online:
                await self.pollModule(module_id, False)
        

    def OnButtonSelectAllModulesClick(self, event):
        self.m_gridModules.SelectAll()
        selectedRows = self.m_gridModules.GetSelectedRows()
        #        for index, (title, config) in enumerate(self.config.modules.items()):
        selected_modules = [list(self.config.modules.keys())[i] for i in selectedRows]

        logging.info("OnModuleGridRangeSelect: %s"%(selected_modules))
        logging.info("OnModuleGridRangeSelect: prev selected %s"%(self.activeModuleId))
        
        if len(selected_modules) > 0 and selected_modules != self.activeModuleId:
            self.SelectModule(selected_modules)

    def OnButtonApplyReferenceClick(self, event):
        global detector
        
        for module_id in self.activeModuleId:
            module_config = self.config.modules[module_id]
            if module_config.online:
                bus_id = self.config.modules[module_id].bus_id
                if module_config.has('hv'): 
                    part_address = int(self.config.modules[module_id].address('hv'))
                    part = detector.buses[bus_id].getPart(part_address) 
                    value = part.valueFromString('SET_PEDESTAL_VOLTAGE', str(module_config.hvPedestal))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_PEDESTAL_VOLTAGE', value)
                    asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))

                    for ch, hv in module_config.hv.items():
                        cap = '%s/SET_VOLTAGE'%(ch)
                        value = part.valueFromString(cap, str(hv))
                        command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
                        asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))

                if module_config.has('led'): 
                    part_address = int(self.config.modules[module_id].address('led'))
                    part = detector.buses[bus_id].getPart(part_address) 
                    value = part.valueFromString('AUTOREG', str(module_config.ledAutoTune))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'AUTOREG', value)
                    asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('SET_FREQUENCY', str(module_config.ledFrequency))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_FREQUENCY', value)
                    asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('SET_AMPLITUDE', str(module_config.ledBrightness))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_AMPLITUDE', value)
                    asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('ADC_SET_POINT', str(module_config.ledPinADCSet))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'ADC_SET_POINT', value)
                    asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
             
        self.UpdateModuleGrid()
        

    def OnCheckBoxOnlineChange(self, event):
        value = self.m_checkBoxOnline.GetValue() > 0
        for moduleId in self.activeModuleId:
            moduleConfig = self.config.modules[moduleId]
            moduleConfig.online = value
        
        self.UpdateModuleGrid()
        

    def OnCheckBoxHVChange(self, event):
        value = HVsysSupply.POWER_ON if self.m_checkBoxHvOn.GetValue() > 0 else HVsysSupply.POWER_OFF
        self.SwitchHV(value)

    def OnCheckBoxLEDChange(self, event):
        global detector
        value = (self.m_checkBoxLedAuto.GetValue() > 0)

        for moduleId in self.activeModuleId:
            moduleConfig = self.config.modules[moduleId]
            
            if moduleConfig.has('led'): 
                bus_id = self.config.modules[moduleId].bus_id
                part_address = int(self.config.modules[moduleId].address('led'))
                part = detector.buses[bus_id].getPart(part_address) 
                command = Message(Message.WRITE_SHORT, part_address, part, 'AUTOREG', value)
                logging.warning('LED switching!')
                asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
            else:
                logging.warning('LED autoreg requested for module without LED part')

    def SwitchHV(self,state):
        global detector

        for moduleId in self.activeModuleId:
            moduleConfig = self.config.modules[moduleId]
            
            if moduleConfig.has('hv'): 
                bus_id = self.config.modules[moduleId].bus_id
                part_address = int(self.config.modules[moduleId].address('hv'))
                part = detector.buses[bus_id].getPart(part_address) 
                command = Message(Message.WRITE_SHORT, part_address, part, 'STATUS', state)
                logging.warning('HV switching!')
                asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))
                asyncio.get_event_loop().create_task(detector.monitor_ramp_status(bus_id, part, part_address, self.DisplayRampStatus))
            else:
                logging.warning('HV ON requested for module without HV part')

    def OnSwitchOnHV(self, e):
        self.SwitchHV(HVsysSupply.POWER_ON)

    def OnSwitchOffHV(self, e):
        self.SwitchHV(HVsysSupply.POWER_OFF)

    def DisplayRampStatus(self, part, progress, value):
        logging.info("DisplayRampStatus: %d", value)
        status = HVStatus(value)
        for ch in range(1,11):
            description = status.channel_description(ch)
            self.m_gridHV.SetCellValue(ch-1, GRID_COLUMN_STATE, description)
            if status.is_ramp():
                description = description + '  ' + '#' * progress
            self.m_statusBar1.SetStatusText(description)

        if not status.is_ramp(): # so its finished
            if len(self.activeModuleId) == 1:
                self.pollModule(self.activeModuleId[0])
            self.UpdateModuleGrid()


    def OnSelectModuleFromGrid(self,e):
        theButton = e.GetEventObject()
        moduleId = theButton.myname
        print("OnSelectModule: %s" % moduleId)
        self.SelectModule(moduleId)
        
    def getPartNameByCap(self, cap:str):
        if cap in self.hvControls:
            return 'hv'
        elif cap in self.ledControls:
            return 'led'
        else:
            raise ValueError('getPartNameByCap: unknown cap '+cap)



    def OnKillFocus(self,e):
        field = e.GetEventObject()
        cap = field.myname
        text_value = field.GetValue()
        logging.debug("OnKillFocus: requested %s = %s" % (cap, text_value))

        bus_id = self.config.modules[self.activeModuleId].bus_id
        part_name = self.getPartNameByCap(cap)
        module_config = self.config.modules[self.activeModuleId]
        part_address = int(module_config.address(part_name))
        part = detector.buses[bus_id].getPart(part_address) 
        reg_value = part.valueFromString(cap, text_value)
        logging.debug("OnKillFocus: translated to %s" % (reg_value))
        command = Message(Message.WRITE_SHORT, part_address, part, cap, reg_value)
        logging.warning('HV setting!')
        asyncio.get_event_loop().create_task(detector.add_task(bus_id, command, part, print))

                
    def set_tri_state(self, checkbox, count, total):
        if count == 0:
            self.m_checkBoxOnline.Set3StateValue( wx.CHK_UNCHECKED )
        elif count == total:
            self.m_checkBoxOnline.Set3StateValue( wx.CHK_CHECKED )
        else:
            self.m_checkBoxOnline.Set3StateValue( wx.CHK_UNDETERMINED )



    def SelectModule(self, module_ids):
        print("SelectModule: %s" % (module_ids))
        self.activeModuleId = module_ids

        if type(module_ids) is not list:
            module_ids = [module_ids] # behave you scalar!!

        if len(module_ids) > 1:
            # multiple module select
            logging.debug("hide all parts")
            for panel in [self.m_collapsiblePaneDebug]:
                panel.Collapse()
#                panel.Disable()

            n_selected = len(module_ids)
            n_online = len([id for id in module_ids if self.config.modules[id].online])
            n_hv_on = 0 #TODO
            self.set_tri_state(self.m_checkBoxOnline, n_online, n_selected)
            self.set_tri_state(self.m_checkBoxPoll, n_online, n_selected)

            self.m_staticTextRightCaption.SetLabelText( "Modules %s " % (', '.join(module_ids)) )

                
        elif len(module_ids) == 1:
            module_id = module_ids[0] # behave you vector!! lol

            listIndex = self.config.modulesOrderedById.index(module_id)
            self.m_gridModules.SelectRow( listIndex )
            self.m_gridModules.MakeCellVisible( listIndex, 0 )

            for button in self.m_moduleMiniButtons.values():
                if button.myname == module_id: 
                    button.SetFont(wx.Font(wx.FontInfo(12).Bold()))
                else:
                    button.SetFont(wx.Font(wx.FontInfo(12)))

            moduleConfig = self.config.modules[module_id]
            partsText = ', '.join(
                ["%s=%d" % (p, moduleConfig.address(p)) for p in moduleConfig.parts]
            )
            self.m_staticTextRightCaption.SetLabelText("Module %s [%s]" % (moduleConfig.id, partsText))

            self.m_checkBoxOnline.Set3StateValue(wx.CHK_CHECKED if moduleConfig.online else wx.CHK_UNCHECKED)

            self.m_collapsiblePaneDebug.Enable()
            self.m_collapsiblePaneDebug.Collapse(True)
            #self.textLedFrequencyRef.SetValue(str(moduleConfig.ledFrequency))
            
            self.m_listBoxParts.Clear() #AAA
            for part in moduleConfig.parts:
                self.m_listBoxParts.Append(part)
                #self.m_listBoxParts.SetClientData(index, address)

            self.m_checkBoxOnline.SetValue( moduleConfig.online )
            self.m_checkBoxPoll.SetValue( moduleConfig.online )

            if moduleConfig.online:
                self.pollModule(module_id)
            else:
                logging.info("Selected module offline, no polling")


    def pollModule(self, moduleId, callback=None):
        moduleConfig = self.config.modules[moduleId]
#        for part in moduleConfig.parts:
        if callback is None:
            callback = self.DisplayValueOnComplete
        elif callback == False:
            callback = lambda *args: None  # empty callback; do nothing
        return asyncio.get_event_loop().create_task(detector.poll_module_important(moduleId, callback))

    def DisplayValueOnComplete(self, part, capability, value):
        
        print("DisplayValueOnComplete: %s=%s"%(capability, value))

        str_value = part.valueToString(capability, value)

        if type(part) in [HVsysSupply, HVsysSupply800c]:
            if capability in hv_grid_coords:
                self.m_gridHV.SetCellValue(hv_grid_coords[capability], str_value)

            if  capability == 'STATUS':
                status = HVStatus(value)
                is_on = status.is_on()
                self.m_checkBoxHvOn.SetValue( is_on )
        elif type(part) is HVsysLED:
            if capability in led_grid_coords:
                self.m_gridLED.SetCellValue(led_grid_coords[capability], str_value)

            if capability == 'AUTOREG':   
                is_on = (value > 0)
                self.m_checkBoxLedAuto.SetValue( is_on )
        
        self.UpdateModuleGrid()  # will switch off if this gets too heavy
        self.m_statusBar1.SetStatusText('TODO: %d'%(detector.queue_length()), 1)

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

    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(datetime.datetime.now().strftime('logs/dcs_log_%Y-%m-%d-%H-%M-%S.txt'))
        ]    
    )

    configuration = config.load("config/PsdSlowControlConfig.xml", schema="config/PsdSlowControlConfig.xsd")

    detector = Detector(configuration)


    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handler)
    
    try:
        print("Staring bus listeners...")
        for id, sm in detector.buses.items():
            await loop.create_task(sm.connect())
            loop.create_task(sm.send())
    except OSError as e:
        print("Cannot connect to system module: %s"%(str(e)))  

    print("Module link ok")
    
    app = WxAsyncApp(False)
    frame = MainWindow(None, "FHcal DCS")
    await frame.pollOnlineModules()
    await app.MainLoop()


if __name__ == '__main__':
    #asyncio.run(main(), debug=True)
    print("Staring main loop...")
    asyncio.get_event_loop().run_until_complete(asyncio.wait([main()]))
    #asyncio.get_event_loop().run_until_complete(app.MainLoop())
