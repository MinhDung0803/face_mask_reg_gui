import sys
import threading
import time
import cv2
import detection_module
detection_module.load_model("./face_mask_model/best.pt", 416, device_str="cpu")


def is_closed_all(list_closed_queue):
	for closed in list_closed_queue:
		if not closed:
			return False

	return True


def sum_fps(info_videos):
	sum_val = 0
	for cam_index in range(len(info_videos)):
		sum_val += info_videos[cam_index][2]
	return sum_val


def num_frame_need_to_detect_in_1s(info_videos, list_step_frame):
	sum_val = 0

	for cam_index in range(len(info_videos)):
		sum_val += info_videos[cam_index][2] / list_step_frame[cam_index]

	return sum_val


def detecting(list_frame_image_buffer, detect_step_list, video_infor_list, detection_list_list_region,
							   min_face_size_list, list_detected_buffer, no_job_sleep_time, event_queue, wait_stop):

	print("(2)--- Running Face_Recognition_search_threading")

	num_frame_need_to_detect = num_frame_need_to_detect_in_1s(video_infor_list, detect_step_list)
	sum_frame_processing = sum_fps(video_infor_list)
	num_cam = len(list_frame_image_buffer)  # len(info_videos)

	list_closed_queue = [False for i in range(num_cam)]
	div_keep = [-1] * num_cam
	count = 0

	pausing = False

	while True:

		if event_queue.empty() != True:
			command = event_queue.get()

			if (command == "stop"):
				print("[INFO]-- Face_Recognition_search_threading is waitting to stop")
				wait_stop.wait()
				print("(2)--- Stoped Face_Recognition_search_threading")
				return
			elif (command == "pause/unpause"):
				pausing = not pausing
				if (pausing): print("[INFO]-- Detecting and Recognizing Threading is pausing")

		if (pausing):
			time.sleep(no_job_sleep_time)
			continue

		have_no_job = True

		time_detected_frame = 0
		time_recognized_face = 0
		num_detected_frame = 0
		num_recognized_face = 0

		for cam_index in range(num_cam):

			if (list_detected_buffer[cam_index].full() == False):

				if (list_frame_image_buffer[cam_index].empty() == False):

					have_no_job = False

					t1 = time.time()
					data = list_frame_image_buffer[cam_index].get()

					ind = data[0]
					frame_ori = data[1]

					if ind != -1:

						div = (ind // detect_step_list[cam_index])

						if div != div_keep[cam_index]:
							div_keep[cam_index] = div

							# headbody
							# head_boxes, _, head_scores, body_boxes, _, body_scores = \
							# 	detection_module.head_and_body_detection(frame_ori, head_score_threshold=0.5,
							# 											 body_score_threshold=0.6)
							# bboxes = head_boxes
							# scores = head_scores
							# class_ids = [0]*len(bboxes)

							# face _ body
							# wanted_labels = ("head", "head_2", "mask")
							# thresholds = (0.1, 0.1, 0.1)

							# call detect
							# bboxes, class_ids, scores = detection_module.face_mask_detection(frame_ori, wanted_labels, thresholds)
							bboxes, class_ids, scores, _ = detection_module.detect(frame_ori, 0.5, classes=None)


							# do not use
							# detection_inf = [head_boxes, head_scores, body_boxes, body_scores]

							# face mask
							# bboxes, class_ids, scores = mask_detection.detection(frame_ori, conf_thresh=0.3,
							# 													 iou_thresh=0.4,
							# 													 target_shape=(360, 360))
							for bbox, class_id in zip(bboxes, class_ids):
								color = (255, 0, 0)
								if class_id == 1:
									color = (0, 255, 0)
								elif class_id == 2:
									color = (0, 0, 255)
								cv2.rectangle(frame_ori, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 3)

							detection_inf = [bboxes, class_ids, scores]

						else:
							detection_inf = []

						list_detected_buffer[cam_index].put([ind, frame_ori, detection_inf])

					else:
						list_detected_buffer[cam_index].put([-1, frame_ori, []])
						list_closed_queue[cam_index] = True

		if is_closed_all(list_closed_queue):

			# print(' Face detection and recognition speed Ave: ', count/ (sum_time), "fps")

			print('[INFO]-- Detection waiting for stop')

			wait_stop.wait()
			return

		elif (have_no_job):
			time.sleep(no_job_sleep_time)

	print("(2)--- Stoped Face_Recognition_search_threading")


def detecting_by_threading(list_frame_image_buffer, detect_step_list, video_infor_list, detection_list_list_region, \
						   min_face_size_list, list_detected_buffer, no_job_sleep_time, event_queue, wait_stop):
	t = threading.Thread(target=detecting,
						 args=[list_frame_image_buffer, detect_step_list, video_infor_list, detection_list_list_region,
							   min_face_size_list, list_detected_buffer, no_job_sleep_time, event_queue, wait_stop])
	t.start()