# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainSiYsfS.ui'
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
        MainWindow.resize(800, 860)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(800, 750))
        self.centralwidget.setMaximumSize(QSize(16777215, 598))
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 311, 601))
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy2)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout_2.addWidget(self.pushButton)

        self.tableWidget = QTableWidget(self.frame)
        if (self.tableWidget.columnCount() < 3):
            self.tableWidget.setColumnCount(3)
        if (self.tableWidget.rowCount() < 10):
            self.tableWidget.setRowCount(10)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(3)

        self.verticalLayout_2.addWidget(self.tableWidget)

        self.columnView = QColumnView(self.frame)
        self.columnView.setObjectName(u"columnView")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.columnView.sizePolicy().hasHeightForWidth())
        self.columnView.setSizePolicy(sizePolicy3)

        self.verticalLayout_2.addWidget(self.columnView)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(310, 0, 494, 752))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.groupBoxHV = QGroupBox(self.frame_2)
        self.groupBoxHV.setObjectName(u"groupBoxHV")
        self.groupBoxHV.setGeometry(QRect(10, 72, 474, 552))
        sizePolicy.setHeightForWidth(self.groupBoxHV.sizePolicy().hasHeightForWidth())
        self.groupBoxHV.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.groupBoxHV)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidgetHV = QTableWidget(self.groupBoxHV)
        if (self.tableWidgetHV.columnCount() < 4):
            self.tableWidgetHV.setColumnCount(4)
        if (self.tableWidgetHV.rowCount() < 19):
            self.tableWidgetHV.setRowCount(19)
        self.tableWidgetHV.setObjectName(u"tableWidgetHV")
        sizePolicy.setHeightForWidth(self.tableWidgetHV.sizePolicy().hasHeightForWidth())
        self.tableWidgetHV.setSizePolicy(sizePolicy)
        self.tableWidgetHV.setMinimumSize(QSize(450, 550))
        self.tableWidgetHV.setShowGrid(True)
        self.tableWidgetHV.setSortingEnabled(False)
        self.tableWidgetHV.setRowCount(19)
        self.tableWidgetHV.setColumnCount(4)

        self.horizontalLayout.addWidget(self.tableWidgetHV)

        self.groupBoxLED = QGroupBox(self.frame_2)
        self.groupBoxLED.setObjectName(u"groupBoxLED")
        self.groupBoxLED.setGeometry(QRect(10, 630, 474, 112))
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.groupBoxLED.sizePolicy().hasHeightForWidth())
        self.groupBoxLED.setSizePolicy(sizePolicy4)
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxLED)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.tableWidget_2 = QTableWidget(self.groupBoxLED)
        if (self.tableWidget_2.columnCount() < 4):
            self.tableWidget_2.setColumnCount(4)
        if (self.tableWidget_2.rowCount() < 6):
            self.tableWidget_2.setRowCount(6)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setMinimumSize(QSize(450, 0))
        self.tableWidget_2.setRowCount(6)
        self.tableWidget_2.setColumnCount(4)

        self.verticalLayout_3.addWidget(self.tableWidget_2)

        self.groupBoxControl = QGroupBox(self.frame_2)
        self.groupBoxControl.setObjectName(u"groupBoxControl")
        self.groupBoxControl.setGeometry(QRect(10, 0, 461, 61))
        self.horizontalLayoutWidget = QWidget(self.groupBoxControl)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(50, 30, 178, 23))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.checkBox = QCheckBox(self.horizontalLayoutWidget)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_2.addWidget(self.checkBox)

        self.checkBox_2 = QCheckBox(self.horizontalLayoutWidget)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.horizontalLayout_2.addWidget(self.checkBox_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 20))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"DCS", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.groupBoxHV.setTitle(QCoreApplication.translate("MainWindow", u"High Voltage", None))
        self.groupBoxLED.setTitle(QCoreApplication.translate("MainWindow", u"LED", None))
        self.groupBoxControl.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"CheckBox", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

if __name__ == '__main__':
    mainWindow = Ui_MainWindow()
    mainWindow.setupUi()