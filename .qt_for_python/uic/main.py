# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(918, 910)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(750, 750))
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionA_bout = QAction(MainWindow)
        self.actionA_bout.setObjectName(u"actionA_bout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QSize(750, 800))
        self.centralwidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_14 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy1)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        self.splitter.setChildrenCollapsible(False)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, -1, 0)
        self.splitter_2 = QSplitter(self.frame)
        self.splitter_2.setObjectName(u"splitter_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy3)
        self.splitter_2.setOrientation(Qt.Vertical)
        self.splitter_2.setOpaqueResize(False)
        self.splitter_2.setHandleWidth(10)
        self.splitter_2.setChildrenCollapsible(False)
        self.groupBox_5 = QGroupBox(self.splitter_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy4)
        self.groupBox_5.setMinimumSize(QSize(0, 150))
        self.verticalLayout_15 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_15.setSpacing(6)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(9, 9, 9, 9)
        self.buttonSelectAll = QPushButton(self.groupBox_5)
        self.buttonSelectAll.setObjectName(u"buttonSelectAll")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.buttonSelectAll.sizePolicy().hasHeightForWidth())
        self.buttonSelectAll.setSizePolicy(sizePolicy5)

        self.verticalLayout_15.addWidget(self.buttonSelectAll)

        self.labelModules = QLabel(self.groupBox_5)
        self.labelModules.setObjectName(u"labelModules")

        self.verticalLayout_15.addWidget(self.labelModules)

        self.moduleList = QTableWidget(self.groupBox_5)
        if (self.moduleList.columnCount() < 3):
            self.moduleList.setColumnCount(3)
        if (self.moduleList.rowCount() < 20):
            self.moduleList.setRowCount(20)
        self.moduleList.setObjectName(u"moduleList")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(2)
        sizePolicy6.setHeightForWidth(self.moduleList.sizePolicy().hasHeightForWidth())
        self.moduleList.setSizePolicy(sizePolicy6)
        self.moduleList.setMinimumSize(QSize(0, 200))
        self.moduleList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.moduleList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.moduleList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.moduleList.setRowCount(20)
        self.moduleList.setColumnCount(3)
        self.moduleList.horizontalHeader().setDefaultSectionSize(60)
        self.moduleList.verticalHeader().setMinimumSectionSize(22)
        self.moduleList.verticalHeader().setDefaultSectionSize(22)

        self.verticalLayout_15.addWidget(self.moduleList)

        self.splitter_2.addWidget(self.groupBox_5)
        self.moduleGrid = QTableWidget(self.splitter_2)
        if (self.moduleGrid.columnCount() < 9):
            self.moduleGrid.setColumnCount(9)
        if (self.moduleGrid.rowCount() < 7):
            self.moduleGrid.setRowCount(7)
        self.moduleGrid.setObjectName(u"moduleGrid")
        sizePolicy6.setHeightForWidth(self.moduleGrid.sizePolicy().hasHeightForWidth())
        self.moduleGrid.setSizePolicy(sizePolicy6)
        self.moduleGrid.setMinimumSize(QSize(280, 100))
        font = QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.moduleGrid.setFont(font)
        self.moduleGrid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.moduleGrid.setRowCount(7)
        self.moduleGrid.setColumnCount(9)
        self.splitter_2.addWidget(self.moduleGrid)
        self.moduleGrid.horizontalHeader().setVisible(False)
        self.moduleGrid.horizontalHeader().setMinimumSectionSize(22)
        self.moduleGrid.horizontalHeader().setDefaultSectionSize(24)
        self.moduleGrid.verticalHeader().setVisible(False)
        self.moduleGrid.verticalHeader().setMinimumSectionSize(22)
        self.moduleGrid.verticalHeader().setDefaultSectionSize(24)
        self.groupBox = QGroupBox(self.splitter_2)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy7 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(2)
        sizePolicy7.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy7)
        self.groupBox.setMinimumSize(QSize(0, 150))
        self.verticalLayout_16 = QVBoxLayout(self.groupBox)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.busGrid = QTableWidget(self.groupBox)
        if (self.busGrid.columnCount() < 4):
            self.busGrid.setColumnCount(4)
        if (self.busGrid.rowCount() < 3):
            self.busGrid.setRowCount(3)
        self.busGrid.setObjectName(u"busGrid")
        sizePolicy8 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(1)
        sizePolicy8.setHeightForWidth(self.busGrid.sizePolicy().hasHeightForWidth())
        self.busGrid.setSizePolicy(sizePolicy8)
        self.busGrid.setMinimumSize(QSize(0, 90))
        self.busGrid.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.busGrid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.busGrid.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.busGrid.setRowCount(3)
        self.busGrid.setColumnCount(4)
        self.busGrid.horizontalHeader().setDefaultSectionSize(60)
        self.busGrid.verticalHeader().setMinimumSectionSize(22)
        self.busGrid.verticalHeader().setDefaultSectionSize(22)

        self.verticalLayout_16.addWidget(self.busGrid)

        self.splitter_2.addWidget(self.groupBox)

        self.verticalLayout.addWidget(self.splitter_2)

        self.splitter.addWidget(self.frame)
        self.rightFrame = QFrame(self.splitter)
        self.rightFrame.setObjectName(u"rightFrame")
        sizePolicy4.setHeightForWidth(self.rightFrame.sizePolicy().hasHeightForWidth())
        self.rightFrame.setSizePolicy(sizePolicy4)
        self.rightFrame.setFrameShape(QFrame.NoFrame)
        self.rightFrame.setFrameShadow(QFrame.Plain)
        self.verticalLayout_2 = QVBoxLayout(self.rightFrame)
        self.verticalLayout_2.setSpacing(12)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.groupBoxPoll = QGroupBox(self.rightFrame)
        self.groupBoxPoll.setObjectName(u"groupBoxPoll")
        self.gridLayout = QGridLayout(self.groupBoxPoll)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 3, -1, 3)
        self.labelLastCorrection = QLabel(self.groupBoxPoll)
        self.labelLastCorrection.setObjectName(u"labelLastCorrection")

        self.gridLayout.addWidget(self.labelLastCorrection, 3, 0, 1, 1)

        self.checkBoxTemperatureControl = QCheckBox(self.groupBoxPoll)
        self.checkBoxTemperatureControl.setObjectName(u"checkBoxTemperatureControl")
        sizePolicy9 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.checkBoxTemperatureControl.sizePolicy().hasHeightForWidth())
        self.checkBoxTemperatureControl.setSizePolicy(sizePolicy9)
        self.checkBoxTemperatureControl.setChecked(True)

        self.gridLayout.addWidget(self.checkBoxTemperatureControl, 1, 3, 1, 1)

        self.spinBoxCorrectionInterval = QSpinBox(self.groupBoxPoll)
        self.spinBoxCorrectionInterval.setObjectName(u"spinBoxCorrectionInterval")
        self.spinBoxCorrectionInterval.setEnabled(True)
        sizePolicy9.setHeightForWidth(self.spinBoxCorrectionInterval.sizePolicy().hasHeightForWidth())
        self.spinBoxCorrectionInterval.setSizePolicy(sizePolicy9)
        self.spinBoxCorrectionInterval.setMaximum(3600)
        self.spinBoxCorrectionInterval.setSingleStep(60)
        self.spinBoxCorrectionInterval.setValue(0)

        self.gridLayout.addWidget(self.spinBoxCorrectionInterval, 1, 2, 1, 1)

        self.labelNextCorrection = QLabel(self.groupBoxPoll)
        self.labelNextCorrection.setObjectName(u"labelNextCorrection")

        self.gridLayout.addWidget(self.labelNextCorrection, 4, 0, 1, 1)

        self.checkBoxPoll = QCheckBox(self.groupBoxPoll)
        self.checkBoxPoll.setObjectName(u"checkBoxPoll")
        sizePolicy9.setHeightForWidth(self.checkBoxPoll.sizePolicy().hasHeightForWidth())
        self.checkBoxPoll.setSizePolicy(sizePolicy9)
        self.checkBoxPoll.setTristate(False)

        self.gridLayout.addWidget(self.checkBoxPoll, 1, 0, 1, 1)

        self.label_2 = QLabel(self.groupBoxPoll)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 4, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBoxPoll)

        self.groupBoxControl = QGroupBox(self.rightFrame)
        self.groupBoxControl.setObjectName(u"groupBoxControl")
        sizePolicy10 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy10.setHorizontalStretch(1)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.groupBoxControl.sizePolicy().hasHeightForWidth())
        self.groupBoxControl.setSizePolicy(sizePolicy10)
        self.verticalLayout_17 = QVBoxLayout(self.groupBoxControl)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(-1, 3, -1, 3)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.checkBoxOnline = QCheckBox(self.groupBoxControl)
        self.checkBoxOnline.setObjectName(u"checkBoxOnline")
        self.checkBoxOnline.setTristate(True)

        self.horizontalLayout_4.addWidget(self.checkBoxOnline)

        self.checkBoxHvOn = QCheckBox(self.groupBoxControl)
        self.checkBoxHvOn.setObjectName(u"checkBoxHvOn")
        self.checkBoxHvOn.setTristate(True)

        self.horizontalLayout_4.addWidget(self.checkBoxHvOn)

        self.checkBoxLedAuto = QCheckBox(self.groupBoxControl)
        self.checkBoxLedAuto.setObjectName(u"checkBoxLedAuto")
        self.checkBoxLedAuto.setTristate(True)

        self.horizontalLayout_4.addWidget(self.checkBoxLedAuto)


        self.verticalLayout_17.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.buttonApplyReferenceHV = QPushButton(self.groupBoxControl)
        self.buttonApplyReferenceHV.setObjectName(u"buttonApplyReferenceHV")

        self.horizontalLayout_3.addWidget(self.buttonApplyReferenceHV)

        self.buttonSetHvOn = QPushButton(self.groupBoxControl)
        self.buttonSetHvOn.setObjectName(u"buttonSetHvOn")

        self.horizontalLayout_3.addWidget(self.buttonSetHvOn)

        self.buttonSetHvOff = QPushButton(self.groupBoxControl)
        self.buttonSetHvOff.setObjectName(u"buttonSetHvOff")

        self.horizontalLayout_3.addWidget(self.buttonSetHvOff)


        self.verticalLayout_17.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.buttonStartAdjust = QPushButton(self.groupBoxControl)
        self.buttonStartAdjust.setObjectName(u"buttonStartAdjust")

        self.horizontalLayout_5.addWidget(self.buttonStartAdjust)

        self.spinBoxAdjust = QDoubleSpinBox(self.groupBoxControl)
        self.spinBoxAdjust.setObjectName(u"spinBoxAdjust")
        self.spinBoxAdjust.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.spinBoxAdjust.setMinimum(-5.000000000000000)
        self.spinBoxAdjust.setMaximum(5.000000000000000)
        self.spinBoxAdjust.setSingleStep(0.100000000000000)
        self.spinBoxAdjust.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)

        self.horizontalLayout_5.addWidget(self.spinBoxAdjust)

        self.buttonFinishAdjust = QPushButton(self.groupBoxControl)
        self.buttonFinishAdjust.setObjectName(u"buttonFinishAdjust")

        self.horizontalLayout_5.addWidget(self.buttonFinishAdjust)

        self.buttonCancelAdjust = QPushButton(self.groupBoxControl)
        self.buttonCancelAdjust.setObjectName(u"buttonCancelAdjust")

        self.horizontalLayout_5.addWidget(self.buttonCancelAdjust)


        self.verticalLayout_17.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addWidget(self.groupBoxControl)

        self.groupBoxHV = QGroupBox(self.rightFrame)
        self.groupBoxHV.setObjectName(u"groupBoxHV")
        sizePolicy11 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy11.setHorizontalStretch(1)
        sizePolicy11.setVerticalStretch(160)
        sizePolicy11.setHeightForWidth(self.groupBoxHV.sizePolicy().hasHeightForWidth())
        self.groupBoxHV.setSizePolicy(sizePolicy11)
        self.groupBoxHV.setMinimumSize(QSize(450, 300))
        self.horizontalLayout = QHBoxLayout(self.groupBoxHV)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.tableHV = QTableWidget(self.groupBoxHV)
        if (self.tableHV.columnCount() < 4):
            self.tableHV.setColumnCount(4)
        if (self.tableHV.rowCount() < 19):
            self.tableHV.setRowCount(19)
        self.tableHV.setObjectName(u"tableHV")
        sizePolicy12 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy12.setHorizontalStretch(1)
        sizePolicy12.setVerticalStretch(20)
        sizePolicy12.setHeightForWidth(self.tableHV.sizePolicy().hasHeightForWidth())
        self.tableHV.setSizePolicy(sizePolicy12)
        self.tableHV.setMinimumSize(QSize(450, 240))
        self.tableHV.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableHV.setShowGrid(True)
        self.tableHV.setSortingEnabled(False)
        self.tableHV.setRowCount(19)
        self.tableHV.setColumnCount(4)
        self.tableHV.verticalHeader().setMinimumSectionSize(20)
        self.tableHV.verticalHeader().setDefaultSectionSize(22)

        self.horizontalLayout.addWidget(self.tableHV)


        self.verticalLayout_2.addWidget(self.groupBoxHV)

        self.groupBoxLED = QGroupBox(self.rightFrame)
        self.groupBoxLED.setObjectName(u"groupBoxLED")
        sizePolicy13 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy13.setHorizontalStretch(1)
        sizePolicy13.setVerticalStretch(80)
        sizePolicy13.setHeightForWidth(self.groupBoxLED.sizePolicy().hasHeightForWidth())
        self.groupBoxLED.setSizePolicy(sizePolicy13)
        self.groupBoxLED.setMinimumSize(QSize(450, 198))
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxLED)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 3, -1, 3)
        self.tableLED = QTableWidget(self.groupBoxLED)
        if (self.tableLED.columnCount() < 3):
            self.tableLED.setColumnCount(3)
        if (self.tableLED.rowCount() < 6):
            self.tableLED.setRowCount(6)
        self.tableLED.setObjectName(u"tableLED")
        sizePolicy1.setHeightForWidth(self.tableLED.sizePolicy().hasHeightForWidth())
        self.tableLED.setSizePolicy(sizePolicy1)
        self.tableLED.setMinimumSize(QSize(450, 160))
        self.tableLED.setRowCount(6)
        self.tableLED.setColumnCount(3)
        self.tableLED.verticalHeader().setMinimumSectionSize(22)
        self.tableLED.verticalHeader().setDefaultSectionSize(22)

        self.verticalLayout_3.addWidget(self.tableLED)


        self.verticalLayout_2.addWidget(self.groupBoxLED)

        self.logo = QLabel(self.rightFrame)
        self.logo.setObjectName(u"logo")
        self.logo.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.logo)

        self.splitter.addWidget(self.rightFrame)

        self.verticalLayout_14.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 918, 20))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionA_bout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DCS", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"&Save", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
        self.actionA_bout.setText(QCoreApplication.translate("MainWindow", u"A&bout", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Detector Map", None))
        self.buttonSelectAll.setText(QCoreApplication.translate("MainWindow", u"Select All Modules", None))
        self.labelModules.setText(QCoreApplication.translate("MainWindow", u"Modules", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"System buses", None))
        self.groupBoxPoll.setTitle(QCoreApplication.translate("MainWindow", u"Temperature Correction", None))
        self.labelLastCorrection.setText(QCoreApplication.translate("MainWindow", u"Last at: -", None))
        self.checkBoxTemperatureControl.setText(QCoreApplication.translate("MainWindow", u"Correction", None))
        self.spinBoxCorrectionInterval.setSpecialValueText(QCoreApplication.translate("MainWindow", u"Disabled", None))
        self.spinBoxCorrectionInterval.setSuffix(QCoreApplication.translate("MainWindow", u" sec", None))
        self.spinBoxCorrectionInterval.setPrefix("")
        self.labelNextCorrection.setText(QCoreApplication.translate("MainWindow", u"Next in: - ", None))
        self.checkBoxPoll.setText(QCoreApplication.translate("MainWindow", u"Poll every", None))
        self.label_2.setText("")
        self.groupBoxControl.setTitle(QCoreApplication.translate("MainWindow", u"Module ", None))
        self.checkBoxOnline.setText(QCoreApplication.translate("MainWindow", u"Online", None))
        self.checkBoxHvOn.setText(QCoreApplication.translate("MainWindow", u"HV ON", None))
        self.checkBoxLedAuto.setText(QCoreApplication.translate("MainWindow", u"LED Auto", None))
        self.buttonApplyReferenceHV.setText(QCoreApplication.translate("MainWindow", u"Apply Reference HV", None))
        self.buttonSetHvOn.setText(QCoreApplication.translate("MainWindow", u"Set HV On", None))
        self.buttonSetHvOff.setText(QCoreApplication.translate("MainWindow", u"Set HV Off", None))
        self.buttonStartAdjust.setText(QCoreApplication.translate("MainWindow", u"Adjust HV", None))
        self.spinBoxAdjust.setSuffix(QCoreApplication.translate("MainWindow", u" V", None))
        self.buttonFinishAdjust.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.buttonCancelAdjust.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.groupBoxHV.setTitle(QCoreApplication.translate("MainWindow", u"High Voltage", None))
        self.groupBoxLED.setTitle(QCoreApplication.translate("MainWindow", u"LED", None))
        self.logo.setText(QCoreApplication.translate("MainWindow", u"Logo", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
    # retranslateUi

