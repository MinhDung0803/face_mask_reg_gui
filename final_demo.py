from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import time
import os
import cv2
import pandas as pd
import threading
import queue
import json
import yaml
import datetime

import face_mask_threading
from mask_utils import global_variable_define as gd
import play_alarm_audio_threading
from mask_utils import app_warning_function
import report_statistics_tab

import warnings

warnings.filterwarnings("ignore")

# variables
name = None
camera_name_input_1 = ""
camera_name_input_2 = ""
count = 0
height = 421
width = 771
w_width = 1080
w_height = 740
light_alarm = 0
sound_alarm = 0
both_alarm = 1
trigger_stop = 0

draw_region_points = []
draw_counting_points = []

draw_region_points_no_scale = []
draw_counting_no_scale = []

draw_region_flag_new = False
draw_count_flag_new = False

draw_region_flag_old = False
draw_count_flag_old = False

set_working_time_flag = False

extra_pixels = 10  # for default points
scale = 3  # for drawing, display drawing and for tracking

# from
from_time_hour = None
from_time_minute = None

# to
to_time_hour = None
to_time_minute = None
new_camera_id = ""
new_camera_path = ""

# config_file
# ----- KEY
config_file = "./configs/test_final.yml"
# ----- KEY

# load dat in config file for the first time when APP is opened
yaml.warnings({'YAMLLoadWarning': False})
with open(config_file, 'r') as fs:
    config = yaml.load(fs)
cam_config_first_time = config["input"]["cam_config"]
with open(cam_config_first_time) as json_file:
    json_data = json.load(json_file)
json_file.close()
data_first_time = json_data["data"]


def create_default_region(w_in, h_in, extra_pixels_in):
    result = [0 + extra_pixels_in, 0 + extra_pixels_in, w_in - extra_pixels_in, 0 + extra_pixels_in,
              w_in - extra_pixels_in,
              h_in - extra_pixels_in, 0 + extra_pixels_in, h_in - extra_pixels_in]
    return result


def create_default_counting_line(w_in, h_in, extra_pixels_in):
    counting_line = [0 + extra_pixels_in, int(h_in / 2), w_in - extra_pixels_in, int(h_in / 2)]
    direction_point = [int(w_in / 2), int(h_in / 2) + 50]
    result = [
        {
            "id": "Counting-1",
            "points": counting_line,
            "direction_point": direction_point
        }
    ]
    return result


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent, g_tong_khong_kt):
        QtCore.QThread.__init__(self, parent)
        self._go = None
        self.g_tong_khong_kt = g_tong_khong_kt
        # self.radioButton_light_option = radioButton_light_option

    def run(self):
        global count, height, width, config_file, trigger_stop, count, light_alarm, sound_alarm, both_alarm, name, \
            set_working_time_flag, from_time_hour, from_time_minute, to_time_hour, to_time_minute

        # # connect to sql database
        conn_display = sqlite3.connect('./database/final_data_base.db')
        c_display = conn_display.cursor()

        # run mode variable
        self._go = True

        # get information from config_file
        yaml.warnings({'YAMLLoadWarning': False})
        with open(config_file, 'r') as fs:
            config = yaml.load(fs)
            # config = yaml.load(fs, Loader=yaml.FullLoader)

        cam_config = config["input"]["cam_config"]

        with open(cam_config) as json_file:
            json_data = json.load(json_file)
        json_file.close()

        cam_infor_list = json_data["data"]
        insert_name = json_data["data"][0]["name"]

        input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list, \
        tracking_regions_list = face_mask_threading.parser_cam_infor(cam_infor_list)

        num_cam = len(input_video_list)
        video_infor_list = []
        max_fps = 0
        for cam_index in range(num_cam):
            width1, height1, fps_video1 = face_mask_threading.get_info_video(input_video_list[cam_index])
            video_infor_list.append([width1, height1, fps_video1])
            if max_fps < fps_video1:
                max_fps = fps_video1

        no_job_sleep_time = (1 / max_fps) / 10

        # create face_mask buffer, forward_message and backward_message
        face_mask_buffer = [queue.Queue(100) for i in range(num_cam)]

        forward_message = queue.Queue()
        backward_message = queue.Queue()

        gd.set_backward_message(backward_message)

        wait_stop = threading.Barrier(5)

        # call face mask threading
        face_mask_threading.face_mask_by_threading(config_file, face_mask_buffer, forward_message, backward_message,
                                                   wait_stop, no_job_sleep_time)

        # event count to update no face mask person and active alarm mode
        event_count = 0

        while self._go:
            if os.path.exists(config_file):
                if trigger_stop == 1:
                    forward_message.put("stop")
                    trigger_stop = 0
                    time.sleep(1)
                    self.stop_thread()

                # self.radioButton_light_option.setChecked(True)

                # get information form the queue
                for cam_index in range(num_cam):
                    face_mask_output_data = face_mask_buffer[cam_index]
                    if not face_mask_output_data.empty():
                        data = face_mask_output_data.get()

                        ind = data[0]
                        frame_ori = data[1]
                        list_count = data[2]

                        if ind != -1:
                            # get number of no face mask person
                            event_count = list_count[0]["Person"]

                            # event
                            if count < event_count:
                                count = event_count

                                # update display_no_face_mask_counting
                                self.g_tong_khong_kt.display(count)

                                # insert data into database when detect new no-face-mask person
                                # AND also check check setting time status
                                if set_working_time_flag and from_time_hour is not None and from_time_minute is not None:
                                    # check setting time (FROM)
                                    information1_time = datetime.datetime.now()
                                    print("Time1:", information1_time)
                                    if (int(information1_time.hour) >= int(from_time_hour)) \
                                            and (int(information1_time.minute) >= int(from_time_minute)):
                                        data = datetime.datetime.now()
                                        data_form = {"Camera_name": insert_name,
                                                     "Minute": data.minute,
                                                     "Hour": data.hour,
                                                     "Day": data.day,
                                                     "Month": data.month,
                                                     "Year": data.year}
                                        data_form_add = pd.DataFrame.from_dict([data_form])
                                        data_form_add.to_sql('DATA', conn_display, if_exists='append', index=False)
                                        print("[INFO]-- Inserted data into Database")
                                        conn_display.commit()
                                else:
                                    data = datetime.datetime.now()
                                    data_form = {"Camera_name": insert_name,
                                                 "Minute": data.minute,
                                                 "Hour": data.hour,
                                                 "Day": data.day,
                                                 "Month": data.month,
                                                 "Year": data.year}
                                    data_form_add = pd.DataFrame.from_dict([data_form])
                                    data_form_add.to_sql('DATA', conn_display, if_exists='append', index=False)
                                    print("[INFO]-- Inserted data into Database")
                                    conn_display.commit()

                                # active alarm
                                if sound_alarm == 1:
                                    print("[INFO]-- Sound")
                                    sound_file = "./sound_alarm/police.mp3"
                                    play_alarm_audio_threading.play_audio_by_threading(sound_file)
                                elif light_alarm == 1:
                                    print("[INFO]-- Light")
                                else:
                                    print("[INFO]-- Sound and light")
                                    sound_file = "./sound_alarm/police.mp3"
                                    play_alarm_audio_threading.play_audio_by_threading(sound_file)

                            # display on APP
                            result_frame = cv2.resize(frame_ori, (width, height))
                            rgbImage = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
                            h_result_frame, w_result_frame, ch = rgbImage.shape
                            bytesPerLine = ch * w_result_frame
                            convertToQtFormat = QtGui.QImage(rgbImage.data, w_result_frame, h_result_frame,
                                                             bytesPerLine, QtGui.QImage.Format_RGB888)
                            p = convertToQtFormat.scaled(width, height, QtCore.Qt.KeepAspectRatio)
                            self.changePixmap.emit(p)

                    else:
                        time.sleep(no_job_sleep_time)

                # check setting time (TO) for STOP
                information2_time = datetime.datetime.now()
                # print("Time2:", information2_time)
                if set_working_time_flag and to_time_hour is not None and to_time_minute is not None:
                    if (int(information2_time.hour) >= int(to_time_hour)) \
                            and (int(information2_time.minute) >= int(to_time_minute)):
                        print("[INFO] All threads are stopped because of out of time (Setting time)")
                        forward_message.put("stop")
                        trigger_stop = 0
                        time.sleep(1)
                        self.stop_thread()

            else:
                app_warning_function.check_config_file()
                time.sleep(0.5)

    def stop_thread(self):
        global draw_region_flag, \
            draw_count_flag, \
            draw_counting_points, \
            draw_region_points, \
            draw_counting_no_scale, \
            draw_region_points_no_scale, \
            set_working_time_flag, \
            from_time_hour, \
            from_time_minute, \
            to_time_hour, \
            to_time_minute

        self._go = False
        draw_region_flag = False
        draw_count_flag = False
        draw_counting_points = []
        draw_region_points = []
        draw_region_points_no_scale = []
        draw_counting_no_scale = []
        set_working_time_flag = True
        from_time_hour = None
        from_time_minute = None
        to_time_hour = None
        to_time_minute = None


def close_window():
    global trigger_stop
    trigger_stop = 1


def shape_selection_for_region(event, x, y, flags, param):
    global draw_region_points, scale, draw_region_points_no_scale, image_region
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = (x, y)
        # with scale
        draw_region_points.append(x * scale)
        draw_region_points.append(y * scale)
        # with no scale
        draw_region_points_no_scale.append(x)
        draw_region_points_no_scale.append(y)
        cv2.circle(image_region, (ref_point[0], ref_point[1]), 4, (0, 0, 255), -2)
        cv2.imshow("Draw Tracking Region", image_region)


def shape_selection_for_counting(event, x, y, flags, param):
    global draw_counting_points, scale, image_counting
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point_c = (x, y)
        # with scale
        draw_counting_points.append(x * scale)
        draw_counting_points.append(y * scale)
        # without scale (for drawing)
        draw_counting_no_scale.append(x)
        draw_counting_no_scale.append(y)
        cv2.circle(image_counting, (ref_point_c[0], ref_point_c[1]), 4, (0, 255, 0), -2)
        for i in range(0, len(draw_region_points_no_scale), 2):
            if i + 3 > len(draw_region_points_no_scale):
                cv2.line(image_region, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                         (draw_region_points_no_scale[0], draw_region_points_no_scale[1]), (0, 255, 255), 1)
            else:
                cv2.line(image_region, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                         (draw_region_points_no_scale[i + 2], draw_region_points_no_scale[i + 3]), (0, 255, 255), 1)
        cv2.imshow("Draw Counting Region", image_counting)


def draw_region(path):
    global width, height, draw_region_points, scale, draw_region_points_no_scale, image_region
    # read and write original image
    cap = cv2.VideoCapture(path)
    # get width, height of camera
    w = int(cap.get(3))
    h = int(cap.get(4))
    ret, frame = cap.read()
    frame = cv2.resize(frame, (int(w / scale), int(h / scale)))
    if ret:
        if os.path.exists("./draw/original_image.jpg"):
            os.remove("./draw/original_image.jpg")
        cv2.imwrite("./draw/original_image.jpg", frame)
        # draw on original image and write when done
        image_region = cv2.imread("./draw/original_image.jpg")
        # clone = image.copy()
        cv2.namedWindow("Draw Tracking Region")
        cv2.setMouseCallback("Draw Tracking Region", shape_selection_for_region)
        while True:
            cv2.imshow("Draw Tracking Region", image_region)
            for i in range(0, len(draw_region_points_no_scale), 2):
                if i + 3 > len(draw_region_points_no_scale):
                    cv2.line(image_region, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                             (draw_region_points_no_scale[0], draw_region_points_no_scale[1]), (0, 255, 255), 1)
                else:
                    cv2.line(image_region, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                             (draw_region_points_no_scale[i + 2], draw_region_points_no_scale[i + 3]), (0, 255, 255), 1)
            key = cv2.waitKey(1)
            if key == 32:
                # image = clone.copy()
                draw_region_points = []
            elif key == 13:
                break

    if os.path.exists('./draw/draw_region_image.jpg'):
        os.remove('./draw/draw_region_image.jpg')
    cv2.imwrite('./draw/draw_region_image.jpg', image_region)
    cap.release()
    cv2.destroyAllWindows()


def draw_counting():
    global width, height, draw_counting_points, image_counting
    image_counting = cv2.imread("./draw/draw_region_image.jpg")
    cv2.namedWindow("Draw Counting Region")
    cv2.setMouseCallback("Draw Counting Region", shape_selection_for_counting)
    while True:
        cv2.imshow("Draw Counting Region", image_counting)
        key = cv2.waitKey(1)
        if key == 32:
            draw_counting_points = []
        elif key == 13:
            break
    for i in range(0, len(draw_counting_no_scale), 2):
        if i + 3 > len(draw_counting_no_scale):
            cv2.line(image_counting, (draw_counting_no_scale[i], draw_counting_no_scale[i + 1]),
                     (draw_counting_no_scale[0], draw_counting_no_scale[1]), (0, 255, 0), 1)
        else:
            cv2.line(image_counting, (draw_counting_no_scale[i], draw_counting_no_scale[i + 1]),
                     (draw_counting_no_scale[i + 2], draw_counting_no_scale[i + 3]), (0, 255, 0), 1)
    if os.path.exists('./draw/draw_counting_image.jpg'):
        os.remove('./draw/draw_counting_image.jpg')
    cv2.imwrite('./draw/draw_counting_image.jpg', image_counting)
    cv2.destroyAllWindows()


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
        MainWindow.resize(1080, 740)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.report_tab = QtWidgets.QTabWidget(self.centralwidget)
        self.report_tab.setGeometry(QtCore.QRect(0, 0, 1071, 691))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        self.report_tab.setFont(font)
        self.report_tab.setObjectName("report_tab")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3.setGeometry(QtCore.QRect(0, 0, 521, 661))
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_110 = QtWidgets.QLabel(self.groupBox_3)
        self.label_110.setGeometry(QtCore.QRect(10, 280, 81, 17))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_110.setFont(font)
        self.label_110.setObjectName("label_110")
        self.label_80 = QtWidgets.QLabel(self.groupBox_3)
        self.label_80.setGeometry(QtCore.QRect(10, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_80.setFont(font)
        self.label_80.setObjectName("label_80")
        self.label_111 = QtWidgets.QLabel(self.groupBox_3)
        self.label_111.setGeometry(QtCore.QRect(120, 40, 351, 16))
        self.label_111.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_111.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_111.setObjectName("label_111")
        self.label_115 = QtWidgets.QLabel(self.groupBox_3)
        self.label_115.setGeometry(QtCore.QRect(10, 120, 61, 17))
        self.label_115.setText("")
        self.label_115.setObjectName("label_115")
        self.label_119 = QtWidgets.QLabel(self.groupBox_3)
        self.label_119.setGeometry(QtCore.QRect(10, 320, 71, 17))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_119.setFont(font)
        self.label_119.setObjectName("label_119")
        self.label_89 = QtWidgets.QLabel(self.groupBox_3)
        self.label_89.setGeometry(QtCore.QRect(10, 80, 121, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_89.setFont(font)
        self.label_89.setObjectName("label_89")
        self.label_117 = QtWidgets.QLabel(self.groupBox_3)
        self.label_117.setGeometry(QtCore.QRect(140, 80, 271, 16))
        self.label_117.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_117.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_117.setObjectName("label_117")
        self.label_90 = QtWidgets.QLabel(self.groupBox_3)
        self.label_90.setGeometry(QtCore.QRect(10, 120, 61, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_90.setFont(font)
        self.label_90.setObjectName("label_90")
        self.label_118 = QtWidgets.QLabel(self.groupBox_3)
        self.label_118.setGeometry(QtCore.QRect(80, 120, 401, 16))
        self.label_118.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_118.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_118.setObjectName("label_118")
        self.label_91 = QtWidgets.QLabel(self.groupBox_3)
        self.label_91.setGeometry(QtCore.QRect(10, 160, 61, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_91.setFont(font)
        self.label_91.setObjectName("label_91")
        self.label_121 = QtWidgets.QLabel(self.groupBox_3)
        self.label_121.setGeometry(QtCore.QRect(80, 160, 401, 16))
        self.label_121.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_121.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_121.setObjectName("label_121")
        self.label_122 = QtWidgets.QLabel(self.groupBox_3)
        self.label_122.setGeometry(QtCore.QRect(100, 200, 271, 16))
        self.label_122.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_122.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_122.setObjectName("label_122")
        self.label_92 = QtWidgets.QLabel(self.groupBox_3)
        self.label_92.setGeometry(QtCore.QRect(10, 200, 81, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_92.setFont(font)
        self.label_92.setObjectName("label_92")
        self.label_93 = QtWidgets.QLabel(self.groupBox_3)
        self.label_93.setGeometry(QtCore.QRect(10, 240, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_93.setFont(font)
        self.label_93.setObjectName("label_93")
        self.label_123 = QtWidgets.QLabel(self.groupBox_3)
        self.label_123.setGeometry(QtCore.QRect(70, 240, 271, 16))
        self.label_123.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_123.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_123.setObjectName("label_123")
        self.t_tt_phien_ban = QtWidgets.QLabel(self.groupBox_3)
        self.t_tt_phien_ban.setGeometry(QtCore.QRect(100, 280, 271, 16))
        self.t_tt_phien_ban.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.t_tt_phien_ban.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.t_tt_phien_ban.setObjectName("t_tt_phien_ban")
        self.t_tt_cap_phep = QtWidgets.QLabel(self.groupBox_3)
        self.t_tt_cap_phep.setGeometry(QtCore.QRect(100, 320, 401, 16))
        self.t_tt_cap_phep.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.t_tt_cap_phep.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.t_tt_cap_phep.setObjectName("t_tt_cap_phep")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab_2)
        self.tabWidget_2.setGeometry(QtCore.QRect(520, 0, 551, 671))
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.t_server_apply_button = QtWidgets.QPushButton(self.tab_7)
        self.t_server_apply_button.setGeometry(QtCore.QRect(230, 190, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_server_apply_button.setFont(font)
        self.t_server_apply_button.setText("")
        self.t_server_apply_button.setObjectName("t_server_apply_button")
        self.t_server_cap_phep = QtWidgets.QLineEdit(self.tab_7)
        self.t_server_cap_phep.setGeometry(QtCore.QRect(170, 50, 371, 21))
        self.t_server_cap_phep.setText("")
        self.t_server_cap_phep.setObjectName("t_server_cap_phep")
        self.label_84 = QtWidgets.QLabel(self.tab_7)
        self.label_84.setGeometry(QtCore.QRect(10, 50, 71, 17))
        self.label_84.setObjectName("label_84")
        self.t_server_cancel_button = QtWidgets.QPushButton(self.tab_7)
        self.t_server_cancel_button.setGeometry(QtCore.QRect(390, 190, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_server_cancel_button.setFont(font)
        self.t_server_cancel_button.setText("")
        self.t_server_cancel_button.setObjectName("t_server_cancel_button")
        self.label_85 = QtWidgets.QLabel(self.tab_7)
        self.label_85.setGeometry(QtCore.QRect(10, 10, 121, 17))
        self.label_85.setObjectName("label_85")
        self.label_116 = QtWidgets.QLabel(self.tab_7)
        self.label_116.setGeometry(QtCore.QRect(10, 90, 151, 17))
        self.label_116.setObjectName("label_116")
        self.t_server_server_dong_bo = QtWidgets.QLineEdit(self.tab_7)
        self.t_server_server_dong_bo.setGeometry(QtCore.QRect(170, 90, 371, 21))
        self.t_server_server_dong_bo.setObjectName("t_server_server_dong_bo")
        self.t_server_ten_thiet_bi = QtWidgets.QLineEdit(self.tab_7)
        self.t_server_ten_thiet_bi.setGeometry(QtCore.QRect(170, 10, 371, 21))
        self.t_server_ten_thiet_bi.setObjectName("t_server_ten_thiet_bi")
        self.t_server_sending_button = QtWidgets.QPushButton(self.tab_7)
        self.t_server_sending_button.setGeometry(QtCore.QRect(150, 190, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_server_sending_button.setFont(font)
        self.t_server_sending_button.setText("")
        self.t_server_sending_button.setObjectName("t_server_sending_button")
        self.label_120 = QtWidgets.QLabel(self.tab_7)
        self.label_120.setGeometry(QtCore.QRect(10, 130, 151, 17))
        self.label_120.setObjectName("label_120")
        self.t_server_confirm_button = QtWidgets.QPushButton(self.tab_7)
        self.t_server_confirm_button.setGeometry(QtCore.QRect(310, 190, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_server_confirm_button.setFont(font)
        self.t_server_confirm_button.setText("")
        self.t_server_confirm_button.setObjectName("t_server_confirm_button")
        self.t_server_key = QtWidgets.QLabel(self.tab_7)
        self.t_server_key.setGeometry(QtCore.QRect(170, 130, 371, 21))
        self.t_server_key.setFrameShape(QtWidgets.QFrame.Box)
        self.t_server_key.setText("")
        self.t_server_key.setObjectName("t_server_key")
        self.tabWidget_2.addTab(self.tab_7, "")
        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.t_pass_change_pass_button = QtWidgets.QPushButton(self.tab_8)
        self.t_pass_change_pass_button.setGeometry(QtCore.QRect(260, 140, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_pass_change_pass_button.setFont(font)
        self.t_pass_change_pass_button.setText("")
        self.t_pass_change_pass_button.setObjectName("t_pass_change_pass_button")
        self.t_pass_moi = QtWidgets.QLineEdit(self.tab_8)
        self.t_pass_moi.setGeometry(QtCore.QRect(180, 50, 361, 21))
        self.t_pass_moi.setText("")
        self.t_pass_moi.setObjectName("t_pass_moi")
        self.label_126 = QtWidgets.QLabel(self.tab_8)
        self.label_126.setGeometry(QtCore.QRect(10, 90, 171, 17))
        self.label_126.setObjectName("label_126")
        self.label_86 = QtWidgets.QLabel(self.tab_8)
        self.label_86.setGeometry(QtCore.QRect(10, 50, 101, 17))
        self.label_86.setObjectName("label_86")
        self.t_pass_cancel_button = QtWidgets.QPushButton(self.tab_8)
        self.t_pass_cancel_button.setGeometry(QtCore.QRect(340, 140, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_pass_cancel_button.setFont(font)
        self.t_pass_cancel_button.setText("")
        self.t_pass_cancel_button.setObjectName("t_pass_cancel_button")
        self.label_87 = QtWidgets.QLabel(self.tab_8)
        self.label_87.setGeometry(QtCore.QRect(10, 10, 121, 17))
        self.label_87.setObjectName("label_87")
        self.t_pass_xac_nhan_moi = QtWidgets.QLineEdit(self.tab_8)
        self.t_pass_xac_nhan_moi.setGeometry(QtCore.QRect(180, 90, 361, 21))
        self.t_pass_xac_nhan_moi.setObjectName("t_pass_xac_nhan_moi")
        self.t_pass_cu = QtWidgets.QLineEdit(self.tab_8)
        self.t_pass_cu.setGeometry(QtCore.QRect(180, 10, 361, 21))
        self.t_pass_cu.setObjectName("t_pass_cu")
        self.t_pass_apply_button = QtWidgets.QPushButton(self.tab_8)
        self.t_pass_apply_button.setGeometry(QtCore.QRect(180, 140, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.t_pass_apply_button.setFont(font)
        self.t_pass_apply_button.setText("")
        self.t_pass_apply_button.setObjectName("t_pass_apply_button")
        self.tabWidget_2.addTab(self.tab_8, "")
        self.report_tab.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_5.setGeometry(QtCore.QRect(0, 0, 281, 461))
        self.groupBox_5.setObjectName("groupBox_5")
        self.g_tt_hoat_dong_table = QtWidgets.QTableWidget(self.groupBox_5)
        self.g_tt_hoat_dong_table.setGeometry(QtCore.QRect(0, 20, 281, 391))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.g_tt_hoat_dong_table.setFont(font)
        self.g_tt_hoat_dong_table.setGridStyle(QtCore.Qt.DashDotLine)
        self.g_tt_hoat_dong_table.setRowCount(40)
        self.g_tt_hoat_dong_table.setColumnCount(2)
        self.g_tt_hoat_dong_table.setObjectName("g_tt_hoat_dong_table")
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_tt_hoat_dong_table.setItem(1, 1, item)
        self.g_tt_hoat_dong_table.horizontalHeader().setDefaultSectionSize(123)
        self.g_tt_hoat_dong_table.horizontalHeader().setMinimumSectionSize(58)
        self.g_tt_hoat_dong_table.verticalHeader().setDefaultSectionSize(21)
        self.g_start_button = QtWidgets.QPushButton(self.groupBox_5)
        self.g_start_button.setGeometry(QtCore.QRect(20, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.g_start_button.setFont(font)
        self.g_start_button.setText("")
        self.g_start_button.setObjectName("g_start_button")
        self.g_pause_play_button = QtWidgets.QPushButton(self.groupBox_5)
        self.g_pause_play_button.setGeometry(QtCore.QRect(110, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.g_pause_play_button.setFont(font)
        self.g_pause_play_button.setText("")
        self.g_pause_play_button.setObjectName("g_pause_play_button")
        self.g_stop_button = QtWidgets.QPushButton(self.groupBox_5)
        self.g_stop_button.setGeometry(QtCore.QRect(200, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.g_stop_button.setFont(font)
        self.g_stop_button.setText("")
        self.g_stop_button.setObjectName("g_stop_button")
        self.groupBox_15 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_15.setGeometry(QtCore.QRect(0, 460, 531, 201))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        self.groupBox_15.setFont(font)
        self.groupBox_15.setObjectName("groupBox_15")
        self.g_ket_qua_chi_tiet_table = QtWidgets.QTableWidget(self.groupBox_15)
        self.g_ket_qua_chi_tiet_table.setGeometry(QtCore.QRect(0, 21, 531, 181))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.g_ket_qua_chi_tiet_table.setFont(font)
        self.g_ket_qua_chi_tiet_table.setGridStyle(QtCore.Qt.DashDotLine)
        self.g_ket_qua_chi_tiet_table.setRowCount(40)
        self.g_ket_qua_chi_tiet_table.setObjectName("g_ket_qua_chi_tiet_table")
        self.g_ket_qua_chi_tiet_table.setColumnCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.g_ket_qua_chi_tiet_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_ket_qua_chi_tiet_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_ket_qua_chi_tiet_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.g_ket_qua_chi_tiet_table.setHorizontalHeaderItem(3, item)
        self.g_ket_qua_chi_tiet_table.horizontalHeader().setDefaultSectionSize(123)
        self.g_ket_qua_chi_tiet_table.verticalHeader().setDefaultSectionSize(21)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_4.setGeometry(QtCore.QRect(280, 0, 791, 461))
        self.groupBox_4.setObjectName("groupBox_4")
        self.g_hien_thi = QtWidgets.QLabel(self.groupBox_4)
        self.g_hien_thi.setGeometry(QtCore.QRect(10, 30, 771, 421))
        self.g_hien_thi.setFrameShape(QtWidgets.QFrame.Box)
        self.g_hien_thi.setAlignment(QtCore.Qt.AlignCenter)
        self.g_hien_thi.setObjectName("g_hien_thi")
        self.groupBox_7 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_7.setGeometry(QtCore.QRect(530, 460, 281, 201))
        self.groupBox_7.setObjectName("groupBox_7")
        self.label_106 = QtWidgets.QLabel(self.groupBox_7)
        self.label_106.setGeometry(QtCore.QRect(10, 40, 111, 41))
        self.label_106.setObjectName("label_106")
        self.label_105 = QtWidgets.QLabel(self.groupBox_7)
        self.label_105.setGeometry(QtCore.QRect(10, 140, 161, 41))
        self.label_105.setObjectName("label_105")
        self.label_109 = QtWidgets.QLabel(self.groupBox_7)
        self.label_109.setGeometry(QtCore.QRect(10, 90, 121, 41))
        self.label_109.setObjectName("label_109")
        self.g_tong_kt = QtWidgets.QLCDNumber(self.groupBox_7)
        self.g_tong_kt.setGeometry(QtCore.QRect(180, 90, 91, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(78, 152, 246))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(65, 126, 205))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(34, 67, 109))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(153, 178, 209))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(78, 152, 246))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(65, 126, 205))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(34, 67, 109))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(153, 178, 209))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(78, 152, 246))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(65, 126, 205))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(34, 67, 109))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(26, 50, 82))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(52, 101, 164))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.g_tong_kt.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.g_tong_kt.setFont(font)
        self.g_tong_kt.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.g_tong_kt.setFrameShadow(QtWidgets.QFrame.Plain)
        self.g_tong_kt.setObjectName("g_tong_kt")
        self.g_tong_vao = QtWidgets.QLCDNumber(self.groupBox_7)
        self.g_tong_vao.setGeometry(QtCore.QRect(180, 40, 91, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 250, 203))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(253, 241, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(168, 155, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(253, 244, 167))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 250, 203))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(253, 241, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(168, 155, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(253, 244, 167))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 250, 203))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(253, 241, 141))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(168, 155, 52))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(126, 116, 39))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(252, 233, 79))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.g_tong_vao.setPalette(palette)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.g_tong_vao.setFont(font)
        self.g_tong_vao.setFrameShadow(QtWidgets.QFrame.Plain)
        self.g_tong_vao.setObjectName("g_tong_vao")
        self.g_tong_khong_kt = QtWidgets.QLCDNumber(self.groupBox_7)
        self.g_tong_khong_kt.setGeometry(QtCore.QRect(180, 140, 91, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 94, 94))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(159, 27, 27))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 148, 148))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 94, 94))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(159, 27, 27))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 148, 148))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 147, 147))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 94, 94))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(159, 27, 27))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(119, 20, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(239, 41, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.g_tong_khong_kt.setPalette(palette)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.g_tong_khong_kt.setFont(font)
        self.g_tong_khong_kt.setFrameShadow(QtWidgets.QFrame.Plain)
        self.g_tong_khong_kt.setObjectName("g_tong_khong_kt")
        self.groupBox_8 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_8.setGeometry(QtCore.QRect(810, 460, 261, 201))
        self.groupBox_8.setObjectName("groupBox_8")
        self.g_date_time = QtWidgets.QLabel(self.groupBox_8)
        self.g_date_time.setGeometry(QtCore.QRect(10, 40, 241, 61))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.g_date_time.setFont(font)
        self.g_date_time.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.g_date_time.setAlignment(QtCore.Qt.AlignCenter)
        self.g_date_time.setObjectName("g_date_time")
        self.groupBox_4.raise_()
        self.groupBox_5.raise_()
        self.groupBox_15.raise_()
        self.groupBox_7.raise_()
        self.groupBox_8.raise_()
        self.report_tab.addTab(self.tab, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.groupBox_10 = QtWidgets.QGroupBox(self.tab_4)
        self.groupBox_10.setGeometry(QtCore.QRect(0, 0, 561, 661))
        self.groupBox_10.setObjectName("groupBox_10")
        self.q_thong_tin_camera_table = QtWidgets.QTableWidget(self.groupBox_10)
        self.q_thong_tin_camera_table.setGeometry(QtCore.QRect(0, 20, 561, 641))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_thong_tin_camera_table.setFont(font)
        self.q_thong_tin_camera_table.setGridStyle(QtCore.Qt.DashDotLine)
        self.q_thong_tin_camera_table.setRowCount(40)
        self.q_thong_tin_camera_table.setColumnCount(7)
        self.q_thong_tin_camera_table.setObjectName("q_thong_tin_camera_table")
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 5, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_thong_tin_camera_table.setItem(0, 6, item)
        self.q_thong_tin_camera_table.horizontalHeader().setDefaultSectionSize(123)
        self.q_thong_tin_camera_table.verticalHeader().setDefaultSectionSize(21)
        self.tabWidget = QtWidgets.QTabWidget(self.tab_4)
        self.tabWidget.setGeometry(QtCore.QRect(560, 0, 511, 661))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.q_moi_time_tu = QtWidgets.QTimeEdit(self.tab_5)
        self.q_moi_time_tu.setGeometry(QtCore.QRect(150, 370, 61, 20))
        self.q_moi_time_tu.setObjectName("q_moi_time_tu")
        self.q_moi_vach_kiem_dem_button = QtWidgets.QPushButton(self.tab_5)
        self.q_moi_vach_kiem_dem_button.setGeometry(QtCore.QRect(130, 210, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.q_moi_vach_kiem_dem_button.setFont(font)
        self.q_moi_vach_kiem_dem_button.setText("")
        self.q_moi_vach_kiem_dem_button.setObjectName("q_moi_vach_kiem_dem_button")
        self.q_moi_webcam = QtWidgets.QRadioButton(self.tab_5)
        self.q_moi_webcam.setGeometry(QtCore.QRect(420, 10, 81, 23))
        self.q_moi_webcam.setObjectName("q_moi_webcam")
        self.q_moi_dia_chi_camera = QtWidgets.QLineEdit(self.tab_5)
        self.q_moi_dia_chi_camera.setGeometry(QtCore.QRect(130, 90, 371, 21))
        self.q_moi_dia_chi_camera.setObjectName("q_moi_dia_chi_camera")
        self.label_98 = QtWidgets.QLabel(self.tab_5)
        self.label_98.setGeometry(QtCore.QRect(10, 170, 121, 17))
        self.label_98.setObjectName("label_98")
        self.q_moi_combobox_den = QtWidgets.QComboBox(self.tab_5)
        self.q_moi_combobox_den.setGeometry(QtCore.QRect(240, 250, 111, 21))
        self.q_moi_combobox_den.setObjectName("q_moi_combobox_den")
        self.q_moi_combobox_den.addItem("")
        self.q_moi_combobox_den.addItem("")
        self.q_moi_combobox_den.addItem("")
        self.label_94 = QtWidgets.QLabel(self.tab_5)
        self.label_94.setGeometry(QtCore.QRect(240, 370, 41, 17))
        self.label_94.setObjectName("label_94")
        self.q_moi_time_den = QtWidgets.QTimeEdit(self.tab_5)
        self.q_moi_time_den.setGeometry(QtCore.QRect(270, 370, 61, 20))
        self.q_moi_time_den.setObjectName("q_moi_time_den")
        self.label_95 = QtWidgets.QLabel(self.tab_5)
        self.label_95.setGeometry(QtCore.QRect(10, 130, 101, 17))
        self.label_95.setObjectName("label_95")
        self.q_moi_combobox_am_thanh = QtWidgets.QComboBox(self.tab_5)
        self.q_moi_combobox_am_thanh.setGeometry(QtCore.QRect(240, 290, 111, 21))
        self.q_moi_combobox_am_thanh.setObjectName("q_moi_combobox_am_thanh")
        self.q_moi_combobox_am_thanh.addItem("")
        self.q_moi_combobox_am_thanh.addItem("")
        self.q_moi_combobox_am_thanh.addItem("")
        self.q_moi_den = QtWidgets.QRadioButton(self.tab_5)
        self.q_moi_den.setGeometry(QtCore.QRect(130, 250, 91, 21))
        self.q_moi_den.setObjectName("q_moi_den")
        self.label_77 = QtWidgets.QLabel(self.tab_5)
        self.label_77.setGeometry(QtCore.QRect(10, 90, 121, 17))
        self.label_77.setObjectName("label_77")
        self.q_moi_ten_camera = QtWidgets.QLineEdit(self.tab_5)
        self.q_moi_ten_camera.setGeometry(QtCore.QRect(130, 10, 181, 21))
        self.q_moi_ten_camera.setObjectName("q_moi_ten_camera")
        self.q_moi_am_thanh = QtWidgets.QRadioButton(self.tab_5)
        self.q_moi_am_thanh.setGeometry(QtCore.QRect(130, 290, 91, 21))
        self.q_moi_am_thanh.setObjectName("q_moi_am_thanh")
        self.q_moi_vung_quan_sat_button = QtWidgets.QPushButton(self.tab_5)
        self.q_moi_vung_quan_sat_button.setGeometry(QtCore.QRect(130, 170, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.q_moi_vung_quan_sat_button.setFont(font)
        self.q_moi_vung_quan_sat_button.setText("")
        self.q_moi_vung_quan_sat_button.setObjectName("q_moi_vung_quan_sat_button")
        self.q_moi_ipcamera = QtWidgets.QRadioButton(self.tab_5)
        self.q_moi_ipcamera.setGeometry(QtCore.QRect(320, 10, 91, 23))
        self.q_moi_ipcamera.setObjectName("q_moi_ipcamera")
        self.label_76 = QtWidgets.QLabel(self.tab_5)
        self.label_76.setGeometry(QtCore.QRect(10, 370, 111, 17))
        self.label_76.setObjectName("label_76")
        self.q_moi_che_do = QtWidgets.QCheckBox(self.tab_5)
        self.q_moi_che_do.setGeometry(QtCore.QRect(130, 130, 51, 21))
        self.q_moi_che_do.setObjectName("q_moi_che_do")
        self.q_moi_che_do.setChecked(True)
        self.label_97 = QtWidgets.QLabel(self.tab_5)
        self.label_97.setGeometry(QtCore.QRect(10, 210, 121, 17))
        self.label_97.setObjectName("label_97")
        self.label_75 = QtWidgets.QLabel(self.tab_5)
        self.label_75.setGeometry(QtCore.QRect(10, 10, 121, 17))
        self.label_75.setObjectName("label_75")
        self.q_moi_ca_hai = QtWidgets.QRadioButton(self.tab_5)
        self.q_moi_ca_hai.setGeometry(QtCore.QRect(130, 330, 81, 21))
        self.q_moi_ca_hai.setObjectName("q_moi_ca_hai")
        self.label_78 = QtWidgets.QLabel(self.tab_5)
        self.label_78.setGeometry(QtCore.QRect(130, 370, 41, 17))
        self.label_78.setObjectName("label_78")
        self.label_96 = QtWidgets.QLabel(self.tab_5)
        self.label_96.setGeometry(QtCore.QRect(10, 250, 121, 17))
        self.label_96.setObjectName("label_96")
        self.q_moi_cancel_button = QtWidgets.QPushButton(self.tab_5)
        self.q_moi_cancel_button.setGeometry(QtCore.QRect(310, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_moi_cancel_button.setFont(font)
        self.q_moi_cancel_button.setText("")
        self.q_moi_cancel_button.setObjectName("q_moi_cancel_button")
        self.q_moi_appy_button = QtWidgets.QPushButton(self.tab_5)
        self.q_moi_appy_button.setGeometry(QtCore.QRect(130, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_moi_appy_button.setFont(font)
        self.q_moi_appy_button.setText("")
        self.q_moi_appy_button.setObjectName("q_moi_appy_button")
        self.q_moi_add_button = QtWidgets.QPushButton(self.tab_5)
        self.q_moi_add_button.setGeometry(QtCore.QRect(220, 420, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_moi_add_button.setFont(font)
        self.q_moi_add_button.setText("")
        self.q_moi_add_button.setObjectName("q_moi_add_button")
        self.label_79 = QtWidgets.QLabel(self.tab_5)
        self.label_79.setGeometry(QtCore.QRect(10, 50, 71, 17))
        self.label_79.setObjectName("label_79")
        self.q_moi_camera_id = QtWidgets.QLabel(self.tab_5)
        self.q_moi_camera_id.setGeometry(QtCore.QRect(130, 50, 371, 21))
        self.q_moi_camera_id.setFrameShape(QtWidgets.QFrame.Box)
        self.q_moi_camera_id.setText("")
        self.q_moi_camera_id.setObjectName("q_moi_camera_id")
        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.label_99 = QtWidgets.QLabel(self.tab_6)
        self.label_99.setGeometry(QtCore.QRect(240, 410, 41, 17))
        self.label_99.setObjectName("label_99")
        self.q_chinh_time_den = QtWidgets.QTimeEdit(self.tab_6)
        self.q_chinh_time_den.setGeometry(QtCore.QRect(270, 410, 61, 20))
        self.q_chinh_time_den.setObjectName("q_chinh_time_den")
        self.q_chinh_ca_hai = QtWidgets.QRadioButton(self.tab_6)
        self.q_chinh_ca_hai.setGeometry(QtCore.QRect(130, 370, 81, 21))
        self.q_chinh_ca_hai.setObjectName("q_chinh_ca_hai")
        self.label_100 = QtWidgets.QLabel(self.tab_6)
        self.label_100.setGeometry(QtCore.QRect(10, 170, 101, 17))
        self.label_100.setObjectName("label_100")
        self.q_chinh_vung_quan_sat = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_vung_quan_sat.setGeometry(QtCore.QRect(130, 210, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.q_chinh_vung_quan_sat.setFont(font)
        self.q_chinh_vung_quan_sat.setText("")
        self.q_chinh_vung_quan_sat.setObjectName("q_chinh_vung_quan_sat")
        self.q_chinh_che_do = QtWidgets.QCheckBox(self.tab_6)
        self.q_chinh_che_do.setGeometry(QtCore.QRect(130, 170, 51, 21))
        self.q_chinh_che_do.setObjectName("q_chinh_che_do")
        self.q_chinh_che_do.setChecked(True)
        self.label_102 = QtWidgets.QLabel(self.tab_6)
        self.label_102.setGeometry(QtCore.QRect(10, 290, 121, 17))
        self.label_102.setObjectName("label_102")
        self.q_chinh_camera_name = QtWidgets.QLineEdit(self.tab_6)
        self.q_chinh_camera_name.setGeometry(QtCore.QRect(130, 10, 311, 21))
        self.q_chinh_camera_name.setObjectName("q_chinh_camera_name")
        self.label_81 = QtWidgets.QLabel(self.tab_6)
        self.label_81.setGeometry(QtCore.QRect(10, 10, 121, 17))
        self.label_81.setObjectName("label_81")
        self.q_chinh_apply_button = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_apply_button.setGeometry(QtCore.QRect(80, 460, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_chinh_apply_button.setFont(font)
        self.q_chinh_apply_button.setText("")
        self.q_chinh_apply_button.setObjectName("q_chinh_apply_button")
        self.q_chinh_delete_button = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_delete_button.setGeometry(QtCore.QRect(170, 460, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_chinh_delete_button.setFont(font)
        self.q_chinh_delete_button.setText("")
        self.q_chinh_delete_button.setObjectName("q_chinh_delete_button")
        self.q_chinh_den = QtWidgets.QRadioButton(self.tab_6)
        self.q_chinh_den.setGeometry(QtCore.QRect(130, 290, 91, 21))
        self.q_chinh_den.setObjectName("q_chinh_den")
        self.q_chinh_vach_kiem_dem = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_vach_kiem_dem.setGeometry(QtCore.QRect(130, 250, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.q_chinh_vach_kiem_dem.setFont(font)
        self.q_chinh_vach_kiem_dem.setText("")
        self.q_chinh_vach_kiem_dem.setObjectName("q_chinh_vach_kiem_dem")
        self.label_82 = QtWidgets.QLabel(self.tab_6)
        self.label_82.setGeometry(QtCore.QRect(10, 410, 111, 17))
        self.label_82.setObjectName("label_82")
        self.q_chinh_combobox_am_thanh = QtWidgets.QComboBox(self.tab_6)
        self.q_chinh_combobox_am_thanh.setGeometry(QtCore.QRect(240, 330, 111, 21))
        self.q_chinh_combobox_am_thanh.setObjectName("q_chinh_combobox_am_thanh")
        self.q_chinh_combobox_am_thanh.addItem("")
        self.q_chinh_combobox_am_thanh.addItem("")
        self.q_chinh_combobox_am_thanh.addItem("")
        self.label_103 = QtWidgets.QLabel(self.tab_6)
        self.label_103.setGeometry(QtCore.QRect(10, 94, 121, 17))
        self.label_103.setObjectName("label_103")
        self.q_chinh_cancel_button = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_cancel_button.setGeometry(QtCore.QRect(350, 460, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_chinh_cancel_button.setFont(font)
        self.q_chinh_cancel_button.setText("")
        self.q_chinh_cancel_button.setObjectName("q_chinh_cancel_button")
        self.label_104 = QtWidgets.QLabel(self.tab_6)
        self.label_104.setGeometry(QtCore.QRect(10, 250, 121, 17))
        self.label_104.setObjectName("label_104")
        self.q_chinh_chinh_sua_button = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_chinh_sua_button.setGeometry(QtCore.QRect(260, 460, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_chinh_chinh_sua_button.setFont(font)
        self.q_chinh_chinh_sua_button.setText("")
        self.q_chinh_chinh_sua_button.setObjectName("q_chinh_chinh_sua_button")
        self.q_chinh_am_thanh = QtWidgets.QRadioButton(self.tab_6)
        self.q_chinh_am_thanh.setGeometry(QtCore.QRect(130, 330, 91, 21))
        self.q_chinh_am_thanh.setObjectName("q_chinh_am_thanh")
        self.label_107 = QtWidgets.QLabel(self.tab_6)
        self.label_107.setGeometry(QtCore.QRect(10, 210, 121, 17))
        self.label_107.setObjectName("label_107")
        self.label_108 = QtWidgets.QLabel(self.tab_6)
        self.label_108.setGeometry(QtCore.QRect(130, 410, 41, 17))
        self.label_108.setObjectName("label_108")
        self.q_chinh_combobox_den = QtWidgets.QComboBox(self.tab_6)
        self.q_chinh_combobox_den.setGeometry(QtCore.QRect(240, 290, 111, 21))
        self.q_chinh_combobox_den.setObjectName("q_chinh_combobox_den")
        self.q_chinh_combobox_den.addItem("")
        self.q_chinh_combobox_den.addItem("")
        self.q_chinh_combobox_den.addItem("")
        self.q_chinh_time_tu = QtWidgets.QTimeEdit(self.tab_6)
        self.q_chinh_time_tu.setGeometry(QtCore.QRect(150, 410, 61, 20))
        self.q_chinh_time_tu.setObjectName("q_chinh_time_tu")
        self.q_chinh_search_button = QtWidgets.QPushButton(self.tab_6)
        self.q_chinh_search_button.setGeometry(QtCore.QRect(450, 10, 51, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.q_chinh_search_button.setFont(font)
        self.q_chinh_search_button.setText("")
        self.q_chinh_search_button.setObjectName("q_chinh_search_button")
        self.q_chinh_output_camera_address = QtWidgets.QLabel(self.tab_6)
        self.q_chinh_output_camera_address.setGeometry(QtCore.QRect(130, 90, 371, 21))
        self.q_chinh_output_camera_address.setFrameShape(QtWidgets.QFrame.Box)
        self.q_chinh_output_camera_address.setText("")
        self.q_chinh_output_camera_address.setObjectName("q_chinh_output_camera_address")
        self.q_chinh_camera_new_name = QtWidgets.QLineEdit(self.tab_6)
        self.q_chinh_camera_new_name.setGeometry(QtCore.QRect(130, 130, 211, 21))
        self.q_chinh_camera_new_name.setObjectName("q_chinh_camera_new_name")
        self.label_83 = QtWidgets.QLabel(self.tab_6)
        self.label_83.setGeometry(QtCore.QRect(10, 130, 121, 17))
        self.label_83.setObjectName("label_83")
        self.label_88 = QtWidgets.QLabel(self.tab_6)
        self.label_88.setGeometry(QtCore.QRect(10, 50, 71, 17))
        self.label_88.setObjectName("label_88")
        self.q_chinh_camera_id = QtWidgets.QLabel(self.tab_6)
        self.q_chinh_camera_id.setGeometry(QtCore.QRect(130, 50, 371, 21))
        self.q_chinh_camera_id.setFrameShape(QtWidgets.QFrame.Box)
        self.q_chinh_camera_id.setText("")
        self.q_chinh_camera_id.setObjectName("q_chinh_camera_id")
        self.q_chinh_rename_status = QtWidgets.QLabel(self.tab_6)
        self.q_chinh_rename_status.setGeometry(QtCore.QRect(360, 130, 141, 21))
        self.q_chinh_rename_status.setFrameShape(QtWidgets.QFrame.Box)
        self.q_chinh_rename_status.setText("")
        self.q_chinh_rename_status.setObjectName("q_chinh_rename_status")
        self.tabWidget.addTab(self.tab_6, "")
        self.report_tab.addTab(self.tab_4, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.display_ploting_1 = QtWidgets.QLabel(self.tab_3)
        self.display_ploting_1.setGeometry(QtCore.QRect(0, 70, 531, 261))
        self.display_ploting_1.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_1.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_1.setObjectName("display_ploting_1")
        self.groupBox_plot1 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_plot1.setGeometry(QtCore.QRect(0, 0, 531, 61))
        self.groupBox_plot1.setObjectName("groupBox_plot1")
        self.b_t1_plot_button = QtWidgets.QPushButton(self.groupBox_plot1)
        self.b_t1_plot_button.setGeometry(QtCore.QRect(390, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t1_plot_button.setFont(font)
        self.b_t1_plot_button.setText("")
        self.b_t1_plot_button.setObjectName("b_t1_plot_button")
        self.b_t1_combobox_kieu_thong_ke = QtWidgets.QComboBox(self.groupBox_plot1)
        self.b_t1_combobox_kieu_thong_ke.setGeometry(QtCore.QRect(110, 30, 151, 21))
        self.b_t1_combobox_kieu_thong_ke.setObjectName("b_t1_combobox_kieu_thong_ke")
        self.b_t1_combobox_kieu_thong_ke.addItem("")
        self.b_t1_combobox_kieu_thong_ke.addItem("")
        self.b_t1_combobox_kieu_thong_ke.addItem("")
        self.b_t1_combobox_camera_name = QtWidgets.QComboBox(self.groupBox_plot1)
        self.b_t1_combobox_camera_name.setGeometry(QtCore.QRect(10, 30, 91, 21))
        self.b_t1_combobox_camera_name.setObjectName("b_t1_combobox_camera_name")
        self.b_t1_combobox_camera_name.addItem("")
        self.b_t1_combobox_camera_name.addItem("")
        self.b_t1_combobox_camera_name.addItem("")
        self.b_t1_date = QtWidgets.QDateEdit(self.groupBox_plot1)
        self.b_t1_date.setGeometry(QtCore.QRect(270, 30, 111, 21))
        self.b_t1_date.setObjectName("b_t1_date")
        self.b_t1_save_button = QtWidgets.QPushButton(self.groupBox_plot1)
        self.b_t1_save_button.setGeometry(QtCore.QRect(440, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t1_save_button.setFont(font)
        self.b_t1_save_button.setText("")
        self.b_t1_save_button.setObjectName("b_t1_save_button")
        self.b_t1_export_button = QtWidgets.QPushButton(self.groupBox_plot1)
        self.b_t1_export_button.setGeometry(QtCore.QRect(490, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t1_export_button.setFont(font)
        self.b_t1_export_button.setText("")
        self.b_t1_export_button.setObjectName("b_t1_export_button")
        self.b_t1_table = QtWidgets.QTableWidget(self.tab_3)
        self.b_t1_table.setGeometry(QtCore.QRect(0, 340, 531, 321))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t1_table.setFont(font)
        self.b_t1_table.setGridStyle(QtCore.Qt.DashDotLine)
        self.b_t1_table.setWordWrap(True)
        self.b_t1_table.setRowCount(20000)
        self.b_t1_table.setColumnCount(9)
        self.b_t1_table.setObjectName("b_t1_table")
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t1_table.setHorizontalHeaderItem(8, item)
        self.b_t1_table.horizontalHeader().setDefaultSectionSize(73)
        self.b_t1_table.horizontalHeader().setMinimumSectionSize(123)
        self.b_t1_table.verticalHeader().setDefaultSectionSize(21)
        self.display_ploting_2 = QtWidgets.QLabel(self.tab_3)
        self.display_ploting_2.setGeometry(QtCore.QRect(530, 70, 531, 261))
        self.display_ploting_2.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_2.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_2.setObjectName("display_ploting_2")
        self.groupBox_plot1_2 = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox_plot1_2.setGeometry(QtCore.QRect(530, 0, 531, 61))
        self.groupBox_plot1_2.setObjectName("groupBox_plot1_2")
        self.b_t2_plot_button = QtWidgets.QPushButton(self.groupBox_plot1_2)
        self.b_t2_plot_button.setGeometry(QtCore.QRect(390, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t2_plot_button.setFont(font)
        self.b_t2_plot_button.setText("")
        self.b_t2_plot_button.setObjectName("b_t2_plot_button")
        self.b_t2_combobox_kieu_thong_ke = QtWidgets.QComboBox(self.groupBox_plot1_2)
        self.b_t2_combobox_kieu_thong_ke.setGeometry(QtCore.QRect(110, 30, 151, 21))
        self.b_t2_combobox_kieu_thong_ke.setObjectName("b_t2_combobox_kieu_thong_ke")
        self.b_t2_combobox_kieu_thong_ke.addItem("")
        self.b_t2_combobox_kieu_thong_ke.addItem("")
        self.b_t2_combobox_kieu_thong_ke.addItem("")
        self.b_t2_combobox_camera_name = QtWidgets.QComboBox(self.groupBox_plot1_2)
        self.b_t2_combobox_camera_name.setGeometry(QtCore.QRect(10, 30, 91, 21))
        self.b_t2_combobox_camera_name.setObjectName("b_t2_combobox_camera_name")
        self.b_t2_combobox_camera_name.addItem("")
        self.b_t2_combobox_camera_name.addItem("")
        self.b_t2_combobox_camera_name.addItem("")
        self.b_t2_date = QtWidgets.QDateEdit(self.groupBox_plot1_2)
        self.b_t2_date.setGeometry(QtCore.QRect(270, 30, 111, 21))
        self.b_t2_date.setObjectName("b_t2_date")
        self.b_t2_save_button = QtWidgets.QPushButton(self.groupBox_plot1_2)
        self.b_t2_save_button.setGeometry(QtCore.QRect(440, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t2_save_button.setFont(font)
        self.b_t2_save_button.setText("")
        self.b_t2_save_button.setObjectName("b_t2_save_button")
        self.b_t2_export_button = QtWidgets.QPushButton(self.groupBox_plot1_2)
        self.b_t2_export_button.setGeometry(QtCore.QRect(490, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t2_export_button.setFont(font)
        self.b_t2_export_button.setText("")
        self.b_t2_export_button.setObjectName("b_t2_export_button")
        self.b_t2_table = QtWidgets.QTableWidget(self.tab_3)
        self.b_t2_table.setGeometry(QtCore.QRect(530, 340, 531, 321))
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.b_t2_table.setFont(font)
        self.b_t2_table.setGridStyle(QtCore.Qt.DashDotLine)
        self.b_t2_table.setWordWrap(True)
        self.b_t2_table.setRowCount(20000)
        self.b_t2_table.setColumnCount(9)
        self.b_t2_table.setObjectName("b_t2_table")
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.b_t2_table.setHorizontalHeaderItem(8, item)
        self.b_t2_table.horizontalHeader().setDefaultSectionSize(123)
        self.b_t2_table.horizontalHeader().setMinimumSectionSize(123)
        self.b_t2_table.verticalHeader().setDefaultSectionSize(21)
        self.report_tab.addTab(self.tab_3, "")

        # ----- set icon
        # giam sat
        self.g_start_button.setIcon(QtGui.QIcon('./icon/start.jpg'))
        self.g_stop_button.setIcon(QtGui.QIcon('./icon/stop.png'))
        self.g_pause_play_button.setIcon(QtGui.QIcon('./icon/pause.png'))
        # quan li camera
        self.q_moi_vung_quan_sat_button.setIcon(QtGui.QIcon('./icon/draw.png'))
        self.q_moi_vach_kiem_dem_button.setIcon(QtGui.QIcon('./icon/draw.png'))
        self.q_moi_appy_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
        self.q_moi_add_button.setIcon(QtGui.QIcon('./icon/add.jpg'))
        self.q_moi_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
        self.q_chinh_search_button.setIcon(QtGui.QIcon('./icon/search.png'))
        self.q_chinh_vung_quan_sat.setIcon(QtGui.QIcon('./icon/draw.png'))
        self.q_chinh_vach_kiem_dem.setIcon(QtGui.QIcon('./icon/draw.png'))
        self.q_chinh_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
        self.q_chinh_chinh_sua_button.setIcon(QtGui.QIcon('./icon/edit.png'))
        self.q_chinh_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
        self.q_chinh_delete_button.setIcon(QtGui.QIcon('./icon/delete.png'))
        # bao cao va thong ke
        self.b_t1_plot_button.setIcon(QtGui.QIcon('./icon/plot.png'))
        self.b_t1_save_button.setIcon(QtGui.QIcon('./icon/save.png'))
        self.b_t1_export_button.setIcon(QtGui.QIcon('./icon/export_data.png'))
        self.b_t2_plot_button.setIcon(QtGui.QIcon('./icon/plot.png'))
        self.b_t2_save_button.setIcon(QtGui.QIcon('./icon/save.png'))
        self.b_t2_export_button.setIcon(QtGui.QIcon('./icon/export_data.png'))
        # thong tin va thiet dat
        self.t_server_sending_button.setIcon(QtGui.QIcon('./icon/sending.png'))
        self.t_server_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
        self.t_server_confirm_button.setIcon(QtGui.QIcon('./icon/update.png'))
        self.t_server_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
        self.t_pass_apply_button.setIcon(QtGui.QIcon('./icon/apply.jpeg'))
        self.t_pass_change_pass_button.setIcon(QtGui.QIcon('./icon/confirm.png'))
        self.t_pass_cancel_button.setIcon(QtGui.QIcon('./icon/cancel.png'))
        # -----

        # -----
        # EVENTS
        # start video
        self.g_start_button.clicked.connect(self.video)
        # stop video
        self.g_stop_button.clicked.connect(close_window)
        # call display video
        global th
        th = Thread(MainWindow, self.g_tong_khong_kt)
        # FOR REPORT AND STATISTICS TAB
        # plotting
        self.b_t1_combobox_kieu_thong_ke.activated.connect(self.change_plot_date_format_1)
        self.b_t2_combobox_kieu_thong_ke.activated.connect(self.change_plot_date_format_2)
        self.update_combobox()  # for update all camera names in configuration file
        self.b_t1_plot_button.clicked.connect(self.call_plotting_1)
        self.b_t2_plot_button.clicked.connect(self.call_plotting_2)
        self.b_t1_save_button.clicked.connect(self.call_save_1)
        self.b_t2_save_button.clicked.connect(self.call_save_2)
        self.b_t1_export_button.clicked.connect(self.call_export_1)
        self.b_t2_export_button.clicked.connect(self.call_export_2)
        # FOR CAMERAS MANAGEMENT TAB
        # update camera information in camera management tab
        self.camera_management_working_status()
        # assign new camera id
        self.q_moi_appy_button.clicked.connect(self.camera_management_assign_camera_id)
        # add new camera
        self.q_moi_add_button.clicked.connect(self.camera_management_add_new)
        # draw new tracking region
        self.q_moi_vung_quan_sat_button.clicked.connect(self.camera_management_draw_region_new)
        # draw new counting line
        self.q_moi_vach_kiem_dem_button.clicked.connect(self.camera_management_draw_counting_new)
        # -----

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 23))
        self.menubar.setObjectName("menubar")
        self.menuHome = QtWidgets.QMenu(self.menubar)
        self.menuHome.setObjectName("menuHome")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLock = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.actionLock.setFont(font)
        self.actionLock.setObjectName("actionLock")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.exit = QtWidgets.QAction(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.exit.setFont(font)
        self.exit.setObjectName("exit")
        self.menuHome.addAction(self.actionLock)
        self.menuHome.addAction(self.exit)
        self.menubar.addAction(self.menuHome.menuAction())
        self.retranslateUi(MainWindow)
        self.report_tab.setCurrentIndex(1)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # FOR REPORT AND STATISTICS TAB
    def change_plot_date_format_1(self):
        if self.b_t1_combobox_kieu_thong_ke.currentText() == "Thống kê theo Ngày":
            self.b_t1_date.setDisplayFormat("dd/MM/yyyy")
        elif self.b_t1_combobox_kieu_thong_ke.currentText() == "Thống kê theo Tháng":
            self.b_t1_date.setDisplayFormat("MM/yyyy")
        elif self.b_t1_combobox_kieu_thong_ke.currentText() == "Thống kê theo Năm":
            self.b_t1_date.setDisplayFormat("yyyy")

    def change_plot_date_format_2(self):
        if self.b_t2_combobox_kieu_thong_ke.currentText() == "Thống kê theo Ngày":
            self.b_t2_date.setDisplayFormat("dd/MM/yyyy")
        elif self.b_t2_combobox_kieu_thong_ke.currentText() == "Thống kê theo Tháng":
            self.b_t2_date.setDisplayFormat("MM/yyyy")
        elif self.b_t2_combobox_kieu_thong_ke.currentText() == "Thống kê theo Năm":
            self.b_t2_date.setDisplayFormat("yyyy")

    def update_combobox(self):
        global data_first_time
        combobox_items = []
        for i in range(len(data_first_time)):
            combobox_items.append(data_first_time[i]["name"])
        self.b_t1_combobox_camera_name.clear()
        self.b_t2_combobox_camera_name.clear()
        for item in combobox_items:
            self.b_t1_combobox_camera_name.addItem(item)
            self.b_t2_combobox_camera_name.addItem(item)

    def call_plotting_1(self):
        name_of_figure = "final_figure_1.png"
        color = "red"
        camera_name_input = self.b_t1_combobox_camera_name.currentText()
        statistics_type = self.b_t1_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t1_date.text()
        save = False
        export = False

        return_data = report_statistics_tab.plot_save_export(name_of_figure,
                                                             color,
                                                             camera_name_input,
                                                             statistics_type,
                                                             date_input,
                                                             save,
                                                             export)
        if len(return_data) != 0:
            column_count = len(return_data[0])
            row_count = len(return_data)
            for row in range(row_count):
                for column in range(column_count):
                    item = str((list(return_data[row])[column]))
                    self.b_t1_table.setItem(row, column, QtWidgets.QTableWidgetItem(item))

            self.display_ploting_1.clear()
            self.display_ploting_1.setScaledContents(True)
            pixmap = QtGui.QPixmap("./figure/" + name_of_figure)
            self.display_ploting_1.setPixmap(pixmap)
        else:
            app_warning_function.plotting_no_data_warning()

    def call_plotting_2(self):
        name_of_figure = "final_figure_1.png"
        color = "purple"
        camera_name_input = self.b_t2_combobox_camera_name.currentText()
        statistics_type = self.b_t2_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t2_date.text()
        save = False
        export = False
        return_data = report_statistics_tab.plot_save_export(name_of_figure,
                                                             color,
                                                             camera_name_input,
                                                             statistics_type,
                                                             date_input,
                                                             save,
                                                             export)
        if len(return_data) != 0:
            column_count = len(return_data[0])
            row_count = len(return_data)
            for row in range(row_count):
                for column in range(column_count):
                    item = str((list(return_data[row])[column]))
                    self.b_t2_table.setItem(row, column, QtWidgets.QTableWidgetItem(item))

            self.display_ploting_2.clear()
            self.display_ploting_2.setScaledContents(True)
            pixmap = QtGui.QPixmap("./figure/" + name_of_figure)
            self.display_ploting_2.setPixmap(pixmap)
        else:
            app_warning_function.plotting_no_data_warning()

    def call_save_1(self):
        name_of_figure = "final_figure_1.png"
        color = "red"
        camera_name_input = self.b_t1_combobox_camera_name.currentText()
        statistics_type = self.b_t1_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t1_date.text()
        save = True
        export = False
        report_statistics_tab.plot_save_export(name_of_figure,
                                               color,
                                               camera_name_input,
                                               statistics_type,
                                               date_input,
                                               save,
                                               export)

    def call_save_2(self):
        name_of_figure = "final_figure_1.png"
        color = "red"
        camera_name_input = self.b_t2_combobox_camera_name.currentText()
        statistics_type = self.b_t2_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t2_date.text()
        save = True
        export = False
        report_statistics_tab.plot_save_export(name_of_figure,
                                               color,
                                               camera_name_input,
                                               statistics_type,
                                               date_input,
                                               save,
                                               export)

    def call_export_1(self):
        name_of_figure = "final_figure_1.png"
        color = "red"
        camera_name_input = self.b_t1_combobox_camera_name.currentText()
        statistics_type = self.b_t1_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t1_date.text()
        save = False
        export = True
        report_statistics_tab.plot_save_export(name_of_figure,
                                               color,
                                               camera_name_input,
                                               statistics_type,
                                               date_input,
                                               save,
                                               export)

    def call_export_2(self):
        name_of_figure = "final_figure_1.png"
        color = "red"
        camera_name_input = self.b_t2_combobox_camera_name.currentText()
        statistics_type = self.b_t2_combobox_kieu_thong_ke.currentText()
        date_input = self.b_t2_date.text()
        save = False
        export = True
        report_statistics_tab.plot_save_export(name_of_figure,
                                               color,
                                               camera_name_input,
                                               statistics_type,
                                               date_input,
                                               save,
                                               export)

    # FOR CAMERAS MANAGEMENT TAB
    def camera_management_working_status(self):
        global data_first_time
        camera_infor = []
        for i in range(len(data_first_time)):
            camera_infor_item = [
                data_first_time[i]["name"],
                data_first_time[i]["url"],
                data_first_time[i]["enable"],
                data_first_time[i]["setting_time"],
                data_first_time[i]["alarm_option"],
                data_first_time[i]["light"],
                data_first_time[i]["sound"]
            ]
            camera_infor.append(camera_infor_item)
        column_count = len(camera_infor[0])
        row_count = len(camera_infor)
        for row in range(row_count):
            for column in range(column_count):
                item = str((list(camera_infor[row])[column]))
                self.q_thong_tin_camera_table.setItem(row, column, QtWidgets.QTableWidgetItem(item))

    def camera_management_assign_camera_id(self):
        global new_camera_id
        new_camera_id = "xzy"

    def camera_management_add_new(self):
        global config_file, new_camera_id, new_camera_path, extra_pixels, draw_region_flag_new, draw_count_flag_new, \
            draw_region_points, draw_counting_points

        # check camera name
        if len(self.q_moi_ten_camera.text()) == 0:
            app_warning_function.check_camera_name()
        else:
            new_camera_name = self.q_moi_ten_camera.text()

        # collect new camera address
        new_camera_address = self.q_moi_dia_chi_camera.text()

        # check status of new_camera_enable = "yes"
        if self.q_moi_che_do.isChecked():
            new_camera_enable = "yes"
        else:
            new_camera_enable = "no"

        # check alarm_option
        if self.q_moi_den.isChecked():
            new_camera_alarm_option = "den bao"
        elif self.q_moi_am_thanh.isChecked():
            new_camera_alarm_option = "am thanh"
        elif self.q_moi_ca_hai.q_moi_ca_hai.isChecked():
            new_camera_alarm_option = "ca hai"

        new_camera_sound_type = self.q_moi_combobox_am_thanh.currentText()
        new_camera_light_type = self.q_moi_combobox_den.currentText()
        new_camera_time_tu = self.q_moi_time_tu.text()
        new_camera_time_den = self.q_moi_time_den.text()

        # ----- get width, height of input
        cap = cv2.VideoCapture(new_camera_address)
        w = int(cap.get(3))
        h = int(cap.get(4))
        cap.release()
        print("w,h: ", w,h)
        # -----

        # check draw_region_flag_new to get for if drawed or not
        new_camera_tracking_region = []
        if draw_region_flag_new:
            new_camera_tracking_region = draw_region_points
            draw_region_flag_new = False
            draw_region_points = []
            print("new_camera_tracking_region", new_camera_tracking_region)
        else:
            new_camera_tracking_region = create_default_region(w, h, extra_pixels)
            print("new_camera_tracking_region - default", new_camera_tracking_region)

        # check draw_count_flag_new to get for if drawed or not
        new_camera_counting_line = []
        if draw_count_flag_new:
            counting_point = draw_counting_points
            if len(counting_point) % 6 == 0:
                j = 0
                for i in range(0, len(counting_point), 6):
                    j += 1
                    item = {
                        "id": f"Counting-{j}",
                        "points": [counting_point[i], counting_point[i + 1], counting_point[i + 2],
                                   counting_point[i + 3]],
                        "direction_point": [counting_point[i + 4], counting_point[i + 5]]
                    }
                    new_camera_counting_line.append(item)
                draw_count_flag_new = False
                draw_counting_points = []
            else:
                app_warning_function.check_new_counting_lines()
                draw_count_flag_new = False
                draw_counting_points = []
        else:
            new_camera_counting_line = create_default_counting_line(w, h, extra_pixels)

        # check camera id to add new camera into config file
        if len(new_camera_id) < 2:
            app_warning_function.check_new_camera_id()
        else:
            new_camera_data = {
                "id": new_camera_id,
                "name": new_camera_name,
                "enable": new_camera_enable,
                "alarm_option": new_camera_alarm_option,
                "sound": new_camera_sound_type,
                "light": new_camera_light_type,
                "setting_time": [new_camera_time_tu, new_camera_time_den],
                "url": new_camera_address,
                "frame_drop": 1,
                "frame_step": 1,
                "tracking_scale": 0.5,
                "ROIs": [
                    {
                        "caption": "ROI-1",
                        "box": [0, 0, 1920, 1080],
                        "show_point": [50, 150]
                    }
                ],
                "tracking_regions": [
                    {
                        "id": "Tracking-1",
                        "points": new_camera_tracking_region,
                        "id_show_point": [965, 644],
                        "trap_lines": {
                            "unlimited_counts": new_camera_counting_line
                        }
                    }
                ]
            }

            print(new_camera_data)

            yaml.warnings({'YAMLLoadWarning': False})
            with open(config_file, 'r') as fs_new:
                config_new = yaml.load(fs_new)
            cam_config_new = config_new["input"]["cam_config"]
            with open(cam_config_new) as json_file_new:
                json_data_new = json.load(json_file_new)
            json_file_new.close()
            # add new camera information
            data_new = json_data_new["data"]
            data_new.append(new_camera_data)
            json_data_new["data"] = data_new
            # write json file
            with open(json_file_new.name, "w") as outfile_new:
                json.dump(json_data_new, outfile_new)
            outfile_new.close()

    def camera_management_draw_region_new(self):
        global new_camera_path, draw_region_flag_new

        # check camera name
        if len(self.q_moi_ten_camera.text()) == 0:
            app_warning_function.check_camera_name()
        else:
            new_camera_name = self.q_moi_ten_camera.text()

        # check camera address
        # for IP camera
        if self.q_moi_ipcamera.isChecked():
            if len(self.q_moi_dia_chi_camera.text()) < 10:
                app_warning_function.check_path_for_ip_camera()
            else:
                new_camera_address = self.q_moi_dia_chi_camera.text()
                new_camera_path = new_camera_address

            # for webcam ID
        elif self.q_moi_webcam.isChecked():
            if len(self.q_moi_dia_chi_camera.text()) > 10:
                app_warning_function.check_path_for_webcam()
            else:
                new_camera_address = self.q_moi_dia_chi_camera.text()
                new_camera_path = new_camera_address

        if len(new_camera_path) != 0:
            draw_region_flag_new = True
            draw_region(new_camera_path)

    def camera_management_draw_counting_new(self):
        global draw_count_flag_new

        draw_count_flag_new = True
        draw_counting()

    def video(self):
        global config_file, count, width, height
        self.g_tong_khong_kt.display(count)
        if not os.path.exists(config_file):
            app_warning_function.camera_config_flie()
        else:
            self.g_hien_thi.resize(width, height)
            th.changePixmap.connect(self.setImage)
            th.start()

    def setImage(self, image):
        self.g_hien_thi.setPixmap(QtGui.QPixmap.fromImage(image))

    # FOR MAIN VIEW

    # def input_camera_source_path_and_name(self):
    #     global config_file
    #     get_path = None
    #     camera_name = None
    #     data_path = self.source_path.text()
    #     camera_name_source = self.source_input_camera_name.text()
    #
    #     # check for IP camera path
    #     if len(camera_name_source) == 0:
    #         app_warning_function.check_camera_name()
    #     if self.radioButton_ip_camera.isChecked():
    #         if len(data_path) < 10:
    #             app_warning_function.check_path_for_ip_camera()
    #         else:
    #             get_path = data_path
    #             camera_name = camera_name_source
    #
    #     # check for webcam ID
    #     elif self.radioButton_webcam.isChecked():
    #         if len(data_path) > 10:
    #             app_warning_function.check_path_for_webcam()
    #         else:
    #             get_path = data_path
    #             camera_name = camera_name_source
    #
    #     if os.path.exists(config_file):
    #         # ----- update json file
    #         # load yaml config file
    #         yaml.warnings({'YAMLLoadWarning': False})
    #         with open(config_file, 'r') as fs:
    #             config = yaml.load(fs)
    #         cam_config = config["input"]["cam_config"]
    #
    #         # open json file
    #         with open(cam_config) as json_file:
    #             json_data = json.load(json_file)
    #         json_file.close()
    #
    #         # update infor in json file
    #         json_data["data"][0]["url"] = get_path
    #         json_data["data"][0]["name"] = camera_name
    #
    #         # write json file
    #         with open(json_file.name, "w") as outfile:
    #             json.dump(json_data, outfile)
    #         outfile.close()
    #         # -----

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GreenGlobal_GreenLabs_FaceMaskRecognitionAPP"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Thông tin ứng dụng"))
        self.label_110.setText(_translate("MainWindow", "Phiên bản:"))
        self.label_80.setText(_translate("MainWindow", "Tên ứng dụng:"))
        self.label_111.setText(_translate("MainWindow", "Face-Mask Recognition APP"))
        self.label_119.setText(_translate("MainWindow", "Cấp phép:"))
        self.label_89.setText(_translate("MainWindow", "Đơn vị phát hành:"))
        self.label_117.setText(_translate("MainWindow", "GreenLabs"))
        self.label_90.setText(_translate("MainWindow", "Công ty:"))
        self.label_118.setText(_translate("MainWindow", "Công ty Cổ Phần Công Nghệ Thông Tin Toàn Cầu Xanh"))
        self.label_91.setText(_translate("MainWindow", "Địa chỉ:"))
        self.label_121.setText(_translate("MainWindow", "31 Đường Trần Phú, Quận Hải Châu I, TP Đà Nẵng"))
        self.label_122.setText(_translate("MainWindow", "02363 833 666"))
        self.label_92.setText(_translate("MainWindow", "Điện thoại:"))
        self.label_93.setText(_translate("MainWindow", "Email:"))
        self.label_123.setText(_translate("MainWindow", "contact@greenglobal.vn"))
        self.t_tt_phien_ban.setText(_translate("MainWindow", "1.0"))
        self.t_tt_cap_phep.setText(_translate("MainWindow", "abcxyz"))
        self.label_84.setText(_translate("MainWindow", "Cấp phép"))
        self.label_85.setText(_translate("MainWindow", "Tên thiết bị"))
        self.label_116.setText(_translate("MainWindow", "Server đồng bộ DL"))
        self.label_120.setText(_translate("MainWindow", "Mã định danh"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_7), _translate("MainWindow", "Thiết đặt"))
        self.label_126.setText(_translate("MainWindow", "Xác nhận mật khẩu mới"))
        self.label_86.setText(_translate("MainWindow", "Mật khẩu mới"))
        self.label_87.setText(_translate("MainWindow", "Mật khẩu cũ"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_8), _translate("MainWindow", "Đổi mật khẩu"))
        self.report_tab.setTabText(self.report_tab.indexOf(self.tab_2),
                                   _translate("MainWindow", "Thông tin và Thiết đặt"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Trạng thái hoạt động"))
        item = self.g_tt_hoat_dong_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tên camera"))
        item = self.g_tt_hoat_dong_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Trạng thái"))
        __sortingEnabled = self.g_tt_hoat_dong_table.isSortingEnabled()
        self.g_tt_hoat_dong_table.setSortingEnabled(False)
        self.g_tt_hoat_dong_table.setSortingEnabled(__sortingEnabled)
        self.groupBox_15.setTitle(_translate("MainWindow", "Kết quả chi tiết"))
        item = self.g_ket_qua_chi_tiet_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tên camera"))
        item = self.g_ket_qua_chi_tiet_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Số lượng(SL) người vào"))
        item = self.g_ket_qua_chi_tiet_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "SL người có khẩu trang(KT)"))
        item = self.g_ket_qua_chi_tiet_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "SL người không có KT"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Màn hình giám sát"))
        self.g_hien_thi.setText(_translate("MainWindow", "Display"))
        self.groupBox_7.setTitle(_translate("MainWindow", "Kết quả"))
        self.label_106.setText(_translate("MainWindow", "Tổng SL người vào"))
        self.label_105.setText(_translate("MainWindow", "Tổng SL người không có KT"))
        self.label_109.setText(_translate("MainWindow", "Tổng SL người có KT"))
        self.groupBox_8.setTitle(_translate("MainWindow", "Thông tin khác"))
        self.g_date_time.setText(_translate("MainWindow", "none"))
        self.report_tab.setTabText(self.report_tab.indexOf(self.tab), _translate("MainWindow", "Giám sát"))
        self.groupBox_10.setTitle(_translate("MainWindow", "Thông tin camera"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tên camera"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Địa chỉ"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Chế độ hoạt động"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Thời gian hoạt động"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Chế độ cảnh báo"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Kiểu cảnh báo đèn"))
        item = self.q_thong_tin_camera_table.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Kiểu cảnh báo âm"))
        __sortingEnabled = self.q_thong_tin_camera_table.isSortingEnabled()
        self.q_thong_tin_camera_table.setSortingEnabled(False)
        self.q_thong_tin_camera_table.setSortingEnabled(__sortingEnabled)
        self.q_moi_webcam.setText(_translate("MainWindow", "Webcam"))
        self.label_98.setText(_translate("MainWindow", "Vùng quan sát"))
        self.q_moi_combobox_den.setItemText(0, _translate("MainWindow", "nhap nhay"))
        self.q_moi_combobox_den.setItemText(1, _translate("MainWindow", "mac dinh"))
        self.q_moi_combobox_den.setItemText(2, _translate("MainWindow", "nhay nhanh"))
        self.label_94.setText(_translate("MainWindow", "Đến"))
        self.label_95.setText(_translate("MainWindow", "Chế độ"))
        self.q_moi_combobox_am_thanh.setItemText(0, _translate("MainWindow", "coi canh sat"))
        self.q_moi_combobox_am_thanh.setItemText(1, _translate("MainWindow", "tieng pip"))
        self.q_moi_combobox_am_thanh.setItemText(2, _translate("MainWindow", "am canh bao"))
        self.q_moi_den.setText(_translate("MainWindow", "Đèn báo"))
        self.label_77.setText(_translate("MainWindow", "Địa chỉ camera"))
        self.q_moi_am_thanh.setText(_translate("MainWindow", "Âm thanh"))
        self.q_moi_ipcamera.setText(_translate("MainWindow", "IP Camera"))
        self.label_76.setText(_translate("MainWindow", "Đặt thời gian"))
        self.q_moi_che_do.setText(_translate("MainWindow", "Bật"))
        self.label_97.setText(_translate("MainWindow", "Vạch kiểm đếm"))
        self.label_75.setText(_translate("MainWindow", "Tên camera"))
        self.q_moi_ca_hai.setText(_translate("MainWindow", "Cả hai"))
        self.label_78.setText(_translate("MainWindow", "Từ"))
        self.label_96.setText(_translate("MainWindow", "Chế độ cảnh báo"))
        self.label_79.setText(_translate("MainWindow", "Camera ID"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "Tạo mới camera"))
        self.label_99.setText(_translate("MainWindow", "Đến"))
        self.q_chinh_ca_hai.setText(_translate("MainWindow", "Cả hai"))
        self.label_100.setText(_translate("MainWindow", "Chế độ"))
        self.q_chinh_che_do.setText(_translate("MainWindow", "Bật"))
        self.label_102.setText(_translate("MainWindow", "Chế độ cảnh báo"))
        self.label_81.setText(_translate("MainWindow", "Tên camera"))
        self.q_chinh_den.setText(_translate("MainWindow", "Đèn báo"))
        self.label_82.setText(_translate("MainWindow", "Đặt thời gian"))
        self.q_chinh_combobox_am_thanh.setItemText(0, _translate("MainWindow", "Còi cảnh sát"))
        self.q_chinh_combobox_am_thanh.setItemText(1, _translate("MainWindow", "Tiếng pip"))
        self.q_chinh_combobox_am_thanh.setItemText(2, _translate("MainWindow", "Âm cảm báo"))
        self.label_103.setText(_translate("MainWindow", "Địa chỉ camera"))
        self.label_104.setText(_translate("MainWindow", "Vạch kiểm đếm"))
        self.q_chinh_am_thanh.setText(_translate("MainWindow", "Âm thanh"))
        self.label_107.setText(_translate("MainWindow", "Vùng quan sát"))
        self.label_108.setText(_translate("MainWindow", "Từ"))
        self.q_chinh_combobox_den.setItemText(0, _translate("MainWindow", "Nhấp nháy"))
        self.q_chinh_combobox_den.setItemText(1, _translate("MainWindow", "Mặc định"))
        self.q_chinh_combobox_den.setItemText(2, _translate("MainWindow", "Nháy nhanh"))
        self.label_83.setText(_translate("MainWindow", "Tên mới"))
        self.label_88.setText(_translate("MainWindow", "Camera ID"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("MainWindow", "Chỉnh sửa camera"))
        self.report_tab.setTabText(self.report_tab.indexOf(self.tab_4), _translate("MainWindow", "Quản lí camera"))
        self.display_ploting_1.setText(_translate("MainWindow", "Biểu đồ 1"))
        self.groupBox_plot1.setTitle(_translate("MainWindow", " Thông số 1"))
        self.b_t1_combobox_kieu_thong_ke.setItemText(0, _translate("MainWindow", "Thống kê theo Ngày"))
        self.b_t1_combobox_kieu_thong_ke.setItemText(1, _translate("MainWindow", "Thống kê theo Tháng"))
        self.b_t1_combobox_kieu_thong_ke.setItemText(2, _translate("MainWindow", "Thống kê theo Năm"))
        item = self.b_t1_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tên camera"))
        item = self.b_t1_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "SL người vào"))
        item = self.b_t1_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "SL người có KT"))
        item = self.b_t1_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "SL người không có KT"))
        item = self.b_t1_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Phút"))
        item = self.b_t1_table.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Giờ"))
        item = self.b_t1_table.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Ngày"))
        item = self.b_t1_table.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Tháng"))
        item = self.b_t1_table.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Năm"))
        self.display_ploting_2.setText(_translate("MainWindow", "Biểu đồ 2"))
        self.groupBox_plot1_2.setTitle(_translate("MainWindow", " Thông số 2"))
        self.b_t2_combobox_kieu_thong_ke.setItemText(0, _translate("MainWindow", "Thống kê theo Ngày"))
        self.b_t2_combobox_kieu_thong_ke.setItemText(1, _translate("MainWindow", "Thống kê theo Tháng"))
        self.b_t2_combobox_kieu_thong_ke.setItemText(2, _translate("MainWindow", "Thống kê theo Năm"))
        item = self.b_t2_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Tên"))
        item = self.b_t2_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "SL người vào"))
        item = self.b_t2_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "SL người có KT"))
        item = self.b_t2_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "SL người không có KT"))
        item = self.b_t2_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Phút"))
        item = self.b_t2_table.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Giờ"))
        item = self.b_t2_table.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Ngày"))
        item = self.b_t2_table.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Tháng"))
        item = self.b_t2_table.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Năm"))
        self.report_tab.setTabText(self.report_tab.indexOf(self.tab_3), _translate("MainWindow", "Báo cáo và Thống kê"))
        self.menuHome.setTitle(_translate("MainWindow", "Tùy chọn"))
        self.actionLock.setText(_translate("MainWindow", "Khóa"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.exit.setText(_translate("MainWindow", "Thoát"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        global w_height, w_width
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(w_width, w_height)
        self.settings = QtCore.QSettings()
        # restore(self.settings)
        self.display_ploting_1.clear()
        self.display_ploting_2.clear()

    def closeEvent(self, event):
        save(self.settings)
        super().closeEvent(event)


if __name__ == '__main__':
    print("(***)--- Running APP threading")
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setOrganizationName("Eyllanesc")
    QtCore.QCoreApplication.setOrganizationDomain("eyllanesc.com")
    QtCore.QCoreApplication.setApplicationName("MyApp")
    w = MainWindow()
    w.show()
    app.exec_()
