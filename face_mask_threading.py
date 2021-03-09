import os
import sys
import queue

import threading
import read_video_threading
import detection_threading
import tracking_threading
import export_data_threading

import cv2
import numpy as np

from datetime import datetime
import time
from mask_utils import region_util
from mask_utils import graphic_utils

from mask_utils import global_variable_define as gd

import yaml
import json
import warnings
warnings.filterwarnings("ignore")
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

    cv2.rectangle(frame, (0, 0), (w, row_hight * row_num), (50, 0, 50), -1)

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
    fx, fy = w / frame_width, h / frame_height
    f = max(fx, fy)
    if f > percen_size:
        m = min(frame_width * percen_size, frame_height * percen_size)
        if f == fx:
            new_f = m / w
        else:
            new_f = m / h

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
    margin = int(min(fr_w, fr_h) * 0.01)
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


def face_mask(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list,detect_step_list,
              tracking_scale_list, regionboxs_list, tracking_regions_list,view_width, view_height, grid_row, grid_col,
              face_mask_buffer, forward_message, backward_message, wait_stop, no_job_sleep_time):

    print("(0)--- Running Face Mask Threading")

    global videowrite_flag
    global save_grid_image
    global min_face_size_list

    if len(time_save_videos_folder_list) == 0:
        videowrite_flag = False

    num_cam = len(input_video_list)

    logo_file = os.path.join(ROOT_DIR, "pictures/LogoTCX_small.png")
    # max_fps = 0
    video_infor_list = []
    logo_info_list = []

    for cam_index in range(num_cam):
        width1, height1, fps_video1 = get_info_video(input_video_list[cam_index])
        video_infor_list.append([width1, height1, fps_video1])
    #     if (max_fps < fps_video1):
    #         max_fps = fps_video1
        # load logo
        logo_rgb_image, invert_alpha_channel = read_transparent_png_and_scale(logo_file, width1, height1, 0.12)
        logo_info_list.append([logo_rgb_image, invert_alpha_channel])

    gd.set_video_infor_list(video_infor_list)

    # currentfile_saved_frame_count_list = [0] * num_cam
    saved_frame_count_list = [0] * num_cam
    # saved_video_count_list = [0] * num_cam
    num_of_frame_in_block_list = [0] * num_cam

    out = []

    change_fps(video_infor_list, frame_drop_list)

    # -----
    if videowrite_flag:
        for cam_index in range(num_cam):
            out1, fps_video1 = VideoWriter_create(cam_index, time_save_videos_folder_list, video_infor_list,
                                                  saved_frame_count_list[cam_index])
            num_of_frame_in_block_list[cam_index] = fps_video1 * time_block_video

            out.append(out1)

    if save_grid_image:
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        size = (640, 480)
        now_st = datetime.now().strftime("%d-%m-%Y_%H:%M:%S:%f")
        grid_video_name = os.path.join("/media/gg-ai-team/DATA/out", now_st + ".mp4")
        grid_videowriter = cv2.VideoWriter(grid_video_name, fourcc, video_infor_list[0][2], size)
    # -----


    list_frame_image_buffer = [queue.Queue(50) for i in range(num_cam)]
    list_detected_buffer = [queue.Queue(50) for i in range(num_cam)]
    list_trackted_buffer = [queue.Queue(50) for i in range(num_cam)]
    export_data_buffer = queue.Queue(50)  # unlimited

    gd.set_ref_export_data_buffer(export_data_buffer)
    # gd.set_backward_message(backward_message)

    event_queue1 = queue.Queue()
    event_queue2 = queue.Queue()
    event_queue3 = queue.Queue()
    event_queue4 = queue.Queue()



    region_scale(tracking_regions_list, tracking_scale_list)

    # cal read video threading - 1
    read_video_threading.read_video_by_threading(input_video_list, frame_drop_list, list_frame_image_buffer,
                                                 no_job_sleep_time, event_queue1, wait_stop)

    # cal detecting threading - 2
    detection_threading.detecting_by_threading(list_frame_image_buffer, detect_step_list, video_infor_list,
                                               regionboxs_list, min_face_size_list, list_detected_buffer,
                                               no_job_sleep_time, event_queue2, wait_stop)

    # call tracking threading - 3
    tracking_threading.tracking_by_threading(list_detected_buffer, export_data_buffer, tracking_scale_list,
                                             video_infor_list, tracking_regions_list, list_trackted_buffer,
                                             no_job_sleep_time, event_queue3, wait_stop)

    # call export data threading - 4
    no_job_sleep_time_for_export_data = no_job_sleep_time
    export_data_threading.export_data_by_threading(export_data_buffer, no_job_sleep_time_for_export_data,
                                                   event_queue4, wait_stop)


    trackregion_color = (0, 255, 255)
    boxregion_color = (0, 255, 0)

    sum_time = 0
    count = 0

    list_closed_cam = [False] * num_cam

    # Map_u = graphic_utils.cal_map_u(10)  # for fast interpolation s-pline
    global delay_time
    pausing = False

    count_test = 0
    sum_test = 0

    while True:
        # print("DUNGPM--" * 100)

        time_start = time.time()
        # if (forward_message is not None) and (forward_message.empty() is False):
        #     # print("forward_message status: ", forward_message.empty())
        if forward_message.empty() is False:
            event_message = forward_message.get()
            if event_message == "stop":
                event_queue1.put("stop")
                event_queue2.put("stop")
                event_queue3.put("stop")
                event_queue4.put("stop")

                print("[INFO]-- Face Mask threading is waitting to stop")
                wait_stop.wait()
                print("(0)--- Stoped Face Mask threading")
                return


                # press_quit = True
                # print("DUNGPM--" * 100)

                # break
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
        have_no_job = True


        for cam_index in range(num_cam):


            if not face_mask_buffer[cam_index].full():
                trackted_buffer = list_trackted_buffer[cam_index]
                if not trackted_buffer.empty():

                    have_no_job = False


                    data = trackted_buffer.get()

                    ind = data[0]
                    frame = data[1]
                    frame_ori = data[2]
                    list_count = data[3]

                    if (ind != -1):

                        # have_input = True

                        save_frame_ori = frame_ori.copy()
                        t1 = time.time()
                        boxs_show = data[4]
                        names_show = data[5]
                        color_show = data[6]
                        tails_show = data[7]

                        # ------------------ draw infor -----------------------

                        up_scale = 1 / tracking_scale_list[cam_index]

                        bbox_thick = int(0.6 * (frame_ori.shape[0] + frame_ori.shape[1]) / 1000)
                        if bbox_thick < 2:
                            bbox_thick = 2
                        font_face = cv2.FONT_HERSHEY_COMPLEX_SMALL
                        font_scale = 0.75 * bbox_thick

                        invert_scale = 1.0 / tracking_scale_list[cam_index]

                        for bbox, name, color, tail in zip(boxs_show, names_show, color_show, tails_show):

                            show_box = [int(bbox[0] * up_scale), int(bbox[1] * up_scale), int(bbox[2] * up_scale),
                                        int(bbox[3] * up_scale)]

                            # OLD
                            # cv2.rectangle(frame_ori, (show_box[0], show_box[1]), (show_box[2], show_box[3]), color,
                            #               bbox_thick)

                            # -----
                            # box_size = str(int((bbox[2] - bbox[0]) * up_scale)) + 'x' + str(
                            #     int((bbox[3] - bbox[1]) * up_scale))

                            # draw_caption(frame_ori, name, show_box, font_face, font_scale, (0, 0, 255), (255, 255, 0),
                            #              bbox_thick)
                            # -----

                            Len = len(tail)
                            if Len >= 4:
                                # cv2.line(frame_ori,(int(tail[0]*scale), int(tail[1]*scale)), (int(tail[Len-2])*scale, int(tail[Len-1])*scale),color, 2)
                                smooth_tail = graphic_utils.filter_tail(tail, 7)

                                # spline_tail = graphic_utils.spline_interpolation_fast(smooth_tail, Map_u)

                                spline_tail = smooth_tail

                                tail_lines = []
                                for i in range(0, len(spline_tail), 2):
                                    tail_lines.append([int(spline_tail[i] * up_scale), int(spline_tail[i + 1] * up_scale)])

                                points = np.array(tail_lines)
                                cv2.polylines(frame_ori, np.int32([points]), 0, color, bbox_thick, cv2.LINE_AA)

                        for tracking_regions in tracking_regions_list[cam_index]:
                            tracking_regions.draw_region(frame_ori, trackregion_color, bbox_thick, invert_scale, True, 1, 1)

                        show_logo(frame_ori, logo_info_list[cam_index])
                        frame_ori = counted_show(frame_ori, frame_ori.shape[1], frame_ori.shape[0], list_count, font_face,
                                                 font_scale * 1.2, bbox_thick)

                        # for regionbox in regionboxs_list[cam_index]:
                        #     regionbox.draw_region(frame_ori, boxregion_color, boxregion_thickness, 1/detection_scale_list[cam_index])

                        # for region in tracking_regions_list[cam_index]:
                        #     region.draw_region(frame_ori, trackregion_color, trackregion_thickness, 1/tracking_scale_list[cam_index], True, 1, 0)

                        # counted_show(frame_ori, frame_ori.shape[1], frame_ori.shape[0], list_count)

                        # put data in to face_mask_buffer
                        # frame_ori = cv2.resize(frame_ori, (640,480))
                        face_mask_buffer[cam_index].put([ind, frame_ori, list_count])

                        # ------------------ end draw infor -----------------------

                        t2 = time.time()

                        fps = (1. / (t2 - t1))
                        # print(" Visualization speed = %f fps"%(fps))

                        sum_time += (t2 - t1)
                        count += 1

                        # -----
                        # if videowrite_flag:
                        #     out[cam_index].write(save_frame_ori)
                        #     saved_frame_count_list[cam_index] += 1
                        #     currentfile_saved_frame_count_list[cam_index] += 1
                        #
                        #     if (currentfile_saved_frame_count_list[cam_index] >= num_of_frame_in_block_list[cam_index]):
                        #         out[cam_index].release()
                        #         currentfile_saved_frame_count_list[cam_index] = 0
                        #         saved_video_count_list[cam_index] += 1
                        #
                        #         out1, fps_video1 = VideoWriter_create(cam_index, time_save_videos_folder_list,
                        #                                               video_infor_list,
                        #                                               saved_frame_count_list[cam_index])
                        #
                        #         out[cam_index] = out1
                        # -----


                    else:

                        # put data in to face_mask_buffer
                        face_mask_buffer[cam_index].put([-1, frame_ori, list_count])
                        list_closed_cam[cam_index] = True

                        # -----
                        # if videowrite_flag:
                        #     if out[cam_index] is not None:
                        #         out[cam_index].release()
                        #         out[cam_index] = None

                        # if (cam_index == 0):
                        #     print(" Spend time 1: ", (t4-t3)/60, "min")
                        # -----
                    # put data into queue
                    # face_mask_buffer[cam_index].put([1, frame_ori, list_count])

                else:
                    time.sleep(no_job_sleep_time)


        if is_closed_all(list_closed_cam):

            print("[INFO]-- Visualization speed Ave: ", count / (sum_time), "fps")
            print('[INFO]-- Face mask threding waiting for stop')
            wait_stop.wait()

        elif (have_no_job):
            time.sleep(no_job_sleep_time)


    print("(0)--- Stopped Face Mask Threading")

    # time_end = time.time()
    #
    # count_test += 1
    # sum_test += time_end - time_start
    #
    # if (count_test % 30) == 0:
    #     print("Spend time: ", time_end - time_start)
    #     print("FPS: ", count_test / sum_test)
    #
    #     # if press_quit == True:
    #     #     break
    #     #
    #     # if is_closed_all(list_closed_cam):
    #     #     break
    #
    # if videowrite_flag:
    #     for i in range(len(out)):
    #         if (out[i] is not None):
    #             out[i].release()
    #
    # # print(" Visualization speed Ave: ", count / (sum_time), "fps")
    #
    # print('Visualization waiting for stop')
    # # wait_stop.wait()
    # print('--------------------------------------------------------------------test stoped')
    # # if backward_message is not None:
    # #     backward_message.put(["stop", "Stopped face recognition monitoring service"])


def parser_cam_infor(cam_infor_list):

    input_video_list = []
    cam_id_list = []
    frame_drop_list = []
    frame_step_list = []
    tracking_scale_list = []
    regionboxs_list = []
    tracking_regions_list = []


    for cam_infor in cam_infor_list:
        id = cam_infor["id"]
        url = cam_infor["url"]
        frame_drop = cam_infor["frame_drop"]
        frame_step = cam_infor["frame_step"]
        tracking_scale = cam_infor["tracking_scale"]

        ROIs_data = cam_infor["ROIs"]
        # print("ROIs_data: ", ROIs_data)
        regionbox_list = region_util.create_regionboxs(ROIs_data)

        tracking_regions_data = cam_infor["tracking_regions"]
        # print("tracking_regions_data: ", tracking_regions_data)
        tracking_region_list = region_util.create_tracking_regions(tracking_regions_data)

        # if cam_infor["enable"] == "yes":
        cam_id_list.append(id)
        input_video_list.append(url)
        frame_drop_list.append(frame_drop)
        frame_step_list.append(frame_step)
        tracking_scale_list.append(tracking_scale)
        regionboxs_list.append(regionbox_list)
        tracking_regions_list.append(tracking_region_list)

    return input_video_list, cam_id_list, frame_drop_list, frame_step_list, tracking_scale_list, regionboxs_list,\
           tracking_regions_list


def face_mask_run(config_file, face_mask_buffer, forward_message, backward_message, wait_stop, no_job_sleep_time):

    global min_face_size_list
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

    video_time_list = [""] * len(cam_id_list)
    min_face_size_list = [10] * len(cam_id_list)

    save_videos_folder_list = [os.path.join(save_videos_folder, id) for id in cam_id_list]
    save_faces_folder_list = [os.path.join(save_faces_folder, id) for id in cam_id_list]
    save_data_folder_list = [os.path.join(save_data_folder, id) for id in cam_id_list]

    # set globals
    gd.set_camera_id_list(cam_id_list)
    gd.set_video_time_list(video_time_list)
    # print("*" * 80, ".....set_camera_id_list.....")
    gd.make_dir_if_not_exist(save_videos_folder_list)
    gd.make_dir_if_not_exist(save_faces_folder_list)
    gd.make_dir_if_not_exist(save_data_folder_list)
    gd.set_time_name_is_now()

    time_save_videos_folder_list = gd.set_folder_save_video_face_data(save_videos_folder_list, save_faces_folder_list,
                                                                      save_data_folder_list)

    # t1 = time.time()


    face_mask(input_video_list, time_save_videos_folder_list, time_block_video, frame_drop_list, frame_step_list,
              tracking_scale_list, regionboxs_list, tracking_regions_list,view_width, view_height, grid_row, grid_col,
              face_mask_buffer, forward_message, backward_message, wait_stop, no_job_sleep_time)

    # t2 = time.time()
    # print("Spend time 2:", (t2 - t1) / 60, "min")

def face_mask_by_threading(config_file, face_mask_buffer, forward_message, backward_message, wait_stop, no_job_sleep_time):
    t = threading.Thread(target=face_mask_run, args=[config_file, face_mask_buffer, forward_message, backward_message,
                                                     wait_stop, no_job_sleep_time])
    t.start()