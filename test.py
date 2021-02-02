# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

import cv2
import sys
# from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
# from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
# from PyQt5.QtGui import QImage, QPixmap

from PyQt5 import QtCore, QtGui, QtWidgets


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture('rtsp://admin:Admin123@192.168.111.211/1')
        while True:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (720,480))
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtCore.QImage(rgbImage.data, w, h, bytesPerLine, QtCore.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.startbutton = QtWidgets.QPushButton(self.centralwidget)
        self.startbutton.setGeometry(QtCore.QRect(70, 60, 89, 25))
        self.startbutton.setObjectName("startbutton")
        self.startbutton.clicked.connect(self.get_data)

        self.stopbutton = QtWidgets.QPushButton(self.centralwidget)
        self.stopbutton.setGeometry(QtCore.QRect(70, 150, 89, 25))
        self.stopbutton.setObjectName("stopbutton")
        self.stopbutton.clicked.connect(self.close_window)

        self.status_start_button = QtWidgets.QLabel(self.centralwidget)
        self.status_start_button.setGeometry(QtCore.QRect(170, 60, 371, 17))
        self.status_start_button.setObjectName("status_start_button")
        self.status_stop_button = QtWidgets.QLabel(self.centralwidget)
        self.status_stop_button.setGeometry(QtCore.QRect(170, 160, 371, 17))
        self.status_stop_button.setObjectName("status_stop_button")
        self.input1 = QtWidgets.QLineEdit(self.centralwidget)
        self.input1.setGeometry(QtCore.QRect(80, 100, 471, 25))
        self.input1.setObjectName("input1")
        self.input2 = QtWidgets.QLineEdit(self.centralwidget)
        self.input2.setGeometry(QtCore.QRect(70, 190, 471, 25))
        self.input2.setObjectName("input2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def close_window(self):
        exit()

    def status(self):
        self.status_start_button.setText("Start button was pushed !")

    def get_data(self):
        data = self.input1.text()
        self.status_start_button.setText("Xin chao " + data)

    def setImage(self, image):
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startbutton.setText(_translate("MainWindow", "startbutton"))
        self.stopbutton.setText(_translate("MainWindow", "stopbutton"))
        self.status_start_button.setText(_translate("MainWindow", "Push the start button !"))
        self.status_stop_button.setText(_translate("MainWindow", "Goodbye !"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
