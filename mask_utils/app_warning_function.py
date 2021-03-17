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
    alert.setText('Sai địa chỉ cho IP Camera, làm ơn kiểm tra và nhập lại lại!')
    alert.exec_()


# kiểm tra địa chỉ cho Webcam có đúng hay không khi chọn loại camera là Webcam
def check_path_for_webcam():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Sai địa chỉ cho Webcam, làm ơn kiểm tra và nhập lại lại!')
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
    alert.setText('Số lượng các điểm cần để tạo Vạch kiểm đếm đang không chính xác, làm ơn vẽ lại vạch kiểm đếm lại!')
    alert.exec_()


# kiểm tra thông tin camera trong config file
def check_camera_in_config_file():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại camera này chưa được đăng kí và thêm vào tập tin thiết đặt cho các Cameras, làm ơn kiểm tra lại!')
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
    alert.setText("Làm ơn nhập đúng Mật khẩu cũ và thực hiện nhập Mật khẩu mới!")
    alert.exec_()


# kiểm old password cho quá trình đổi pass
def check_password_old():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Mật khẩu cũ chưa chính xác, làm ơn kiểm tra và nhập lại!")
    alert.exec_()


# kiểm old password cho quá trình đổi pass
def check_lenght_password_new():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Mật khẩu mới cần có ít nhất 10 kí tự, làm ơn nhập lại Mật khẩu phù hợp!")
    alert.exec_()


# Đổi password thành công
def check_password_changed_succesfully():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Mật khẩu đã được đổi thành công, xin cảm ơn!")
    alert.exec_()


# kiểm tra new password and confirm password
def check_password_new_and_confirm_new():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText("Mật khẩu mới và xác nhận Mật khẩu mới hiện không đồng nhất, làm ơn kiểm tra và nhập lại!")
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
    alert.setText('Hiện tại không có thông tin cho thời gian và Camera đã được nhập, làm ơn kiểm tra lại!')
    alert.exec_()


def query_camera_id_warning():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Hiện tại Camera này chưa được đăng kí hoặc mất trường thông tin Camera Id, làm ơn kiểm tra lại!')
    alert.exec_()


def stop_all_thread():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Thay đổi về cấu hình camera(hoặc thêm mới camera) đã được ghi nhận, toàn bộ tiến trình đang '
                  'chạy(nếu có) sẽ bị dừng để đảm bảo thông tin, vui lòng kích hoạt lại!')
    alert.exec_()


# Báo nhập mật khẩu để lock hoặc unlock
def input_pass_for_lock():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Làm ơn nhập Mật khẩu trước khi thực hiện thao tác tiếp theo!')
    alert.exec_()


# Nhập sai mật khấu cho lock hoặc unlock
def input_pass_for_lock():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Mật khẩu chưa chính xác, xin vui lòng nhập lại!')
    alert.exec_()


# Địa điểm đã được đăng kí object id và không thể đăng kí lại
def check_object_id():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Địa điểm này đã được đăng kí Mã định danh, vui lòng không thực hiện lại thao tác này!')
    alert.exec_()


# Nhập tên thiết bị cho quá trình đăng kí Mã định danh
def check_name_for_object_id():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Vui lòng nhập tên của thiết bị cho quá trình đăng kí Mã định danh!')
    alert.exec_()


# Nhập licence cho quá trình đăng kí Mã định danh
def check_licence_for_object_id():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Vui lòng nhập Mã cấp phép cho quá trình đăng kí Mã định danh!')
    alert.exec_()


# Đăng kí Mã định danh thành công
def register_object_id_successful():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Mã định danh đã được đăng kí và cập nhật thành công!')
    alert.exec_()


# Đăng kí Mã định danh thất bại
def register_object_id_falied():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Đăng kí Mã định danh thất bại do sự cố ngắt kết nối mạng hoặc một vài lí do khác, vui lòng kiểm tra '
                  'đường truyền và thực hiện đăng kí lại!')
    alert.exec_()


# Đăng kí Mã định danh thất bại
def licence_already_used():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Đăng kí Mã định danh thất bại do Mã cấp phép đã được sử dụng hoặc không có sẵn, vui lòng kiểm tra '
                  'lại Mã cấp phép và thực hiện đăng kí lại!')
    alert.exec_()


# Object_id chưa được đăng kí
def non_object_id():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Thiết bị này hiện chưa được đăng kí Mã định danh, vui lòng thực hiện bước đăng kí Mã định danh!')
    alert.exec_()


# Đăng kí camera_id thất bại
def register_camera_id_falied():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Đăng kí Mã định danh cho Camera thất bại do sự cố ngắt kết nối mạng hoặc một vài lí do khác, vui lòng kiểm tra '
                  'đường truyền và thực hiện đăng kí lại!')
    alert.exec_()


# Nhập địa chỉ truy cập cho camera
def check_camera_address():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Vui lòng nhập địa chỉ truy cập cho Camera hiện tại!')
    alert.exec_()


# Rename cho camera thất bại
def camera_rename_failed():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Thực hiện đổi tên cho Camera hiện tại thất bại do sự cố ngắt kết nối mạng hoặc một vài lí do khác, vui lòng kiểm tra '
                  'đường truyền và thực hiện lại!')
    alert.exec_()

def camera_delete_failed():
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle("Cảnh báo")
    alert.setText('Thực hiện xóa Camera hiện tại thất bại do sự cố ngắt kết nối mạng hoặc một vài lí do khác, vui lòng kiểm tra '
                  'đường truyền và thực hiện lại!')
    alert.exec_()