# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'switchjkZOOQ.ui'
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

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(14)
        self.pushButton_3.setFont(font1)

        self.gridLayout.addWidget(self.pushButton_3, 2, 2, 1, 1)

        self.lineAddress4 = QLineEdit(self.centralwidget)
        self.lineAddress4.setObjectName(u"lineAddress4")
        self.lineAddress4.setFont(font)

        self.gridLayout.addWidget(self.lineAddress4, 1, 3, 1, 1)

        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy1.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy1)
        self.pushButton_2.setFont(font1)

        self.gridLayout.addWidget(self.pushButton_2, 2, 1, 1, 1)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)
        self.pushButton.setFont(font1)

        self.gridLayout.addWidget(self.pushButton, 2, 0, 1, 1)

        self.lineAddress3 = QLineEdit(self.centralwidget)
        self.lineAddress3.setObjectName(u"lineAddress3")
        self.lineAddress3.setFont(font)

        self.gridLayout.addWidget(self.lineAddress3, 1, 2, 1, 1)

        self.pushButton_4 = QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy1.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy1)
        self.pushButton_4.setFont(font1)

        self.gridLayout.addWidget(self.pushButton_4, 2, 3, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font1)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font1)

        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lineAddress2.setText(QCoreApplication.translate("MainWindow", u"10.18.88.102:5001", None))
        self.lineAddress1.setText(QCoreApplication.translate("MainWindow", u"10.18.88.101:5001", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.lineAddress4.setText(QCoreApplication.translate("MainWindow", u"10.18.88.104:5001", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.lineAddress3.setText(QCoreApplication.translate("MainWindow", u"10.18.88.103:5001", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Switch", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Wall 1", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Wall 2", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Wall 3", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Veto", None))
    # retranslateUi

