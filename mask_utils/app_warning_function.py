from PyQt5 import QtCore, QtGui, QtWidgets


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


def check_config_file():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Loading config file")
    alert.setText('There are no config file, please check again!')
    alert.exec_()


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


def check_setting_time():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Setting Time Warning")
    alert.setText('Wrong time information has been input, please check again!')
    alert.exec_()

def plotting_no_data_warning():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại không có thông tin cho thời gian và camera đã nhập, vui lòng kiểm tra lại!')
    alert.exec_()

def query_camera_id_warning():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại Camera này chưa được đăng kí hoặc mất thông tin camera_id, vui lòng kiểm tra lại!')
    alert.exec_()