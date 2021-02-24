import os
# from timeit import time
import warnings
import sys
import cv2
import numpy as np
import queue
import threading
import time

def release_all_video_capture(list_video_capture, list_released):
    for cap, released in zip(list_video_capture, list_released):
        if (released == False):
            cap.release()

def is_released_all(list_released):
    for rel in list_released:
        if rel == False:
            return False
    
    return True

def read_video(list_filename, list_num_framedrop, list_frame_image_buffer, no_job_sleep_time, event_queue, wait_stop):
    """
        full_delay_time is num of second to set sleep time
    """
    print("(1)--- Running Read_video_threading")
    num_cam = len(list_filename)

    list_video_capture = []
    list_video_infor = []

    for filename in list_filename:
        video_capture = cv2.VideoCapture(filename)
        w = int(video_capture.get(3))
        h = int(video_capture.get(4))
        ori_fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_len = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        is_camera = (filename.find("://") != -1)
        
        list_video_capture.append(video_capture)

        list_video_infor.append((w, h, ori_fps, frame_len, is_camera))


        # Only for testing
        # video_capture.set(cv2.CAP_PROP_POS_FRAMES, 310 * 3)


    list_released_cam = [False]*num_cam

    list_frameCount = [0]*num_cam
    list_frame_index = [-1]*num_cam
    sum_time = 0
    count = 0
    
    pausing = False
    read_unsuccessful_count = 0

    pause_start = None
    pause_stop = None
    pause_to_disconection = None

    while True:
        
        if event_queue.empty() != True:
            command = event_queue.get()

            if (command == "stop"):
                release_all_video_capture(list_video_capture, list_released_cam)
                wait_stop.wait()
                print("(1)--- Stoped Read_video_threading")
                return
            elif (command == "pause/unpause"):
                pausing = not pausing

                if pausing:  # camera release
                    for cam_index in range(num_cam):
                        if list_video_infor[cam_index][4] is True:
                            list_video_capture[cam_index].release()
                else: # camera open
                    for cam_index in range(num_cam):
                        if list_video_infor[cam_index][4] is True:
                            list_video_capture[cam_index] = cv2.VideoCapture(filename)


        if (pausing):
            time.sleep(no_job_sleep_time)
            continue


        have_no_job = True

        for cam_index in range(num_cam):

            if (not list_released_cam[cam_index]) and (list_frame_image_buffer[cam_index].full() == False):
                
                have_no_job = False

                cap = list_video_capture[cam_index]

                # t1 = time.time()

                ret, frame_ori = cap.read()

                # t2 = time.time()

                w, h, ori_fps, frame_len, is_camera = list_video_infor[cam_index]

                # if list_frameCount[cam_index] > 100:
                #     ret = False
                #     list_frame_image_buffer[cam_index].put([-1, None])
                #     list_released_cam[cam_index] = True
                #     break

                if ret != True:

                    print("@" * 80)
                    print("Camera {} capture stopped".format(cam_index))

                    read_unsuccessful_count += 1

                    current_frame_index = list_frameCount[cam_index]  # cap.get(cv2.CAP_PROP_POS_FRAMES)


                    if (frame_len > current_frame_index) and (read_unsuccessful_count <=100):  # (frameLen - 1 > cap.get(cv2.CAP_PROP_POS_FRAMES)):

                        # print("--------------------------(ret != True)-------------------------",frameLen - 1 , current_frame_index)
                        # cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, current_frame_index + 2)

                        continue

                    list_frame_image_buffer[cam_index].put([-1, frame_ori]) # index = -1 for Stoped, Frame is empty
                    cap.release()
                    list_released_cam[cam_index] = True

                else:

                    count += 1

                    read_unsuccessful_count = 0
                    # frame = cv2.resize(frame_ori, ((w//2), (h//2)) , interpolation = cv2.INTER_CUBIC)

                    list_frameCount[cam_index] += 1

                    # if (list_frameCount[cam_index] < 310*3):
                    #     continue
                    # elif (list_frameCount[cam_index] > 450*3):
                    #     list_frame_image_buffer[cam_index].put([-1, frame_ori])
                    #     cap.release()
                    #     list_released[cam_index] = True
                    #
                    #     break

                    if int(list_frameCount[cam_index]) % int(list_num_framedrop[cam_index]) != 0:
                        continue
                                    
                    list_frame_index[cam_index] += 1

                    # print("read frame: ",frameCount)
                    # print("read Index: ",frame_index)
                    # print("list_frame_index[i]---------------", list_frame_index[i])

                    list_frame_image_buffer[cam_index].put([list_frame_index[cam_index], frame_ori])

        if is_released_all(list_released_cam):

            print('Read-Video waiting for stop')
            wait_stop.wait()
            return    
        elif (have_no_job):
            time.sleep(no_job_sleep_time)

    print("(1)--- Stoped Read_video_threading")

def read_video_by_threading(list_filename, list_num_framedrop, list_frame_image_buffer, no_job_sleep_time, event_queue, wait_stop):
    """
        full_delay_time is num of second to set sleep time
    """
    t = threading.Thread(target=read_video, args=[list_filename, list_num_framedrop, list_frame_image_buffer, no_job_sleep_time, event_queue, wait_stop])
    t.start()

