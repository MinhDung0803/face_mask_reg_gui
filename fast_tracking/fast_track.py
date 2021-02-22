import os
from datetime import datetime, timedelta
import cv2
import numpy as np
import time

from mask_utils import graphic_utils
from mask_utils import global_variable_define as gd

_unknown_ID_ = -1  # must be asign true value later

#--- begin: for face detection demo only
NOTIFY_TIME_INTERVAL = 3
EXPORT_API = True  # Assign to False for save data in local disk

#--- end: for face detection demo only

debug_win_title = "show image for debug"


#***********************************************************************************

class TrackState:
    """
    Enumeration type for the single target track state. Newly created tracks are
    classified as `tentative` until enough evidence has been collected. Then,
    the track state is changed to `confirmed`. Tracks that are no longer alive
    are classified as `deleted` to mark them for removal from the set of active
    tracks.

    """

    Tentative = 1
    Confirmed = 2
    Deleted = 3

#***********************************************************************************

class FastTrack:
    """
    Idea: Quá trình tracking gồm có 3 giai đoạn: 
    Chú ý: Bộ Detector có thể cung cấp hình ảnh để update nhưng gián đoạn cao về thời gian, đây là một thách thức lớn.

    1. Giai đoạn thăm dò (Tentative): 
 
    2. Giai đoạn tham chiếu (Confirmed): 
        
    3. Giai đoạn hủy theo dõi (Deteted): 
       
    Parameters
    ----------


    Attributes
    ----------

    """

    # ***********************************************************************************

    def __init__(self, root_bbox, track_id, class_name, mask_id,\
            max_age_init, max_age, max_update_pass_init, image, frame_index, camera_index,\
            match_threshold=0.15, match_threshold2=0.20, x_move_threshold=100, y_move_threshold=100):

        self._KILL_SIZE_ = 10
        # root bounding box [x1,y1,x2,y2] (left_top and right_bottom)
        self.root_bbox = root_bbox.copy()
        self.track_id = track_id
        self.class_name = class_name

        # if self.time_since_update is langer than self.max_age then delete track
        self.max_age = max_age
        # when status = tentative, if time_since_update_tentative is langer than max_age_init then delete track
        self.max_age_init = max_age_init
        # if self.count_updated_tentative >= self.max_update_pass_init then pass to Confirm
        self.max_update_pass_init = max_update_pass_init

        self.ori_obj_img = image[root_bbox[1]:root_bbox[3], root_bbox[0]:root_bbox[2], :].copy()
        self.shot_image = np.copy(self.ori_obj_img)
        self.IMAGE_SHAPE = image.shape
        self._begin_frame_index = frame_index
        self._end_frame_index = frame_index
        self.match_threshold = match_threshold
        self.match_threshold2 = match_threshold2

        self.x_move_threshold = x_move_threshold
        self.y_move_threshold = y_move_threshold
        
        self.time_since_update = 0
        self.last_update_is_success = True
        self.time_since_predict = 0
        
        self.time_at_last_PredictOrDetect = -1
        self.state = TrackState.Tentative
        if self.max_age_init <= 1:
            self.state = TrackState.Confirmed
            
        self.age = 0  # num of false pass

        # cv2.TM_CCOEFF_NORMED #  cv2.TM_CCORR_NORMED  #   cv2.TM_CCORR_NORMED # cv2.TM_CCOEFF_NORMED
        self.matchTemplateMethod = cv2.TM_SQDIFF_NORMED
        # it is tail of moving object, store as [x1 y1 x2 y2 x3 y3 ...]
        self.moving_list = [(self.root_bbox[0]+self.root_bbox[2])//2, self.root_bbox[3]]
        # 3600 elements = 1800 points = 1 min with video format is 30fps
        self.__MAX_TAIL = 3600

        self.count_updated_tentative = 0
        self.score_predict = 0
        self.score_predict_normed = 0
        self.bbox_predict_fail = []
        self.match_level2 = False
        self.counted = False
        self.camera_index = camera_index
        self.camera_id = gd.camera_id_list[camera_index]
        self.video_time = gd.video_time_list[self.camera_index]

        self._begin_datetime_ = self.get_ref_datetime(frame_index)
        self._end_datetime_ = self._begin_datetime_

        # for predict position of object
        self.predict_filter = [2 / 10, 3 / 10, 5 / 10]
        self.predict_filter_2 = [4 / 10, 6 / 10]
        # list of the bounding box of the object from past to present, len(position_list) <= len(predict_filter)
        self.past_bboxs = [((root_bbox[0] + root_bbox[2])/2, (root_bbox[1] + root_bbox[3])/2,
                           (root_bbox[2] - root_bbox[0]), (root_bbox[3] - root_bbox[1]))]  # (cx, cy, w, h)
        self.predict_pos = None
        self.predict_box = None
        self.dic_mask_id = {}
        self.dic_mask_id[mask_id] = 1

        print("@"*80)
        print("track_id : ", track_id)

    # ***********************************************************************************
    def get_ref_datetime(self, frame_index):
        if self.video_time is None:
            return datetime.now()
        else:
            offset_second = (frame_index / gd.video_infor_list[self.camera_index][2])
            return self.video_time + timedelta(0, seconds=offset_second)


    # ***********************************************************************************
    def normalization_moving_list(self):
        nor_moving_list = []
        height, width = self.IMAGE_SHAPE[0:2]
        for i in range(0, len(self.moving_list) - 1, 2):
            nor_moving_list += [self.moving_list[i]/width, self.moving_list[i+1]/height]

        return nor_moving_list

    # ***********************************************************************************
    def export_tracking_person(self, export_case, head_image=None):

        # print("--------- call export_tracking_person")
        if export_case == gd.Export_Case.tracking_data:

            if export_case == gd.Export_Case.tracking_data:
                # print("Time : {0} - {1}".format(self._begin_datetime_, self._end_datetime_))

                cam_id = gd.camera_id_list[self.camera_index]

                face_tracking_data = [
                    cam_id,
                    self.track_id,
                    self._begin_datetime_,
                    self._end_datetime_,
                    self._begin_frame_index,
                    self._end_frame_index,
                ]

                gd.export_data_buffer.put([export_case, face_tracking_data])

        elif export_case == gd.Export_Case.found_person_in_blacklist:
            print("gd.Export_Case.found_person_in_blacklist")

    # ***********************************************************************************
    def set_delete(self, export_data=True):
        
        if self.state == TrackState.Deleted:
            return

        self.state = TrackState.Deleted

        self._end_datetime_ = self.get_ref_datetime(self._end_frame_index)

        if export_data is True:
            self.export_tracking_person(gd.Export_Case.tracking_data)


        self.root_bbox = None
        self.ori_obj_img = None

        if self.moving_list is not None:
            # self.moving_list.clear()  # done clear "self.moving_list" because it put to export_data_buffer 
            self.moving_list = None

    # ***********************************************************************************
    def delete_older(self):
        if (self.time_since_update > self.max_age):
            self.set_delete()

    # ***********************************************************************************
    def is_past_life(self, past_track):

        if (self._begin_frame_index > past_track._begin_frame_index):
            time_at_last_Detect = past_track.time_at_last_PredictOrDetect # Detected face or Update track
            if (past_track.time_since_predict < past_track.time_since_update):
                time_at_last_Detect -= (past_track.time_since_update - past_track.time_since_predict)

            return (self._begin_frame_index > time_at_last_Detect)
                
        return False

    # ***********************************************************************************
    def Set_MAX_TAIL(self, val):
        self.__MAX_TAIL = val

    # ***********************************************************************************
    def get_center(self):
        """Get newest center position of predict or update object. It is centre of root_bbox + (newest_move_x, newest_move_y).

        """
        
        return [(self.root_bbox[0] + self.root_bbox[2])/2, (self.root_bbox[1] + self.root_bbox[3])/2]

    # ***********************************************************************************
    def get_tail_point(self):
        """Get newest tail position of predict or update object. It is tail of root_bbox.

        """
        return [(self.root_bbox[0] + self.root_bbox[2])//2, self.root_bbox[3]]

    # ***********************************************************************************
    def add_bbox_with_vector(self, bbox, vector):
        box = [bbox[0] + vector[0], bbox[1] + vector[1], bbox[2] + vector[0], bbox[3] + vector[1]]

        return box

    # ***********************************************************************************
    def get_ref_rectangle(self, imWidth, imHeight):

        if self.predict_box is None:
            # vùng hình chữ nhật gốc (root_bbox) được mở rộng phạm vi ra bởi vector (x_move_threshold, y_move_threshold)
            rec = self.root_bbox.copy()
            dx = self.x_move_threshold
            dy = self.y_move_threshold
        else:
            rec = self.predict_box.copy()
            dx = (self.predict_box[2] - self.predict_box[0])//2
            dy = (self.predict_box[3] - self.predict_box[1])//2
            if (rec[2] - rec[0]) + 2*dx <= self.ori_obj_img.shape[1]:
                dx = (self.ori_obj_img.shape[1] - (rec[2] - rec[0]))//2 + 5
            if (rec[3] - rec[1]) + 2*dy <= self.ori_obj_img.shape[0]:
                dy = (self.ori_obj_img.shape[0] - (rec[3] - rec[1]))//2 + 5

        rec[0] -= dx
        rec[2] += dx
        rec[1] -= dy
        rec[3] += dy

        if rec[0] < 0:
            rec[0] = 0
        if rec[1] < 0:
            rec[1] = 0
        
        if rec[2] >= imWidth:
            rec[2] = imWidth - 1
        if rec[3] >= imHeight:
            rec[3] = imHeight - 1

        return rec

    # ***********************************************************************************
    def match_template_roi(self, image):

        rec = self.get_ref_rectangle(image.shape[1], image.shape[0])

        ROI_image = image[rec[1]:rec[3]+1, rec[0]:rec[2]+1, :]

        if (rec[0] >= rec[2]) or (rec[1] >= rec[3]) or (ROI_image.shape[0] <= self.ori_obj_img.shape[0]) or \
                (ROI_image.shape[1] <= self.ori_obj_img.shape[1]):
            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if self.matchTemplateMethod in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = None
                val = 10000
            else:
                top_left = None
                val = 0

            return val, None


        # print("@"*120)
        # print("ROI_image = {}, self.ori_obj_img = {}".format(ROI_image.shape[0:2], self.ori_obj_img.shape[0:2]))
        res = cv2.matchTemplate(ROI_image, self.ori_obj_img, self.matchTemplateMethod)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if self.matchTemplateMethod in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
            val = min_val
        else:
            top_left = max_loc
            val = max_val

        bottom_right = (top_left[0] + (self.root_bbox[2]-self.root_bbox[0]), top_left[1] + (self.root_bbox[3]-self.root_bbox[1]))
        
        bbox = [top_left[0], top_left[1],bottom_right[0], bottom_right[1]] # bounding box in ROI_image

        # Need map to Image (or Frame)
        box = self.add_bbox_with_vector(bbox, rec[:2])

        return val, box

    # ***********************************************************************************
    def match_template(self, image):
        score, bbox = self.match_template_roi(image)
        self.score_predict = score
        if self.matchTemplateMethod in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            self.score_predict_normed = - self.score_predict
        else:
            self.score_predict_normed = self.score_predict

        if (score <= self.match_threshold) or (self.predict_pos is not None):  # success

            if score <= self.match_threshold:
                self.reset_root_bbox_and_image(bbox, image)
            elif self.predict_pos is not None:
                self.reset_root_bbox_and_image(self.predict_box, image)

            self.update_position_list(self.root_bbox, append=True)

            return True

        elif score <= self.match_threshold2:
            self.bbox_predict_fail = bbox.copy()
            self.match_level2 = True

            if len(self.past_bboxs) <= len(self.predict_filter_2):
                self.reset_root_bbox_and_image(bbox, image)
                self.update_position_list(self.root_bbox, append=True)
                return True

            return False
        else:
            self.match_level2 = False

            return False

    # ***********************************************************************************
    def update_position_list(self, bbox, append=True, clear=False):
        if clear:
            self.past_bboxs.clear()
            self.predict_pos = None
            self.predict_box = None
            return

        if (self.past_bboxs is []) or append:
            self.past_bboxs.append(
                ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2, bbox[2] - bbox[0], bbox[3] - bbox[1]))
            if len(self.past_bboxs) > len(self.predict_filter) + 1:
                del self.past_bboxs[0]
        else:
            self.past_bboxs[-1] = (
            (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2, bbox[2] - bbox[0], bbox[3] - bbox[1])

    # ***********************************************************************************
    def predict_position_by_filter(self, predict_filter):

        len_filter = len(predict_filter)
        len_pos_list = len(self.past_bboxs)
        if len_pos_list < (len_filter + 1):
            self.predict_pos = None
            self.predict_box = None

            return

        delta_x, delta_y, delta_w, delta_h = 0, 0, 0, 0

        for index in range(len_pos_list - 1):
            cx1, cy1, w1, h1 = self.past_bboxs[index]
            cx2, cy2, w2, h2 = self.past_bboxs[index+1]
            delta_x += (cx2 - cx1) * predict_filter[index]
            delta_y += (cy2 - cy1) * predict_filter[index]
            delta_w += (w2 - w1) * predict_filter[index]
            delta_h += (h2 - h1) * predict_filter[index]

        delta_x = int(delta_x)
        delta_y = int(delta_y)
        current_cx, current_cy, current_w, current_h = self.past_bboxs[-1]

        self.predict_pos = (current_cx + delta_x, current_cy + delta_y)
        predict_w = current_w + delta_w
        predict_h = current_h + delta_h

        self.predict_box = [int(self.predict_pos[0] - predict_w/2), int(self.predict_pos[1] - predict_h/2),
                            int(self.predict_pos[0] + predict_w / 2), int(self.predict_pos[1] + predict_h / 2)]

        return

    # ***********************************************************************************
    def predict_position(self):

        len_filter = len(self.predict_filter)
        len_filter_2 = len(self.predict_filter_2)
        len_pos_list = len(self.past_bboxs)
        if len_pos_list < (len_filter_2 + 1):
            self.predict_pos = None
            self.predict_box = None

            return
        elif len_pos_list == (len_filter_2 + 1):
            self.predict_position_by_filter(self.predict_filter_2)
        else:
            self.predict_position_by_filter(self.predict_filter)

        return

    # ***********************************************************************************
    def predic_tentative(self, image, frame_index): # hoạt động thường xuyên theo định kỳ (ví dụ bằng với tốc độ khung hình của video)

        self.time_since_predict +=1
        self.time_since_update +=1 # đếm theo predict, vì hàm update có thể không thực hiện vì không tìm được Object phù hợp

        
        if self.match_template(image):
            self.time_since_predict = 0

            if (self.count_updated_tentative >= self.max_update_pass_init):
                # Change to Confirmed
                self.state = TrackState.Confirmed
                return

        
        if (self.time_since_update > self.max_age_init):
            self.set_delete()
    
    # 2. Giai đoạn tham chiếu (Confirmed): 

    # ***********************************************************************************
    def predict(self, image, frame_index):

        if (self.state == TrackState.Tentative):
            self.predic_tentative(image, frame_index)
            return

        self.predict_position()

        self.time_since_predict += 1
        self.time_since_update += 1  # đếm theo predict, vì hàm update có thể không thực hiện vì không tìm được Object phù hợp

        self.age += 1

        if self.match_template(image):
            self.time_since_predict = 0
            self.time_at_last_PredictOrDetect = frame_index


        if (self.time_since_update > self.max_age):
            self.set_delete()
            return

        if (self.ori_obj_img.shape[0] < self._KILL_SIZE_) or (self.ori_obj_img.shape[1] < self._KILL_SIZE_):
            self.set_delete()
            return
           
        if (self.state == TrackState.Confirmed) and (len(self.moving_list) >= self.__MAX_TAIL):
            old_len = len(self.moving_list)
            # t1 = time.time()
            graphic_utils.reduce_size_of_long_tail(self.moving_list)
            # t2 = time.time()
            # print("Reduce size of long tail had spend time ", t2-t1)
            new_len = len(self.moving_list)
            print("reduce size of long tail from {0} to {1}".format(old_len, new_len))

    def update_mask_id(self, mask_id):
        if mask_id in self.dic_mask_id:
            self.dic_mask_id[mask_id] += 1
        else:
            self.dic_mask_id[mask_id] = 1

    # ***********************************************************************************
    def update(self, detection_inf, image, frame_index):
        """ this methode may be call many time in a frame cycle """
        # det_face_infor_list -> list of [bbox, landmark, angles, aligned, fsharp, extface]

        bbox, mask_id, score = detection_inf

        if self.time_since_predict == 0:  # Predict success

            v1, v2 = graphic_utils.overlap(self.root_bbox, bbox)

            if (v1 >= 0.10) or (v2 >= 0.10):
                self.time_since_update = 0
                self.time_at_last_PredictOrDetect = frame_index

                self.reset_root_bbox_and_image(bbox, image)
                self.update_position_list(self.root_bbox, append=False)

                self._end_frame_index = frame_index
                self.last_update_is_success = True
                self.update_mask_id(mask_id)

                return 0  # update success

        else:

            v1, v2 = 0, 0
            # if self.match_level2:
            #     v1, v2 = graphic_utils.overlap(self.bbox_predict_fail, head_bbox)
            # else:
            #     v1, v2 = graphic_utils.overlap(self.root_bbox, head_bbox)

            v1, v2 = graphic_utils.overlap(self.root_bbox, bbox)

            if (v1 >= 0.30) or (v2 >= 0.30):
                self.time_since_update = 0
                self.time_at_last_PredictOrDetect = frame_index

                self.reset_root_bbox_and_image(bbox, image)
                self.update_position_list(self.root_bbox, append=True)

                self._end_frame_index = frame_index
                self.last_update_is_success = True
                self.update_mask_id(mask_id)

                return 0  # update success

        self.update_position_list(self.root_bbox, append=True, clear=True)

        return 1  # update unsuccessful

    # ***********************************************************************************
    def fix_in_image(self, bbox, im_width, im_height):
        re_box = bbox[:]
        if (re_box[0] < 0):
            re_box[0] = 0
        if (re_box[1] < 0):
            re_box[1] = 0

        if (re_box[2] >= im_width):
            re_box[2] = im_width -1
        if (re_box[3] >= im_height):
            re_box[3] = im_height -1

        return re_box

    # ***********************************************************************************
    def get_crop_image(self, bbox, image):
        im_height, im_width = image.shape[0:2]
        x1,y1,x2,y2 = bbox
        if (x1<0): x1 = 0
        if (y1<0): y1 = 0
        if (x2 > im_width): x2 = im_width
        if (y2 > im_height): y2 = im_height

        return image[y1:y2, x1:x2]

    # ***********************************************************************************
    def get_crop_image_extend(self, bbox, image, extend_percen):

        im_height, im_width = image.shape[0:2]
        x1,y1,x2,y2 = bbox
        extend_x = int((x2-x1)*extend_percen)
        extend_y = int((y2-y1)*extend_percen)
        x1 -= extend_x
        x2 += extend_x
        y1 -= extend_y
        y2 += extend_y

        if (x1<0): x1 = 0
        if (y1<0): y1 = 0
        if (x2 > im_width): x2 = im_width
        if (y2 > im_height): y2 = im_height

        return image[y1:y2, x1:x2]

    # ***********************************************************************************
    def reset_root_bbox_and_image(self, bbox, image):

        self.root_bbox = self.fix_in_image(bbox, image.shape[1], image.shape[0])

        self.ori_obj_img = np.copy(image[self.root_bbox[1]:self.root_bbox[3]+1, self.root_bbox[0]:self.root_bbox[2]+1, :])

        
        if (self.time_since_predict == 0) and (self.time_since_update == 0):
            # new predict and update success. Need only keep tail of update
            Len = len(self.moving_list)
            if (Len>0):
                self.moving_list[Len-2:Len] = self.get_tail_point()
            else:
                self.moving_list += self.get_tail_point()
        else:
            self.moving_list += self.get_tail_point()

    # ***********************************************************************************
    def is_tentative(self):
        """Returns True if this track is tentative (unconfirmed).
        """
        return self.state == TrackState.Tentative

    # ***********************************************************************************
    def is_confirmed(self):
        """Returns True if this track is confirmed."""
        return self.state == TrackState.Confirmed

    # ***********************************************************************************
    def is_deleted(self):
        """Returns True if this track is dead and should be deleted."""
        return (self.state == TrackState.Deleted)

    # ***********************************************************************************
    def set_counted(self):
        self.counted = True

    # ***********************************************************************************
    def get_last_line(self):
        Len = len(self.moving_list)

        if Len >= 4:
            return [self.moving_list[Len-4], self.moving_list[Len-3]], [self.moving_list[Len-2], self.moving_list[Len-1]]

        else:  # counted or not enough point to check
            return None, None

    # ***********************************************************************************
    def get_start_end_points(self):
        Len = len(self.moving_list)

        if Len >= 4:
            return [self.moving_list[0], self.moving_list[1]], [self.moving_list[Len-2], self.moving_list[Len-1]]

        else:  # counted or not enough point to check
            return None, None
