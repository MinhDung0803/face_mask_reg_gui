# import pandas as pd
# import matplotlib.pyplot as plt
# import datetime
# import os
# import shutil
# import sqlite3

# read data from csv file
# data = pd.read_csv('data.csv')
# print(data)
# a = data["Country_ID"]

# a = {"T1": 4, "T2": 5, "T3": 8, "T4": 9, "T5": 4}
# names = list(a.keys())
# values = list(a.values())
# #tick_label does the some work as plt.xticks()
# plt.bar(range(len(a)),values,tick_label=names)
# plt.savefig('bar.png')
# plt.show()

# plt.bar(*zip(*a.items()))
# plt.savefig('figure2.png')
# plt.show()

# x = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
# y = [3, 4, 5, 6, 7, 4, 4, 7, 4, 9, 2, 2]
#
# plt.figure(figsize=(10, 5))
# plt.bar(x, y)
# plt.xlabel('Month')
# plt.ylabel('Number of No Face-Mask')
# for index, value in enumerate(y):
#     plt.text(index, value, str(value), color ="red", size='xx-large')
# plt.savefig('bar.png')
# plt.show()

# x = ["M%d" % i for i in range(1, 13, 1)]
# print(x)

# if os.path.exists("figure1.png"):
#     print("True")
#     shutil.rmtree("./figure1.png")
# else:
#     print("False")

# even_month = [i for i in range(1, 13, 2)]
# print(even_month)
# old_month = [i for i in range(2, 13, 2)]
# print(old_month)
# camera_name_input = "A"
# year_input = 2020
#
# conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
# c = conn.cursor()
#
# query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
#                 f"and Year = {year_input}"
# c.execute(query)
# return_data = c.fetchall()
# df = DataFrame(return_data, columns=["Camera name", "Minute", "Hour", "Day", "Month", "Year"])
# df.to_csv('./export_data/export_data_example.csv')
# print(df)

# import sys
# sys.path.append(("/home/gg-greenlab/Desktop/Project/dungpm/face_mask_reg_gui/face_mask_detection.py"))
# import detection_module

# os.system("python face_mask_detection.py ./configs/Cam_PTZ.yml")

# import json
# import yaml
#
#
# json_file = 'Camera_PTZ.json'
# f = open(json_file)
# json_data = json.load(f)
# f.close()
# data = json_data["data"]
#
# data[0]["url"] = "a"
#
# with open(json_file, "w") as outfile:
#     json.dump(data, outfile)
#
# print(data)

# print("A"*150)
#
# from playsound import playsound
# playsound('police.mp3')

# import pyglet
#
# music = pyglet.resource.media('police.mp3')
# music.play()
# pyglet.app.run()

# list_test = [1, 2, 3, 4, 5, 6, 7, 8]
# for i in range(0, len(list_test), 2):
#     if i+3 > len(list_test):
#         print("first point: ", (list_test[i], list_test[i+1]), "second point: ", (list_test[0], list_test[1]))
#     else:
#         print("first point: ", (list_test[i], list_test[i+1]), "second point: ", (list_test[i+2], list_test[i+3]))


# name = "camera1"
# data = datetime.datetime.now()
# data_form = {"Camera_name": name,
#              "Minute": int(data.minute),
#              "Hour": int(data.hour),
#              "Day": int(data.day),
#              "Month": int(data.month),
#              "Year": int(data.year)}
# print(data_form)
# data_form_add = pd.DataFrame.from_dict([data_form])
# print(data_form_add)


# from pydub import AudioSegment
# from pydub.playback import play
# import threading
#
#
# def play_audio(file):
#     # Input an existing wav filename
#     # wavFile = "police.mp3"
#     # load the file into pydub
#     sound = AudioSegment.from_file(file)
#     print("Playing wav file...")
#     # play the file
#     play(sound)
#
#
# def play_audio_by_threading(file):
#     t = threading.Thread(target = play_audio, args = [file])
#     t.start()
#
#
# if __name__ == "__main__":
#     # Input an existing wav filename
#     wavFile = "./sound_alarm/police.mp3"
#     play_audio_by_threading(wavFile)

# def insert_data(self):
#     data = [
#         {"camera_name": "camera1", "status": "working"},
#         {"camera_name": "camera2", "status": "stopped"},
#         {"camera_name": "camera3", "status": "working"},
#         {"camera_name": "camera4", "status": "working"}
#     ]
#
#     row_count = (len(data))
#     column_count = (len(data[0]))
#     # self.table.setHorizontalHeaderLabels((list(data[0].keys())))
#     for row in range(row_count):  # add items from array to QTableWidget
#         for column in range(column_count):
#             item = (list(data[row].values())[column])
#             self.table.setItem(row, column, QtWidgets.QTableWidgetItem(item))
#
# def get_date(self):
#     date = self.combo_box.currentText()
#     if str(date) == "Ngày":
#         self.display1.display(1)
#         self.output.setText(str(1))
#     elif str(date) == "Tháng":
#         self.display1.display(2)
#         self.output.setText(str(2))
#     elif str(date) == "Năm":
#         self.display1.display(3)
#         self.output.setText(str(3))

# # event
# self.exit.triggered.connect(exit_app)

# # icon
# self.plot_1.setIcon(QtGui.QIcon('./icon/plot.png'))
# self.save_1.setIcon(QtGui.QIcon('./icon/save.png'))
# self.export_1.setIcon(QtGui.QIcon('./icon/export.jpeg'))
#
# self.plot_5.setIcon(QtGui.QIcon('./icon/plot.png'))
# self.save_5.setIcon(QtGui.QIcon('./icon/save.png'))
# self.export_5.setIcon(QtGui.QIcon('./icon/export.jpeg'))
#
# # event
# self.comboBox_3.activated.connect(self.change_plot_date_format)
#
#
# def change_plot_date_format(self):
#     if self.comboBox_3.currentText() == "Thống kê theo Ngày":
#         self.dateEdit.setDisplayFormat("dd/MM/yyyy")
#     elif self.comboBox_3.currentText() == "Thống kê theo Tháng":
#         self.dateEdit.setDisplayFormat("MM/yyyy")
#     elif self.comboBox_3.currentText() == "Thống kê theo Năm":
#         self.dateEdit.setDisplayFormat("yyyy")


# # ----- set icon
# # giam sat
# self.g_start_button.setIcon(QtGui.QIcon('./icon/start.jpg'))
# self.g_stop_button.setIcon(QtGui.QIcon('./icon/stop.png'))
# self.g_pause_play_button.setIcon(QtGui.QIcon('./icon/pause.png'))
# # quan li camera
# self.q_moi_vung_quan_sat_button.setIcon(QtGui.QIcon('./icon/draw.png'))
# self.q_moi_vach_kiem_dem_button.setIcon(QtGui.QIcon('./icon/draw.png'))
# self.q_moi_appy_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
# self.q_moi_add_button.setIcon(QtGui.QIcon('./icon/add.jpg'))
# self.q_moi_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
# self.q_chinh_search_button.setIcon(QtGui.QIcon('./icon/search.png'))
# self.q_chinh_vung_quan_sat.setIcon(QtGui.QIcon('./icon/draw.png'))
# self.q_chinh_vach_kiem_dem.setIcon(QtGui.QIcon('./icon/draw.png'))
# self.q_chinh_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
# self.q_chinh_chinh_sua_button.setIcon(QtGui.QIcon('./icon/edit.png'))
# self.q_chinh_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
# # bao cao va thong ke
# self.b_t1_plot_button.setIcon(QtGui.QIcon('./icon/plot.png'))
# self.b_t1_save_button.setIcon(QtGui.QIcon('./icon/save.png'))
# self.b_t1_export_button.setIcon(QtGui.QIcon('./icon/export_data.png'))
# self.b_t2_plot_button.setIcon(QtGui.QIcon('./icon/plot.png'))
# self.b_t2_save_button.setIcon(QtGui.QIcon('./icon/save.png'))
# self.b_t2_export_button.setIcon(QtGui.QIcon('./icon/export_data.png'))
# # thong tin va thiet dat
# self.t_server_sending_button.setIcon(QtGui.QIcon('./icon/sending.png'))
# self.t_server_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
# self.t_server_confirm_button.setIcon(QtGui.QIcon('./icon/update.png'))
# self.t_server_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
# self.t_pass_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
# self.t_pass_change_pass_button.setIcon(QtGui.QIcon('./icon/confirm.png'))
# self.t_pass_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
# # -----

# import sqlite3
# def chk_conn(conn):
#     try:
#         conn.cursor()
#         return True
#     except Exception as ex:
#         return False
# conn_display1 = sqlite3.connect('./database/Face_Mask_Recognition_DataBase1.db')
# print(chk_conn(conn_display1))
# import pandas as pd
# # fake_data = pd.read_csv('./data/fake_data.csv')
# # print(fake_data.type)
# import datetime
#
# object_id = "abcxyz"
# camera_name = "C"
# num_in = 10
# num_mask = 7
# num_no_mask = num_in-num_mask
# data = datetime.datetime.now()
# data_form = {"object_id": object_id,
#              "camera_name": camera_name,
#              "num_in": num_in,
#              "num_mask": num_mask,
#              "num_no_mask": num_no_mask,
#              "minute": data.minute,
#              "hour": data.hour,
#              "day": data.day,
#              "month": data.month,
#              "year": data.year}
#
# insert_data = []
# for i in range(10):
#     insert_data.append(data_form)
#
# data_form_add = pd.DataFrame.from_dict([insert_data])
# print(data_form_add)

# def create_default_counting_line(w_in, h_in, extra_pixels_in):
#     counting_line = [0 + extra_pixels_in, int(h_in / 2), w_in - extra_pixels_in, int(h_in / 2)]
#     direction_point = [int(w_in / 2), int(h_in / 2) + 50]
#     result = [
#         {
#             "id": "Counting-1",
#             "points": counting_line,
#             "direction_point": direction_point
#         }
#     ]
#     return result
#
# w = 1080
# h = 720
# extra_pixels = 3
#
# c = create_default_counting_line(w, h, extra_pixels)
# print(c)


# def test():
#     lst = [1,2,3,4,5,6,7,8,9,10,11,12]
#     result = []
#     j = 0
#     for i in range(0,len(lst),6):
#         j += 1
#         item = {
#             "id": f"Counting-{j}",
#             "points": [lst[i], lst[i+1], lst[i+2], lst[i+3]],
#             "direction_point": [lst[i+4], lst[i+5]]
#         }
#         print(item)
#         result.append(item)
#     return result
#
# z = test()
# print(z)

# lst = [1,2,3,4,5,6,7,8,9,10,11,12]
# print(len(lst)%6 == 0)

import yaml
import json

# data_item = {
#     "camera_name": None,
#     "person": 0,
#     "no_mask": 0,
#     "mask": 0,
#     "status": "stopped",
#     "setting_time": None
# }
#
# # load dat in config file
# config_file = "./configs/test_final.yml"
# yaml.warnings({'YAMLLoadWarning': False})
# with open(config_file, 'r') as fs:
#     config = yaml.load(fs)
# cam_config_first_time = config["input"]["cam_config"]
# with open(cam_config_first_time) as json_file:
#     json_data = json.load(json_file)
# json_file.close()
# data = json_data["data"]
#
# num_cam = 4
#
# list_data = [data_item.copy() for i in range(num_cam)]
#
# for cam_index in range(num_cam):
#     # print(cam_index)
#     list_data[cam_index]["camera_name"] = data[cam_index]["name"]
#     print(list_data[cam_index])
#
#
# print("list data: ", list_data)


# import cv2
# old_password = "dungpm@greenglobal.vn"
# # password_threading.password_by_threading()
# cap = cv2.VideoCapture(0)
# # ret, frame = cap.read()
# while True:
#     ret, frame = cap.read()
#     frame = cv2.resize(frame, (480, 360))
#     if ret:
#         cv2.imshow("show", frame)
#         key = cv2.waitKey(1)
#         if key == ord("q"):
#             break
# cap.release()
# cv2.destroyAllWindows()
#
# a = [
#     [[424, 90, 517, 201], [1292, 597, 1534, 918], [147, 207, 278, 364], [634, 22, 733, 148], [753, 302, 933, 520], [1691, 488, 1905, 718]],
#     [0.7914899, 0.7924527, 0.83863705, 0.8657681, 0.86999285, 0.88042307],
#     [[291, 92, 596, 346], [598, 14, 814, 491]],
#     [0.73263156, 0.8111926]
# ]


# from PyQt5.QtGui import QApplication, QMainWindow, QPushButton, \
#             QLabel, QVBoxLayout, QWidget
# from PyQt5.QtCore import pyqtSignal

# from PyQt5 import QtCore, QtGui, QtWidgets
# import threading
#
# hide_trigger = False
# w_width = 400
# w_height = 150
#
#
# class Ui_Password(object):
#     def setupUi(self, Password):
#
#         # self.input_pass = input_pass
#
#         Password.setObjectName("Password")
#         Password.resize(400, 139)
#         self.centralwidget = QtWidgets.QWidget(Password)
#         self.centralwidget.setObjectName("centralwidget")
#         self.label = QtWidgets.QLabel(self.centralwidget)
#         self.label.setGeometry(QtCore.QRect(0, 10, 391, 20))
#         self.label.setAlignment(QtCore.Qt.AlignCenter)
#         self.label.setObjectName("label")
#         self.pass_input = QtWidgets.QLineEdit(self.centralwidget)
#         self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
#         self.pass_input.setGeometry(QtCore.QRect(10, 40, 381, 25))
#         self.pass_input.setAlignment(QtCore.Qt.AlignCenter)
#         self.pass_input.setObjectName("pass_input")
#         self.ok_button = QtWidgets.QPushButton(self.centralwidget)
#         self.ok_button.setGeometry(QtCore.QRect(80, 80, 89, 31))
#         self.ok_button.setObjectName("ok_button")
#         self.cancel_button = QtWidgets.QPushButton(self.centralwidget)
#         self.cancel_button.setGeometry(QtCore.QRect(240, 80, 89, 31))
#         self.cancel_button.setObjectName("cancel_button")
#         self.hide_unhide_button = QtWidgets.QPushButton(self.centralwidget)
#         self.hide_unhide_button.setGeometry(QtCore.QRect(359, 40, 31, 25))
#         self.hide_unhide_button.setText("")
#         self.hide_unhide_button.setObjectName("hide_unhide_button")
#
#         # icon for button
#         self.ok_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
#         self.cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
#         self.hide_unhide_button.setIcon(QtGui.QIcon('./icon/unhide.png'))
#
#         # event button
#         self.hide_unhide_button.clicked.connect(self.hide_unhide_pass)
#         # apply button
#         self.ok_button.clicked.connect(self.newWindow)
#
#
#         Password.setCentralWidget(self.centralwidget)
#         self.statusbar = QtWidgets.QStatusBar(Password)
#         self.statusbar.setObjectName("statusbar")
#         Password.setStatusBar(self.statusbar)
#         self.retranslateUi(Password)
#         QtCore.QMetaObject.connectSlotsByName(Password)
#
#     def hide_unhide_pass(self):
#         global hide_trigger
#         hide_trigger = not hide_trigger
#         if hide_trigger:
#             self.pass_input.setEchoMode(QtWidgets.QLineEdit.Normal)
#         else:
#             self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
#
#     def newWindow(self):
#         self.mainwindow2 = MainWindow2()
#         # self.mainwindow2.closed.connect(self.show)
#         self.mainwindow2.show()
#         # self.hide()
#
#     def retranslateUi(self, Password):
#         _translate = QtCore.QCoreApplication.translate
#         Password.setWindowTitle(_translate("Password", "Password Window"))
#         self.label.setText(_translate("Password", "Vui lòng nhập Password !"))
#
#
# class MainWindow(QtWidgets.QMainWindow, Ui_Password):
#     def __init__(self):
#         global w_height, w_width
#         super().__init__()
#         self.setupUi(self)
#         self.setFixedSize(w_width, w_height)
#
#     def closeEvent(self, event):
#         super().closeEvent(event)
#
#
# class Ui_Password2(object):
#     def setupUi(self, Password2):
#
#         # self.input_pass = input_pass
#
#         Password2.setObjectName("Password")
#         Password2.resize(400, 139)
#         self.centralwidget = QtWidgets.QWidget(Password2)
#         self.centralwidget.setObjectName("centralwidget")
#         self.label = QtWidgets.QLabel(self.centralwidget)
#         self.label.setGeometry(QtCore.QRect(0, 10, 391, 20))
#         self.label.setAlignment(QtCore.Qt.AlignCenter)
#         self.label.setObjectName("label")
#         self.pass_input = QtWidgets.QLineEdit(self.centralwidget)
#         self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
#         self.pass_input.setGeometry(QtCore.QRect(10, 40, 381, 25))
#         self.pass_input.setAlignment(QtCore.Qt.AlignCenter)
#         self.pass_input.setObjectName("pass_input")
#         self.ok_button = QtWidgets.QPushButton(self.centralwidget)
#         self.ok_button.setGeometry(QtCore.QRect(80, 80, 89, 31))
#         self.ok_button.setObjectName("ok_button")
#         self.cancel_button = QtWidgets.QPushButton(self.centralwidget)
#         self.cancel_button.setGeometry(QtCore.QRect(240, 80, 89, 31))
#         self.cancel_button.setObjectName("cancel_button")
#         self.hide_unhide_button = QtWidgets.QPushButton(self.centralwidget)
#         self.hide_unhide_button.setGeometry(QtCore.QRect(359, 40, 31, 25))
#         self.hide_unhide_button.setText("")
#         self.hide_unhide_button.setObjectName("hide_unhide_button")
#
#         # icon for button
#         self.ok_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
#         self.cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
#         self.hide_unhide_button.setIcon(QtGui.QIcon('./icon/unhide.png'))
#
#         # event button
#         self.hide_unhide_button.clicked.connect(self.hide_unhide_pass)
#
#
#         Password2.setCentralWidget(self.centralwidget)
#         self.statusbar = QtWidgets.QStatusBar(Password2)
#         self.statusbar.setObjectName("statusbar")
#         Password2.setStatusBar(self.statusbar)
#         self.retranslateUi(Password2)
#         QtCore.QMetaObject.connectSlotsByName(Password2)
#
#     def hide_unhide_pass(self):
#         global hide_trigger
#         hide_trigger = not hide_trigger
#         if hide_trigger:
#             self.pass_input.setEchoMode(QtWidgets.QLineEdit.Normal)
#         else:
#             self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
#
#     def retranslateUi(self, Password):
#         _translate = QtCore.QCoreApplication.translate
#         Password.setWindowTitle(_translate("Password", "Password Window"))
#         self.label.setText(_translate("Password", "Vui lòng nhập Password lần 2 !"))
#
#
# class MainWindow2(QtWidgets.QMainWindow, Ui_Password2):
#
#     # QMainWindow doesn't have a closed signal, so we'll make one.
#     closed = QtCore.pyqtSignal()
#
#     def __init__(self):
#         global w_height, w_width
#         super().__init__()
#         self.setupUi(self)
#         self.setFixedSize(w_width, w_height)
#
#     def closeEvent(self, event):
#         super().closeEvent(event)
#
#
# if __name__ == '__main__':
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     QtCore.QCoreApplication.setOrganizationName("Eyllanesc")
#     QtCore.QCoreApplication.setOrganizationDomain("eyllanesc.com")
#     QtCore.QCoreApplication.setApplicationName("MyApp")
#     w = MainWindow()
#     w.show()
#     app.exec_()


# # send request to Re-ID API to get body vectors
# api_path = f"http://{os.getenv('MODEL_REID_HOST')}:{os.getenv('MODEL_REID_PORT')}/v2/predict/person_embedding_batch"
# if len(files) > 0:
#     response = requests.request("POST", api_path, files=files)
#     data = response.json()["data"]

import requests
# import json
# import yaml
# import face_mask_threading
# config_file = "./configs/cameras_config.yml"
# def read_config_file():
#     global config_file
#     # load dat in config file
#     yaml.warnings({'YAMLLoadWarning': False})
#     with open(config_file, 'r') as fs:
#         config = yaml.load(fs)
#     cam_config_first_time = config["input"]["cam_config"]
#     with open(cam_config_first_time) as json_file:
#         json_data = json.load(json_file)
#     json_file.close()
#     # data = json_data["data"]
#     return json_data
#
# json_data = read_config_file()
# cam_infor_list = json_data["data"]
#
# # print("cam_infor_list", cam_infor_list)
#
# # parse all information of each camera
# input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list, \
# tracking_regions_list = face_mask_threading.parser_cam_infor(cam_infor_list)
#
# num_cam = len(input_video_list)
# # print("num_cam: ", num_cam)
#
# # prepare data for updating information on main view and alarm
# view_item = {
#     "camera_name": None,
#     "camera_id": None,
#     "person": 0,
#     "no_mask": 0,
#     "mask": 0,
#     "status": "stopped",
#     "setting_time": [],
#     "alarm_option": "",
#     "sound": "",
#     "light": "",
# }
#
# # create view_data with the same length as num_cam
# view_data = [view_item.copy() for i in range(len(cam_infor_list))]
#
# # prepare data to insert into data
# database_item = {
#     "object_id": "",
#     "camera_name": "",
#     "camera_id": None,
#     "num_in": 0,
#     "num_mask": 0,
#     "num_no_mask": 0,
#     "minute": None,
#     "hour": None,
#     "day": None,
#     "month": None,
#     "year": None
# }
#
# # create database_data with the same lenght as num_cam
# database_data = [database_item.copy() for i in range(num_cam)]
#
# enable_data = []
# for cam_index in range(len(cam_infor_list)):
#     # for view_data
#     view_data[cam_index]["camera_name"] = cam_infor_list[cam_index]["name"]
#     view_data[cam_index]["setting_time"] = cam_infor_list[cam_index]["setting_time"]
#     view_data[cam_index]["alarm_option"] = cam_infor_list[cam_index]["alarm_option"]
#     view_data[cam_index]["light"] = cam_infor_list[cam_index]["light"]
#     view_data[cam_index]["sound"] = cam_infor_list[cam_index]["sound"]
#
#     if cam_infor_list[cam_index]["enable"] == "yes":
#         enable_data.append(cam_infor_list[cam_index])
#
# # for database_data
# for cam_index_enable in range(len(enable_data)):
#     database_data[cam_index_enable]["object_id"] = json_data["object_id"]
#     database_data[cam_index_enable]["camera_name"] = enable_data[cam_index_enable]["name"]
#     database_data[cam_index_enable]["camera_id"] = enable_data[cam_index_enable]["id"]
#
# print("len database_data: ", database_data)
# print("---"*20)
# print("len view_data: ", len(view_data))

#
# setting_time = ["00:00", "12:20"]
# print(int(setting_time[0][0:2]))
# print(int(setting_time[0][3:5]))

# # insert data into database when detect new no-face-mask person
# # AND also check check setting time status
# if set_working_time_flag and from_time_hour is not None and from_time_minute is not None:
#     # check setting time (FROM)
#     information1_time = datetime.datetime.now()
#     print("Time1:", information1_time)
#     if (int(information1_time.hour) >= int(from_time_hour)) \
#             and (int(information1_time.minute) >= int(from_time_minute)):
#         data = datetime.datetime.now()
#         data_form = {"Camera_name": insert_name,
#                      "Minute": data.minute,
#                      "Hour": data.hour,
#                      "Day": data.day,
#                      "Month": data.month,
#                      "Year": data.year}
#         data_form_add = pd.DataFrame.from_dict([data_form])
#         data_form_add.to_sql('DATA', conn_display, if_exists='append', index=False)
#         print("[INFO]-- Inserted data into Database")
#         conn_display.commit()
# else:
#     data = datetime.datetime.now()
#     data_form = {"Camera_name": insert_name,
#                  "Minute": data.minute,
#                  "Hour": data.hour,
#                  "Day": data.day,
#                  "Month": data.month,
#                  "Year": data.year}
#     data_form_add = pd.DataFrame.from_dict([data_form])
#     data_form_add.to_sql('DATA', conn_display, if_exists='append', index=False)
#     print("[INFO]-- Inserted data into Database")
#     conn_display.commit()


import requests


# import sqlite3
# from mask_utils import app_warning_function
#
# # connect to sql database
# conn = sqlite3.connect('./database/final_data_base.db')
# c = conn.cursor()
# return_data = []
# camera_name_input = "A"
# from_month = 5
# to_month = 5
#
# from_day = 1
# to_day = 5
#
# # get camera_id of camera_name_input
# query_id = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
#            f"day BETWEEN {from_day} AND {to_day} AND " \
#            f"month BETWEEN {from_month} AND {to_month}"
# c.execute(query_id)
# # id_data = c.fetchall()
# # if len(c.fetchall()) > 0:
# #     print(c.fetchall())
# id_data = c.fetchall()
#
# if len(id_data) == 0:
#     app_warning_function.query_camera_id_warning()
# else:
#
#     # camera_id = id_data[0][0]
#     camera_id = id_data
#
# data = []
# # print(len(camera_id))
# # print(camera_id)
#
# for i in range(len(camera_id)):
#     item = str(camera_id[i])
#     item = item.replace("(", "")
#     item = item.replace(")", "")
#     data.append(item)

# print("final data: ", data)



import datetime
import sqlite3


# # call latest time
# token = "d41d8cd98f00b204e9800998ecf8427e"
# setting_server_url = "192.168.111.182:9000/api/objects/get_latest_result_sync"
# check_latest_time_form = {
#     "object_id": 4,
# }
# # send request to API
# api_path = f"http://{setting_server_url}"
# headers = {"token": token}
# response = requests.request("POST", api_path, json=check_latest_time_form, headers=headers)
# check_latest_time_data = response.json()
# print(check_latest_time_data)
#
# # connect to sql database
# conn = sqlite3.connect('./database/final_data_base.db')
# c = conn.cursor()
#
# time_query_minute = 5
# time_query_hour = 5
# time_query_day = 3
# time_query_month = 2
# time_query_year = 2020
#
#
# for item in check_latest_time_data["data"]:
#
#     camera_id = item["camera_id"]
#
#     query_minute = item["minutes"]
#     query_hour = item["hours"]
#     query_day = item["date"]
#     query_month = item["month"]
#     query_year = item["year"]
#
#     # print(query_minute,query_hour,query_day,query_month,query_year)
#     # print(time_query.minute,time_query.hour,time_query.day,time_query.month,time_query.year)
#
#     # query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
#     #              f"camera_id = '{camera_id}' AND " \
#     #              f"minute BETWEEN {query_minute} AND {time_query.minute} OR " \
#     #              f"hour BETWEEN {query_hour} AND {time_query.hour} OR " \
#     #              f"day BETWEEN {query_day} AND {time_query.day} OR " \
#     #              f"month BETWEEN {query_month} AND {time_query.month} OR " \
#     #              f"year BETWEEN {query_year} AND {time_query.year}"
#
#     query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
#                  f"camera_id = '{camera_id}' AND " \
#                  f"hour BETWEEN {query_hour} AND {time_query_hour} AND " \
#                  f"day BETWEEN {query_day} AND {time_query_day} AND " \
#                  f"month BETWEEN {query_month} AND {time_query_month} AND " \
#                  f"year BETWEEN {query_year} AND {time_query_year}"
#
#     # camera_name_input = 'tang1'
#     # query = f"SELECT * FROM DATA WHERE camera_name = '{camera_name_input}'"
#
#     c.execute(query_test)
#     sending_data = []
#
#     updated_data = c.fetchall()
#     if len(updated_data) > 0:
#         print("query_data: ", updated_data)
#         for i in range(len(updated_data)):
#             item = str(updated_data[i])
#             item = item.replace("(", "")
#             item = item.replace(")", "")
#             sending_data.append(item)
#
#         print("sending data: ", len(sending_data))
#
#         if len(sending_data) > 0:
#
#             insert_data = {
#                 "camera_id": camera_id,
#                 "data": sending_data
#             }
#
#             data_form = {
#                 "object_id": 4,
#                 "data": [insert_data]
#             }
#
#             token = "d41d8cd98f00b204e9800998ecf8427e"
#             setting_server_url = "192.168.111.182:9000/api/objects/sync"
#             api_path = f"http://{setting_server_url}"
#             headers = {"token": token}
#             response = requests.request("POST", api_path, json=data_form, headers=headers)
#             insert_data = response.json()
#             print(insert_data)

import sqlite3
# connect to sql database
conn = sqlite3.connect('./database/final_data_base.db')
c = conn.cursor()

camera_id = 4
year_input = 2020

# query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
#              f"camera_id = '{camera_id}' AND " \
#              f"(substr(year,1,4)||substr(substr('00'||month,-2),1,2)||substr(substr('00'||day,-2),1,2)||" \
#              f"substr(substr('00'||hour,-2),1,2)||substr(substr('00'||minute,-2),1,2)) " \
#              f"BETWEEN '202001010502' AND '202103160835'"

query_test = f"SELECT camera_name,num_in,num_mask,num_no_mask,minute,hour,day,month,year " \
        f"FROM DATA WHERE camera_id = '{camera_id}' and year = {year_input}"

c.execute(query_test)
updated_data = c.fetchall()
print(len(updated_data))
print(updated_data)

print("test:", updated_data[0][0])

y_in = [0 for i in range(1, 13, 1)]
print(y_in)


# import datetime
# now = datetime.datetime.now()
# to_time = now.strftime("%Y%m%d%H%M")
# print("to_time: ", to_time)
#
# data = {'minutes': 5, 'hours': 5, 'date': 2, 'month': 1, 'year': 2020}
# data_lst = (str(data["year"]), str(data["month"]).zfill(2), str(data["date"]).zfill(2), str(data["hours"]).zfill(2), str(data["minutes"]).zfill(2))
# from_time = "".join(data_lst)
# print("from_time: ", from_time)





# update data
# tang1 - 4
# insert_data = {
#     "camera_id": 4,
#     "data": [
#         "5, 3, 2, 1, 4, 1, 1, 2020",
#         "6, 3, 3, 2, 4, 1, 1, 2020",
#         "2, 1, 1, 3, 4, 1, 1, 2020"
#     ]
# }
# data_form = {
#     "object_id": 2,
#     "data": [insert_data]
# }

# # tang2 - 5
# insert_data = {
#     "camera_id": 5,
#     "data": [
#         "5, 3, 2, 1, 3, 1, 1, 2020",
#         "6, 3, 3, 2, 3, 1, 1, 2020",
#         "2, 1, 1, 3, 3, 1, 1, 2020"
#     ]
# }
# data_form = {
#     "object_id": 2,
#     "data": [insert_data]
# }

# # # tang3 - 5
# insert_data = {
#     "camera_id": 6,
#     "data": [
#         "5, 3, 2, 1, 2, 1, 1, 2020",
#         "6, 3, 3, 2, 2, 1, 1, 2020",
#         "2, 1, 1, 3, 2, 1, 1, 2020"
#     ]
# }
# data_form = {
#     "object_id": 2,
#     "data": [insert_data]
# }
# # #
# token = "9de8ee9598522adacfd704a2f2f44b62"
# setting_server_url = "192.168.111.133:9050/api/objects/sync"
# api_path = f"http://{setting_server_url}"
# headers = {"token": token}
# response = requests.request("POST", api_path, json=data_form, headers=headers)
# insert_data = response.json()
# print(insert_data)

# lst = [i for i in range(1, 2039, 1)]
# print(lst)
# num = 500
#
# div_lay_du = len(lst) % num
# div_lay_nguyen = len(lst) // num
# print(div_lay_nguyen)
# print(div_lay_du)
#
# data_test = []
# for i in range(div_lay_nguyen+1):
#     if i == 0:
#         item_data = lst[0:num]
#     elif 0 < i < div_lay_nguyen+1:
#         item_data = lst[num*i:num*i+num]
#     elif i == div_lay_nguyen+1:
#         item_data = lst[num*i:num*i+div_lay_du]
#     print("item_data: ", item_data)
#     print("-"*100)
#     data_test.append(item_data)
#
# print("final data: ",data_test)
import time
# import datetime
#
# num = 5
# check_time_1 = 0
#
# while True:
#     check_time_2 = datetime.datetime.now()
#     if check_time_1 == 0:
#         check_time_1 = check_time_2
#
#     time_delta = (check_time_2 - check_time_1)
#     total_seconds = time_delta.total_seconds()
#
#     if total_seconds >= num:
#         check_time_1 = check_time_2
#         print(total_seconds)
#         print("update data")

# import json
#
# configuration_file = "./configs/configuration.json"
# with open(configuration_file) as json_file:
#     json_data = json.load(json_file)
# json_file.close()
#
# host = json_data["host"]
# port = json_data["port"]
# token = json_data["token"]
