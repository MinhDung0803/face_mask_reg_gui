from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import matplotlib.pyplot as plt
import time
import os
import cv2
import pandas as pd
import threading
import queue
import json
import yaml
import pyglet
from pydub import AudioSegment
from pydub.playback import play
import datetime

import face_mask_threading
from mask_utils import global_variable_define as gd
import play_alarm_audio_threading

import warnings
warnings.filterwarnings("ignore")


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
light_alarm = 0
sound_alarm = 0
both_alarm = 1
draw_region_points = []
draw_region_points_no_scale = []
extra_pixels = 10  # for default points
scale = 3
# default_region_points = [(0 + extra_pixels, 0 + extra_pixels),(width - extra_pixels, 0 + extra_pixels),
#                          (width - extra_pixels, height - extra_pixels),(0 + extra_pixels, height - extra_pixels)]
draw_region_flag = False
draw_counting_points = []
default_counting_points = [[(0, int(height / 2)), (width, int(height / 2))]]
draw_count_flag = False
trigger_stop = 0

# config_file
config_file = "./configs/all_cameras.yml"


def create_default_region(w_in, h_in, extra_pixels_in):
    result = [0 + extra_pixels_in, 0 + extra_pixels_in, w_in - extra_pixels_in, 0 + extra_pixels_in, w_in - extra_pixels_in,
              h_in - extra_pixels_in, 0 + extra_pixels_in, h_in - extra_pixels_in]
    return result


def create_default_counting_line(w_in, h_in, extra_pixels_in):
    result = [0+extra_pixels_in, int(h_in / 2), w_in-extra_pixels_in, int(h_in / 2)]
    return result

def create_direction_point(w_in, h_in):
    result = [int(w_in/2), int(h_in/2)+50]
    return result


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent, display_no_face_mask_counting):
        QtCore.QThread.__init__(self, parent)
        self._go = None
        self.display_no_face_mask_counting = display_no_face_mask_counting

    def run(self):
        global count, \
            height, \
            width, \
            config_file, \
            trigger_stop, \
            count, \
            light_alarm, \
            sound_alarm, \
            both_alarm, \
            name

        # connect to sql database
        conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
        # c = conn.cursor()

        # run mode variable
        self._go = True

        # get infor from config_file
        yaml.warnings({'YAMLLoadWarning': False})
        with open(config_file, 'r') as fs:
            config = yaml.load(fs)
            # config = yaml.load(fs, Loader=yaml.FullLoader)

        cam_config = config["input"]["cam_config"]

        with open(cam_config) as json_file:
            json_data = json.load(json_file)
        json_file.close()

        cam_infor_list = json_data["data"]

        input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list, \
        tracking_regions_list = face_mask_threading.parser_cam_infor(cam_infor_list)

        num_cam = len(input_video_list)
        video_infor_list = []
        max_fps = 0
        for cam_index in range(num_cam):
            width1, height1, fps_video1 = face_mask_threading.get_info_video(input_video_list[cam_index])
            video_infor_list.append([width1, height1, fps_video1])
            if (max_fps < fps_video1):
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
            if path is not None:
                if trigger_stop == 1:
                    forward_message.put("stop")
                    trigger_stop = 0
                    time.sleep(1)
                    self.stop_thread()

                # get information form the queue
                for cam_index in range(num_cam):
                    face_mask_output_data = face_mask_buffer[cam_index]
                    if face_mask_output_data.empty() == False:
                        data = face_mask_output_data.get()

                        ind = data[0]
                        frame_ori = data[1]
                        list_count = data[2]

                        if ind != -1:

                            # update, active alarm option
                            event_count = list_count[0]["Person"]
                            self.display_no_face_mask_counting.setText(str(event_count))
                            if event_count < count:
                                count = event_count

                                # update display_no_face_mask_counting
                                self.display_no_face_mask_counting.setText(str(count))

                                # insert data into database when detect new no-face-mask person
                                data = datetime.datetime.now()
                                data_form = {"Camera_name": name,
                                             "Minute": data.minute,
                                             "Hour": data.hour,
                                             "Day": data.day,
                                             "Month": data.month,
                                             "Year": data.year}
                                data_form_add = pd.DataFrame.from_dict([data_form])
                                data_form_add.to_sql('DATA', conn, if_exists='append', index=False)
                                conn.commit()

                                # active alarm
                                if sound_alarm == 1 or both_alarm == 1:
                                    sound_file = "./sound_alarm/police.mp3"
                                    play_alarm_audio_threading.play_audio_by_threading(sound_file)
                                    print("sound")
                                elif light_alarm == 1 or both_alarm ==1:
                                    print("light")
                                else:
                                    sound_file = "./sound_alarm/police.mp3"
                                    play_alarm_audio_threading.play_audio_by_threading(sound_file)
                                    print("sound and light")

                            result_frame = cv2.resize(frame_ori, (width, height))
                            rgbImage = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
                            h_result_frame, w_result_frame, ch = rgbImage.shape
                            bytesPerLine = ch * w_result_frame
                            convertToQtFormat = QtGui.QImage(rgbImage.data, w_result_frame, h_result_frame,
                                                             bytesPerLine, QtGui.QImage.Format_RGB888)
                            p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                            self.changePixmap.emit(p)

                    else:
                        time.sleep(no_job_sleep_time)

            else:
                check_input_frame()
                # time.sleep(0.5)

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
        # time.sleep(1)
        # exit()


def close_window():
    global trigger_stop
    trigger_stop = 1
    # th.stop_thread()


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


def shape_selection_for_region(event, x, y, flags, param):
    global draw_region_points, scale, draw_region_points_no_scale
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = (x, y)
        # with scale
        draw_region_points.append(x*scale)
        draw_region_points.append(y*scale)
        # with no scale
        draw_region_points_no_scale.append(x)
        draw_region_points_no_scale.append(y)

        cv2.circle(image, (ref_point[0], ref_point[1]), 4, (0, 0, 255), -2)
        cv2.imshow("Draw Tracking Region", image)


def shape_selection_for_counting(event, x, y, flags, param):
    global ref_point_c, draw_counting_points, scale
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point_c = (x, y)
        # with scale
        draw_counting_points.append(x * scale)
        draw_counting_points.append(y * scale)

        cv2.circle(image, (ref_point_c[0], ref_point_c[1]), 4, (0, 255, 0), -2)
        cv2.imshow("Draw Counting Region", image)


def draw_region():
    global path, width, height, draw_region_points, image, draw_region_flag, scale, draw_region_points_no_scale
    draw_region_flag = True
    # read and write original image
    cap = cv2.VideoCapture(path)
    w = int(cap.get(3))
    h = int(cap.get(4))
    ret, frame = cap.read()
    frame = cv2.resize(frame, (int(w/scale), int(h/scale)))
    if ret:
        cv2.imwrite("./draw/original_image.jpg", frame)
        # draw on original image and write when done
        image = cv2.imread("./draw/original_image.jpg")
        clone = image.copy()
        cv2.namedWindow("Draw Tracking Region")
        cv2.setMouseCallback("Draw Tracking Region", shape_selection_for_region)
        while True:
            cv2.imshow("Draw Tracking Region", image)
            key = cv2.waitKey(1)
            if key == 32:
                image = clone.copy()
                draw_region_points = []
            elif key == 13:
                break
        for i in range(0, len(draw_region_points_no_scale), 2):
            if i + 3 > len(draw_region_points_no_scale):
                cv2.line(image, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                         (draw_region_points_no_scale[0], draw_region_points_no_scale[1]), (0, 255, 255), 1)
            else:
                cv2.line(image, (draw_region_points_no_scale[i], draw_region_points_no_scale[i + 1]),
                         (draw_region_points_no_scale[i + 2], draw_region_points_no_scale[i + 3]), (0, 255, 255), 1)

    cv2.imwrite('./draw/draw_region_image.jpg', image)
    cap.release()
    cv2.destroyAllWindows()


def draw_counting():
    global path, width, height, draw_counting_points, image, draw_count_flag
    draw_count_flag = True
    image = cv2.imread("./draw/draw_region_image.jpg")
    clone = image.copy()
    cv2.namedWindow("Draw Counting Region")
    cv2.setMouseCallback("Draw Counting Region", shape_selection_for_counting)
    while True:
        cv2.imshow("Draw Counting Region", image)
        key = cv2.waitKey(1)
        if key == 32:
            image = clone.copy()
            draw_counting_points = []
        elif key == 13:
            break
    cv2.imwrite('./draw/draw_counting_image.jpg', image)
    cv2.destroyAllWindows()


def plotting(name,
             color,
             camera_name_input,
             day_input,
             month_input,
             year_input,
             check_day,
             check_month,
             check_year):
    # connect to sql database
    conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
    c = conn.cursor()

    if check_day == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input} " \
                f"and Day = {day_input}" \
                f"and Month = {month_input}"
        c.execute(query)
        return_data = c.fetchall()
        x = ["%d" % i for i in range(1, 25, 1)]
        y = [0 for i in range(1, 25, 1)]
        for elem in return_data:
            for i in range(len(y)):
                if elem[2] - 1 == i:
                    y[i] += 1
        plt.figure(figsize=(10, 5))
        plt.bar(x, y)
        plt.title("Bar chart describes Number of No Face-Mask in "
                  + str(year_input) + "-"
                  + str(month_input) + "-"
                  + str(day_input) + "("
                  + str(len(return_data)) + ")")
        plt.xlabel('Hour')
        plt.ylabel('Number of No Face-Mask')
        for index, value in enumerate(y):
            if value != 0:
                plt.text(index-0.2, value, str(value), color=color, size='xx-large')
        if os.path.exists("./figure/" + name):
            os.remove("./figure/" + name)
        plt.savefig("./figure/" + name)
        plt.close()
        time.sleep(0.5)
    elif check_month == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input} and Month = {month_input}"
        c.execute(query)
        return_data = c.fetchall()
        month_30 = [2, 4, 6, 9, 11]
        if month_input in month_30:
            x = ["%d" % i for i in range(1, 31, 1)]
            y = [0 for i in range(1, 31, 1)]
        else:
            x = ["%d" % i for i in range(1, 32, 1)]
            y = [0 for i in range(1, 32, 1)]
        for elem in return_data:
            for i in range(len(y)):
                if elem[3] - 1 == i:
                    y[i] += 1
        plt.figure(figsize=(10, 5))
        plt.bar(x, y)
        plt.title("Bar chart describes Number of No Face-Mask in "
                  + str(year_input) + "-"
                  + str(month_input) + "("
                  + str(len(return_data)) + ")")
        plt.xlabel('Day')
        plt.ylabel('Number of No Face-Mask')
        for index, value in enumerate(y):
            if value != 0:
                plt.text(index - 0.3, value, str(value), color=color, size='xx-large')
        if os.path.exists("./figure/" + name):
            os.remove("./figure/" + name)
        plt.savefig("./figure/" + name)
        plt.close()
        time.sleep(0.5)
    elif check_year == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input}"
        c.execute(query)
        return_data = c.fetchall()
        x = ["M%d" % i for i in range(1, 13, 1)]
        y = [0 for i in range(1, 13, 1)]
        for elem in return_data:
            for i in range(len(y)):
                if elem[4] - 1 == i:
                    y[i] += 1
        plt.figure(figsize=(10, 5))
        plt.bar(x, y)
        plt.title("Bar chart describes Number of No Face-Mask in "
                  + str(year_input) + "("
                  + str(len(return_data)) + ")")
        plt.xlabel('Month')
        plt.ylabel('Number of No Face-Mask')
        for index, value in enumerate(y):
            if value != 0:
                plt.text(index-0.2, value, str(value), color=color, size='xx-large')
        if os.path.exists("./figure/" + name):
            os.remove("./figure/" + name)
        plt.savefig("./figure/" + name)
        plt.close()
        time.sleep(0.5)
    # commit database
    conn.commit()


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


def export_data(camera_name_input,
               day_input,
               month_input,
               year_input,
               check_day,
               check_month,
               check_year):
    # connect to sql database
    conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
    c = conn.cursor()

    if check_day == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input} " \
                f"and Day = {day_input} " \
                f"and Month = {month_input} "
        c.execute(query)
        return_data = c.fetchall()
        df = pd.DataFrame(return_data, columns=["Camera name", "Minute", "Hour", "Day", "Month", "Year"])
        name = str(camera_name_input)+"-"\
               +str(day_input)+"."\
               +str(month_input)+"."\
               +str(year_input)+"-"\
               +"NoFaceMaskData.csv"
        df.to_csv('./export_data/' + name)
    elif check_month == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input} " \
                f"and Month = {month_input} "
        c.execute(query)
        return_data = c.fetchall()
        df = pd.DataFrame(return_data, columns=["Camera name", "Minute", "Hour", "Day", "Month", "Year"])
        name = str(camera_name_input) + "-" \
               + str(month_input) + "." \
               + str(year_input) + "-" \
               + "NoFaceMaskData.csv"
        df.to_csv('./export_data/' + name)
    elif check_year == 1:
        query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
                f"and Year = {year_input} "
        c.execute(query)
        return_data = c.fetchall()
        df = pd.DataFrame(return_data, columns=["Camera name", "Minute", "Hour", "Day", "Month", "Year"])
        name = str(camera_name_input) + "-" \
               + str(year_input) + "-" \
               + "NoFaceMaskData.csv"
        df.to_csv('./export_data/' + name)
    # commit data base
    conn.commit()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        ### design
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
        font = QtGui.QFont()
        font.setBold(True)
        self.apply = QtWidgets.QPushButton(self.groupBox)
        self.apply.setFont(font)
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
        self.radioButton_light_and_sound_option.setChecked(True)

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
        self.pushButton_set_time.setFont(font)
        self.pushButton_set_time.setGeometry(QtCore.QRect(70, 60, 89, 25))
        self.pushButton_set_time.setObjectName("pushButton_set_time")

        self.groupBox_5 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_5.setGeometry(QtCore.QRect(660, 280, 221, 151))
        self.groupBox_5.setObjectName("groupBox_5")
        self.display_no_face_mask_counting = QtWidgets.QLabel(self.groupBox_5)
        self.display_no_face_mask_counting.setGeometry(QtCore.QRect(20, 30, 181, 101))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(25)
        self.display_no_face_mask_counting.setFont(font)
        self.display_no_face_mask_counting.setFrameShape(QtWidgets.QFrame.Box)
        self.display_no_face_mask_counting.setLineWidth(5)
        self.display_no_face_mask_counting.setTextFormat(QtCore.Qt.AutoText)
        self.display_no_face_mask_counting.setScaledContents(False)
        self.display_no_face_mask_counting.setAlignment(QtCore.Qt.AlignCenter)
        self.display_no_face_mask_counting.setIndent(-1)
        self.display_no_face_mask_counting.setObjectName("display_no_face_mask_counting")

        font = QtGui.QFont()
        font.setBold(True)
        self.start = QtWidgets.QPushButton(self.tab)
        self.start.setFont(font)
        self.start.setGeometry(QtCore.QRect(670, 450, 81, 71))
        self.start.setObjectName("start")

        self.draw_region = QtWidgets.QPushButton(self.tab)
        self.draw_region.setFont(font)
        self.draw_region.setGeometry(QtCore.QRect(760, 450, 111, 71))
        self.draw_region.setObjectName("draw_region")

        self.stop = QtWidgets.QPushButton(self.tab)
        self.stop.setFont(font)
        self.stop.setGeometry(QtCore.QRect(670, 540, 81, 71))
        self.stop.setObjectName("stop")

        self.draw_count = QtWidgets.QPushButton(self.tab)
        self.draw_count.setFont(font)
        self.draw_count.setGeometry(QtCore.QRect(760, 540, 111, 71))
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
        self.radioButton_year_1.setChecked(True)
        self.plot1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.plot1.setFont(font)
        self.plot1.setGeometry(QtCore.QRect(10, 200, 81, 41))
        self.plot1.setObjectName("plot1")

        self.export_1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.export_1.setFont(font)
        self.export_1.setGeometry(QtCore.QRect(110, 200, 81, 41))
        self.export_1.setObjectName("export_1")

        self.label_2 = QtWidgets.QLabel(self.groupBox_plot1)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_2.setObjectName("label_2")
        self.input_camera_name_1 = QtWidgets.QLineEdit(self.groupBox_plot1)
        self.input_camera_name_1.setGeometry(QtCore.QRect(10, 60, 131, 25))
        self.input_camera_name_1.setObjectName("input_camera_name_1")
        self.button_camera_name_1 = QtWidgets.QPushButton(self.groupBox_plot1)
        self.button_camera_name_1.setFont(font)
        self.button_camera_name_1.setGeometry(QtCore.QRect(150, 54, 41, 31))
        self.button_camera_name_1.setObjectName("button_camera_name_1")

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
        self.radioButton_year_2.setChecked(True)
        self.plot2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.plot2.setFont(font)
        self.plot2.setGeometry(QtCore.QRect(10, 200, 81, 41))
        self.plot2.setObjectName("plot2")

        self.export_2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.export_2.setFont(font)
        self.export_2.setGeometry(QtCore.QRect(110, 200, 81, 41))
        self.export_2.setObjectName("export_2")

        self.label_3 = QtWidgets.QLabel(self.groupBox_3_plot2)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 121, 17))
        self.label_3.setObjectName("label_3")
        self.input_camera_name_2 = QtWidgets.QLineEdit(self.groupBox_3_plot2)
        self.input_camera_name_2.setGeometry(QtCore.QRect(10, 60, 131, 25))
        self.input_camera_name_2.setObjectName("input_camera_name_2")
        self.button_camera_name_2 = QtWidgets.QPushButton(self.groupBox_3_plot2)
        self.button_camera_name_2.setFont(font)
        self.button_camera_name_2.setGeometry(QtCore.QRect(150, 54, 41, 31))
        self.button_camera_name_2.setObjectName("button_camera_name_2")

        self.display_ploting_2 = QtWidgets.QLabel(self.tab_2)
        self.display_ploting_2.setGeometry(QtCore.QRect(10, 320, 661, 291))
        self.display_ploting_2.setFrameShape(QtWidgets.QFrame.Box)
        self.display_ploting_2.setAlignment(QtCore.Qt.AlignCenter)
        self.display_ploting_2.setObjectName("display_ploting_2")
        self.tabWidget.addTab(self.tab_2, "")

        ######
        ## events
        # get camera name and plot - 1
        self.plot1.clicked.connect(self.display_plotting_figure_1)
        self.button_camera_name_1.clicked.connect(self.get_camera_name_1)
        # get camera name and plot - 2
        self.plot2.clicked.connect(self.display_plotting_figure_2)
        self.button_camera_name_2.clicked.connect(self.get_camera_name_2)
        # alarm option
        self.radioButton_light_option.clicked.connect(self.check_alarm_option)
        self.radioButton_sound_option.clicked.connect(self.check_alarm_option)
        self.radioButton_light_and_sound_option.clicked.connect(self.check_alarm_option)
        # get camera source path
        self.apply.clicked.connect(self.get_path)
        # start video
        self.start.clicked.connect(self.video)
        # stop video
        self.stop.clicked.connect(close_window)
        # draw region
        self.draw_region.clicked.connect(self.region)
        # draw counting line
        self.draw_count.clicked.connect(self.counting)
        # export data - 2
        self.export_2.clicked.connect(self.call_export_data_2)
        # export data - 1
        self.export_1.clicked.connect(self.call_export_data_1)
        # call display video
        global th
        th = Thread(MainWindow, self.display_no_face_mask_counting)
        #####

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

    def region(self):
        global path
        if path is None or len(path) == 0:
            camera_source_alarm()
        else:
            draw_region()

    def counting(self):
        global path
        if path is None or len(path) == 0:
            camera_source_alarm()
        else:
            draw_counting()

    def check_alarm_option(self):
        global light_alarm, sound_alarm, both_alarm
        if self.radioButton_light_option.isChecked():
            light_alarm = 1
            sound_alarm = 0
            both_alarm = 0
        elif self.radioButton_sound_option.isChecked():
            light_alarm = 0
            sound_alarm = 1
            both_alarm = 0
        elif self.radioButton_light_and_sound_option.isChecked():
            light_alarm = 0
            sound_alarm = 0
            both_alarm = 1
        # check alarm option status
        # self.display_no_face_mask_counting.setText(str(light_alarm)+" "+
        #                                            str(sound_alarm)+" "+
        #                                            str(both_alarm))
        return light_alarm, sound_alarm, both_alarm

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
        global path, \
            name, \
            config_file, \
            width, \
            height,\
            draw_region_points, \
            draw_region_flag, \
            default_counting_points, \
            draw_count_flag, \
            draw_counting_points, \
            extra_pixels

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
                path = data_path

                # ----- get width, height of input
                cap = cv2.VideoCapture(path)
                w = int(cap.get(3))
                h = int(cap.get(4))
                cap.release()
                # -----

                # ----- get tracking region
                if draw_region_flag:
                    final_draw_region = draw_region_points
                else:
                    final_draw_region = create_default_region(w, h, extra_pixels)
                # print("final_draw_region: ", final_draw_region)

                # ----- get counting line
                if draw_count_flag:
                    final_counting_line = draw_counting_points
                    final_direction_point = [int(final_counting_line[2]/2), final_counting_line[1]+100]
                else:
                    final_counting_line = create_default_counting_line(w, h, extra_pixels)
                    final_direction_point = create_direction_point(w, h)

                # ----- update json file
                # load yaml config file
                yaml.warnings({'YAMLLoadWarning': False})
                with open(config_file, 'r') as fs:
                    config = yaml.load(fs)
                cam_config = config["input"]["cam_config"]

                # open json file
                with open(cam_config) as json_file:
                    json_data = json.load(json_file)
                json_file.close()

                # update infor in json file
                json_data["data"][0]["url"] = path
                json_data["data"][0]["tracking_regions"][0]["points"] = final_draw_region
                json_data["data"][0]["tracking_regions"][0]["trap_lines"]["unlimited_counts"][0]["points"] = \
                    final_counting_line
                json_data["data"][0]["tracking_regions"][0]["trap_lines"]["unlimited_counts"][0]["direction_point"] = \
                    final_direction_point
                json_data["data"][0]["tracking_regions"][0]["id_show_point"] = final_direction_point


                # write json file
                with open(json_file.name, "w") as outfile:
                    json.dump(json_data, outfile)
                # -----

        # check for webcam ID
        if self.radioButton_webcam.isChecked():
            if len(data_path) > 10:
                check_path_for_webcam()
            else:
                path = data_path
        return path

    def get_camera_name_1(self):
        global camera_name_input_1
        camera_name_input_1 = self.input_camera_name_1.text()

    def display_plotting_figure_1(self):
        global camera_name_input_1, conn, c
        if len(camera_name_input_1) == 0:
            check_camera_name_plotting()
        else:
            check_day_1 = 0
            check_month_1 = 0
            check_year_1 = 1
            name1 = "figure1.png"
            color1 = "red"

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

            plotting(name1,
                     color1,
                     camera_name_input_1,
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
                pixmap = QtGui.QPixmap("./figure/" + name1)
                # os.remove('./figure/figure1.png')
                self.display_ploting_1.setPixmap(pixmap)

    def get_camera_name_2(self):
        global camera_name_input_2
        camera_name_input_2 = self.input_camera_name_2.text()

    def display_plotting_figure_2(self):
        global camera_name_input_2, conn, c
        if len(camera_name_input_2) == 0:
            check_camera_name_plotting()
        else:
            check_day_2 = 0
            check_month_2 = 0
            check_year_2 = 1
            name2 = "figure2.png"
            color2 = "purple"

            day_input_2 = self.input_day_2.text()
            month_input_2 = self.input_month_2.text()
            year_input_2 = self.input_year_2.text()
            if self.radioButton_day_2.isChecked():
                check_day_2 = 1
                check_month_2 = 0
                check_year_2 = 0
            elif self.radioButton_month_2.isChecked():
                check_day_2 = 0
                check_month_2 = 1
                check_year_2 = 0
            elif self.radioButton_year_1.isChecked():
                check_day_2 = 0
                check_month_2 = 0
                check_year_2 = 1

            plotting(name2,
                     color2,
                     camera_name_input_2,
                     day_input_2,
                     month_input_2,
                     year_input_2,
                     check_day_2,
                     check_month_2,
                     check_year_2)

            self.display_ploting_2.clear()
            if len(camera_name_input_2) == 0:
                print("None")
            else:
                self.display_ploting_2.setScaledContents(True)
                pixmap = QtGui.QPixmap("./figure/" + name2)
                # os.remove('./figure/figure2.png')
                self.display_ploting_2.setPixmap(pixmap)

    def call_export_data_1(self):
        global camera_name_input_1
        if len(camera_name_input_1) == 0:
            check_camera_name_plotting()
        else:
            check_day_1 = 0
            check_month_1 = 0
            check_year_1 = 1

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

            export_data(camera_name_input_1,
                        day_input_1,
                        month_input_1,
                        year_input_1,
                        check_day_1,
                        check_month_1,
                        check_year_1)

    def call_export_data_2(self):
        global camera_name_input_2
        if len(camera_name_input_2) == 0:
            check_camera_name_plotting()
        else:
            check_day_2 = 0
            check_month_2 = 0
            check_year_2 = 1

            day_input_2 = self.input_day_2.text()
            month_input_2 = self.input_month_2.text()
            year_input_2 = self.input_year_2.text()
            if self.radioButton_day_2.isChecked():
                check_day_2 = 1
                check_month_2 = 0
                check_year_2 = 0
            elif self.radioButton_month_2.isChecked():
                check_day_2 = 0
                check_month_2 = 1
                check_year_2 = 0
            elif self.radioButton_year_1.isChecked():
                check_day_2 = 0
                check_month_2 = 0
                check_year_2 = 1

            export_data(camera_name_input_2,
                       day_input_2,
                       month_input_2,
                       year_input_2,
                       check_day_2,
                       check_month_2,
                       check_year_2)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GreenGlobal - GreenLabs - Face-Mask Recognition APP"))
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
        self.pushButton_set_time.setText(_translate("MainWindow", "SET TIME"))
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
        self.display_ploting_2.setText(_translate("MainWindow", "Ploting_2"))
        self.export_1.setText(_translate("MainWindow", "EXPORT 1"))
        self.export_2.setText(_translate("MainWindow", "EXPORT 2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menuMain.setTitle(_translate("MainWindow", "Main"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        global w_height, w_width
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(w_width, w_height)
        self.settings = QtCore.QSettings()
        restore(self.settings)

    def closeEvent(self, event):
        save(self.settings)
        super().closeEvent(event)


# def app():
#     print("(***)--- Running APP threading")
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     QtCore.QCoreApplication.setOrganizationName("Eyllanesc")
#     QtCore.QCoreApplication.setOrganizationDomain("eyllanesc.com")
#     QtCore.QCoreApplication.setApplicationName("MyApp")
#     w = MainWindow()
#     w.show()
#     app.exec_()
#     # sys.exit(app.exec_())
#
#
# def app_threading():
#     t = threading.Thread(target=app, args=[])
#     t.start()


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