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
global th, \
    path, \
    light_alarm, \
    sound_alarm, \
    both_alarm, \
    count, \
    height, \
    width, \
    draw_region_points, \
    default_region_points, \
    draw_region_flag, \
    draw_count_flag, \
    default_counting_points, \
    draw_counting_points

# variables
path = None
count = 0
height = 480
width = 640
draw_region_points = []
extra_pixels = 5  # for default points
default_region_points = [
    [(0+extra_pixels, 0+extra_pixels), (width-extra_pixels, 0+extra_pixels)],
    [(width-extra_pixels, 0+extra_pixels), (width-extra_pixels, height-extra_pixels)],
    [(width-extra_pixels, height-extra_pixels), (0+extra_pixels, height-extra_pixels)],
    [(0+extra_pixels, height-extra_pixels), (0+extra_pixels, 0+extra_pixels)]
]
draw_region_flag = False

draw_counting_points = []
default_counting_points = [[(0, int(height/2)), (width, int(height/2))]]
draw_count_flag = False


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self._go = None

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
            default_region_points, \
            default_counting_points, \
            draw_count_flag
        self._go = False
        path = None
        draw_region_flag = False
        draw_count_flag = False
        default_counting_points = []
        default_region_points = []


def close_window():
    th.stop_thread()
    time.sleep(1)


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


def mouse_callback(event, x, y, flags, param):
    global mouse_down
    global step

    mouse_down = False

    if event == cv2.EVENT_LBUTTONDOWN:
        if mouse_down is False:
            mouse_down = True
            step = 0
        else:
            step += 1

    elif event == cv2.EVENT_LBUTTONUP and mouse_down:
        mouse_down = False


def shape_selection_for_region(event, x, y, flags, param):
    global ref_point, draw_region_points
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:

        ref_point.append((x, y))
        draw_region_points.append(ref_point)
        cv2.line(image, ref_point[0], ref_point[1], (0, 0, 255), 2)
        cv2.imshow("Draw ROI", image)


def shape_selection_for_counting(event, x, y, flags, param):
    global ref_point_c, draw_counting_points
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point_c = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:

        ref_point_c.append((x, y))
        draw_counting_points.append(ref_point_c)
        cv2.line(image, ref_point_c[0], ref_point_c[1], (0, 255, 255), 2)
        cv2.imshow("Draw Counting Region", image)


def draw_region():
    global path, width, height, draw_region_points, image, draw_region_flag
    draw_region_flag = True
    # read and write original image
    cap = cv2.VideoCapture(path)
    ret, frame = cap.read()
    frame = cv2.resize(frame, (width, height))
    if ret:
        cv2.imwrite("original_image.jpg", frame)
        # draw on original image and write when done
        image = cv2.imread("original_image.jpg")
        clone = image.copy()
        cv2.namedWindow("Draw ROI")
        cv2.setMouseCallback("Draw ROI", shape_selection_for_region)
        while True:
            cv2.imshow("Draw ROI", image)
            key = cv2.waitKey(1)
            if key == 32:
                image = clone.copy()
                draw_region_points = []
            elif key == 13:
                break
    cv2.imwrite('draw_region_image.jpg', image)
    cap.release()
    cv2.destroyAllWindows()


def draw_counting():
    global path, width, height, draw_counting_points, image, draw_count_flag
    draw_count_flag = True
    image = cv2.imread("draw_region_image.jpg")
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
    cv2.imwrite('draw_counting_image.jpg', image)
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
        MainWindow.resize(900, 650)

        # define video thread
        global th, width, height
        th = Thread(MainWindow)

        MainWindow.setMouseTracking(True)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        self.display_video = QtWidgets.QLabel(self.centralwidget)
        self.display_video.setGeometry(QtCore.QRect(30, 20, width, height))
        self.display_video.setFrameShape(QtWidgets.QFrame.Box)
        self.display_video.setAlignment(QtCore.Qt.AlignCenter)
        self.display_video.setObjectName("display_video")


        self.input = QtWidgets.QLineEdit(self.centralwidget)
        self.input.setGeometry(QtCore.QRect(30, 510, 541, 25))
        self.input.setObjectName("input")

        # draw region
        self.draw_region_button = QtWidgets.QPushButton(self.centralwidget)
        self.draw_region_button.setGeometry(QtCore.QRect(730, 230, 89, 25))
        self.draw_region_button.setObjectName("draw_region_button")
        self.draw_region_button.clicked.connect(self.region)

        # draw counting line
        self.draw_count_button = QtWidgets.QPushButton(self.centralwidget)
        self.draw_count_button.setGeometry(QtCore.QRect(730, 280, 89, 25))
        self.draw_count_button.setObjectName("draw_count_button")
        self.draw_count_button.clicked.connect(self.counting)


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
        self.draw_region_button.setText(_translate("MainWindow", "Draw ROI"))
        self.draw_count_button.setText(_translate("MainWindow", "Draw Count"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(900, 650)
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

