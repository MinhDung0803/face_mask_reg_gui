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


# kiểm tra nhập password cho quá trình đổi pass
def check_password_input():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Làm ơn nhập đúng password cũ và thực hiện nhập password mới!")
    alert.exec_()


# kiểm old password cho quá trình đổi pass
def check_password_old():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Password cũ chưa chính xác, làm ơn kiểm tra và nhập lại!")
    alert.exec_()


# kiểm old password cho quá trình đổi pass
def check_lenght_password_new():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Password mới cần có ít nhất 10 kí tự, làm ơn kiểm tra và nhập lại!")
    alert.exec_()


# Đổi password thành công
def check_password_changed_succesfully():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Password đã được đổi thành công, xin cảm !")
    alert.exec_()


# kiểm tra new password and confirm password
def check_password_new_and_confirm_new():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Password mới và xác nhận Password mới hiện không đồng nhất, làm ơn kiểm tra và nhập lại!")
    alert.exec_()


def check_config_file():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Không tìm thấy tập tin thiết đặt cho các camera, làm ơn kiểm tra lại!')
    alert.exec_()


def check_camera_name():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Làm ơn nhập tên cho Camera hiện tại!')
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

def stop_all_thread():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Thay đổi về cấu hình camera được ghi nhận, toàn bộ tiến trình đang chạy(nếu có) sẽ được dừng để '
                  'đảm bảo thông tin, vui lòng kích hoạt lại!')
    alert.exec_()