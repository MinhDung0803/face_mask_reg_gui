# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './design/log_test_2.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import matplotlib.pyplot as plt
import time
import os
import cv2
import pandas as pd
import threading


# variables
path = None
name = None
camera_name_input_1 = ""
camera_name_input_2 = ""
count = 0
height = 480
width = 640
w_width = 900
w_height = 700
light_alarm = 1
sound_alarm = 0
both_alarm = 0
draw_region_points = []
extra_pixels = 5  # for default regions
default_region_points = [
    [(0 + extra_pixels, 0 + extra_pixels), (width - extra_pixels, 0 + extra_pixels)],
    [(width - extra_pixels, 0 + extra_pixels), (width - extra_pixels, height - extra_pixels)],
    [(width - extra_pixels, height - extra_pixels), (0 + extra_pixels, height - extra_pixels)],
    [(0 + extra_pixels, height - extra_pixels), (0 + extra_pixels, 0 + extra_pixels)]]
draw_region_flag = False
draw_counting_points = []
default_counting_points = [[(0, int(height / 2)), (width, int(height / 2))]]
draw_count_flag = False
check_list = []

# connect to sql database
conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
c = conn.cursor()


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent, abc):
        QtCore.QThread.__init__(self, parent)
        self._go = None
        self.abc = abc

    def run(self):
        global count, \
            height, \
            width, \
            draw_region_points, \
            default_region_points, \
            draw_region_flag, \
            default_counting_points, \
            draw_count_flag, \
            draw_counting_points
        cap = cv2.VideoCapture(path)
        self._go = True
        while self._go:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (width, height))
                print("dung pm check status:", self.abc)

                # condition to draw region
                if not draw_region_flag:
                    final_region_points = default_region_points
                else:
                    final_region_points = draw_region_points
                # draw region
                for i, point in enumerate(final_region_points):
                    cv2.line(frame, point[0], point[1], (0, 0, 255), 2)

                # condition to draw counting region
                if not draw_count_flag:
                    final_counting_points = default_counting_points
                else:
                    final_counting_points = draw_counting_points
                # draw counting region
                for i, point in enumerate(final_counting_points):
                    cv2.line(frame, point[0], point[1], (0, 255, 255), 2)

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
        global path, \
            draw_region_flag, \
            draw_count_flag, \
            draw_counting_points, \
            draw_region_points
        self._go = False
        path = None
        draw_region_flag = False
        draw_count_flag = False
        draw_counting_points = []
        draw_region_points = []


def close_window():
    th.stop_thread()
    time.sleep(0.5)
    # exit()


def camera_source_alarm():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Camera Source Warning")
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


def check_camera_name():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Camera Name Warning")
    alert.setText('Please set the name of Camera!')
    alert.exec_()


def check_camera_name_plotting():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Camera Name for Statistics Warning")
    alert.setText('Please input the name of Camera to query in Database!')
    alert.exec_()


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
    def setupUi(self, MainWindow, abc):
        self.abc = abc
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 694)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 891, 651))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.display_video = QtWidgets.QLabel(self.tab)
        self.display_video.setGeometry(QtCore.QRect(10, 10, 640, 480))
        self.display_video.setFrameShape(QtWidgets.QFrame.Box)
        self.display_video.setAlignment(QtCore.Qt.AlignCenter)
        self.display_video.setObjectName("display_video")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(10, 500, 641, 121))
        self.groupBox.setObjectName("groupBox")
        self.radioButton_ip_camera = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_ip_camera.setGeometry(QtCore.QRect(10, 30, 112, 23))
        self.radioButton_ip_camera.setObjectName("radioButton_ip_camera")
        self.radioButton_ip_camera.setChecked(True)
        self.radioButton_webcam = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_webcam.setGeometry(QtCore.QRect(130, 30, 112, 23))
        self.radioButton_webcam.setObjectName("radioButton_webcam")
        self.source_input_camera_name = QtWidgets.QLineEdit(self.groupBox)
        self.source_input_camera_name.setGeometry(QtCore.QRect(170, 60, 371, 25))
        self.source_input_camera_name.setObjectName("source_input_camera_name")
        self.source_path = QtWidgets.QLineEdit(self.groupBox)
        self.source_path.setGeometry(QtCore.QRect(60, 90, 481, 25))
        self.source_path.setObjectName("source_path")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(20, 60, 141, 17))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(20, 90, 41, 17))
        self.label_6.setObjectName("label_6")
        self.apply = QtWidgets.QPushButton(self.groupBox)
        self.apply.setGeometry(QtCore.QRect(550, 30, 81, 81))
        font = QtGui.QFont()
        font.setBold(True)
        self.apply.setFont(font)
        self.apply.setObjectName("apply")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setGeometry(QtCore.QRect(660, 10, 221, 151))
        self.groupBox_3.setObjectName("groupBox_3")
        self.radioButton_light_option = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_light_option.setGeometry(QtCore.QRect(10, 30, 112, 23))
        self.radioButton_light_option.setObjectName("radioButton_light_option")
        self.radioButton_sound_option = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_sound_option.setGeometry(QtCore.QRect(10, 70, 112, 23))
        self.radioButton_sound_option.setObjectName("radioButton_sound_option")
        self.radioButton_light_and_sound_option = QtWidgets.QRadioButton(self.groupBox_3)
        self.radioButton_light_and_sound_option.setGeometry(QtCore.QRect(10, 110, 141, 23))
        self.radioButton_light_and_sound_option.setObjectName("radioButton_light_and_sound_option")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setGeometry(QtCore.QRect(660, 180, 221, 91))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label = QtWidgets.QLabel(self.groupBox_4)
        self.label.setGeometry(QtCore.QRect(10, 30, 41, 17))
        self.label.setObjectName("label")
        self.from_time = QtWidgets.QTimeEdit(self.groupBox_4)
        self.from_time.setGeometry(QtCore.QRect(50, 30, 61, 26))
        self.from_time.setObjectName("from_time")
        self.label_4 = QtWidgets.QLabel(self.groupBox_4)
        self.label_4.setGeometry(QtCore.QRect(120, 30, 21, 17))
        self.label_4.setObjectName("label_4")
        self.to_time = QtWidgets.QTimeEdit(self.groupBox_4)
        self.to_time.setGeometry(QtCore.QRect(150, 30, 61, 26))
        self.to_time.setObjectName("to_time")
        self.pushButton_set_time = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_set_time.setGeometry(QtCore.QRect(70, 60, 89, 25))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_set_time.setFont(font)
        self.pushButton_set_time.setObjectName("pushButton_set_time")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_5.setGeometry(QtCore.QRect(660, 280, 221, 151))
        self.groupBox_5.setObjectName("groupBox_5")
        self.display_no_face_mask_counting = QtWidgets.QLabel(self.groupBox_5)
        self.display_no_face_mask_counting.setGeometry(QtCore.QRect(20, 30, 181, 101))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.display_no_face_mask_counting.setFont(font)
        self.display_no_face_mask_counting.setFrameShape(QtWidgets.QFrame.Box)
        self.display_no_face_mask_counting.setLineWidth(5)
        self.display_no_face_mask_counting.setTextFormat(QtCore.Qt.AutoText)
        self.display_no_face_mask_counting.setScaledContents(False)
        self.display_no_face_mask_counting.setAlignment(QtCore.Qt.AlignCenter)
        self.display_no_face_mask_counting.setIndent(-1)
        self.display_no_face_mask_counting.setObjectName("display_no_face_mask_counting")
        self.start = QtWidgets.QPushButton(self.tab)
        self.start.setGeometry(QtCore.QRect(670, 450, 81, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.start.setFont(font)
        self.start.setObjectName("start")
        self.draw_region = QtWidgets.QPushButton(self.tab)
        self.draw_region.setGeometry(QtCore.QRect(760, 450, 111, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.draw_region.setFont(font)
        self.draw_region.setObjectName("draw_region")
        self.stop = QtWidgets.QPushButton(self.tab)
        self.stop.setGeometry(QtCore.QRect(670, 540, 81, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.stop.setFont(font)
        self.stop.setObjectName("stop")
        self.draw_count = QtWidgets.QPushButton(self.tab)
        self.draw_count.setGeometry(QtCore.QRect(760, 540, 111, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.draw_count.setFont(font)
        self.draw_count.setObjectName("draw_count")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.display_ploting_1 = QtWidgets.QLabel(self.tab_2)
        self.display_ploting_1.setGeometry(QtCore.QRect(10, 10, 661, 291))
        self.display_ploting_1.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_1.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_1.setObjectName("display_ploting_1")
        self.groupBox_plot1 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_plot1.setGeometry(QtCore.QRect(680, 30, 201, 251))
        self.groupBox_plot1.setObjectName("groupBox_plot1")
        self.label_15 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_15.setGeometry(QtCore.QRect(10, 160, 51, 17))
        self.label_15.setObjectName("label_15")
        self.label_14 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_14.setGeometry(QtCore.QRect(10, 130, 51, 17))
        self.label_14.setObjectName("label_14")
        self.input_day_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_day_1.setGeometry(QtCore.QRect(60, 100, 61, 25))
        self.input_day_1.setObjectName("input_day_1")
        self.radioButton_day_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_day_1.setGeometry(QtCore.QRect(130, 100, 51, 23))
        self.radioButton_day_1.setObjectName("radioButton_day_1")
        self.input_year_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_year_1.setGeometry(QtCore.QRect(60, 160, 61, 25))
        self.input_year_1.setObjectName("input_year_1")
        self.label_13 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_13.setGeometry(QtCore.QRect(10, 100, 31, 17))
        self.label_13.setObjectName("label_13")
        self.input_month_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_month_1.setGeometry(QtCore.QRect(60, 130, 61, 25))
        self.input_month_1.setObjectName("input_month_1")
        self.radioButton_month_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_month_1.setGeometry(QtCore.QRect(130, 130, 71, 23))
        self.radioButton_month_1.setObjectName("radioButton_month_1")
        self.radioButton_year_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_year_1.setGeometry(QtCore.QRect(130, 160, 61, 23))
        self.radioButton_year_1.setObjectName("radioButton_year_1")
        self.plot1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.plot1.setGeometry(QtCore.QRect(10, 200, 81, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.plot1.setFont(font)
        self.plot1.setObjectName("plot1")
        self.label_2 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_2.setObjectName("label_2")
        self.input_camera_name_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_camera_name_1.setGeometry(QtCore.QRect(10, 60, 131, 25))
        self.input_camera_name_1.setObjectName("input_camera_name_1")
        self.button_camera_name_1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.button_camera_name_1.setGeometry(QtCore.QRect(150, 54, 41, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_camera_name_1.setFont(font)
        self.button_camera_name_1.setObjectName("button_camera_name_1")
        self.export_1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.export_1.setGeometry(QtCore.QRect(110, 200, 81, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.export_1.setFont(font)
        self.export_1.setObjectName("export_1")
        self.groupBox_3_plot2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3_plot2.setGeometry(QtCore.QRect(680, 340, 201, 251))
        self.groupBox_3_plot2.setObjectName("groupBox_3_plot2")
        self.label_16 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_16.setGeometry(QtCore.QRect(10, 160, 51, 17))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_17.setGeometry(QtCore.QRect(10, 130, 51, 17))
        self.label_17.setObjectName("label_17")
        self.input_day_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_day_2.setGeometry(QtCore.QRect(60, 100, 61, 25))
        self.input_day_2.setObjectName("input_day_2")
        self.radioButton_day_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_day_2.setGeometry(QtCore.QRect(130, 100, 51, 23))
        self.radioButton_day_2.setObjectName("radioButton_day_2")
        self.input_year_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_year_2.setGeometry(QtCore.QRect(60, 160, 61, 25))
        self.input_year_2.setObjectName("input_year_2")
        self.label_18 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_18.setGeometry(QtCore.QRect(10, 100, 31, 17))
        self.label_18.setObjectName("label_18")
        self.input_month_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_month_2.setGeometry(QtCore.QRect(60, 130, 61, 25))
        self.input_month_2.setObjectName("input_month_2")
        self.radioButton_month_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_month_2.setGeometry(QtCore.QRect(130, 130, 71, 23))
        self.radioButton_month_2.setObjectName("radioButton_month_2")
        self.radioButton_year_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_year_2.setGeometry(QtCore.QRect(130, 160, 61, 23))
        self.radioButton_year_2.setObjectName("radioButton_year_2")
        self.plot2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.plot2.setGeometry(QtCore.QRect(10, 200, 81, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.plot2.setFont(font)
        self.plot2.setObjectName("plot2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_3.setObjectName("label_3")
        self.input_camera_name_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_camera_name_2.setGeometry(QtCore.QRect(10, 60, 131, 25))
        self.input_camera_name_2.setObjectName("input_camera_name_2")
        self.button_camera_name_2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.button_camera_name_2.setGeometry(QtCore.QRect(150, 54, 41, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.button_camera_name_2.setFont(font)
        self.button_camera_name_2.setObjectName("button_camera_name_2")
        self.export_2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.export_2.setGeometry(QtCore.QRect(110, 200, 81, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.export_2.setFont(font)
        self.export_2.setObjectName("export_2")
        self.display_ploting_2 = QtWidgets.QLabel(self.tab_2)
        self.display_ploting_2.setGeometry(QtCore.QRect(10, 320, 661, 291))
        self.display_ploting_2.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_2.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_2.setObjectName("display_ploting_2")
        self.tabWidget.addTab(self.tab_2, "")

        # get camera source path
        self.apply.clicked.connect(self.get_path)
        # start video
        self.start.clicked.connect(self.video)
        # stop video
        self.stop.clicked.connect(close_window)
        # call display video
        global th
        th = Thread(MainWindow, self.abc)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 22))
        self.menubar.setObjectName("menubar")
        self.menuMain = QtWidgets.QMenu(self.menubar)
        self.menuMain.setObjectName("menuMain")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuMain.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def video(self):
        global path, count
        self.display_no_face_mask_counting.setText(str(count))
        if path is None or len(path) == 0:
            camera_source_alarm()
        else:
            self.display_video.resize(640, 480)
            th.changePixmap.connect(self.setImage)
            th.start()

    def setImage(self, image):
        self.display_video.setPixmap(QtGui.QPixmap.fromImage(image))

    def get_path(self):
        global path, name
        data_path = self.source_path.text()
        camera_name_source = self.source_input_camera_name.text()
        # check for IP camera path
        if len(camera_name_source) == 0:
            check_camera_name()
        else:
            name = camera_name_source
        if self.radioButton_ip_camera.isChecked():
            if len(data_path) < 10:
                check_path_for_ip_camera()
            else:
                ###
                path = data_path
                # json_file = 'json_test_file.json'
                # f = open(json_file)
                # json_data = json.load(f)
                # f.close()
                # json_data["data"][0]["url"] = str(path)
                # with open(json_file, 'w') as f:
                #     json.dump(json_data, f)
        # check for webcam ID
        if self.radioButton_webcam.isChecked():
            if len(data_path) > 10:
                check_path_for_webcam()
            else:
                ###
                path = data_path
        return path

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.display_video.setText(_translate("MainWindow", "Video"))
        self.groupBox.setTitle(_translate("MainWindow", "Source"))
        self.radioButton_ip_camera.setText(_translate("MainWindow", "IP Camera"))
        self.radioButton_webcam.setText(_translate("MainWindow", "Webcam"))
        self.label_5.setText(_translate("MainWindow", "Set name of camera"))
        self.label_6.setText(_translate("MainWindow", "Path"))
        self.apply.setText(_translate("MainWindow", "APPLY"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Alarm Option"))
        self.radioButton_light_option.setText(_translate("MainWindow", "Light"))
        self.radioButton_sound_option.setText(_translate("MainWindow", "Sound"))
        self.radioButton_light_and_sound_option.setText(_translate("MainWindow", "Light and Sound"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Setting Time"))
        self.label.setText(_translate("MainWindow", "From"))
        self.label_4.setText(_translate("MainWindow", "To"))
        self.pushButton_set_time.setText(_translate("MainWindow", "SET TIME"))
        self.groupBox_5.setTitle(_translate("MainWindow", "No Face Mask Counting"))
        self.display_no_face_mask_counting.setText(_translate("MainWindow", "Counting"))
        self.start.setText(_translate("MainWindow", "START"))
        self.draw_region.setText(_translate("MainWindow", "DRAW REGION"))
        self.stop.setText(_translate("MainWindow", "STOP"))
        self.draw_count.setText(_translate("MainWindow", "DRAW COUNT"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.display_ploting_1.setText(_translate("MainWindow", "Ploting_1"))
        self.groupBox_plot1.setTitle(_translate("MainWindow", "Setting Plot 1"))
        self.label_15.setText(_translate("MainWindow", "Year"))
        self.label_14.setText(_translate("MainWindow", "Month"))
        self.radioButton_day_1.setText(_translate("MainWindow", "Day"))
        self.label_13.setText(_translate("MainWindow", "Day"))
        self.radioButton_month_1.setText(_translate("MainWindow", "Month"))
        self.radioButton_year_1.setText(_translate("MainWindow", "Year"))
        self.plot1.setText(_translate("MainWindow", "PLOT 1"))
        self.label_2.setText(_translate("MainWindow", "Name of camera"))
        self.button_camera_name_1.setText(_translate("MainWindow", "OK"))
        self.export_1.setText(_translate("MainWindow", "EXPORT 1"))
        self.groupBox_3_plot2.setTitle(_translate("MainWindow", "Setting Plot 2"))
        self.label_16.setText(_translate("MainWindow", "Year"))
        self.label_17.setText(_translate("MainWindow", "Month"))
        self.radioButton_day_2.setText(_translate("MainWindow", "Day"))
        self.label_18.setText(_translate("MainWindow", "Day"))
        self.radioButton_month_2.setText(_translate("MainWindow", "Month"))
        self.radioButton_year_2.setText(_translate("MainWindow", "Year"))
        self.plot2.setText(_translate("MainWindow", "PLOT 2"))
        self.label_3.setText(_translate("MainWindow", "Name of camera"))
        self.button_camera_name_2.setText(_translate("MainWindow", "OK"))
        self.export_2.setText(_translate("MainWindow", "EXPORT 2"))
        self.display_ploting_2.setText(_translate("MainWindow", "Ploting_2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menuMain.setTitle(_translate("MainWindow", "Main"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, abc):
        global w_height, w_width
        super().__init__()
        self.abc = abc
        self.setupUi(self, self.abc)
        self.setFixedSize(w_width, w_height)
        self.settings = QtCore.QSettings()
        # print(self.settings.fileName())
        restore(self.settings)

    def closeEvent(self, event):
        save(self.settings)
        super().closeEvent(event)


def app(abc):
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setOrganizationName("Eyllanesc")
    QtCore.QCoreApplication.setOrganizationDomain("eyllanesc.com")
    QtCore.QCoreApplication.setApplicationName("MyApp")
    w = MainWindow(abc)
    w.show()
    app.exec_()
    # sys.exit(app.exec_())


def app_threading(abc):
    t = threading.Thread(target=app,
                         args=[abc])
    t.start()


# if __name__ == "__main__":
#     abc = 123
#     app(abc)
