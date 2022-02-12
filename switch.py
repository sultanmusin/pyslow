# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'switch.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

import logging
import socket
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"Switch")
        MainWindow.resize(711, 256)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineAddress2 = QLineEdit(self.centralwidget)
        self.lineAddress2.setObjectName(u"lineAddress2")
        font = QFont()
        font.setPointSize(12)
        self.lineAddress2.setFont(font)

        self.gridLayout.addWidget(self.lineAddress2, 1, 1, 1, 1)

        self.lineAddress1 = QLineEdit(self.centralwidget)
        self.lineAddress1.setObjectName(u"lineAddress1")
        self.lineAddress1.setFont(font)

        self.gridLayout.addWidget(self.lineAddress1, 1, 0, 1, 1)

        self.pushButton3 = QPushButton(self.centralwidget)
        self.pushButton3.setObjectName(u"pushButton3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton3.sizePolicy().hasHeightForWidth())
        self.pushButton3.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(14)
        self.pushButton3.setFont(font1)

        self.gridLayout.addWidget(self.pushButton3, 2, 2, 1, 1)

        self.lineAddress4 = QLineEdit(self.centralwidget)
        self.lineAddress4.setObjectName(u"lineAddress4")
        self.lineAddress4.setFont(font)

        self.gridLayout.addWidget(self.lineAddress4, 1, 3, 1, 1)

        self.pushButton2 = QPushButton(self.centralwidget)
        self.pushButton2.setObjectName(u"pushButton2")
        sizePolicy1.setHeightForWidth(self.pushButton2.sizePolicy().hasHeightForWidth())
        self.pushButton2.setSizePolicy(sizePolicy1)
        self.pushButton2.setFont(font1)

        self.gridLayout.addWidget(self.pushButton2, 2, 1, 1, 1)

        self.pushButton1 = QPushButton(self.centralwidget)
        self.pushButton1.setObjectName(u"pushButton")
        sizePolicy1.setHeightForWidth(self.pushButton1.sizePolicy().hasHeightForWidth())
        self.pushButton1.setSizePolicy(sizePolicy1)
        self.pushButton1.setFont(font1)

        self.gridLayout.addWidget(self.pushButton1, 2, 0, 1, 1)

        self.lineAddress3 = QLineEdit(self.centralwidget)
        self.lineAddress3.setObjectName(u"lineAddress3")
        self.lineAddress3.setFont(font)

        self.gridLayout.addWidget(self.lineAddress3, 1, 2, 1, 1)

        self.pushButton4 = QPushButton(self.centralwidget)
        self.pushButton4.setObjectName(u"pushButton4")
        sizePolicy1.setHeightForWidth(self.pushButton4.sizePolicy().hasHeightForWidth())
        self.pushButton4.setSizePolicy(sizePolicy1)
        self.pushButton4.setFont(font1)

        self.gridLayout.addWidget(self.pushButton4, 2, 3, 1, 1)

        self.label1 = QLabel(self.centralwidget)
        self.label1.setObjectName(u"label")
        self.label1.setFont(font1)

        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)

        self.label2 = QLabel(self.centralwidget)
        self.label2.setObjectName(u"label2")
        self.label2.setFont(font1)

        self.gridLayout.addWidget(self.label2, 0, 1, 1, 1)

        self.label3 = QLabel(self.centralwidget)
        self.label3.setObjectName(u"label3")
        self.label3.setFont(font1)

        self.gridLayout.addWidget(self.label3, 0, 2, 1, 1)

        self.label4 = QLabel(self.centralwidget)
        self.label4.setObjectName(u"label4")
        self.label4.setFont(font1)

        self.gridLayout.addWidget(self.label4, 0, 3, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

        readSwitch(self.lineAddress1.text(), 1, lambda state: print(f"1 -> {state}"))
        readSwitch(self.lineAddress2.text(), 1, lambda state: print(f"2 -> {state}"))
        readSwitch(self.lineAddress3.text(), 1, lambda state: print(f"3 -> {state}"))
        readSwitch(self.lineAddress4.text(), 1, lambda state: print(f"4 -> {state}"))
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("Switch", u"Switch", None))
        self.lineAddress1.setText(QCoreApplication.translate("MainWindow", u"10.18.88.101:5001", None))
        self.lineAddress2.setText(QCoreApplication.translate("MainWindow", u"10.18.88.102:5001", None))
        self.lineAddress3.setText(QCoreApplication.translate("MainWindow", u"10.18.88.103:5001", None))
        self.lineAddress4.setText(QCoreApplication.translate("MainWindow", u"10.18.88.104:5001", None))
        self.pushButton1.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.pushButton2.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.pushButton3.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.pushButton4.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"Wall 1", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"Wall 2", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"Wall 3", None))
        self.label4.setText(QCoreApplication.translate("MainWindow", u"Veto", None))
    # retranslateUi

def readSwitch(address:str, chan: int, callback):
    (host, port) = address.split(':')
    port = int(port)
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(1)
        clientSocket.connect((host, port))
        # Send data to server
        cmd = "\x01\x02\x00\x01\x01"            # cmd=READ  ver=2 err=0 len=1 chan=1  TODO chan
        logging.info(f"Sending to {host}:{port} : {cmd.encode()}")
        clientSocket.send(cmd.encode())

        response = clientSocket.recv(1024)
        clientSocket.close()
        # Print to the console
        logging.info(f'Response: {len(response)} bytes')
        logging.info([int(byte) for byte in response])      # Печатает 7 байт ответа 1 2 0 3 1 1 0 
        logging.info(['OK', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7'][response[2]])
        callback(int(response[6]))
    except TimeoutError as e:
        logging.warning(f"Timeout on {host}:{port}, skipping")

def setSwitch(address:str, chan: int, value:int):
    (host, port) = address.split(':')
    port = int(port)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.settimeout(1)
    try:
        clientSocket.connect((host, port))
        # Send data to server
        cmd = "\x02\x02\x00\x03\x01\x01\x00"  # cmd=WRITE ver=2 err=0 len=3 chan=1 dir=OUT value=LOW  TODO chan
        logging.info(f"Sending to {host}:{port} : {cmd.encode()}")
        clientSocket.send(cmd.encode())

        response = clientSocket.recv(1024)
        clientSocket.close()
        # Print to the console
        logging.info(f'Response: {len(response)} bytes')
        logging.info([int(byte) for byte in response])      # Печатает 5 байт ответа
        logging.info(['OK', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7'][response[2]])
    except TimeoutError as e:
        logging.warning(f"Timeout on {host}:{port}, skipping")


def main(argv):
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler()
        ]    
    )

    app = QApplication([])
    app.setApplicationName("Switch")
    window = MainWindow()
    window.setupUi(window)
    window.show()
    app.exec_()

if __name__ == '__main__':
    main(sys.argv[1:])
