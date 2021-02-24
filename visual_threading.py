import threading
import time
import cv2
from mask_utils import graphic_utils
import numpy as np
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def get_info_video(fullfilename):

    video_capture = cv2.VideoCapture(fullfilename)
    width = int(video_capture.get(3))
    height = int(video_capture.get(4))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    video_capture.release()

    return width, height, fps


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


def visual(input_video_list, list_trackted_buffer, tracking_scale_list,tracking_regions_list, list_visual_buffer,
           no_job_sleep_time, event_queue, wait_stop):

    print("(8)--- Running Tracking_threading")

    trackregion_color = (0, 255, 255)
    num_cam = len(input_video_list)

    logo_file = os.path.join(ROOT_DIR, "pictures/LogoTCX_small.png")
    max_fps = 0
    logo_info_list = []

    for cam_index in range(num_cam):
        width1, height1, fps_video1 = get_info_video(input_video_list[cam_index])
        # video_infor_list.append([width1, height1, fps_video1])
        if (max_fps < fps_video1):
            max_fps = fps_video1

        # load logo
        logo_rgb_image, invert_alpha_channel = read_transparent_png_and_scale(logo_file, width1, height1, 0.12)
        logo_info_list.append([logo_rgb_image, invert_alpha_channel])

    pausing = False

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

            trackted_buffer = list_trackted_buffer[cam_index]
            if trackted_buffer.empty() == False:
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

                        cv2.rectangle(frame_ori, (show_box[0], show_box[1]), (show_box[2], show_box[3]), color,
                                      bbox_thick)

                        # box_size = str(int((bbox[2] - bbox[0]) * up_scale)) + 'x' + str(
                        #     int((bbox[3] - bbox[1]) * up_scale))

                        # draw_caption(frame_ori, name, show_box, font_face, font_scale, (0, 0, 255), (255, 255, 0),
                        #              bbox_thick)

                        Len = len(tail)
                        if Len >= 4:
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

                    frame_result = cv2.resize(frame_ori, (640,480))

                    list_visual_buffer[cam_index].put([ind, frame_result])

                else:
                    list_visual_buffer[cam_index].put([-1, frame_ori])

    print("(8)--- Stopped Tracking_threading")

def visual_by_threading(input_video_list, list_trackted_buffer, tracking_scale_list, tracking_regions_list,
                        list_visual_buffer, no_job_sleep_time, event_queue, wait_stop):
    t = threading.Thread(target=visual, args=[input_video_list, list_trackted_buffer, tracking_scale_list,
                                              tracking_regions_list, list_visual_buffer, no_job_sleep_time, event_queue,
                                              wait_stop])
    t.start()