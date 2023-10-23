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
import getopt
import functools
import logging
import os
import qasync
from qasync import asyncSlot, asyncClose, QApplication
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QKeySequence, QImage, QPixmap, QIcon
from PyQt5.QtCore import QItemSelectionModel, QTimer, Qt, QByteArray

import string
import sys

sys.path.append('.')
sys.path.append('lib/hvsys')
import config
from message import Message
from detector import *
from hvsyssupply import HVsysSupply
from hvsyssupply800c import HVsysSupply800c
from hvsyswall import HVsysWall
from hvsysled import HVsysLED
from hvstatus import HVStatus

COLOR_OFFLINE = QColor(192,192,192)
COLOR_HV_OFF = QColor(224,224,96)
COLOR_RAMP = QColor(96,96,224)
COLOR_ERROR = QColor(224,48,48)
COLOR_NOT_REFERENCE = QColor(224,48,224)
COLOR_OK = QColor(128,224,48)
COLOR_ONLINE = QColor(128,224,48)
COLOR_WHITE = QColor(255,255,255)

GRID_COLUMN_ONLINE = 0
GRID_COLUMN_HV_ON = 1
GRID_COLUMN_LEFT_STATE = 2

# HV grid legend

N_SECTIONS = 16
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

GRID_COLUMN_REQUESTED_LED = 0
GRID_COLUMN_SET_LED = 1
GRID_COLUMN_MEAS_LED = 2
GRID_COLUMN_STATE_LED = 3
GRID_COLUMNS_LED = 4

# All grids column legend
GRID_COLUMN_FILE = 0
GRID_COLUMN_REFERENCE = 1
GRID_COLUMN_CORRECTED = 2
GRID_COLUMN_MEAS = 3
GRID_COLUMN_STATE = 4
GRID_COLUMNS = 5

hv_grid_coords = {
    "1/REF_VOLTAGE": (0,GRID_COLUMN_REFERENCE),
    "2/REF_VOLTAGE": (1,GRID_COLUMN_REFERENCE),
    "3/REF_VOLTAGE": (2,GRID_COLUMN_REFERENCE),
    "4/REF_VOLTAGE": (3,GRID_COLUMN_REFERENCE),
    "5/REF_VOLTAGE": (4,GRID_COLUMN_REFERENCE),
    "6/REF_VOLTAGE": (5,GRID_COLUMN_REFERENCE),
    "7/REF_VOLTAGE": (6,GRID_COLUMN_REFERENCE),
    "8/REF_VOLTAGE": (7,GRID_COLUMN_REFERENCE),
    "9/REF_VOLTAGE": (8,GRID_COLUMN_REFERENCE),
    "10/REF_VOLTAGE": (9,GRID_COLUMN_REFERENCE),
    "11/REF_VOLTAGE": (10,GRID_COLUMN_REFERENCE),
    "12/REF_VOLTAGE": (11,GRID_COLUMN_REFERENCE),
    "13/REF_VOLTAGE": (12,GRID_COLUMN_REFERENCE),
    "14/REF_VOLTAGE": (13,GRID_COLUMN_REFERENCE),
    "15/REF_VOLTAGE": (14,GRID_COLUMN_REFERENCE),
    "16/REF_VOLTAGE": (15,GRID_COLUMN_REFERENCE),
    "REF_PEDESTAL_VOLTAGE": (GRID_ROW_PEDESTAL,GRID_COLUMN_REFERENCE),
    "1/CORR_VOLTAGE": (0,GRID_COLUMN_CORRECTED),
    "2/CORR_VOLTAGE": (1,GRID_COLUMN_CORRECTED),
    "3/CORR_VOLTAGE": (2,GRID_COLUMN_CORRECTED),
    "4/CORR_VOLTAGE": (3,GRID_COLUMN_CORRECTED),
    "5/CORR_VOLTAGE": (4,GRID_COLUMN_CORRECTED),
    "6/CORR_VOLTAGE": (5,GRID_COLUMN_CORRECTED),
    "7/CORR_VOLTAGE": (6,GRID_COLUMN_CORRECTED),
    "8/CORR_VOLTAGE": (7,GRID_COLUMN_CORRECTED),
    "9/CORR_VOLTAGE": (8,GRID_COLUMN_CORRECTED),
    "10/CORR_VOLTAGE": (9,GRID_COLUMN_CORRECTED),
    "11/CORR_VOLTAGE": (10,GRID_COLUMN_CORRECTED),
    "12/CORR_VOLTAGE": (11,GRID_COLUMN_CORRECTED),
    "13/CORR_VOLTAGE": (12,GRID_COLUMN_CORRECTED),
    "14/CORR_VOLTAGE": (13,GRID_COLUMN_CORRECTED),
    "15/CORR_VOLTAGE": (14,GRID_COLUMN_CORRECTED),
    "16/CORR_VOLTAGE": (15,GRID_COLUMN_CORRECTED),
    "CORR_PEDESTAL_VOLTAGE": (GRID_ROW_PEDESTAL,GRID_COLUMN_CORRECTED),
    "TEMPERATURE": (GRID_ROW_TEMPERATURE,GRID_COLUMN_MEAS),
    "1/MEAS_VOLTAGE": (0,GRID_COLUMN_MEAS),
    "2/MEAS_VOLTAGE": (1,GRID_COLUMN_MEAS),
    "3/MEAS_VOLTAGE": (2,GRID_COLUMN_MEAS),
    "4/MEAS_VOLTAGE": (3,GRID_COLUMN_MEAS),
    "5/MEAS_VOLTAGE": (4,GRID_COLUMN_MEAS),
    "6/MEAS_VOLTAGE": (5,GRID_COLUMN_MEAS),
    "7/MEAS_VOLTAGE": (6,GRID_COLUMN_MEAS),
    "8/MEAS_VOLTAGE": (7,GRID_COLUMN_MEAS),
    "9/MEAS_VOLTAGE": (8,GRID_COLUMN_MEAS),
    "10/MEAS_VOLTAGE": (9,GRID_COLUMN_MEAS),        
    "11/MEAS_VOLTAGE": (10,GRID_COLUMN_MEAS),        
    "12/MEAS_VOLTAGE": (11,GRID_COLUMN_MEAS),        
    "13/MEAS_VOLTAGE": (12,GRID_COLUMN_MEAS),        
    "14/MEAS_VOLTAGE": (13,GRID_COLUMN_MEAS),        
    "15/MEAS_VOLTAGE": (14,GRID_COLUMN_MEAS),        
    "16/MEAS_VOLTAGE": (15,GRID_COLUMN_MEAS),        
    "MEAS_PEDESTAL_VOLTAGE": (GRID_ROW_PEDESTAL,GRID_COLUMN_MEAS),
}

capability_by_hv_grid_coords = {val : key for key, val in hv_grid_coords.items()}

led_grid_coords = {
    "SET_FREQUENCY": (GRID_ROW_FREQUENCY,GRID_COLUMN_REFERENCE),
    "SET_AMPLITUDE": (GRID_ROW_AMPLITUDE,GRID_COLUMN_REFERENCE),
    "ADC_SET_POINT": (GRID_ROW_ADC_SET_POINT,GRID_COLUMN_REFERENCE),
    "AVERAGE_POINTS": (GRID_ROW_AVERAGE_POINTS,GRID_COLUMN_REFERENCE),
    "AUTOREG": (GRID_ROW_AUTOREG,GRID_COLUMN_REFERENCE),
    "AVERAGE_ADC": (GRID_ROW_AVERAGE_ADC,GRID_COLUMN_REFERENCE),
}

capability_by_led_grid_coords = {val : key for key, val in led_grid_coords.items()}

MODULE_LIST_HEADERS = ['Online', 'HV ON', 'State', 'hv id', 'led id']


class CallbackHandler(logging.StreamHandler):
    def __init__(self, cb):
        logging.StreamHandler.__init__(self)
        self.cb = cb

    def emit(self, record):
        if record.levelno >= 30:
            msg = record.levelname + ': ' + self.format(record)
            self.cb(msg)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config):
        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('main.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        self.dirname = ''
        self.CONFIG_EDIT_MODE = False

        self.config = config
        self.detector = Detector(self.config)

        self.ApplyConfigToLayout()

        # select first online module (if any...)
        self.SelectFirstOnlineModule()
        self.ShowReferenceParameters()
        self.pollAllStatus()
        #self.pollAllTemperature(False) # no callbacks
        #self.SetReferenceParameters()
        #self.UpdateModuleGrid()

    def onEditModeToggled(self):
        if self.CONFIG_EDIT_MODE:
            self.onEditModeOff()
        else:
            self.onEditModeOn()

    def onEditModeOn(self):
        print('Turning on edit mode')
        self.CONFIG_EDIT_MODE = True
        self.moduleList.setColumnCount(5)
        self.moduleList.setHorizontalHeaderLabels(MODULE_LIST_HEADERS)
        self.expandModuleListTableOnEditMode()

    def onEditModeOff(self):
        self.CONFIG_EDIT_MODE = False
        print('Turning off edit mode')
        self.moduleList.setColumnCount(3)
        self.moduleList.setHorizontalHeaderLabels(MODULE_LIST_HEADERS[:3])


    def expandModuleListTableOnEditMode(self):
        for module_id, (title, module) in enumerate(self.config.modules.items()):
            self.moduleList.setItem(module_id, 3, QtWidgets.QTableWidgetItem(f"{module.addr['hv']}"))
            # self.moduleList.item(module_id, 3).setFlags(~Qt.ItemIsEditable)
            self.moduleList.setItem(module_id, 4, QtWidgets.QTableWidgetItem(f"{module.addr['led']}"))
            # self.moduleList.item(module_id, 4).setFlags(~Qt.ItemIsEditable)

    def OnLogMessage(self, msg):
        self.logArea.setTextColor(COLOR_WHITE)
        self.logArea.setTextBackgroundColor(COLOR_ERROR)
        self.logArea.setText(msg)

    def OnResetLogMessage(self, msg):
        self.logArea.setText("")


    def SelectFirstOnlineModule(self):
        for m in self.config.modules.values():
            if m.online:
                self.SelectModule([m.id])
                break


    def ApplyConfigToLayout(self):
        self.setWindowTitle(self.config.title)
        self.logo = self.findChild(QtWidgets.QLabel, 'logo') 
        #s = "iVBORw0KGgoAAAANSUhEUgAAAlgAAABkCAYAAABaQU4jAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAABblJREFUeF7t3M1RwkAYBmDuXjzqgXiyARuwAiugAzuwBwdwxps10ARd0EwiX2AxxKCEmRB+Hmcy4yTLZvMsh3c2HzsY+CNAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECDQu8DtZ3GTfRRPXQ4k+r9/zx+r92g61+UY9E2AAAECBAgQOJrAcJq/ZdOi6DJkZZN8sTzmWwGr4dzRHtqNCBAgQIAAAQJdCghYXerqmwABAgQIELhKAQHrKqfdQxMgQIAAAQJdCtQDVtRKxevCfV4ZDsf5XWpbr7H673Vg02vDLp9T3wQIECBAgACBowmkgPUwKZ6Hk3xW1mOlI+qkdhTAl23j+nb7eVN7NVhHm043IkCAAAECBE5BYLOCtS46z6b5KEJS5fxWcXqMOQrWI1gtQ9ZXWsGq9hMrW1awTmF2jYEAAQIECBDoRWCfIFVdlUrtI1zVB5yN89d18JoJWL1Mp5sSIECAAAECpyDwV5F7WqmqBqx0blfN1fp14ELAOoXZNQYCBAgQIECgF4EDAtaq7ipeEzYf5fVqAFOD1cvUuikBAgQIECDQl0AHAasMXgJWXzPqvgQIECBAgEDvAgcFrGVBfJuBW8Fqo6UtAQIECBAgcPYCbQPWz1YO+ajp4aO/OKrXBKyz/5p4AAIECBAgQKCNQNuAFftlpRqsX9sx+BVhG3ptCRAgQIAAgUsVaBuwwqHc/2pV6L6I/8tVq7RJ6fJc/ReGVrAu9dvjuQgQIECAAIFGgXLvqlpRempYBqnd1142u7mvNildha3aJqPrQDar75sVn23aS8s0ESBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBwrQLfmeUk6E23pFsAAAAASUVORK5CYII="
        if self.config.logo is not None:
            by = QByteArray.fromBase64(self.config.logo.encode("ascii"))
            image = QImage.fromData(by, "PNG")
            pixmap = QPixmap.fromImage(image)
            self.logo.setPixmap(pixmap)
            self.logo.show() 
            self.setWindowIcon(QIcon(pixmap))

        #TODO statusbar
        #TODO menu events

        self.shortcut_refresh = QtWidgets.QShortcut(QKeySequence('F5'), self)
        self.shortcut_refresh.activated.connect(self.on_refresh)
        self.shortcut_refresh2 = QtWidgets.QShortcut(QKeySequence('Ctrl+R'), self)
        self.shortcut_refresh2.activated.connect(self.on_refresh)

        self.buttonSelectAll = self.findChild(QtWidgets.QPushButton, 'buttonSelectAll') 
        self.buttonSelectAll.clicked.connect(self.buttonSelectAllPressed) 

        self.moduleList = self.findChild(QtWidgets.QTableWidget, 'moduleList') 
        self.moduleList.setColumnCount(3)
        self.moduleList.setHorizontalHeaderLabels(MODULE_LIST_HEADERS[:3])

        self.moduleList.setRowCount(len(self.config.modules))
        self.moduleList.setVerticalHeaderLabels([f'Module {id}' for id in self.config.modules])

        self.moduleList.itemSelectionChanged.connect(self.moduleListSelectionChanged)
        vh = self.moduleList.verticalHeader()
        vhi = self.moduleList.verticalHeaderItem(0)
        vh.sectionClicked.connect(self.moduleListHeaderClicked)

        self.moduleGrid = self.findChild(QtWidgets.QTableWidget, 'moduleGrid') 
        self.moduleGrid.setRowCount(self.config.geom_height)
        self.moduleGrid.setColumnCount(self.config.geom_width)
        self.moduleGrid.horizontalHeader().setDefaultSectionSize(int(self.moduleGrid.width() / self.config.geom_width - 1))
        self.moduleGrid.verticalHeader().setDefaultSectionSize(int(self.moduleGrid.height() / self.config.geom_height - 1))

        self.moduleGrid.itemSelectionChanged.connect(self.moduleGridSelectionChanged)

        for index, (title, config) in enumerate(self.config.modules.items()):
            self.moduleList.setItem(index, GRID_COLUMN_ONLINE, QtWidgets.QTableWidgetItem("⬤")) 
            self.moduleList.item(index, GRID_COLUMN_ONLINE).setForeground(QBrush(COLOR_ONLINE if config.online else COLOR_OFFLINE))
            self.moduleList.setItem(index, GRID_COLUMN_HV_ON, QtWidgets.QTableWidgetItem("⬤")) 
            self.moduleList.item(index,GRID_COLUMN_HV_ON).setForeground(QBrush(COLOR_OFFLINE))
            self.moduleList.setItem(index, GRID_COLUMN_LEFT_STATE, QtWidgets.QTableWidgetItem("⬤")) 
            self.moduleList.item(index,GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_OFFLINE))

            item = QtWidgets.QTableWidgetItem(title)
            item.setTextAlignment(Qt.AlignCenter)
            self.moduleGrid.setItem(config.y, config.x, QtWidgets.QTableWidgetItem(item))

        self.busGrid = self.findChild(QtWidgets.QTableWidget, 'busGrid') 
        self.busGrid.setColumnCount(4)
        self.busGrid.setHorizontalHeaderLabels(['Address', 'Queue', 'Link', 'Latency'])
        self.busGrid.setRowCount(len(self.config.buses))
        self.busGrid.setVerticalHeaderLabels([id for id in self.config.buses])

        self.busTimers = {}

        for index, (title, config) in enumerate(self.config.buses.items()):
            self.busGrid.setItem(index, 0, QtWidgets.QTableWidgetItem(f" {config.host}:{config.port} ")) 
            self.busGrid.setItem(index, 1, QtWidgets.QTableWidgetItem("0")) 
            self.busGrid.setItem(index, GRID_COLUMN_LEFT_STATE, QtWidgets.QTableWidgetItem("⬤")) 
            self.busGrid.setItem(index, 3, QtWidgets.QTableWidgetItem("")) 
            self.busGrid.item(index,2).setForeground(QBrush(COLOR_OFFLINE))
            self.busTimers[title] = QTimer()
            self.busTimers[title].timeout.connect(self.busTimerFired)
            self.busTimers[title].setProperty('bus_id', title)

        self.busGrid.resizeColumnsToContents()
        
        self.groupBoxControl = self.findChild(QtWidgets.QGroupBox, 'groupBoxControl') 

        self.checkBoxOnline = self.findChild(QtWidgets.QCheckBox, 'checkBoxOnline') 
        self.checkBoxHvOn = self.findChild(QtWidgets.QCheckBox, 'checkBoxHvOn') 
        self.checkBoxPoll = self.findChild(QtWidgets.QCheckBox, 'checkBoxPoll') 
        self.checkBoxPoll.stateChanged.connect(self.OnCheckBoxPollChanged)
        self.checkBoxLedAuto = self.findChild(QtWidgets.QCheckBox, 'checkBoxLedAuto') 
        self.checkBoxTemperatureControl = self.findChild(QtWidgets.QCheckBox, 'checkBoxTemperatureControl') 
        self.labelLastCorrection = self.findChild(QtWidgets.QLabel, 'labelLastCorrection') 
        self.labelNextCorrection = self.findChild(QtWidgets.QLabel, 'labelNextCorrection') 
        self.spinBoxCorrectionInterval = self.findChild(QtWidgets.QSpinBox, 'spinBoxCorrectionInterval') 
        self.spinBoxCorrectionInterval.setValue(self.config.query_delay)
        self.spinBoxCorrectionInterval.valueChanged.connect(self.spinBoxCorrectionIntervalValueChanged)


        self.buttonApplyReferenceHV = self.findChild(QtWidgets.QPushButton, 'buttonApplyReferenceHV') 
        self.buttonApplyReferenceHV.clicked.connect(self.buttonApplyReferenceHVPressed) 

        self.buttonStartAdjust = self.findChild(QtWidgets.QPushButton, 'buttonStartAdjust') 
        self.buttonStartAdjust.clicked.connect(self.buttonStartAdjustPressed) 

        self.spinBoxAdjust = self.findChild(QtWidgets.QDoubleSpinBox, 'spinBoxAdjust') 
        self.spinBoxAdjust.valueChanged.connect(self.spinBoxAdjustValueChanged)

        self.buttonFinishAdjust = self.findChild(QtWidgets.QPushButton, 'buttonFinishAdjust') 
        self.buttonFinishAdjust.clicked.connect(self.buttonFinishAdjustPressed) 

        self.buttonCancelAdjust = self.findChild(QtWidgets.QPushButton, 'buttonCancelAdjust') 
        self.buttonCancelAdjust.clicked.connect(self.buttonCancelAdjustPressed) 
        # also run in once to hide appropriate interface parts
        self.buttonCancelAdjustPressed()

        self.buttonSetHvOn = self.findChild(QtWidgets.QPushButton, 'buttonSetHvOn') 
        self.buttonSetHvOn.clicked.connect(self.buttonSetHvOnPressed) 

        self.buttonSetHvOff = self.findChild(QtWidgets.QPushButton, 'buttonSetHvOff') 
        self.buttonSetHvOff.clicked.connect(self.buttonSetHvOffPressed) 

        self.tableHV = self.findChild(QtWidgets.QTableWidget, 'tableHV') 
        self.tableHV.setHorizontalHeaderLabels(['Reference', 'Requested', 'Corrected', 'Measured', 'State'])
        #self.tableHV.setRowCount(len(self.config.modules))
        self.tableHV.setVerticalHeaderLabels(self.config.modules)

        # Rows
        self.tableHV.setVerticalHeaderLabels(["Section %d"%(row+1) for row in range(GRID_ROWS_HV-3)] + ['Pedestal', 'Temperature', 'Slope'])

        # Create items, some of them readonly
        for row in range(GRID_ROWS_HV):
            for col in range(GRID_COLUMNS):
                item = QtWidgets.QTableWidgetItem("")
                self.tableHV.setItem(row, col, item)
                if col != 1 or row in [GRID_ROW_TEMPERATURE, GRID_ROW_SLOPE]: 
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            self.tableHV.item(row, GRID_COLUMN_STATE).setText("OK")
        
        self.tableHV.itemChanged.connect(self.tableHVitemChanged)

        self.tableLED = self.findChild(QtWidgets.QTableWidget, 'tableLED') 
        self.tableLED.setHorizontalHeaderLabels(['Requested', 'Set', 'Measured'])
        #self.tableLED.setRowCount(len(self.config.modules))
        self.tableLED.setVerticalHeaderLabels([
            "Frequency", 
            "Amplitude", 
            "ADC Setpoint", 
            "Average points", 
            "Autoregulation on/off", 
            "Average ADC readout" ])

        # Create items, some of them readonly
        for row in range(GRID_ROWS_LED):
            for col in range(GRID_COLUMNS_LED):
                item = QtWidgets.QTableWidgetItem("")
                self.tableLED.setItem(row, col, item)
                if col>0: 
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            self.tableLED.setItem(row, GRID_COLUMN_STATE, QtWidgets.QTableWidgetItem("OK"))
        
        self.tableLED.itemChanged.connect(self.tableLEDitemChanged)

        self.splitter = self.findChild(QtWidgets.QSplitter, 'splitter')
        self.splitter.setSizes([400,600]) 

        self.statusBar = self.findChild(QtWidgets.QStatusBar, 'statusBar') 
        
        self.pollTimer = QTimer()
        self.pollTimer.timeout.connect(self.pollTimerFired)
        if self.config.query_delay > 0:
            self.pollTimer.start(self.config.query_delay * 1000)
            logging.info("First poll timer start!")

        self.guiTimer = QTimer()
        self.guiTimer.timeout.connect(self.guiTimerFired)
        self.guiTimer.start(1000)

        self.logArea = self.findChild(QtWidgets.QTextEdit, 'logArea')
        self.logArea.setText('')
        self.logArea.setReadOnly(True)

        self.pushButtonReset = self.findChild(QtWidgets.QPushButton, 'pushButtonReset')
        self.pushButtonReset.clicked.connect(self.OnResetLogMessage)

        # self.actionChange_config.triggered.connect(self.onEditModeToggled)


    def on_refresh(self):
        if len(self.activeModuleId) == 1:
            self.ShowReferenceParameters()

        for module_id in self.activeModuleId:
            module_config = self.config.modules[module_id]
            if module_config.online:
                self.pollModule(module_id)


    def buttonSelectAllPressed(self):
        self.moduleList.selectAll()


    def buttonApplyReferenceHVPressed(self):        
        for module_id in self.activeModuleId:
            module_config = self.config.modules[module_id]
            if module_config.online:
                bus_id = self.config.modules[module_id].bus_id
                if module_config.has('hv'): 
                    part_address = int(self.config.modules[module_id].address('hv'))
                    part = self.detector.buses[bus_id].getPart(part_address) 
                    part.state['REF_PEDESTAL_VOLTAGE'] = module_config.hv_pedestal
                    value = part.valueFromString('SET_PEDESTAL_VOLTAGE', str(module_config.hv_pedestal + part.voltage_correction()))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_PEDESTAL_VOLTAGE', value)
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))

                    for ch, hv in module_config.hv.items():
                        cap = '%s/SET_VOLTAGE'%(ch)
                        value = part.valueFromString(cap, str(hv)) # + part.voltage_correction()))
                        part.state[f'{ch}/REF_VOLTAGE'] = hv
                        command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
                        asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))

                if False: # module_config.has('led'): # disable led settings applying
                    part_address = int(self.config.modules[module_id].address('led'))
                    part = self.detector.buses[bus_id].getPart(part_address) 
                    value = part.valueFromString('AUTOREG', str(module_config.ledAutoTune))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'AUTOREG', value)
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('SET_FREQUENCY', str(module_config.ledFrequency))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_FREQUENCY', value)
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('SET_AMPLITUDE', str(module_config.ledBrightness))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'SET_AMPLITUDE', value)
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                    value = part.valueFromString('ADC_SET_POINT', str(module_config.ledPinADCSet))
                    command = Message(Message.WRITE_SHORT, part_address, part, 'ADC_SET_POINT', value)
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))

        if len(self.activeModuleId) == 1:
            self.ShowReferenceParameters()

        self.UpdateModuleGrid()

    def moduleListHeaderClicked(self, index):
        logging.info(f"clicked: {index}")

    def moduleListSelectionChanged(self):
        selected_rows = list(set([self.moduleList.row(x) for x in self.moduleList.selectedItems()]))
        if len(selected_rows) > 0:
            logging.info("moduleListSelectionChanged: %s"%(selected_rows))
            self.moduleGrid.itemSelectionChanged.disconnect() # temporarily disconnect or we get a loop call and stack overflow
            self.moduleGrid.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            self.moduleGrid.clearSelection()
            for index, (id, config) in enumerate(self.config.modules.items()):
                if index in selected_rows:
                    rng = QtWidgets.QTableWidgetSelectionRange(config.y, config.x, config.y, config.x)
                    self.moduleGrid.setRangeSelected(rng, True)
            self.moduleGrid.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.moduleGrid.itemSelectionChanged.connect(self.moduleGridSelectionChanged) #connect it back
            
            self.moduleGridSelectionChanged()


    def moduleGridSelectionChanged(self):
        selected_modules = [x.text() for x in self.moduleGrid.selectedItems()]
        logging.info("moduleGridSelectionChanged: %s"%(selected_modules))

        self.moduleList.itemSelectionChanged.disconnect() # temporarily disconnect or we get a loop call and stack overflow

        self.moduleList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.moduleList.clearSelection()
        for index, (id, config) in enumerate(self.config.modules.items()):
            if id in selected_modules:
                self.moduleList.selectRow(index)
        self.moduleList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.moduleList.itemSelectionChanged.connect(self.moduleListSelectionChanged) #connect it back
        self.SelectModule(selected_modules)
        self.buttonCancelAdjustPressed()

    def buttonStartAdjustPressed(self):
        self.buttonStartAdjust.hide() 
        self.spinBoxAdjust.show()
        self.buttonFinishAdjust.show()
        self.buttonCancelAdjust.show() 
        self.spinBoxAdjust.setValue(0.0)

    def spinBoxAdjustValueChanged(self):
        pass

    def buttonFinishAdjustPressed(self):
        self.buttonStartAdjust.show() 
        self.spinBoxAdjust.hide()
        self.buttonFinishAdjust.hide()
        self.buttonCancelAdjust.hide() 
        adjustment = float(self.spinBoxAdjust.value())
        logging.info(f"buttonFinishAdjustPressed: {adjustment}")

        for module_id in self.activeModuleId:
            active_module_config = self.config.modules[module_id]
            if active_module_config.has('hv'):
                bus_id = self.config.modules[module_id].bus_id
                part_address = int(self.config.modules[module_id].address('hv'))
                part = self.detector.buses[bus_id].getPart(part_address) 
                old_ped_v = part.state['REF_PEDESTAL_VOLTAGE']
                new_value = float(old_ped_v) + adjustment
                cap = 'REF_PEDESTAL_VOLTAGE' 
                logging.info(f'Adjust: {cap} reference change request, {old_ped_v} --> {new_value}')
                command = part.request_voltage_change(cap, new_value)
                self.ShowReferenceParameters()
                logging.info(f'Sending as: {command}')
                asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                self.pollModule(module_id)


    def buttonCancelAdjustPressed(self):
        self.buttonStartAdjust.show() 
        self.spinBoxAdjust.hide()
        self.buttonFinishAdjust.hide()
        self.buttonCancelAdjust.hide() 
        self.spinBoxAdjust.setValue(0.0)


    def spinBoxCorrectionIntervalValueChanged(self):
        self.config.query_delay = self.spinBoxCorrectionInterval.value()
        if self.config.query_delay > 0: 
            self.pollTimer.start(self.config.query_delay * 1000)
        else:
            self.pollTimer.stop()

    def buttonSetHvOnPressed(self):
        self.SwitchHV(HVsysSupply.POWER_ON)
    

    def buttonSetHvOffPressed(self):
        self.SwitchHV(HVsysSupply.POWER_OFF)


    def tableHVitemChanged(self, item):
        logging.debug(f'Changed: {item.row()} x {item.column()} = {item.text()}')
        module_id = self.activeModuleId[0]
        active_module_config = self.config.modules[module_id]
        if active_module_config.has('hv'):
            bus_id = self.config.modules[module_id].bus_id
            part_address = int(self.config.modules[module_id].address('hv'))
            part = self.detector.buses[bus_id].getPart(part_address) 
            try:
                if item.column() == GRID_COLUMN_REFERENCE and item.row() <= GRID_ROW_PEDESTAL:
                    new_value = float(item.text())
                    section = item.row() + 1
                    cap = 'REF_PEDESTAL_VOLTAGE' if item.row() == GRID_ROW_PEDESTAL else f'{section}/REF_VOLTAGE'
                    logging.info(f'Changed: {cap} reference change request')
                    command = part.request_voltage_change(cap, new_value)
                    self.ShowReferenceParameters()
                    logging.info(f'Sending as: {command}')
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                    self.pollModule(module_id)
                else:
                    logging.info("No action")
            except ValueError as e:
                logging.warning(e)
                self.tableHV.itemChanged.disconnect()  #remove the handler temporarily

                if item.row() == GRID_ROW_PEDESTAL:
                    ped_v = part.state['REF_PEDESTAL_VOLTAGE']
                    item.setText(str(ped_v))
                elif item.row() < N_SECTIONS:
                    ch = item.row()
                    hv = part.state[f'{ch}/REF_VOLTAGE'] 
                    item.setText(str(hv))
                
                self.tableHV.itemChanged.connect(self.tableHVitemChanged)  # ... and restore the handler

    def tableLEDitemChanged(self, item):
        logging.debug(f'LED Changed: {item.row()} x {item.column()} = {item.text()}')
        module_id = self.activeModuleId[0]
        active_module_config = self.config.modules[module_id]
        if active_module_config.has('led'):
            bus_id = self.config.modules[module_id].bus_id
            part_address = int(self.config.modules[module_id].address('led'))
            part = self.detector.buses[bus_id].getPart(part_address) 
            try:
                if item.column() == GRID_COLUMN_REQUESTED_LED:
                    cap = capability_by_led_grid_coords[(item.row(), item.column())]
                    logging.info(f'LED Changed: {cap} reference change request')
                    new_value = part.valueFromString(cap, item.text()) # now just converts str to int
                    part.state[cap] = new_value
                    command = Message(Message.WRITE_SHORT, part_address, part, cap, new_value)
                    self.ShowReferenceParameters()
                    logging.info(f'Sending as: {command}')
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                    self.pollModule(module_id)
                else:
                    logging.info("No action")
            except ValueError as e:
                logging.warning(e)
                self.tableLED.itemChanged.disconnect()  #remove the handler temporarily

                val = part.state[cap]
                item.setText(str(val))
                
                self.tableLED.itemChanged.connect(self.tableLEDitemChanged)  # ... and restore the handler

    def UpdateModuleGrid(self):
        for index, (title, config) in enumerate(self.config.modules.items()):
            self.moduleList.item(index, GRID_COLUMN_ONLINE).setForeground(QBrush(COLOR_ONLINE if config.online is not None else COLOR_OFFLINE))

            if config.has('hv'): 
                bus_id = config.bus_id
                part_address = int(config.address('hv'))
                part = self.detector.buses[bus_id].getPart(part_address) 

                if 'STATUS' in part.state and part.state['STATUS'] is not None:
                    status = HVStatus(part.state['STATUS'])
                    self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setText(str(status))
                    self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setToolTip(str(status))
                    if status.is_on():
                        self.moduleList.item(index, GRID_COLUMN_HV_ON).setForeground(QBrush(COLOR_OK))   
                    else:
                        self.moduleList.item(index, GRID_COLUMN_HV_ON).setForeground(QBrush(COLOR_HV_OFF))    
                    if status.is_error():
                        self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_ERROR))  
                    if not part.has_reference_voltage():
                        self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_NOT_REFERENCE))  
                    if status.is_ramp():
                        self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_RAMP))  

                else:
                    # not polled yet, strange
                    self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setText("unknown" if config.online else "offline")
                    self.moduleList.item(index, GRID_COLUMN_HV_ON).setForeground(QBrush(COLOR_HV_OFF))    
                    self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_OFFLINE))  
            else:
                # no HV 
                self.moduleList.item(index, GRID_COLUMN_HV_ON).setForeground(QBrush(COLOR_HV_OFF))    
                self.moduleList.item(index, GRID_COLUMN_LEFT_STATE).setText("no HV" if config.online else "offline")

    def SelectModule(self, module_ids):
        print("SelectModule: %s" % (module_ids))
        self.activeModuleId = module_ids

        if type(module_ids) is not list:
            module_ids = [module_ids] # behave you scalar!!

        if len(module_ids) > 1:
            # multiple module select
            self.groupBoxHV.hide()
            self.groupBoxLED.hide()

            n_selected = len(module_ids)
            n_online = len([id for id in module_ids if self.config.modules[id].online])
            n_hv_on = 0 #TODO
            self.checkBoxOnline.setChecked(Qt.Unchecked if n_online == 0 else Qt.Checked if n_online == n_selected else Qt.PartiallyChecked)
            self.checkBoxPoll.setChecked(Qt.Unchecked if n_online == 0 else Qt.Checked if n_online == n_selected else Qt.PartiallyChecked)

            self.groupBoxControl.setTitle( "Modules %s " % (', '.join(module_ids)) )
                
        elif len(module_ids) == 1:
            module_id = module_ids[0] # behave you vector!! lol
            self.groupBoxHV.setVisible(self.config.modules[module_id].has('hv'))
            self.groupBoxLED.setVisible(self.config.modules[module_id].has('led'))

            listIndex = self.config.modulesOrderedById.index(module_id)
            self.moduleList.setCurrentCell( listIndex, 0 )

            moduleConfig = self.config.modules[module_id]
            partsText = ', '.join(
                ["%s=%d" % (p, moduleConfig.address(p)) for p in moduleConfig.parts]
            )
            self.groupBoxControl.setTitle("Module %s [%s]" % (moduleConfig.id, partsText))

            if moduleConfig.has('hv'):
                for ch in range(moduleConfig.n_channels):
                    self.tableHV.showRow(ch)
                for ch in range(moduleConfig.n_channels, N_SECTIONS):
                    self.tableHV.hideRow(ch)

            self.checkBoxOnline.setChecked(Qt.Checked if moduleConfig.online else Qt.Unchecked)

            self.checkBoxOnline.setChecked(Qt.Checked if moduleConfig.online else Qt.Unchecked)
            self.checkBoxPoll.setChecked(Qt.Checked if moduleConfig.online else Qt.Unchecked)

            self.ShowReferenceParameters()
            
            if moduleConfig.online:
                self.pollModule(module_id)
            else:
                logging.info("Selected module offline, no polling")

    async def pollOnlineModules(self):
        last_task = None
        for module_id, module_config in self.config.modules.items():
            if module_config.online:
                await self.pollModule(module_id, False)
        


    def pollModule(self, moduleId, callback=None):
        moduleConfig = self.config.modules[moduleId]
#        for part in moduleConfig.parts:
        if callback is None:
            callback = self.DisplayValueOnComplete
        elif callback == False:
            callback = lambda *args: None  # empty callback; do nothing
        return asyncio.get_event_loop().create_task(self.detector.poll_module_important(moduleId, callback))


    def pollAllStatus(self, callback=None):
        if callback is None:
            callback = self.DisplayValueOnComplete
        elif callback == False:
            callback = lambda *args: None  # empty callback; do nothing
        return asyncio.get_event_loop().create_task(self.detector.poll_all_status(callback))


    def pollAllTemperature(self, callback=None):
        if callback is None:
            callback = self.DisplayValueOnComplete
        elif callback == False:
            callback = lambda *args: None  # empty callback; do nothing
        return asyncio.get_event_loop().create_task(self.detector.poll_all_temperature(callback))


    def DisplayValueOnComplete(self, part, capability, value):        
        print("DisplayValueOnComplete: %s=%s"%(capability, value))

        str_value = part.valueToString(capability, value)

        if type(part) in [HVsysSupply, HVsysSupply800c, HVsysWall]:
            self.tableHV.itemChanged.disconnect(self.tableHVitemChanged)  # temporarily disable the handler as we change the table values
            if type(part) is HVsysWall:
                capability = capability.replace('SET', 'MEAS')

            if capability in hv_grid_coords:
                (row, col) = hv_grid_coords[capability] 
                self.tableHV.item(row, col).setText(str_value)
            
            if capability == 'TEMPERATURE':
                self.tableHV.item(GRID_ROW_TEMPERATURE, GRID_COLUMN_MEAS).setText("%.2f °C"%(float(str_value)))
                logging.info('part %s temperature = %s'%(part, str_value))  

                # calculate and display voltage correction (if needed and capable - first times will fail without knowing calibration)
                try:
                    active_module_config = self.config.modules[self.activeModuleId[0]]
                    if active_module_config.has('hv'):
                        correction = float(part.voltage_correction())
                        self.tableHV.item(GRID_ROW_TEMPERATURE, GRID_COLUMN_CORRECTED).setText("%+.2f V"%(float(correction)))
                        for ch in range(1, part.config.n_channels+1):
                            hv = float(part.state[f'{ch}/REF_VOLTAGE'])
                            corrected_hv = round(hv + correction, part.VOLTAGE_DECIMAL_PLACES)
                            self.tableHV.item(int(ch)-1, GRID_COLUMN_CORRECTED).setText(str(corrected_hv))  
                            logging.info("DisplayValueOnComplete temp: desired = %s corrected = %s correction = %s"%(hv, corrected_hv, correction))
                except ValueError as e:
                    pass

            if  capability == 'STATUS':
                status = HVStatus(value)
                self.checkBoxHvOn.setChecked( Qt.Checked if status.is_on() else Qt.Unchecked )
                self.UpdateModuleGrid() # test remove this if it is too heavy

            self.tableHV.itemChanged.connect(self.tableHVitemChanged)  # ... and restore the handler

        elif type(part) is HVsysLED:
            self.tableLED.itemChanged.disconnect()  # ... and restore the handler
            if capability in led_grid_coords:
                (row, col) = led_grid_coords[capability] 
                self.tableLED.item(row, col).setText(str_value)

            if capability == 'AUTOREG':   
                self.checkBoxLedAuto.setChecked( Qt.Checked if value > 0 else Qt.Unchecked )

            self.tableLED.itemChanged.connect(self.tableLEDitemChanged)  # ... and restore the handler
        
        self.UpdateModuleGrid()  # will switch off if this gets too heavy
        #self.statusBar.showMessage('%d'%(self.detector.queue_length()), 1)


    def ShowReferenceParameters(self):
        logging.info("ShowReferenceParameters: %s" % self.activeModuleId)
        if type(self.activeModuleId) is list and len(self.activeModuleId) == 1:
            module_id = self.activeModuleId[0]
            active_module_config = self.config.modules[module_id]
            if active_module_config.has('hv'):
                bus_id = self.config.modules[module_id].bus_id
                part_address = int(self.config.modules[module_id].address('hv'))
                part = self.detector.buses[bus_id].getPart(part_address) 

                self.tableHV.itemChanged.disconnect()
                self.tableLED.itemChanged.disconnect()

                for ch in active_module_config.hv.keys():
                    file_hv = self.config.modules[module_id].hv[ch]
                    hv = part.state[f'{ch}/REF_VOLTAGE'] 
                    self.tableHV.item(int(ch)-1, GRID_COLUMN_FILE).setText(str(file_hv))    
                    self.tableHV.item(int(ch)-1, GRID_COLUMN_REFERENCE).setText(str(hv))    

                file_ped_v = self.config.modules[module_id].hv_pedestal
                ped_v = part.state['REF_PEDESTAL_VOLTAGE']
                self.tableHV.item(GRID_ROW_PEDESTAL, GRID_COLUMN_FILE).setText(str(file_ped_v))
                self.tableHV.item(GRID_ROW_PEDESTAL, GRID_COLUMN_REFERENCE).setText(str(ped_v))
                self.tableHV.item(GRID_ROW_TEMPERATURE, GRID_COLUMN_REFERENCE).setText("%.2f °C"%(self.config.reference_temperature))
                self.tableHV.item(GRID_ROW_SLOPE, GRID_COLUMN_REFERENCE).setText("%+.0f mV/°C"%(-self.config.temperature_slope))
                self.tableHV.item(GRID_ROW_TEMPERATURE, GRID_COLUMN_STATE).setText("Sensor: %s"%(str(active_module_config.temperature_from_module)))

                self.tableHV.itemChanged.connect(self.tableHVitemChanged)
                self.tableLED.itemChanged.connect(self.tableLEDitemChanged)

    def SwitchHV(self,state):
        for moduleId in self.activeModuleId:
            moduleConfig = self.config.modules[moduleId]
            
            if moduleConfig.online and moduleConfig.has('hv'): 
                bus_id = self.config.modules[moduleId].bus_id
                part_address = int(self.config.modules[moduleId].address('hv'))
                part = self.detector.buses[bus_id].getPart(part_address) 
                command = Message(Message.WRITE_SHORT, part_address, part, 'STATUS', state)
                logging.warning('HV switching!')
                asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))
                # TODO fix asyncio.get_event_loop().create_task(self.detector.monitor_ramp_status(bus_id, part, part_address, self.DisplayRampStatus))
            else:
                logging.warning('HV switch requested for module without HV part')
        
        self.checkBoxHvOn.setChecked(Qt.Checked if state > 0 else Qt.Unchecked)

    def busResponseReceived(self, bus, data):
        for index, (title, config) in enumerate(self.config.buses.items()):
            if title == bus.id:
                self.busGrid.item(index,1).setText(str(bus.queue_length()))
                self.busGrid.item(index,GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_ONLINE if data is not None else COLOR_ERROR))
                self.busGrid.item(index,3).setText(str(bus.latency()))
                self.busTimers[title].start(100)

    def busTimerFired(self):
        #logging.info(self.sender().property('bus_id'))
        for index, (title, config) in enumerate(self.config.buses.items()):
            #logging.info(f"Timer: {title}")
            if title == self.sender().property('bus_id'):
                #logging.info(index)
                self.busGrid.item(index,GRID_COLUMN_LEFT_STATE).setForeground(QBrush(COLOR_OFFLINE))
        self.sender().stop()


    def pollTimerFired(self):
        logging.info("Poll timer fired!")

        self.pollAllTemperature(False)
        # TODO self.pollAllStatus(self.checkStatus)
        for module_id, config in self.config.modules.items():
            if config.online:
                if config.has('hv') and self.checkBoxTemperatureControl.isChecked():
                    # do the temperature HV correction 
                    # select the part
                    bus_id = config.bus_id
                    part_address = int(config.address('hv'))
                    part = self.detector.buses[bus_id].getPart(part_address) 
                    
                    # get the reference (or user-entered) ped v
                    pedestal_voltage = float(part.state['REF_PEDESTAL_VOLTAGE'])
                    # get the corrected ped v
                    correction = part.voltage_correction()
                    set_pedestal_voltage = pedestal_voltage + correction
                    # fire
                    cap = 'SET_PEDESTAL_VOLTAGE'
                    value = part.valueFromString(cap, str(set_pedestal_voltage))
                    command = Message(Message.WRITE_SHORT, part_address, part, cap, value)
                    logging.info('Going to set corrected ped v of module %s to %s (%s)'%(module_id, set_pedestal_voltage, value))
                    asyncio.get_event_loop().create_task(self.detector.add_task(bus_id, command, part, print))


        logging.info("Poll complete.")

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.labelLastCorrection.setText(f'Last at: {now}')
        self.UpdateModuleGrid()


    def guiTimerFired(self):
        time_remaining = datetime.timedelta(seconds=int(self.pollTimer.remainingTime()/1000))
        self.labelNextCorrection.setText(f'Next in: {time_remaining}')


    def OnCheckBoxPollChanged(self, state):
        logging.info("OnCheckBoxPollChange")
        logging.info(str(state))
        if state == Qt.Checked and self.config.query_delay > 0:
            self.pollTimer.start(self.config.query_delay * 1000)
            logging.info("Poll timer started!")
        else:
            self.pollTimer.stop()
            logging.info("Poll timer stopped!")

        controls = [self.checkBoxTemperatureControl, self.spinBoxCorrectionInterval, self.labelLastCorrection, self.labelNextCorrection]
        for c in controls:
            c.setEnabled(state == Qt.Checked)


    @asyncClose
    async def closeEvent(self, event):
        #close all connections
        for id, bus in self.detector.buses.items():
            await bus.disconnect()

def handler(loop, context):
    print(context)


def print_usage():
    print('Usage: gui.py [-c <configfile>]')
    print('E.g. : gui.py -c config.xml\n')

    sys.exit()


async def main(argv):
    # c7A9KzKcjZ4dkVbq8n9e
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(datetime.datetime.now().strftime('logs/dcs_log_%Y-%m-%d-%H-%M-%S.txt'))
        ]    
    )

    config_file = dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../config/PsdSlowControlConfig.xml"
    schema_path = dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../config/PsdSlowControlConfig.xsd"

    opts, args = getopt.getopt(argv,"hc:",["config="])
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
        elif opt in ("-c", "--config"):
            config_file = arg
    
    if len(args) > 0:
        print_usage()


    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    configuration = config.load(config_file, schema=schema_path)
    mainWindow = MainWindow(configuration)
    mainWindow.show()

    loop = asyncio.get_event_loop()
    #loop.set_exception_handler(handler)

    logging.getLogger().addHandler(CallbackHandler(mainWindow.OnLogMessage))

    try:
        logging.info("Staring bus listeners...")
        for id, bus in mainWindow.detector.buses.items():
            bus.register_global_response_callback(mainWindow.busResponseReceived)
            await loop.create_task(bus.connect())
            loop.create_task(bus.send())
            logging.info("Bus '%s' %s."%(id, "online" if bus.online else "offline"))
        await mainWindow.pollOnlineModules()
    except OSError as e:
        logging.info("Cannot connect to system module: %s"%(str(e)))  
    except asyncio.exceptions.CancelledError:
        sys.exit(0)

    await future
    return True


def start(argv):
    try:
        qasync.run(main(argv))
    except asyncio.exceptions.CancelledError:
        logging.info("Application exit.")  
        sys.exit(0)


if __name__ == '__main__':
    start(sys.argv[1:])
