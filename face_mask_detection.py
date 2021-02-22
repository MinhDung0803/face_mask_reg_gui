import os
import sys
import queue

import threading
import read_video_threading
import detection_threading
import tracking_threading
# from fast_tracking_topN_Face import fast_tracker
from fast_tracking import fast_track
import export_data_threading

import cv2
import numpy as np

from datetime import datetime
import time
from mask_utils import region_util
from mask_utils import graphic_utils

from mask_utils import global_variable_define as gd
from mask_utils import grid_view_video as gv_video

import yaml
import json
# from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(ROOT_DIR)

delay_time = 5

videowrite_flag = False
save_grid_image = True

def get_info_video(fullfilename):

    video_capture = cv2.VideoCapture(fullfilename)
    width = int(video_capture.get(3))
    height = int(video_capture.get(4))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    video_capture.release() 

    return width, height, fps

def counted_show(frame, w, h, list_count, font_face, font_scale, text_thickness, down_offset=0):
    h_margin = 50
    (text_width, text_height), baseline = cv2.getTextSize("Ag", font_face, font_scale, thickness=text_thickness)
    row_num = int(len(list_count))
    row_hight = int((text_height + baseline) * 1.2)
    added_line = int(row_hight * row_num - down_offset)
    new_frame = np.zeros([h + added_line, w, 3], dtype=np.uint8)

    new_frame[added_line:added_line + h, :] = frame
    frame = new_frame
    text_color = (0, 255, 0)

    cv2.rectangle(frame, (0, 0), (w, row_hight*row_num), (50, 0, 50), -1)

    for index in range(row_num):
        if index == 0:
            row_caption = 'Counting:'

        cv2.putText(frame, row_caption, (h_margin, row_hight * (index + 1) - baseline), font_face, font_scale,
                    text_color, text_thickness, cv2.LINE_AA)

        (text_width1, text_height1), _ = cv2.getTextSize(row_caption, font_face, font_scale, thickness=text_thickness)

        st = ''
        for class_name in list_count[index]:
            st = st + class_name + ':' + "%4d" % list_count[index][class_name] + '  '

        cv2.putText(frame, st, (h_margin + text_width1 + h_margin // 2, row_hight * (index + 1) - baseline), font_face,
                    font_scale, text_color, text_thickness)

    return frame

def read_transparent_png_and_scale(filename, frame_width, frame_height, percen_size):
    if not os.path.exists(filename):
        return None, None

    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    h, w = image_4channel.shape[0:2]
    fx, fy = w/frame_width, h/frame_height
    f = max(fx, fy)
    if f > percen_size:
        m = min(frame_width*percen_size, frame_height*percen_size)
        if f==fx:
            new_f = m/w
        else:
            new_f = m/h

        image_4channel = cv2.resize(image_4channel, (0, 0), fx=new_f, fy=new_f)

    alpha_channel = image_4channel[:, :, 3] / 255.0
    rgb_channels = image_4channel[:, :, :3]

    rgb_channels[:, :, 0] = rgb_channels[:, :, 0] * alpha_channel
    rgb_channels[:, :, 1] = rgb_channels[:, :, 1] * alpha_channel
    rgb_channels[:, :, 2] = rgb_channels[:, :, 2] * alpha_channel

    invert_alpha_channel = 1 - alpha_channel

    return rgb_channels, invert_alpha_channel

def show_logo(frame, logo_info):
    logo_rgb_image, invert_alpha_channel = logo_info
    if (logo_rgb_image is None) or (invert_alpha_channel is None):
        return

    fr_h, fr_w, _ = frame.shape
    h, w, _ = logo_rgb_image.shape
    margin = int(min(fr_w, fr_h)*0.01)
    x, y = fr_w - w - margin, margin

    ROI_image = frame[y:y + h, x:x + w]
    # cv2.copyTo(logo_rgb_image, logo_alpha_image, ROI_image)

    ROI_image[:, :, 0] = invert_alpha_channel * ROI_image[:, :, 0] + logo_rgb_image[:, :, 0]
    ROI_image[:, :, 1] = invert_alpha_channel * ROI_image[:, :, 1] + logo_rgb_image[:, :, 1]
    ROI_image[:, :, 2] = invert_alpha_channel * ROI_image[:, :, 2] + logo_rgb_image[:, :, 2]

def is_closed_all(list_closed_cam):
    for closed in list_closed_cam:
        if closed == False:
            return False
    
    return True

def region_scale(list_list_region, list_scale):
    num_cam = len(list_scale)
    
    for cam_index in range(num_cam):
        for i in range(len(list_list_region[cam_index])):
            # for j in range(len(list_list_region[cam_index][i])):
            list_list_region[cam_index][i].make_scale(list_scale[cam_index])


def change_fps(info_videos, frame_drop_list):
    for cam_index in range(len(info_videos)):
        info_videos[cam_index][2] /= frame_drop_list[cam_index]

def add_time_and_count_into_file(time_save_videos_folder, saved_frame_count):
    # name, extend = os.path.splitext(filename)
    # return name + "_" + gd.TIME_NAME + "_" + str(file_count) + extend

    return os.path.join(time_save_videos_folder, str(saved_frame_count) + ".mp4")

def VideoWriter_create(cam_index, time_save_videos_folder_list, info_videos, saved_frame_count):

    video_filename = add_time_and_count_into_file(time_save_videos_folder_list[cam_index], saved_frame_count)
    width1, height1, fps_video1 = info_videos[cam_index]

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out1 = cv2.VideoWriter(video_filename, fourcc, fps_video1, (width1, height1))
    # out1.set(cv2.VIDEOWRITER_PROP_QUALITY, 80)

    return out1, fps_video1

def draw_caption(image, label, bbox, font_face, font_scale, bbox_color, text_color, text_thickness):
    x1, y1, x2, y2 = bbox
    # get text size
    (text_width, text_height), baseline = cv2.getTextSize(label, font_face, font_scale, thickness=text_thickness)
    # put filled text rectangle
    cv2.rectangle(image, (x1, y1), (x1 + text_width, y1 - text_height - baseline), bbox_color, thickness=cv2.FILLED)

    # put text above rectangle
    cv2.putText(image, label, (x1, y1 - 4), font_face, font_scale, text_color, text_thickness, lineType=cv2.LINE_AA)


def reading_threading(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list,
                          detect_step_list, tracking_scale_list, regionboxs_list, tracking_regions_list,
                      view_width, view_height, grid_row, grid_col, forward_message=None, backward_message=None):

    grid_view = gv_video.Grid_View("Camera Viewer", view_width, view_height, grid_row, grid_col, 2, (255,0,0), gd.camera_id_list, (0,255,0), direct_show=True)

    global videowrite_flag
    global save_grid_image



    if len(time_save_videos_folder_list) == 0:
        videowrite_flag = False

    num_cam = len(input_video_list)

    logo_file = os.path.join(ROOT_DIR, "pictures/LogoTCX_small.png")
    max_fps = 0
    video_infor_list = []
    logo_info_list = []

    for cam_index in range(num_cam):
        width1, height1, fps_video1 = get_info_video(input_video_list[cam_index])
        video_infor_list.append([width1, height1, fps_video1])
        if (max_fps < fps_video1): max_fps = fps_video1

        # load logo
        logo_rgb_image, invert_alpha_channel = read_transparent_png_and_scale(logo_file, width1, height1, 0.12)
        logo_info_list.append([logo_rgb_image, invert_alpha_channel])





    gd.set_video_infor_list(video_infor_list)

    currentfile_saved_frame_count_list = [0]*num_cam
    saved_frame_count_list = [0]*num_cam
    saved_video_count_list = [0]*num_cam
    num_of_frame_in_block_list = [0]*num_cam

    out = []

    change_fps(video_infor_list, frame_drop_list)

    if videowrite_flag:
        for cam_index in range(num_cam):
            out1, fps_video1 = VideoWriter_create(cam_index, time_save_videos_folder_list, video_infor_list, saved_frame_count_list[cam_index])
            num_of_frame_in_block_list[cam_index] = fps_video1 * time_block_video

            out.append(out1)
    
    if save_grid_image:

        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        grid_size = grid_view.get_windows_size()
        now_st = datetime.now().strftime("%d-%m-%Y_%H:%M:%S:%f")
        grid_video_name = os.path.join("/media/gg-ai-team/DATA/out", now_st + ".mp4")
        grid_videowriter = cv2.VideoWriter(grid_video_name, fourcc, video_infor_list[0][2], grid_size)


    # regionboxs_list, tracking_regions_list = get_default_region(video_infor_list, margin=0)

    list_frame_image_buffer = [queue.Queue(50) for i in range(num_cam)]
    list_detected_buffer = [queue.Queue(50) for i in range(num_cam)]
    list_trackted_buffer = [queue.Queue(50) for i in range(num_cam)]
    export_data_buffer = queue.Queue(100)  # unlimited

    gd.set_ref_export_data_buffer(export_data_buffer)
    gd.set_backward_message(backward_message)

    event_queue1 = queue.Queue()
    event_queue2 = queue.Queue()
    event_queue3 = queue.Queue()
    event_queue4 = queue.Queue()

    wait_stop = threading.Barrier(5)
    press_quit = False

    region_scale(tracking_regions_list, tracking_scale_list)

    no_job_sleep_time = 1/max_fps

    read_video_threading.read_video_by_threading(input_video_list, frame_drop_list, list_frame_image_buffer, no_job_sleep_time, event_queue1, wait_stop)

    num_face_recognition_in_1step = [0]
    detection_threading.detecting_by_threading(list_frame_image_buffer, detect_step_list, video_infor_list, regionboxs_list, min_face_size_list, list_detected_buffer, no_job_sleep_time, event_queue2, wait_stop)

    tracking_threading.tracking_by_threading(list_detected_buffer, export_data_buffer, tracking_scale_list, video_infor_list, tracking_regions_list, list_trackted_buffer, no_job_sleep_time, event_queue3, wait_stop)

    no_job_sleep_time_for_export_data = no_job_sleep_time
    export_data_threading.export_data_by_threading(export_data_buffer, no_job_sleep_time_for_export_data, event_queue4, wait_stop)

    trackregion_color = (0, 255, 255)
    boxregion_color = (0, 255, 0)

    sum_time = 0
    count = 0

    # list_winname = [ 'cam' + str(i) for i in range(num_cam)]

    # print("-------------------------------------------------------------------------------------------------")
    # print(list_winname)

    list_closed_cam = [False]*num_cam

    # Map_u = graphic_utils.cal_map_u(10)  # for fast interpolation s-pline
    global delay_time
    pausing = False

    count_test = 0
    sum_test = 0
    while True:

        time_start = time.time()
        if (forward_message is not None) and (forward_message.empty() is False):
            event_message = forward_message.get()
            if event_message == "stop":
                event_queue1.put("stop")
                event_queue2.put("stop")
                event_queue3.put("stop")
                event_queue4.put("stop")

                press_quit = True
                
                break
            elif event_message == "pause/unpause":
                event_queue1.put("pause/unpause")
                event_queue2.put("pause/unpause")
                event_queue3.put("pause/unpause")
                event_queue4.put("pause/unpause")
                pausing = not pausing

            elif event_message == "update-view":
                event_queue4.put("update-view")

        if (pausing):
            time.sleep(no_job_sleep_time)
            continue

        have_input = False
        for cam_index in range(num_cam):
            
            trackted_buffer = list_trackted_buffer[cam_index]
            if trackted_buffer.empty() == False :
                data = trackted_buffer.get()

                ind = data[0]
                frame = data[1]
                frame_ori = data[2]
                list_count = data[3]

                if (ind != -1):

                    have_input = True

                    save_frame_ori = frame_ori.copy()
                    t1 = time.time()
                    boxs_show = data[4]
                    names_show = data[5]
                    color_show = data[6]
                    tails_show = data[7]
                    
                    # ------------------ draw infor -----------------------

                    up_scale = 1/tracking_scale_list[cam_index]


                    bbox_thick = int(0.6 * (frame_ori.shape[0] + frame_ori.shape[1]) / 1000)
                    if bbox_thick < 2:
                        bbox_thick = 2
                    font_face = cv2.FONT_HERSHEY_COMPLEX_SMALL
                    font_scale = 0.75 * bbox_thick

                    invert_scale = 1.0 / tracking_scale_list[cam_index]


                    for bbox, name, color, tail in zip(boxs_show, names_show, color_show, tails_show):
                        
                        show_box = [int(bbox[0]*up_scale), int(bbox[1]*up_scale), int(bbox[2]*up_scale), int(bbox[3]*up_scale)]

                        cv2.rectangle(frame_ori, (show_box[0], show_box[1]), (show_box[2], show_box[3]), color, bbox_thick)


                        # box_size = str(int((bbox[2] - bbox[0]) * up_scale)) + 'x' + str(
                        #     int((bbox[3] - bbox[1]) * up_scale))

                        # draw_caption(frame_ori, name, show_box, font_face, font_scale, (0, 0, 255), (255, 255, 0),
                        #              bbox_thick)


                        Len = len(tail)
                        if Len >= 4:
                            # cv2.line(frame_ori,(int(tail[0]*scale), int(tail[1]*scale)), (int(tail[Len-2])*scale, int(tail[Len-1])*scale),color, 2)
                            smooth_tail = graphic_utils.filter_tail(tail, 7)

                            # spline_tail = graphic_utils.spline_interpolation_fast(smooth_tail, Map_u)

                            spline_tail = smooth_tail

                            tail_lines = []
                            for i in range(0, len(spline_tail), 2):
                                tail_lines.append([int(spline_tail[i]*up_scale), int(spline_tail[i+1]*up_scale)])

                            points = np.array(tail_lines)
                            cv2.polylines(frame_ori, np.int32([points]), 0, color, bbox_thick, cv2.LINE_AA)

                    for tracking_regions in tracking_regions_list[cam_index]:
                        tracking_regions.draw_region(frame_ori, trackregion_color, bbox_thick, invert_scale, True, 1, 1)

                    show_logo(frame_ori, logo_info_list[cam_index])
                    frame_ori = counted_show(frame_ori, frame_ori.shape[1], frame_ori.shape[0], list_count, font_face,
                                             font_scale*1.2, bbox_thick)


                    # for regionbox in regionboxs_list[cam_index]:
                    #     regionbox.draw_region(frame_ori, boxregion_color, boxregion_thickness, 1/detection_scale_list[cam_index])

                    # for region in tracking_regions_list[cam_index]:
                    #     region.draw_region(frame_ori, trackregion_color, trackregion_thickness, 1/tracking_scale_list[cam_index], True, 1, 0)
                    

                    # counted_show(frame_ori, frame_ori.shape[1], frame_ori.shape[0], list_count)

                    # ------------------ end draw infor -----------------------
                    
                    # Counted_list[cam_index] = list_count


                    grid_view.set_cell_image(frame_ori, cam_index)

                    t2 = time.time()

                    fps = (1. / (t2 - t1))
                    # print(" Visualization speed = %f fps"%(fps))

                    sum_time += (t2 - t1)
                    count += 1

                    if videowrite_flag:
                        out[cam_index].write(save_frame_ori)
                        saved_frame_count_list[cam_index] += 1
                        currentfile_saved_frame_count_list[cam_index] += 1

                        if (currentfile_saved_frame_count_list[cam_index] >= num_of_frame_in_block_list[cam_index]):
                            out[cam_index].release()
                            currentfile_saved_frame_count_list[cam_index] = 0
                            saved_video_count_list[cam_index] += 1

                            out1, fps_video1 = VideoWriter_create(cam_index, time_save_videos_folder_list, video_infor_list,
                                                                  saved_frame_count_list[cam_index])

                            out[cam_index] = out1


                else:
                
                    list_closed_cam[cam_index] = True
                    t4 = time.time()

                    if videowrite_flag:
                        if out[cam_index] is not None:
                            out[cam_index].release()
                            out[cam_index] = None

                    # if (cam_index == 0):
                    #     print(" Spend time 1: ", (t4-t3)/60, "min")
                    
                    
                    break
            else:

                time.sleep(no_job_sleep_time)

        time_end = time.time()

        count_test += 1
        sum_test += time_end - time_start

        if (count_test % 30) == 0:
            print("Spend time: ", time_end - time_start)
            print("FPS: ", count_test/sum_test)




        if have_input:
            char = grid_view.show(delay_time)
        else:
            char = cv2.waitKeyEx(delay_time)

        if (char & 0xFF00 == 0):  # normal keys press
            # Press Q to stop!
            if (char & 0xFF) in [ord('q'), ord('Q'), 27]:
                # read_video_threading.
                event_queue1.put("stop")
                event_queue2.put("stop")
                event_queue3.put("stop")
                event_queue4.put("stop")
                press_quit = True

                break
            elif (char & 0xFF) in [ord('p'), ord('P')]:
                event_queue1.put("pause/unpause")
                event_queue2.put("pause/unpause")
                event_queue3.put("pause/unpause")
                event_queue4.put("pause/unpause")

                char = cv2.waitKey()

                event_queue1.put("pause/unpause")
                event_queue2.put("pause/unpause")
                event_queue3.put("pause/unpause")
                event_queue4.put("pause/unpause")

            elif (char & 0xFF) in [ord('v'), ord('V')]:
                event_queue4.put("update-view")

        else:  # controller keys press
            if (char & 0xFF) == 81:
                delay_time = int(2 * delay_time)
                if delay_time > 30000:
                    delay_time = 30000

            elif (char & 0xFF) == 83:
                delay_time = int(0.5 * delay_time)
                if (delay_time < 1):
                    delay_time = 1

        if save_grid_image and have_input:
            grid_videowriter.write(grid_view.get_capture_image())   
   
        if press_quit == True:
            break

        if is_closed_all(list_closed_cam):

            break

    if videowrite_flag:
        for i in range(len(out)):
            if (out[i] is not None):
                out[i].release()
               
    grid_view.release()

    if save_grid_image:
        grid_videowriter.release()


    print(" Visualization speed Ave: ", count/ (sum_time), "fps")

    print('Visualization waiting for stop')
    wait_stop.wait()
    print('--------------------------------------------------------------------test stoped')
    if backward_message is not None:
        backward_message.put(["stop", "Stopped face recognition monitoring service"])


def read_camera_infor(json_filename):
    cam_infor_list = []
    with open(json_filename) as json_file:
        json_data = json.load(json_file)
        video_list = json_data["videos"]

        cam_id_list = []
        cam_url_list = []
        frame_drop_list = []
        frame_step_list = []
        detection_scale_list = []
        tracking_scale_list = []
        min_face_size_list = []
        max_roll_list = []
        max_pitch_list = []
        max_yaw_list = []


        for item in video_list:
            id = str(item["id"])
            url = item["url"]
            frame_drop = item["frame_drop"]
            frame_step = item["frame_step"]
            detection_scale = item["detection_scale"]
            tracking_scale = item["tracking_scale"]
            min_face_size = item["min_face_size"]
            max_roll = item["max_roll"]
            max_pitch = item["max_pitch"]
            max_yaw = item["max_yaw"]


            cam_id_list.append(id)
            cam_url_list.append(url)
            frame_drop_list.append(frame_drop)
            frame_step_list.append(frame_step)
            detection_scale_list.append(detection_scale)
            tracking_scale_list.append(tracking_scale)
            min_face_size_list.append(min_face_size)
            max_roll_list.append(max_roll)
            max_pitch_list.append(max_pitch)
            max_yaw_list.append(max_yaw)

            print(
                "id = {0}, url = {1}, frame_drop = {2}, frame_step = {3}, detection_scale = {4}, tracking_scale {5}".format(
                    id, url, frame_drop, frame_step, detection_scale, tracking_scale))
            print("min_face_size = {0}, max_roll = {1}, max_pitch = {2}, max_yaw = {3}".format(min_face_size, max_roll,
                                                                                               max_pitch, max_yaw))
            cam_infor_list.append([id, url, frame_drop, frame_step, detection_scale, tracking_scale, min_face_size,
                                   max_roll, max_pitch, max_yaw])
        display = json_data["display"]
        display_width = display["width"]
        display_height = display["height"]
        print("display_width = {0}, display_height = {1}".format(display_width, display_height))

    return cam_infor_list, display_width, display_height


# def auto_run(cam_infor_list, display_width, display_height, ENCODING_VECTORS_FILE, SAVE_FACES_FOLDER,
#         SAVE_VIDEO_CLIPS_FOLDER, SAVE_VIDEOS_FOLDER, SAVE_DATA_FOLDER, time_block_video,
#              forward_message, backward_message, SIMILARITY_THRESHOLD=0.9):
#
#     my_final_deploy_search.Euclid_distance_threshold = SIMILARITY_THRESHOLD
#     cam_num = len(cam_infor_list)
#
#     input_video_list = []
#     cam_id_list = []
#     frame_drop_list = []
#     frame_step_list = []
#     detection_scale_list = []
#     tracking_scale_list = []
#     min_face_size_list = []
#     MAX_ROLLs = []
#     MAX_PITCHs = []
#     MAX_YAWs = []
#
#     for cam_infor in cam_infor_list:
#         id, url, frame_drop, frame_step, detection_scale, tracking_scale, min_face_size, max_roll, max_pitch, max_yaw = cam_infor
#
#         cam_id_list.append(id)
#         input_video_list.append(url)
#         frame_drop_list.append(frame_drop)
#         frame_step_list.append(frame_step)
#         detection_scale_list.append(detection_scale)
#         tracking_scale_list.append(tracking_scale)
#         min_face_size_list.append(min_face_size)
#         MAX_ROLLs.append(max_roll)
#         MAX_PITCHs.append(max_pitch)
#         MAX_YAWs.append(max_yaw)
#
#
#
#     time_block_video = time_block_video
#
#     view_width = display_width
#     view_height = display_height
#     grid_row = cam_num**0.5
#     grid_col = cam_num**0.5
#
#     if int(grid_col) < grid_col:
#         grid_col = int(grid_col) + 1
#
#     grid_row = int(grid_row)
#
#     if grid_row * grid_col < cam_num:
#         grid_row += 1
#
#
#     # get Black-List or/and VIP-List
#
#     get_ENCODING_VECTORS(ENCODING_VECTORS_FILE)
#
#     save_videos_folder_list = [os.path.join(SAVE_VIDEOS_FOLDER, id) for id in cam_id_list]
#     save_faces_folder_list = [os.path.join(SAVE_FACES_FOLDER, id) for id in cam_id_list]
#     save_data_folder_list = [os.path.join(SAVE_DATA_FOLDER, id) for id in cam_id_list]
#
#     # set globals
#     gd.set_camera_id_list(cam_id_list)
#     print("*"*80, ".....set_camera_id_list.....")
#     gd.make_dir_if_not_exist(save_videos_folder_list)
#     gd.make_dir_if_not_exist(save_faces_folder_list)
#     gd.make_dir_if_not_exist(save_data_folder_list)
#     gd.set_time_name_is_now()
#
#
#     time_save_videos_folder_list = gd.set_folder_save_video_face_data(save_videos_folder_list, save_faces_folder_list, save_data_folder_list)
#
#     print("(1)", "-"*50)
#     t1 = time.time()
#     fast_track.FACE_DETECTION_NOTIFY_FLAG = False
#     reading_threading(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list, frame_step_list, detection_scale_list,\
#         tracking_scale_list, min_face_size_list, MAX_ROLLs, MAX_PITCHs, MAX_YAWs, view_width, view_height, grid_row, grid_col, forward_message, backward_message)
#
#     t2 = time.time()
#
#     print("Spend time 2:",(t2-t1)/60, "min")
#
#     print("Stoped main Thread")

def auto_run_only_face_detection(video_url, NOTIFY_TIME_INTERVAL, forward_message, backward_message):

    cam_num = 1

    ENCODING_VECTORS_FILE = ""
    SAVE_FACES_FOLDER = ""
    SAVE_VIDEO_CLIPS_FOLDER = ""
    SAVE_VIDEOS_FOLDER = ""
    SAVE_DATA_FOLDER = ""
    time_block_video = 1000
    display_width = 1280
    display_height = 720

    input_video_list = [video_url]
    cam_id_list = ["Customer Video"]

    frame_step_list = [2]

    min_face_size_list = [30]
    MAX_ROLLs = [45]
    MAX_PITCHs = [45]
    MAX_YAWs = [45]

    width, height, fps = get_info_video(video_url)
    print("url : ", video_url)
    print("width = {0}, height = {1}, fps = {2}".format(width, height, fps))

    # frame_drop = (fps/30)
    # if frame_drop > int(fps/30):
    #     frame_drop = int(fps / 30) + 1

    frame_drop = (fps/30) if (fps/30) == int(fps/30) else int(fps / 30) + 1
    frame_drop_list = [frame_drop]

    detection_scale = 1 if height < 480 else 480/height
    detection_scale_list= [detection_scale]

    tracking_scale = 1 if height < 1080 else 1080/height
    tracking_scale_list = [tracking_scale]

    print("*"*80)
    print("frame_drop_list = {0}, frame_step_list = {1}, detection_scale_list = {2}, tracking_scale_list = {3}, min_face_size_list = {4}".format(frame_drop_list, frame_step_list, detection_scale_list, tracking_scale_list, min_face_size_list))

    view_width = display_width
    view_height = display_height

    grid_row = 1
    grid_col = 1

    # get Black-List or/and VIP-List

    list_id_featureVectors = []
    _unknown_ID_ = -1

    global dic_name_and_avatar
    dic_name_and_avatar = {}
    gd.set_dic_name_and_avatar(dic_name_and_avatar)

    save_videos_folder_list = []
    save_faces_folder_list = []
    save_data_folder_list = []

    # set globals
    gd.set_camera_id_list(cam_id_list)
    time_save_videos_folder_list = []
    t1 = time.time()

    fast_track.FACE_DETECTION_NOTIFY_FLAG = True
    fast_track.NOTIFY_TIME_INTERVAL = NOTIFY_TIME_INTERVAL
    export_data_threading.face_detection_notify_flag = True

    reading_threading(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list,
                      frame_step_list, detection_scale_list,
                      tracking_scale_list, min_face_size_list, MAX_ROLLs, MAX_PITCHs, MAX_YAWs, view_width, view_height,
                      grid_row, grid_col, forward_message, backward_message)

    t2 = time.time()

    print("Spend time 2:", (t2 - t1) / 60, "min")

    print("Stoped main Thread")


def start_face_recogniton_system(forward_message, backward_message):

    cam_infor_list, display_width, display_height = read_camera_infor("/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/database/video_camera.json")
    ENCODING_VECTORS_FILE = "/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/input/BlackList/encoding_vectors_file.pickle"
    SAVE_FACES_FOLDER = "/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/output/public/Faces"
    SAVE_VIDEO_CLIPS_FOLDER = "/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/output/public/VideoClips"
    SAVE_VIDEOS_FOLDER = "/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/output/private/Videos"
    SAVE_DATA_FOLDER = "/media/gg-ai-team/DATA/TaiNH/hcs1-face-extraction/service1.2/output/private/Data"
    TIME_BLOCK_VIDEO = 1000

    auto_run(cam_infor_list, display_width, display_height, ENCODING_VECTORS_FILE, SAVE_FACES_FOLDER,
        SAVE_VIDEO_CLIPS_FOLDER, SAVE_VIDEOS_FOLDER, SAVE_DATA_FOLDER, TIME_BLOCK_VIDEO, forward_message, backward_message)


def parser_cam_infor(cam_infor_list):

    input_video_list = []
    cam_id_list = []
    frame_drop_list = []
    frame_step_list = []
    tracking_scale_list = []
    regionboxs_list = []
    tracking_regions_list = []

    tracing_region_datas = []

    for cam_infor in cam_infor_list:
        id = cam_infor["id"]
        url = cam_infor["url"]
        frame_drop = cam_infor["frame_drop"]
        frame_step = cam_infor["frame_step"]
        tracking_scale = cam_infor["tracking_scale"]

        ROIs_data = cam_infor["ROIs"]
        regionbox_list = region_util.create_regionboxs(ROIs_data)

        tracking_regions_data = cam_infor["tracking_regions"]
        tracking_region_list = region_util.create_tracking_regions(tracking_regions_data)

        cam_id_list.append(id)
        input_video_list.append(url)
        frame_drop_list.append(frame_drop)
        frame_step_list.append(frame_step)
        tracking_scale_list.append(tracking_scale)
        regionboxs_list.append(regionbox_list)
        tracking_regions_list.append(tracking_region_list)

    return input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list,\
           tracking_regions_list


if __name__ == '__main__':

    # start_face_recogniton_system()

    if len(sys.argv) < 2:
        print(
            "------------------------------------------------------------------------------------\n"
            "Call this program like this:\n\n"
            "python  ./face_recognition_demo.py path_to_config_file.yml"
            "\n"
            )
        
        exit()
    
    print('\n--------------------------------- Face Recognition System ---------------------------------\n\n')

    print("S keypress: Change small size view <-> original size view")
    print("P keypress: Pause")
    print("Q or Esc keypress: Quit")
    print('\n\n-----------------------------------------------------------------------------------\n')

    config_file = sys.argv[1]

    yaml.warnings({'YAMLLoadWarning': False})
    with open(config_file, 'r') as fs:
        config = yaml.load(fs)
        # config = yaml.load(fs, Loader=yaml.FullLoader)

    print("------------------------------")

    cam_config = config["input"]["cam_config"]
    save_videos_folder = config["output"]["save_videos_folder"]
    save_faces_folder = config["output"]["save_faces_folder"]
    save_data_folder = config["output"]["save_data_folder"]
    time_block_video = config["output"]["time_block_video"]

    view_width = config["view_window"]["width"]
    view_height = config["view_window"]["height"]
    grid_row = config["view_window"]["grid_row"]
    grid_col = config["view_window"]["grid_col"]


    with open(cam_config) as json_file:
        json_data = json.load(json_file)
    json_file.close()

    cam_infor_list = json_data["data"]

    input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list, \
    tracking_regions_list = parser_cam_infor(cam_infor_list)

    video_time_list = [""]*len(cam_id_list)
    min_face_size_list = [10]*len(cam_id_list)


    save_videos_folder_list = [os.path.join(save_videos_folder, id) for id in cam_id_list]
    save_faces_folder_list = [os.path.join(save_faces_folder, id) for id in cam_id_list]
    save_data_folder_list = [os.path.join(save_data_folder, id) for id in cam_id_list]
    
    # set globals 
    gd.set_camera_id_list(cam_id_list)
    gd.set_video_time_list(video_time_list)
    print("*"*80, ".....set_camera_id_list.....")
    gd.make_dir_if_not_exist(save_videos_folder_list)
    gd.make_dir_if_not_exist(save_faces_folder_list)
    gd.make_dir_if_not_exist(save_data_folder_list)
    gd.set_time_name_is_now()

    time_save_videos_folder_list = gd.set_folder_save_video_face_data(save_videos_folder_list, save_faces_folder_list, save_data_folder_list)

    t1 = time.time()


    reading_threading(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list, frame_step_list, \
        tracking_scale_list, regionboxs_list, tracking_regions_list, view_width, view_height, grid_row, grid_col)


    t2 = time.time()

    print("Spend time 2:", (t2-t1)/60, "min")


# For Examples:

# python face_recognition_demo.py configs/face_recognition_config_video.yml

