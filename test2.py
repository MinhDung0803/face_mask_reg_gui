# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test2.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import cv2


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent):
        # changePixmap = QtCore.pyqtSignal(QtGui.QImage)
        QtCore.QThread.__init__(self, parent)

    def run(self):
        cap = cv2.VideoCapture('rtsp://admin:Admin123@192.168.111.211/1')

        while True:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


def close_window():
    exit()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1080, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.startbutton = QtWidgets.QPushButton(self.centralwidget)
        self.startbutton.setGeometry(QtCore.QRect(70, 60, 89, 25))
        self.startbutton.setObjectName("startbutton")
        self.startbutton.clicked.connect(self.video)

        self.stopbutton = QtWidgets.QPushButton(self.centralwidget)
        self.stopbutton.setGeometry(QtCore.QRect(70, 150, 89, 25))
        self.stopbutton.setObjectName("stopbutton")
        self.stopbutton.clicked.connect(close_window)

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

        # # video
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 250, 471, 271))
        self.label.setObjectName("label")

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

    def video(self):
        self.label.resize(640, 480)
        th = Thread(MainWindow)
        th.changePixmap.connect(self.setImage)
        th.start()

    def setImage(self, image):
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def status(self):
        self.status_start_button.setText("Start button was pushed !")

    def get_data(self):
        data = self.input1.text()
        self.status_start_button.setText("Xin chao " + data)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startbutton.setText(_translate("MainWindow", "startbutton"))
        self.stopbutton.setText(_translate("MainWindow", "stopbutton"))
        self.status_start_button.setText(_translate("MainWindow", "Push the start button !"))
        self.status_stop_button.setText(_translate("MainWindow", "Goodbye !"))
        self.label.setText(_translate("MainWindow", "Video"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
