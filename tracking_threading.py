import os
import sys
import cv2
import numpy as np
import math
import threading
import time

from mask_utils import graphic_utils
from fast_tracking import fast_tracker
from mask_utils import global_variable_define as gd

def get_valid_inside(im_width, im_height, boxs_tlbr, infor_list=None):

    re_boxs_tlbr = []
    re_infor_list = []
    
    for i in range(len(boxs_tlbr)):
        if (boxs_tlbr[i][0] > 0) and (boxs_tlbr[i][1] > 0) and (boxs_tlbr[i][2] < im_width) and (boxs_tlbr[i][3] < im_height):
           re_boxs_tlbr.append(boxs_tlbr[i])
           if infor_list != None:
               re_infor_list.append(infor_list[i])

    return re_boxs_tlbr, re_infor_list

def get_valid_inside_and_fix_small_error(im_width, im_height, boxs_tlbr, percent, infor_list):
    re_boxs_tlbr = []
    re_infor_list = [[] for x in range(len(infor_list))]
    for index, box in enumerate(boxs_tlbr):
        box_width, box_height = (box[2] - box[0]), (box[3] - box[1])
        if (box[0] > 0) and (box[1] > 0) and (box[2] < im_width) and (box[3] < im_height):
            re_boxs_tlbr.append(box)
            for k in range(len(infor_list)):
                re_infor_list[k].append(infor_list[k][index])
        else:
            if (box[0] < 0) and (-box[0] / box_width < percent):
                box[0] = 0
            else:
                continue
            if (box[1] < 0) and (-box[1] / box_height < percent):
                box[1] = 0
            else:
                continue
            if (box[2] >= im_width) and ((box[2] - im_width) / box_width < percent):
                box[2] = im_width - 1
            else:
                continue
            if (box[3] >= im_height) and ((box[3] - im_height) / box_height < percent):
                box[3] = im_height - 1
            else:
                continue
            re_boxs_tlbr.append(box)
            for k in range(len(infor_list)):
                re_infor_list[k].append(infor_list[k][index])
    return re_boxs_tlbr, re_infor_list


# def get_valid_inside_and_fix_small_error(im_width, im_height, boxs_tlbr, percent, infor_list=None):
#     re_boxs_tlbr = []
#     re_infor_list = []
#
#     for index, box in enumerate(boxs_tlbr):
#         box_width, box_height = (box[2] - box[0]), (box[3] - box[1])
#         if (box[0] > 0) and (box[1] > 0) and (box[2] < im_width) and (box[3] < im_height):
#             re_boxs_tlbr.append(box)
#             if infor_list != None:
#                 re_infor_list.append(infor_list[index])
#         else:
#             if (box[0] < 0) and (-box[0]/box_width < percent):
#                 box[0] = 0
#             else:
#                 continue
#
#             if (box[1] < 0) and (-box[1]/box_height < percent):
#                 box[1] = 0
#             else:
#                 continue
#
#             if (box[2] >= im_width) and ((box[2] - im_width)/box_width < percent):
#                 box[2] = im_width -1
#             else:
#                 continue
#
#             if (box[3] >= im_height) and ((box[3] - im_height)/box_height < percent):
#                 box[3] = im_height - 1
#             else:
#                 continue
#
#             re_boxs_tlbr.append(box)
#             if infor_list != None:
#                 re_infor_list.append(infor_list[index])
#
#     return re_boxs_tlbr, re_infor_list


def get_inside_regions_2(list_region, boxs_tlbr, infors_list=None):
    re_boxs = []

    print("@" * 30, "boxs_tlbr (1) : ", boxs_tlbr)
    print("@"*30, "infors_list (1) : ", infors_list)

    if infors_list != None:
        len_infors_list = len(infors_list)
        re_infors_list = [[] for i in range(len_infors_list)]
    else:
        len_infors_list = 0
        re_infors_list = None

    for k in range(len(list_region)):

        list_point = graphic_utils.get_list_bottom_mid_of_box_tlbr(boxs_tlbr)

        inside_indexs = graphic_utils.get_list_index_inside(list_point, list_region[k].list_point)

        for i in range(len(inside_indexs)):
            if inside_indexs[i]:
                re_boxs.append(boxs_tlbr[i])
                if len_infors_list > 0:
                    for j in range(len_infors_list):
                        print("j = {}, i = {}".format(j, i))
                        re_infors_list[j].append(infors_list[j][i])

    # print("@" * 30, "re_boxs (2) : ", re_boxs)
    # print("@" * 30, "re_infors_list (2) : ", re_infors_list)

    return re_boxs, re_infors_list

def scale_box(boxs, int_scale):
    for i in range(len(boxs)):
        boxs[i][0] *= int_scale
        boxs[i][1] *= int_scale
        boxs[i][2] *= int_scale
        boxs[i][3] *= int_scale
    return boxs

def scale_list_boxes(list_boxes, scale):
    for i in range(len(list_boxes)):
        length = len(list_boxes[i])
        for j in range(length):
            list_boxes[i][j][0] = int(scale * list_boxes[i][j][0])
            list_boxes[i][j][1] = int(scale * list_boxes[i][j][1])
            list_boxes[i][j][2] = int(scale * list_boxes[i][j][2])
            list_boxes[i][j][3] = int(scale * list_boxes[i][j][3])
    return

def inside_regions(list_region, point2d):
    for i in range(len(list_region)):
        if (list_region[i].is_inside(point2d)):
            return True


def is_closed_all(list_closed_cam):
    for closed in list_closed_cam:
        if closed == False:
            return False

    return True

def remove_small_size(area_thres, boxs_det, names_det, scores_det, ids_det):
    boxs = []
    names = []
    scores = []
    ids = []

    for i in range(len(boxs_det)):
        if (boxs_det[i][2] - boxs_det[i][0])*(boxs_det[i][3] - boxs_det[i][1]) > area_thres :
            boxs.append(boxs_det[i].copy())
            names.append(names_det[i])
            scores.append(scores_det[i])
            ids.append(ids_det[i])

    return boxs, names, scores, ids

def tracking(list_detected_buffer, export_data_buffer, tracking_scales, video_infor_list, list_list_region, list_trackted_buffer, no_job_sleep_time, event_queue, wait_stop):
    """
        full_delay_time is num of second to set sleep time
    """
    print("(4)--- Running Tracking_threading")

    num_cam = len(list_detected_buffer)
    # list_closed_queue = [[False, False]] * num_cam # 2 queue list_detected_buffer and list_faceID_buffer is closed

    list_closed_queue = []
    list_counting_dictionaries = []

    for i in range(num_cam):
        list_closed_queue.append(False)
        list_counting_dictionaries.append([{'Person': 0, 'None face-mask': 0}])


    print("------------------------------------------------- list_closed_queue = ", list_closed_queue)

    list_tracker = [fast_tracker.FastTracker(camera_index=cam_index) for cam_index in range(num_cam)]


    sum_time = 0
    count = 0
    pausing = False
    update_view = False

    while True:
        
        if event_queue.empty() != True:
            command = event_queue.get()

            if (command == "stop"):
                wait_stop.wait()
                print("(4)--- Stoped Tracking_threading")
                return
            elif (command == "pause/unpause"):
                pausing = not pausing
                if (pausing):   print("Tracking Threading is pausing")
            elif (command == "update-view"):
                update_view = not update_view

        if (pausing):
            time.sleep(no_job_sleep_time)
            continue

        have_no_job = True

        for cam_index in range(num_cam):

            tracker = list_tracker[cam_index]

            if (list_trackted_buffer[cam_index].full() == False):
                if (list_detected_buffer[cam_index].empty() == False):

                    have_no_job = False

                    data = list_detected_buffer[cam_index].get()

                    ind = data[0]
                    frame_ori = data[1]

                    if (ind != -1):

                        t1 = time.time()
                        detection_inf = data[2]

                        if len(detection_inf) > 0:
                            bboxes, class_ids, scores = detection_inf
                            face_bboxs, face_scores, detected_face_infor_list, nor_body_images = [], [], [], []
                        else:
                            bboxes, class_ids, scores = [], [], []

                        trk_scale = tracking_scales[cam_index]
                        frame = cv2.resize(frame_ori, (int(video_infor_list[cam_index][0] * trk_scale), int(video_infor_list[cam_index][1] * trk_scale)))

                        tracker.predict(frame, ind)
                        # tracker.predict_visualization(frame_ori, 1/tracking_scales[cam_index])

                        # change for head_boxes
                        if len(bboxes) > 0:

                            scale_list_boxes([bboxes], tracking_scales[cam_index])

                            bboxes, re_infors_list = get_inside_regions_2(list_list_region[cam_index], bboxes,
                                                                          infors_list=[class_ids, scores])
                            class_ids, scores = re_infors_list

                            bboxes, re_infors_list = get_valid_inside_and_fix_small_error(frame.shape[1],
                                                                                           frame.shape[0],
                                                                                           bboxes, 0.2,
                                                                                          [class_ids, scores])
                            class_ids, scores = re_infors_list

                            head_mask_infor = [bboxes, class_ids, scores]
                            tracker.update_detected_objects(head_mask_infor, frame, ind, frame)


                        tracker.counter(list_list_region[cam_index], list_counting_dictionaries[cam_index], frame, ind)

                        tracker.delete_outside(list_list_region[cam_index], frame)


                        boxs_show, names_show, color_show, tails_show = tracker.get_infor(update_view)

                        list_counts_show = []
                        for list_count in list_counting_dictionaries[cam_index]:
                            list_counts_show.append(list_count.copy())

                        list_trackted_buffer[cam_index].put([ind, frame, frame_ori, list_counts_show, boxs_show, names_show, color_show, tails_show])
                        
                        t2 = time.time()
                        # print(' Tracking speed: ', 1/(t2 - t1), "fps")
                        sum_time += (t2 - t1)
                        count += 1

                    else:
                        
                        tracker.export_alldata_for_destroy()
                        list_trackted_buffer[cam_index].put([-1, frame, frame_ori, [], [], [], [], []])
                        list_closed_queue[cam_index] = True

        if is_closed_all(list_closed_queue):

            print(' Tracking speed Ave: ', count/ (sum_time), "fps")



            export_data_buffer.put([gd.Export_Case.stopped_command, "Stop all camera"])

            print('Tracking waiting for stop')

            wait_stop.wait()
            return
        elif (have_no_job):
            time.sleep(no_job_sleep_time)

    print("(4)--- Stoped Tracking_threading")


def tracking_by_threading(list_detected_buffer, export_data_buffer, tracking_scales, video_infor_list, list_list_region, list_trackted_buffer, no_job_sleep_time, event_queue, wait_stop):
    """
        full_delay_time is num of second to set sleep time
    """

    t = threading.Thread(target=tracking, args=[list_detected_buffer, export_data_buffer, tracking_scales, video_infor_list, list_list_region, list_trackted_buffer, no_job_sleep_time, event_queue, wait_stop])
    t.start()

