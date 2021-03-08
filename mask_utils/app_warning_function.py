from PyQt5 import QtCore, QtGui, QtWidgets


# kiểm tra config file có hay không
def camera_config_flie():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Không tìm thấy tập tin thiết đặt cho các camera, làm ơn kiểm tra lại!')
    alert.exec_()


# kiểm tra địa chỉ cho ip camera có đúng hay không khi chọn loại camera là IP Camera
def check_path_for_ip_camera():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Sai địa chỉ cho IP Camera, làm ơn kiểm tra lại!')
    alert.exec_()


# kiểm tra địa chỉ cho Webcam có đúng hay không khi chọn loại camera là Webcam
def check_path_for_webcam():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Sai địa chỉ cho Webcam, làm ơn kiểm tra lại!')
    alert.exec_()


# kiểm tra camera id khi tạo mới một camera
def check_new_camera_id():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Quá trình đăng kí thông tin cho Camera hiện tại chưa thành công, làm ơn kiểm tra lại!')
    alert.exec_()


# kiểm tra thông in các kiểm trong quá trình vẽ counting line:
def check_new_counting_lines():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Số lượng các điểm cần để tạo Vạch kiểm đếm đang không chính xác, làm ơn kiểm tra lại!')
    alert.exec_()

# kiểm tra thông tin camera trong config file
def check_camera_in_config_file():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại camera này chưa được đăng kí và thêm vào tập tin thiết đặt, làm ơn kiểm tra lại!')
    alert.exec_()

# kiểm tra tên mới của camera trước khi thực hiện rename
def check_camera_name_for_rename():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Làm ơn nhập tên mới cho camera nếu muốn thực hiện đổi tên cho camera này!')
    alert.exec_()


# kiểm tra alarm option
def check_alarm_option():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Làm ơn chọn phương thức cảnh báo áp dụng cho camera hiện tại!')
    alert.exec_()


def check_config_file():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Loading config file")
    alert.setText('There are no config file, please check again!')
    alert.exec_()


def check_camera_name():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Làm ơn nhập tên cho Camera hiện tại!')
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
    alert.setText('Hiện tại không có thông tin cho thời gian và camera đã nhập, làm ơn kiểm tra lại!')
    alert.exec_()

def query_camera_id_warning():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại Camera này chưa được đăng kí hoặc mất trường thông tin Camera Id, làm ơn kiểm tra lại!')
    alert.exec_()