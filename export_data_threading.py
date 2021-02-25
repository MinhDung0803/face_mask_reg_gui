import os
import threading
import time
import pickle
from mask_utils import global_variable_define as gd
import cv2
from datetime import datetime
# import pymysql

cam_id_to_index_dic = None
file_counts = None
item_counts = None
current_file_name_list = None
record_ID = 0

#--- begin: for face detection demo only
face_detection_notify_flag = False
#--- end: for face detection demo only

MAX_WRITE_MONGODB_BLOCK_SIZE = 5

def get_cam_id_to_index_dic():
    cam_id_to_index_dic = {}
    for i, cam_id in enumerate(gd.camera_id_list):
        cam_id_to_index_dic[cam_id] = i

    return cam_id_to_index_dic

def set_file_count():
    global file_counts, item_counts
    file_counts = [0]*len(gd.camera_id_list)
    item_counts = [0]*len(gd.camera_id_list)


def get_current_file_name_list():
    global file_counts
    current_file_name_list = []

    for i in range(len(gd.time_save_data_folder_list)):
        filename = os.path.join(gd.time_save_data_folder_list[i], str(file_counts[i]) + "_encodings.pickle")
        current_file_name_list.append(filename)

    return current_file_name_list

def init():
    global file_counts, item_counts, cam_id_to_index_dic, current_file_name_list

    cam_id_to_index_dic = get_cam_id_to_index_dic()
    set_file_count()
    current_file_name_list = get_current_file_name_list()

    print(" cam_id_to_index_dic = ", cam_id_to_index_dic)

# current_file_list = None


def get_id_path(camera_index, track_id, person_id, person_name, score):


    if person_id >= 0:
        id_path_root = os.path.join(gd.time_face_save_folder_known_list[camera_index], str(person_id))
        if (os.path.exists(id_path_root) is not True):
            os.mkdir(id_path_root)

        sim = str(sim_converter.convert_dis2sim(score)) + "%" + " score " + str(int(score*100)/100)
        id_path = os.path.join(id_path_root, str(track_id) + "_" + person_name + " " + sim)

    else:
        id_path = os.path.join(gd.time_face_save_folder_unknown_list[camera_index], str(track_id))

    if (os.path.exists(id_path) is not True):
        os.mkdir(id_path)

    return id_path

def get_id_path_for_body(camera_index, track_id):


    id_path = os.path.join(gd.time_face_save_folder_unknown_list[camera_index], str(track_id)+ "_body")

    if (os.path.exists(id_path) is not True):
        os.mkdir(id_path)

    return id_path

# def change_data(face_inf_list, camera_index, track_id, person_id, person_name, begin_datetime_str):
#
#     # face_inf_list -> list of [bbox, landmark5, roll_pitch_yaw, aligned, blur_var, extface, frame_index, vector]
#     id_path = get_id_path(camera_index, track_id, person_id, person_name)
#
#     face_data = []
#
#     for i in range(len(face_inf_list)):
#         mormal_box = face_inf_list[i][0]
#         face_image, frame_index, vector = face_inf_list[i][5:8]
#
#         face_filename = os.path.join(id_path, "id_" + str(person_id) + "_frame_" + str(frame_index) + "_datetime_" + begin_datetime_str + ".jpg")
#         cv2.imwrite(face_filename, face_image)
#
#         face_data.append([vector, frame_index, mormal_box, face_filename])
#         # data = (bbox, landmark5, roll_pitch_yaw, aligned, blur_var, crop_face, frame_index)
#         # print("--- out data : frame_index = {0}, bbox = {1} ".format(self.face_inf_list[i][6], self.face_inf_list[i][0]))
#
#     return face_data


def change_data(face_inf_list, camera_index, track_id, person_id, person_name, score, begin_datetime_str):
    # face_inf_list -> list of [bbox, landmark5, roll_pitch_yaw, aligned, blur_var, extface, frame_index, vector]
    id_path = get_id_path(camera_index, track_id, person_id, person_name, score)

    face_data = []

    for i in range(len(face_inf_list)):
        mormal_box = face_inf_list[i][0]
        face_image, frame_index, vector = face_inf_list[i][5:8]

        face_filename = os.path.join(id_path, "id_" + str(person_id) + "_frame_" + str(
            frame_index) + "_datetime_" + begin_datetime_str + ".png")
        cv2.imwrite(face_filename, face_image)

        face_data.append([vector, frame_index, mormal_box, face_filename])
        # data = (bbox, landmark5, roll_pitch_yaw, aligned, blur_var, crop_face, frame_index)
        # print("--- out data : frame_index = {0}, bbox = {1} ".format(self.face_inf_list[i][6], self.face_inf_list[i][0]))

    return face_data
# def write_to_file(item_list):
#     #item_list is list of face_tracking_data = list of [cam_id, track_id, person_id, person_name, self._begin_datetime_, self._end_datetime_,\
#     #                                 self._begin_frame_index, self._end_frame_index, self.face_inf_list]


#     global cam_id_to_index_dic, current_file_name_list
#     file_handle_list = [None]*len(gd.camera_id_list)

#     for item in item_list:
#         export_case, data = item
#         cam_id, track_id, person_id, person_name, begin_datetime, end_datetime, begin_frame_index, end_frame_index, face_inf_list = data

#         cam_index = cam_id_to_index_dic[cam_id]

#         # print("---------cam_id = {0}, export person_name : {1}, len(face_inf_list) = {2}".format(cam_id, person_name, len(face_inf_list)))

#         face_data = change_data(face_inf_list, cam_index, track_id, person_id, person_name)

#         new_item = [cam_id, person_id, person_name, begin_datetime, end_datetime, begin_frame_index, end_frame_index, face_data]

#         if (file_handle_list[cam_index] is None):
#             filename = current_file_name_list[cam_index]
#             if (os.path.exists(filename) is False):
#                 f = open(filename, 'wb')
#                 file_handle_list[cam_index] = f
#             else:
#                 f = open(filename, 'ab')
#                 file_handle_list[cam_index] = f


#         # write data to file
#         f = file_handle_list[cam_index]

#         pickle.dump(new_item, f)


#     for f in file_handle_list:
#         if f is not None:
#             f.close()


"""
'faceBlacklist', 'ID', 'int(11)', ''
'faceBlacklist', 'CameraName', 'varchar(255)', ''
'faceBlacklist', 'CameraID', 'int(11)', ''
'faceBlacklist', 'PersonID', 'int(11)', ''
'faceBlacklist', 'PersonName', 'varchar(255)', ''
'faceBlacklist', 'InTime', 'datetime', ''
'faceBlacklist', 'OutTime', 'datetime', ''
'faceBlacklist', 'VideoURI', 'varchar(255)', ''
'faceBlacklist', 'ImageURI', 'varchar(255)', ''
'faceBlacklist', 'WarningType', 'varchar(90)', ''
'faceBlacklist', 'WarningText', 'varchar(255)', ''
'faceBlacklist', 'EventTime', 'datetime', ''
"""


# def export_to_database(export_case, data):

#     if (export_case == gd.Export_Case.found_person_in_blacklist):
#         print("@"*30)
#         print(data)
#         print("@"*30)
#         print(" case found_person_in_blacklist, export to database: data ")
#         with connection.cursor() as cursor:
#             sql = "INSERT INTO `faceBlacklist` \
#                 (`CameraName`, `CameraID`, `PersonID`, `PersonName`, `InTime`, `OutTime`, `VideoURI`, `ImageURI`, `WarningType`, `WarningText`, `EventTime`) \
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#             cursor.execute(sql, (
#                 data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10]
#             ))

#             print('&' * 100, "before connection.commit()")
#             print(sql)
#             print('&' * 100)
#             connection.commit()

#             print('&' * 100)
#             print(sql)
#             print('&' * 100)

#             # Read a single record
#             sql = "SELECT * FROM `faceBlacklist` WHERE `CameraName`=%s"
#             cursor.execute(sql, (data[0],))
#             result = cursor.fetchone()
#             print('&' * 100)
#             print(result)
#             print(sql)
#             print('&' * 100)


#     else:
#         print(" case tracking_data, export to database: data ")


# def export_to_database(export_case, data):
#
#     if (export_case == gd.Export_Case.found_person_in_blacklist):
#         # print("@"*30)
#         # print(data)
#         # print("@"*30)
#         # print(" case found_person_in_blacklist, export to database: data ")
#         with connection.cursor() as cursor:
#             sql = f'INSERT INTO `faceBlacklist` \
#                 (`CameraName`, `CameraID`, `PersonID`, `PersonName`, `InTime`, `OutTime`, `VideoURI`, `ImageURI`, `WarningType`, `WarningText`, `EventTime`) \
#                 VALUES ("{data[0]}", {data[1]}, {data[2]}, "{data[3]}", "{data[4]}", "{data[5]}", "{data[6]}", "{data[7]}", "{data[8]}", "{data[9]}", "{data[10]}")'
#
#             # print('&' * 100, "before connection.commit()")
#             # print(sql)
#             # print('&' * 100)
#
#             cursor.execute(sql)
#
#             connection.commit()
#
#             # print('&' * 100)
#             # print(sql)
#             # print('&' * 100)
#
#             # # Read a single record
#             # sql = "SELECT * FROM `faceBlacklist` WHERE `CameraName`=%s order by EventTime DESC "
#             # cursor.execute(sql, (data[0],))
#             # result = cursor.fetchone()
#             # print('&' * 100)
#             # print(result)
#             # print(sql)
#             # print('&' * 100)
#
#     else:
#         print(" case tracking_data, export to database: data ")


def write_to_file(item_list):
    #item_list is list of face_tracking_data = list of [cam_id, track_id, person_id, person_name, self._begin_datetime_, self._end_datetime_,\
    #                                 self._begin_frame_index, self._end_frame_index, self.face_inf_list, self.moving_list]

    return

    global cam_id_to_index_dic, current_file_name_list
    global file_counts, item_counts

    file_handle_list = [None]*len(gd.camera_id_list)

    for item in item_list:
        export_case, data = item
        cam_id, track_id, person_id, person_name, score, begin_datetime, end_datetime, begin_frame_index,\
        end_frame_index, face_inf_list, moving_list = data

        cam_index = cam_id_to_index_dic[cam_id]

        begin_datetime_str = begin_datetime.strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # print("---------cam_id = {0}, export person_name : {1}, len(face_inf_list) = {2}".format(cam_id, person_name, len(face_inf_list)))

        face_data = change_data(face_inf_list, cam_index, track_id, person_id, person_name, score, begin_datetime_str)

        # (`CameraName`, `CameraID`, `PersonID`, `PersonName`, `InTime`, `OutTime`, `VideoURI`, `ImageURI`, `WarningType`, `WarningText`, `EventTime`)

        new_item = [cam_id, person_id, person_name, begin_datetime, end_datetime, begin_frame_index, end_frame_index, face_data, moving_list]



        export_item = [cam_id, cam_index, person_id, person_name, begin_datetime_str, end_datetime_str,\
                       "", face_data[0][3], "BlackList", "Phát hiện đối tượng trong BlackList", begin_datetime_str]

        # export_to_database(export_case, export_item)

        if (export_case == gd.Export_Case.tracking_data):

            if (file_handle_list[cam_index] is None):
                filename = current_file_name_list[cam_index]
                f = open(filename, 'ab')
                file_handle_list[cam_index] = f

            # write data to file
            f = file_handle_list[cam_index]

            pickle.dump(new_item, f)

            item_counts[cam_index] += 1


    for f in file_handle_list:
        if f is not None:
            f.close()

    next_file = False
    for i in range(len(item_counts)):
        if (item_counts[i] > 10):
            file_counts[i] += 1
            item_counts[i] = 0
            next_file = True

    if (next_file):
        current_file_name_list = get_current_file_name_list()


def write_body_to_file(item_list):

    global cam_id_to_index_dic, current_file_name_list
    global file_counts, item_counts


    for item in item_list:
        if len(item) != 3:
            print("#"*120)
            print("item[0] = {} item[1] = {}".format(item[0], item[1]))

        print("Len of Item = ", len(item))
        camera_id, track_id, body_inf = item
        bbox, normal_image, frame_index = body_inf

        cam_index = cam_id_to_index_dic[camera_id]



        id_path = get_id_path_for_body(cam_index, track_id)
        print("#" * 100, "id_path : ", id_path)

        filename = datetime.now().strftime("%d-%m-%Y_%H:%M:%S:%f") + ".jpg"
        cv2.imwrite(os.path.join(id_path, filename), normal_image)


def export_data(export_data_buffer, no_job_sleep_time, event_queue, wait_stop):
    print("(4)--- Running export_data_threading")

    if not face_detection_notify_flag:
        init()

    print("export_data init oke")

    pausing = False
    stop = False

    while not stop:
        if event_queue.empty() != True:
            command = event_queue.get()

            if (command == "stop"):
                # write all data to file before stop
                if (export_data_buffer.empty() == False):
                    item_list = []
                    while export_data_buffer.empty() == False:
                        data = export_data_buffer.get()
                        item_list.append(data)

                    write_to_file(item_list)

                print("export_data is waitting to stop")

                wait_stop.wait()
                print("(5)--- Stoped export_data_threading")
                return
            elif (command == "pause/unpause"):
                pausing = not pausing
                if (pausing):
                    print("Tracking Threading is pausing")

        if pausing:
            time.sleep(no_job_sleep_time)
            continue

        if not export_data_buffer.empty():
            item_list = []
            while (not export_data_buffer.empty()) and (len(item_list) < MAX_WRITE_MONGODB_BLOCK_SIZE):
                data = export_data_buffer.get()
                export_case, detail_data = data
                if export_case == gd.Export_Case.stopped_command:
                    stop = True
                    print("@"*160)
                    print("export_case == gd.Export_Case.stopped_command ")
                else:
                    item_list.append(data)

            write_to_file(item_list)

        time.sleep(no_job_sleep_time)

    print('Export waiting for stop')

    wait_stop.wait()

    print("(4)--- Stoped export_data_threading")


def export_data_by_threading(export_data_buffer, no_job_sleep_time, event_queue, wait_stop):
    """
        full_delay_time is num of second to set sleep time
    """

    t = threading.Thread(target=export_data, args=[export_data_buffer, no_job_sleep_time, event_queue, wait_stop])
    t.start()
