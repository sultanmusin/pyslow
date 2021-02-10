# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Feb  8 2021)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class MainWindow
###########################################################################

class MainWindow ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"FHCal DCS", pos = wx.DefaultPosition, size = wx.Size( 1200,1000 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_statusBar1 = self.CreateStatusBar( 5, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menuFile = wx.Menu()
        self.m_menuItem1 = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Open", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuItem1 )

        self.m_menuItem2 = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Save", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuItem2 )

        self.m_menuItem3 = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"&Preferences", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuItem3 )

        self.m_menuItem4 = wx.MenuItem( self.m_menuFile, wx.ID_ANY, u"E&xit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuFile.Append( self.m_menuItem4 )

        self.m_menubar1.Append( self.m_menuFile, u"&File" )

        self.m_menuHelp = wx.Menu()
        self.m_menuItem5 = wx.MenuItem( self.m_menuHelp, wx.ID_ANY, u"A&bout", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menuHelp.Append( self.m_menuItem5 )

        self.m_menubar1.Append( self.m_menuHelp, u"&Help" )

        self.SetMenuBar( self.m_menubar1 )

        bSizerMain = wx.BoxSizer( wx.HORIZONTAL )

        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_THEME|wx.TAB_TRAVERSAL )
        self.m_panel1.SetMaxSize( wx.Size( 400,-1 ) )

        bSizerLeft = wx.BoxSizer( wx.VERTICAL )

        self.m_staticTextLeftCaption = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Detector Map", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextLeftCaption.Wrap( -1 )

        bSizerLeft.Add( self.m_staticTextLeftCaption, 0, wx.ALL, 5 )

        m_checkListModulesChoices = []
        self.m_checkListModules = wx.CheckListBox( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkListModulesChoices, 0 )
        bSizerLeft.Add( self.m_checkListModules, 0, wx.ALL|wx.EXPAND, 5 )

        fgSizerModuleGrid = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizerModuleGrid.SetFlexibleDirection( wx.BOTH )
        fgSizerModuleGrid.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        bSizerLeft.Add( fgSizerModuleGrid, 1, wx.EXPAND, 5 )


        self.m_panel1.SetSizer( bSizerLeft )
        self.m_panel1.Layout()
        bSizerLeft.Fit( self.m_panel1 )
        bSizerMain.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )

        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_THEME|wx.TAB_TRAVERSAL )
        bSizerRight = wx.BoxSizer( wx.VERTICAL )

        self.m_staticTextRightCaption = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Module #", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticTextRightCaption.Wrap( -1 )

        bSizerRight.Add( self.m_staticTextRightCaption, 0, wx.ALL, 5 )

        self.m_collapsiblePaneMulti = wx.CollapsiblePane( self.m_panel2, wx.ID_ANY, u"Module Control", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE )
        self.m_collapsiblePaneMulti.Collapse( False )

        bSizerMulti = wx.BoxSizer( wx.VERTICAL )

        self.m_checkBoxOnline = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"Online", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxOnline, 0, wx.ALL, 5 )

        self.m_checkBoxHvOn = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"HV ON", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxHvOn, 0, wx.ALL, 5 )

        self.m_checkBoxLedOn = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"LED ON", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxLedOn, 0, wx.ALL, 5 )

        self.m_checkBoxPoll = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"Poll", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxPoll, 0, wx.ALL, 5 )

        self.m_checkBoxTemperatureControl = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"Temperature Control", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxTemperatureControl, 0, wx.ALL, 5 )

        self.m_checkBoxAlertsEnabled = wx.CheckBox( self.m_collapsiblePaneMulti.GetPane(), wx.ID_ANY, u"Alerts Enabled", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerMulti.Add( self.m_checkBoxAlertsEnabled, 0, wx.ALL, 5 )


        self.m_collapsiblePaneMulti.GetPane().SetSizer( bSizerMulti )
        self.m_collapsiblePaneMulti.GetPane().Layout()
        bSizerMulti.Fit( self.m_collapsiblePaneMulti.GetPane() )
        bSizerRight.Add( self.m_collapsiblePaneMulti, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_collapsiblePaneHV = wx.CollapsiblePane( self.m_panel2, wx.ID_ANY, u"High Voltage", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE )
        self.m_collapsiblePaneHV.Collapse( False )

        bSizerHV = wx.BoxSizer( wx.VERTICAL )

        self.m_gridHV = wx.grid.Grid( self.m_collapsiblePaneHV.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridHV.CreateGrid( 11, 4 )
        self.m_gridHV.EnableEditing( True )
        self.m_gridHV.EnableGridLines( True )
        self.m_gridHV.EnableDragGridSize( False )
        self.m_gridHV.SetMargins( 0, 0 )

        # Columns
        self.m_gridHV.EnableDragColMove( False )
        self.m_gridHV.EnableDragColSize( True )
        self.m_gridHV.SetColLabelValue( 0, u"Reference" )
        self.m_gridHV.SetColLabelValue( 1, u"Set" )
        self.m_gridHV.SetColLabelValue( 2, u"Measured" )
        self.m_gridHV.SetColLabelValue( 3, u"State" )
        self.m_gridHV.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.m_gridHV.EnableDragRowSize( False )
        self.m_gridHV.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.m_gridHV.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizerHV.Add( self.m_gridHV, 0, wx.ALL, 5 )


        self.m_collapsiblePaneHV.GetPane().SetSizer( bSizerHV )
        self.m_collapsiblePaneHV.GetPane().Layout()
        bSizerHV.Fit( self.m_collapsiblePaneHV.GetPane() )
        bSizerRight.Add( self.m_collapsiblePaneHV, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_collapsiblePaneLED = wx.CollapsiblePane( self.m_panel2, wx.ID_ANY, u"LED Control", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE )
        self.m_collapsiblePaneLED.Collapse( False )

        bSizerLED = wx.BoxSizer( wx.VERTICAL )

        self.m_gridLED = wx.grid.Grid( self.m_collapsiblePaneLED.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridLED.CreateGrid( 5, 5 )
        self.m_gridLED.EnableEditing( True )
        self.m_gridLED.EnableGridLines( True )
        self.m_gridLED.EnableDragGridSize( False )
        self.m_gridLED.SetMargins( 0, 0 )

        # Columns
        self.m_gridLED.EnableDragColMove( False )
        self.m_gridLED.EnableDragColSize( True )
        self.m_gridLED.SetColLabelValue( 0, u"Reference" )
        self.m_gridLED.SetColLabelValue( 1, u"Set" )
        self.m_gridLED.SetColLabelValue( 2, u"Measured" )
        self.m_gridLED.SetColLabelValue( 3, u"State" )
        self.m_gridLED.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.m_gridLED.EnableDragRowSize( True )
        self.m_gridLED.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.m_gridLED.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizerLED.Add( self.m_gridLED, 0, wx.ALL, 5 )

        self.m_toggleBtn7 = wx.ToggleButton( self.m_collapsiblePaneLED.GetPane(), wx.ID_ANY, u"LED ON", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_toggleBtn7.SetValue( True )
        bSizerLED.Add( self.m_toggleBtn7, 0, wx.ALL, 5 )


        self.m_collapsiblePaneLED.GetPane().SetSizer( bSizerLED )
        self.m_collapsiblePaneLED.GetPane().Layout()
        bSizerLED.Fit( self.m_collapsiblePaneLED.GetPane() )
        bSizerRight.Add( self.m_collapsiblePaneLED, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_collapsiblePaneDebug = wx.CollapsiblePane( self.m_panel2, wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE )
        self.m_collapsiblePaneDebug.Collapse( True )

        bSizerDebug = wx.BoxSizer( wx.HORIZONTAL )

        m_listBox1Choices = []
        self.m_listBox1 = wx.ListBox( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, 0 )
        bSizerDebug.Add( self.m_listBox1, 0, wx.ALL, 5 )

        m_listBox2Choices = []
        self.m_listBox2 = wx.ListBox( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox2Choices, 0 )
        bSizerDebug.Add( self.m_listBox2, 0, wx.ALL, 5 )

        self.m_textCtrl1 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

        self.m_button1 = wx.Button( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_textCtrl2 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl2, 0, wx.ALL, 5 )

        self.m_button2 = wx.Button( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_button2, 0, wx.ALL, 5 )

        self.m_textCtrl3 = wx.TextCtrl( self.m_collapsiblePaneDebug.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizerDebug.Add( self.m_textCtrl3, 0, wx.ALL, 5 )


        self.m_collapsiblePaneDebug.GetPane().SetSizer( bSizerDebug )
        self.m_collapsiblePaneDebug.GetPane().Layout()
        bSizerDebug.Fit( self.m_collapsiblePaneDebug.GetPane() )
        bSizerRight.Add( self.m_collapsiblePaneDebug, 0, wx.ALL|wx.EXPAND, 5 )


        self.m_panel2.SetSizer( bSizerRight )
        self.m_panel2.Layout()
        bSizerRight.Fit( self.m_panel2 )
        bSizerMain.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_gridHV.Bind( wx.grid.EVT_GRID_CELL_CHANGING, self.OnHVGridChange )




        N_SEC = 10
        N_COL = 4

        self.m_gridHV.SetDefaultEditor(wx.grid.GridCellFloatEditor(width=3, precision=1))
        for row in range(N_SEC):
            self.m_gridHV.SetRowLabelValue(row, "Section %d"%(row+1))
            for col in range(N_COL):
                self.m_gridHV.SetReadOnly(row, col, True)
                self.m_gridHV.SetCellValue(row, col, "0.0")

            self.m_gridHV.SetReadOnly(row, 1, False)
            self.m_gridHV.SetCellValue(row, 3, "OK")

        self.m_gridHV.SetRowLabelValue(N_SEC, "Pedestal")
        for col in range(N_COL):
            self.m_gridHV.SetReadOnly(N_SEC, col, True)
            self.m_gridHV.SetCellValue(N_SEC, col, "0.0")

        self.m_gridHV.SetReadOnly(N_SEC, 1, False)
        self.m_gridHV.SetCellValue(N_SEC, 3, "")


    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def OnHVGridChange( self, event ):
        print(event.GetString())
        event.Skip()




app = wx.App()
frame = MainWindow(None)
frame.Show(True)
app.MainLoop()
