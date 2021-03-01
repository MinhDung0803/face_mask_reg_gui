import os
from datetime import datetime
from enum import Enum


NUM_OF_KEEPING_FRONT_FACE = 20
NUM_OF_KEEPING_FRONTLESS_FACE = 10
dic_name_and_avatar = None
backward_message = None
export_data_buffer = None
TIME_NAME = None
camera_id_list = None
video_time_list = None
time_face_save_folder_list = None
time_face_save_folder_known_list = None
time_face_save_folder_unknown_list = None
time_save_videos_folder_list = None
time_save_data_folder_list = None
video_infor_list = None
front_face_angles = [90, 90, 90]

class Export_Case(Enum):
    stopped_command = 0
    found_person_in_blacklist = 1
    tracking_data = 2


def set_backward_message(backward_message_queue):
    global backward_message
    backward_message = backward_message_queue

def set_dic_name_and_avatar(ref_dic_name_and_avatar):
    global dic_name_and_avatar
    dic_name_and_avatar = ref_dic_name_and_avatar

def set_ref_export_data_buffer(ref_export_data_buffer):
    global export_data_buffer
    export_data_buffer = ref_export_data_buffer

def set_time_name_is_now():

    global TIME_NAME
    # now = datetime.now()
    # print("now =", now)
    # dt_string = now.strftime("%d-%m-%Y_%H:%M:%S:%f")
    # print("date and time =", dt_string)
    TIME_NAME = datetime.now().strftime("%d-%m-%Y_%H:%M:%S:%f")

def set_camera_id_list(ref_camera_id_list):
    global camera_id_list
    camera_id_list = []
    for i in range(len(ref_camera_id_list)):
        camera_id_list.append(ref_camera_id_list[i])

def set_video_time_list(ref_video_time_list):
    global video_time_list  # reference by camera index
    video_time_list = []

    for time_st in ref_video_time_list:
        if time_st != "":
            start_time = datetime.strptime(time_st, '%d-%m-%Y %I:%M%p')
        else:
            start_time = None

        video_time_list.append(start_time)


def set_front_face_angles(ref_front_face_angles):
    global front_face_angles
    front_face_angles = ref_front_face_angles


def set_video_infor_list(ref_video_infor_list):
    global video_infor_list
    video_infor_list = ref_video_infor_list

def make_dir_if_not_exist(folder_list):
    for full_path in folder_list:
        if (os.path.exists(full_path) is not True):
            os.mkdir(full_path)

def set_folder_save_video_face_data(save_videos_folder_list, save_faces_folder_list, save_data_folder_list):
    global time_face_save_folder_list, time_face_save_folder_known_list, time_face_save_folder_unknown_list
    global time_save_videos_folder_list, time_save_data_folder_list

    time_face_save_folder_list = []
    for folder in save_faces_folder_list:
        new_folder = os.path.join(folder, TIME_NAME)
        time_face_save_folder_list.append(new_folder)
        # print("new_folder : ", new_folder)
        if (os.path.exists(new_folder) is not True):
            os.mkdir(new_folder)

    
    time_face_save_folder_known_list = []
    for folder in time_face_save_folder_list:
        new_folder = os.path.join(folder, "Known")
        time_face_save_folder_known_list.append(new_folder)
        
        if (os.path.exists(new_folder) is not True):
            os.mkdir(new_folder)

    time_face_save_folder_unknown_list = []
    for folder in time_face_save_folder_list:
        new_folder = os.path.join(folder, "Unknown")
        time_face_save_folder_unknown_list.append(new_folder)
        
        if (os.path.exists(new_folder) is not True):
            os.mkdir(new_folder)

    time_save_videos_folder_list = []
    for folder in save_videos_folder_list:
        new_folder = os.path.join(folder, TIME_NAME)
        time_save_videos_folder_list.append(new_folder)
        
        if (os.path.exists(new_folder) is not True):
            os.mkdir(new_folder)

    time_save_data_folder_list = []
    for folder in save_data_folder_list:
        new_folder = os.path.join(folder, TIME_NAME)
        time_save_data_folder_list.append(new_folder)
        
        if (os.path.exists(new_folder) is not True):
            os.mkdir(new_folder)


    return time_save_videos_folder_list

# only for face recognition offline-search 

