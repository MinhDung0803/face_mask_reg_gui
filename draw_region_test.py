# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import cv2


# all global variables
global th, path, light_alarm, sound_alarm, both_alarm, count
path = None
count = 0


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self._go = None

    def run(self):
        global count
        cap = cv2.VideoCapture(path)
        self._go = True
        while self._go:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
            else:
                check_input_frame()
                time.sleep(0.5)

    def stop_thread(self):
        global path
        self._go = False
        path = None


def close_window():
    th.stop_thread()
    time.sleep(1)
    # exit()


def camera_source_alarm():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Input Camera Warning")
    alert.setText('Please input the camera source!')
    alert.exec_()


def check_path_for_ip_camera():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("IP Camera Warning")
    alert.setText('Wrong IP address for IPCamera! Please check again!')
    alert.exec_()


def check_path_for_webcam():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Webcam Warning")
    alert.setText('Wrong ID for Webcam! Please check again!')
    alert.exec_()


def check_input_frame():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Read Camera Warning")
    alert.setText('No video input, please check again!')
    alert.exec_()
    th.stop_thread()
    time.sleep(1)


def restore(settings):
    finfo = QtCore.QFileInfo(settings.fileName())
    if finfo.exists() and finfo.isFile():
        for w in QtWidgets.qApp.allWidgets():
            mo = w.metaObject()
            if w.objectName() and not w.objectName().startswith("qt_"):
                settings.beginGroup(w.objectName())
                for i in range(mo.propertyCount(), mo.propertyOffset() - 1, -1):
                    prop = mo.property(i)
                    if prop.isWritable():
                        name = prop.name()
                        val = settings.value(name, w.property(name))
                        if str(val).isdigit():
                            val = int(val)
                        w.setProperty(name, val)
                settings.endGroup()


def save(settings):
    for w in QtWidgets.qApp.allWidgets():
        mo = w.metaObject()
        if w.objectName() and not w.objectName().startswith("qt_"):
            settings.beginGroup(w.objectName())
            for i in range(mo.propertyCount()):
                prop = mo.property(i)
                name = prop.name()
                if prop.isWritable():
                    settings.setValue(name, w.property(name))
            settings.endGroup()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 650)

        # define video thread
        global th
        th = Thread(MainWindow)

        MainWindow.setMouseTracking(True)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        self.display_video = QtWidgets.QLabel(self.centralwidget)
        self.display_video.setGeometry(QtCore.QRect(30, 20, 640, 480))
        self.display_video.setFrameShape(QtWidgets.QFrame.Box)
        self.display_video.setAlignment(QtCore.Qt.AlignCenter)
        self.display_video.setObjectName("display_video")


        self.input = QtWidgets.QLineEdit(self.centralwidget)
        self.input.setGeometry(QtCore.QRect(30, 510, 541, 25))
        self.input.setObjectName("input")


        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(730, 330, 89, 25))
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.video)


        self.stopbutton = QtWidgets.QPushButton(self.centralwidget)
        self.stopbutton.setGeometry(QtCore.QRect(730, 380, 89, 25))
        self.stopbutton.setObjectName("stopbutton")
        self.stopbutton.clicked.connect(close_window)


        self.applybutton = QtWidgets.QPushButton(self.centralwidget)
        self.applybutton.setGeometry(QtCore.QRect(580, 510, 89, 25))
        self.applybutton.setObjectName("applybutton")
        self.applybutton.clicked.connect(self.get_path)


        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def video(self):
        global path, count
        if path is None or len(path) == 0:
            camera_source_alarm()
        else:
            self.display_video.resize(640, 480)
            th.changePixmap.connect(self.setImage)
            th.start()

    def setImage(self, image):
        self.display_video.setPixmap(QtGui.QPixmap.fromImage(image))

    def get_path(self):
        global path
        data_path = self.input.text()
        # get path
        path = data_path
        return path



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.display_video.setText(_translate("MainWindow", "Video"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.stopbutton.setText(_translate("MainWindow", "Stop"))
        self.applybutton.setText(_translate("MainWindow", "Apply"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.settings = QtCore.QSettings()
        restore(self.settings)

    def closeEvent(self, event):
        save(self.settings)
        super().closeEvent(event)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setOrganizationName("Eyllanesc")
    QtCore.QCoreApplication.setOrganizationDomain("eyllanesc.com")
    QtCore.QCoreApplication.setApplicationName("MyApp")
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

