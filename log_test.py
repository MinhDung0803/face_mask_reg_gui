# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log_test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import matplotlib.pyplot as plt
import time
import os

global conn, c
conn = sqlite3.connect('Face_Mask_Recognition_DataBase.db')
c = conn.cursor()

def plotting_1(camera_name_input_1,
               day_input_1,
               month_input_1,
               year_input_1,
               check_day_1,
               check_month_1,
               check_year_1):
    global c
    if check_day_1 == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input_1}' " \
                f"and Year = {year_input_1} and Day = {day_input_1}"
        c.execute(query)
        return_data = c.fetchall()

    elif check_month_1 == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input_1}' " \
                f"and Year = {year_input_1} and Month = {month_input_1}"
        c.execute(query)
        return_data = c.fetchall()
    elif check_year_1 == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input_1}' " \
                f"and Year = {year_input_1}"
        c.execute(query)
        return_data = c.fetchall()
        t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        # x = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
        x = ["M%d" % i for i in range(1, 13, 1)]
        # y = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]
        y = [0 for i in range(1, 13, 1)]
        for elem in return_data:
            for i in range(len(y)):
                if elem[4]-1 == i:
                    y[i] += 1
        plt.bar(x, y)
        plt.xlabel('Month')
        plt.ylabel('Number of No Face-Mask')
        for index, value in enumerate(y):
            plt.text(index, value, str(value), color="red")
        if os.path.exists("figure1.png") is True:
            os.remove("figure1.png")
            time.sleep(1)
        plt.savefig('figure1.png')
        time.sleep(0.5)



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
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
        self.label.setGeometry(QtCore.QRect(10, 40, 41, 17))
        self.label.setObjectName("label")
        self.from_time = QtWidgets.QTimeEdit(self.groupBox_4)
        self.from_time.setGeometry(QtCore.QRect(50, 40, 61, 26))
        self.from_time.setObjectName("from_time")
        self.label_4 = QtWidgets.QLabel(self.groupBox_4)
        self.label_4.setGeometry(QtCore.QRect(120, 40, 21, 17))
        self.label_4.setObjectName("label_4")
        self.to_time = QtWidgets.QTimeEdit(self.groupBox_4)
        self.to_time.setGeometry(QtCore.QRect(150, 40, 61, 26))
        self.to_time.setObjectName("to_time")
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
        self.start.setObjectName("start")
        self.draw_region = QtWidgets.QPushButton(self.tab)
        self.draw_region.setGeometry(QtCore.QRect(760, 450, 111, 71))
        self.draw_region.setObjectName("draw_region")
        self.stop = QtWidgets.QPushButton(self.tab)
        self.stop.setGeometry(QtCore.QRect(670, 540, 81, 71))
        self.stop.setObjectName("stop")
        self.draw_count = QtWidgets.QPushButton(self.tab)
        self.draw_count.setGeometry(QtCore.QRect(760, 540, 111, 71))
        self.draw_count.setObjectName("draw_count")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.display_ploting_1 = QtWidgets.QLabel(self.tab_2)
        self.display_ploting_1.setGeometry(QtCore.QRect(10, 10, 581, 291))
        self.display_ploting_1.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_1.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_1.setObjectName("display_ploting_1")

        self.groupBox_plot1 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_plot1.setGeometry(QtCore.QRect(600, 30, 271, 251))
        self.groupBox_plot1.setObjectName("groupBox_plot1")
        self.label_15 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_15.setGeometry(QtCore.QRect(10, 160, 51, 17))
        self.label_15.setObjectName("label_15")
        self.label_14 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_14.setGeometry(QtCore.QRect(10, 130, 51, 17))
        self.label_14.setObjectName("label_14")

        # input and button day 1
        self.input_day_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_day_1.setGeometry(QtCore.QRect(70, 100, 113, 25))
        self.input_day_1.setObjectName("input_day_1")
        self.radioButton_day_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_day_1.setGeometry(QtCore.QRect(200, 100, 112, 23))
        self.radioButton_day_1.setObjectName("radioButton_day_1")

        # input and button year 1
        self.input_year_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_year_1.setGeometry(QtCore.QRect(70, 160, 113, 25))
        self.input_year_1.setObjectName("input_year_1")
        self.radioButton_year_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_year_1.setGeometry(QtCore.QRect(200, 160, 112, 23))
        self.radioButton_year_1.setObjectName("radioButton_year_1")

        self.label_13 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_13.setGeometry(QtCore.QRect(10, 100, 31, 17))
        self.label_13.setObjectName("label_13")

        # input and button month 1
        self.input_month_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_month_1.setGeometry(QtCore.QRect(70, 130, 113, 25))
        self.input_month_1.setObjectName("input_month_1")
        self.radioButton_month_1 = QtWidgets.QRadioButton(self.groupBox_plot1)
        self.radioButton_month_1.setGeometry(QtCore.QRect(200, 130, 112, 23))
        self.radioButton_month_1.setObjectName("radioButton_month_1")

        self.plot1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.plot1.setGeometry(QtCore.QRect(90, 200, 101, 41))
        self.plot1.setObjectName("plot1")
        self.plot1.clicked.connect(self.display_plotting_figure_1)

        self.label_2 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_2.setObjectName("label_2")

        # input camera 1
        self.input_camera_name_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_camera_name_1.setGeometry(QtCore.QRect(10, 60, 191, 25))
        self.input_camera_name_1.setObjectName("input_camera_name_1")
        self.button_camera_name_1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.button_camera_name_1.setGeometry(QtCore.QRect(210, 44, 51, 41))
        self.button_camera_name_1.setObjectName("button_camera_name_1")
        self.button_camera_name_1.clicked.connect(self.get_camera_name_1)

        self.groupBox_3_plot2 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3_plot2.setGeometry(QtCore.QRect(600, 340, 271, 251))
        self.groupBox_3_plot2.setObjectName("groupBox_3_plot2")
        self.label_16 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_16.setGeometry(QtCore.QRect(10, 160, 51, 17))
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_17.setGeometry(QtCore.QRect(10, 130, 51, 17))
        self.label_17.setObjectName("label_17")

        # input and button day 2
        self.input_day_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_day_2.setGeometry(QtCore.QRect(70, 100, 113, 25))
        self.input_day_2.setObjectName("input_day_2")
        self.radioButton_day_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_day_2.setGeometry(QtCore.QRect(200, 100, 112, 23))
        self.radioButton_day_2.setObjectName("radioButton_day_2")

        # input and button year 2
        self.input_year_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_year_2.setGeometry(QtCore.QRect(70, 160, 113, 25))
        self.input_year_2.setObjectName("input_year_2")
        self.radioButton_year_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_year_2.setGeometry(QtCore.QRect(200, 160, 112, 23))
        self.radioButton_year_2.setObjectName("radioButton_year_2")

        self.label_18 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_18.setGeometry(QtCore.QRect(10, 100, 31, 17))
        self.label_18.setObjectName("label_18")

        # input and button month 2
        self.input_month_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_month_2.setGeometry(QtCore.QRect(70, 130, 113, 25))
        self.input_month_2.setObjectName("input_month_2")
        self.radioButton_month_2 = QtWidgets.QRadioButton(self.groupBox_3_plot2)
        self.radioButton_month_2.setGeometry(QtCore.QRect(200, 130, 112, 23))
        self.radioButton_month_2.setObjectName("radioButton_month_2")

        self.plot2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.plot2.setGeometry(QtCore.QRect(90, 200, 101, 41))
        self.plot2.setObjectName("plot2")
        self.plot2.clicked.connect(self.display_ploting_figure_2)

        self.label_3 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_3.setObjectName("label_3")

        self.input_camera_name_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_camera_name_2.setGeometry(QtCore.QRect(10, 60, 191, 25))
        self.input_camera_name_2.setObjectName("input_camera_name_2")
        self.button_camera_name_2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.button_camera_name_2.setGeometry(QtCore.QRect(210, 44, 51, 41))
        self.button_camera_name_2.setObjectName("button_camera_name_2")

        self.display_ploting_2 = QtWidgets.QLabel(self.tab_2)
        self.display_ploting_2.setGeometry(QtCore.QRect(10, 320, 581, 291))
        self.display_ploting_2.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_2.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_2.setObjectName("display_ploting_2")
        self.tabWidget.addTab(self.tab_2, "")
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

    def get_camera_name_1(self):
        global camera_name_input_1
        camera_name_input_1 = self.input_camera_name_1.text()

    def display_plotting_figure_1(self):
        global camera_name_input_1
        check_day_1 = 0
        check_month_1 = 0
        check_year_1 = 0

        day_input_1 = self.input_day_1.text()
        month_input_1 = self.input_month_1.text()
        year_input_1 = self.input_year_1.text()
        if self.radioButton_day_1.isChecked():
            check_day_1 = 1
            check_month_1 = 0
            check_year_1 = 0
        elif self.radioButton_month_1.isChecked():
            check_day_1 = 0
            check_month_1 = 1
            check_year_1 = 0
        elif self.radioButton_year_1.isChecked():
            check_day_1 = 0
            check_month_1 = 0
            check_year_1 = 1

        plotting_1(camera_name_input_1,
                   day_input_1,
                   month_input_1,
                   year_input_1,
                   check_day_1,
                   check_month_1,
                   check_year_1)
        self.display_ploting_1.clear()
        if len(camera_name_input_1) == 0:
            print("None")
        else:
            self.display_ploting_1.setScaledContents(True)
            pixmap = QtGui.QPixmap('figure1.png')
            # print(pixmap)
            self.display_ploting_1.setPixmap(pixmap)
            os.remove("figure1.png")

    def display_ploting_figure_2(self):
        self.display_ploting_2.setScaledContents(True)
        pixmap = QtGui.QPixmap('figure2.png')
        self.display_ploting_2.setPixmap(pixmap)

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
        self.groupBox_5.setTitle(_translate("MainWindow", "No Face Mask Counting"))
        self.display_no_face_mask_counting.setText(_translate("MainWindow", "Counting"))
        self.start.setText(_translate("MainWindow", "START"))
        self.draw_region.setText(_translate("MainWindow", "DRAW REGION"))
        self.stop.setText(_translate("MainWindow", "STOP"))
        self.draw_count.setText(_translate("MainWindow", "DRAW COUNT"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.display_ploting_1.setText(_translate("MainWindow", "Ploting_1"))
        self.groupBox_plot1.setTitle(_translate("MainWindow", "Option Plot 1"))
        self.label_15.setText(_translate("MainWindow", "Year"))
        self.label_14.setText(_translate("MainWindow", "Month"))
        self.radioButton_day_1.setText(_translate("MainWindow", "Day"))
        self.label_13.setText(_translate("MainWindow", "Day"))
        self.radioButton_month_1.setText(_translate("MainWindow", "Month"))
        self.radioButton_year_1.setText(_translate("MainWindow", "Year"))
        self.plot1.setText(_translate("MainWindow", "PLOT"))
        self.label_2.setText(_translate("MainWindow", "Name of camera"))
        self.button_camera_name_1.setText(_translate("MainWindow", "OK"))
        self.groupBox_3_plot2.setTitle(_translate("MainWindow", "Option Plot 2"))
        self.label_16.setText(_translate("MainWindow", "Year"))
        self.label_17.setText(_translate("MainWindow", "Month"))
        self.radioButton_day_2.setText(_translate("MainWindow", "Day"))
        self.label_18.setText(_translate("MainWindow", "Day"))
        self.radioButton_month_2.setText(_translate("MainWindow", "Month"))
        self.radioButton_year_2.setText(_translate("MainWindow", "Year"))
        self.plot2.setText(_translate("MainWindow", "PLOT"))
        self.label_3.setText(_translate("MainWindow", "Name of camera"))
        self.button_camera_name_2.setText(_translate("MainWindow", "OK"))
        self.display_ploting_2.setText(_translate("MainWindow", "Ploting_2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menuMain.setTitle(_translate("MainWindow", "Main"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

