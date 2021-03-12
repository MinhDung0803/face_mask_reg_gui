import cv2
import numpy as np
from operator import itemgetter

from fast_tracking import fast_track

from mask_utils import graphic_utils
from mask_utils import region_util

_unknown_ID_ = -1 # must be asign true value later

#***********************************************************************************
def initialization_module(unknown_id):
    # assert(unknown_id != -1)
    global _unknown_ID_
    _unknown_ID_ = unknown_id
    fast_track.initialization_module(_unknown_ID_)

#***********************************************************************************
def best_inside_iou(bbox, bboxes, pass_list):
    max_iou = 0
    max_index = -1
    for index in range(len(bboxes)):
        if pass_list[index]:
            continue

        iou = graphic_utils.iou(bbox, bboxes[index])

        if max_iou < iou:
            max_iou = iou
            max_index = index

    return max_iou, max_index

#***********************************************************************************
def best_head_and_body_overlap(head_bbox, body_bboxes, pass_list):

    best_ratio = 7
    min_diff = 1000
    min_index = -1

    for index in range(len(body_bboxes)):
        if pass_list[index]:
            continue

        head_overlap, body_overlap = graphic_utils.overlap(head_bbox, body_bboxes[index])
        if head_overlap >= 0.8:
            top_diff = abs(head_bbox[1] - body_bboxes[index][1])
            head_height, body_height = head_bbox[3]-head_bbox[1], body_bboxes[index][3]-body_bboxes[index][1]
            ratio = body_height/head_height
            if ((top_diff/head_height) <= 0.2) and ((top_diff/body_height) <= 0.1) and (ratio >= 4) and (ratio <= 9):
                if min_index == -1:
                    min_diff = abs(best_ratio - ratio)
                    min_index = index
                elif min_diff > abs(best_ratio - ratio):
                    min_diff = abs(best_ratio - ratio)
                    min_index = index

    return min_index

#***********************************************************************************
def filter_face_inside_head(head_boxs, face_boxs, face_scores, detected_face_infor_list):

    len_head_boxs = len(head_boxs)
    len_face_boxs = len(face_boxs)
    head_boxs_pass = [False] * len_head_boxs
    face_boxs_pass = [False] * len_face_boxs

    re_face_boxs = []
    re_detected_face_infor_list = []
    re_face_scores = []

    for index in range(len_head_boxs):
        found = False
        max_iou_1, max_index_1 = best_inside_iou(head_boxs[index], face_boxs, face_boxs_pass)
        if (max_index_1 >= 0) and (max_iou_1 >= 0.25):
            head_overlap, face_overlap = graphic_utils.overlap(head_boxs[index], face_boxs[max_index_1])
            if (face_overlap >= 0.8) and (head_overlap >= 0.4):
                max_iou_2, max_index_2 = best_inside_iou(face_boxs[max_index_1], head_boxs, head_boxs_pass)

                if max_index_2 == index:
                    found = True
                    head_boxs_pass[index] = True
                    face_boxs_pass[max_index_1] = True

        if found:
            re_face_boxs.append(face_boxs[max_index_1])
            re_detected_face_infor_list.append(detected_face_infor_list[max_index_1])
            re_face_scores.append(face_scores[max_index_1])
        else:
            re_face_boxs.append(None)
            re_detected_face_infor_list.append(None)
            re_face_scores.append(None)

    remain_face_boxs = []
    remain_detected_face_infor_list = []
    remain_face_scores = []
    for index in range(len(face_boxs)):
        if face_boxs_pass[index] is False:
            remain_face_boxs.append(face_boxs[index])
            remain_detected_face_infor_list.append(detected_face_infor_list[index])
            remain_face_scores.append(face_scores[index])

    return re_face_boxs, re_face_scores, re_detected_face_infor_list,\
           remain_face_boxs, remain_face_scores, remain_detected_face_infor_list

#***********************************************************************************
def get_extend_bbox(bbox, pitch_angle, top_extend_percen, lr_extend_percen, im_width, im_height):

    x1,y1,x2,y2 = bbox
    top_extend = int((y2-y1)*top_extend_percen)
    if pitch_angle is None:
        pitch_angle = 0

    if pitch_angle > 45:
        top_extend += top_extend
    else:
        top_extend += int(top_extend*(pitch_angle/45.0))

    lr_extend = int((x2-x1)*lr_extend_percen)

    x1 -= lr_extend
    x2 += lr_extend
    y1 -= top_extend
    # y2 += extend_y

    if (x1<0): x1 = 0
    if (y1<0): y1 = 0
    if (x2 > im_width): x2 = im_width
    if (y2 > im_height): y2 = im_height

    return [x1, y1, x2, y2]

#***********************************************************************************
def make_head_detections_from_face_detection(detected_head_boxs, face_boxs, face_scores, detected_face_infor_list,
                                             im_width, im_height):

    pass_list = [False]*len(detected_head_boxs)
    made_head_boxs = []
    made_head_scores = []
    made_face_boxs = []
    made_face_scores = []
    made_detected_face_infor_list = []

    for index in range(len(face_boxs)):
        max_iou, max_index = best_inside_iou(face_boxs[index], detected_head_boxs, pass_list)
        if max_index < 0:
            pitch_angle = 0
            if (detected_face_infor_list[index] is not None) and (detected_face_infor_list[index][2] is not None) and \
                    (detected_face_infor_list[index][2][1] is not None):
                    pitch_angle = detected_face_infor_list[index][2][1]

            bbox = get_extend_bbox(face_boxs[index], pitch_angle, 0.2, 0.1, im_width, im_height)
            made_head_boxs.append(bbox)
            made_head_scores.append(face_scores[index])
            made_face_boxs.append(face_boxs[index])
            made_face_scores.append(face_scores[index])
            made_detected_face_infor_list.append(detected_face_infor_list[index])

    return made_head_boxs, made_head_scores, made_face_boxs, made_face_scores, made_detected_face_infor_list

#***********************************************************************************
def filter_body_inside_head(head_boxs, body_boxs, body_scores, body_images):

    len_head_boxs = len(head_boxs)
    len_body_boxs = len(body_boxs)
    head_boxs_pass = [False] * len_head_boxs
    body_boxs_pass = [False] * len_body_boxs

    re_body_boxs = []
    re_body_scores = []
    re_body_images = []
    for index in range(len_head_boxs):
        found = False
        best_index = best_head_and_body_overlap(head_boxs[index], body_boxs, body_boxs_pass)

        if best_index >= 0:  # validate value or found the best body_box
            found = True
            head_boxs_pass[index] = True
            body_boxs_pass[best_index] = True

            re_body_boxs.append(body_boxs[best_index])
            re_body_scores.append(body_scores[best_index])
            re_body_images.append(body_images[best_index])
        else:
            re_body_boxs.append(None)
            re_body_scores.append(None)
            re_body_images.append(None)

    return re_body_boxs, re_body_scores, re_body_images

#***********************************************************************************
class FastTracker:
    """
    
    """

    def __init__(self, max_iou_distance=0.3, max_age_init=0, max_age=15, max_update_pass_init=0, camera_index=0,
                 detection_step=1):

        self.max_iou_distance = max_iou_distance
        self.max_age_init = max_age_init
        self.max_age = max_age
        self.max_update_pass_init = max_update_pass_init
        self.tracks = []
        self._next_id = 0
        self.min_size_threshold_to_init_track = 15
        self.camera_index = camera_index
        self.detection_step = detection_step

    # ***********************************************************************************
    def find_max_iou(self, box, boxs, pass_elements):
        Len = len(boxs)
        if Len <= 0:
            return -1, 0

        max_iou = 0
        index = -1
        for i in range(Len):
            if (not pass_elements[i]):
                iou = graphic_utils.iou(box, boxs[i])
                if (max_iou < iou):
                    max_iou = iou
                    index = i
        
        return index, max_iou

    # ***********************************************************************************
    def find_same_id_and_closest(self, box, boxs, class_name, class_names, human_id, human_ids, pass_elements):
        if (human_id <0): 
            return -1, 0
        Len = len(boxs)
        if Len <= 0:
            return -1, 0

        cx1 = (box[2]+box[0])/2
        cy1 = (box[3]+box[1])/2

        found = False
        min_l2_distance = 100000
        index = -1
        for i in range(Len):
            if (not found) and (not pass_elements[i]) and (human_id == human_ids[i]) and (class_name == class_names[i]):
                found = True
                index = i

                cx2 = (boxs[i][2] + boxs[i][0]) / 2
                cy2 = (boxs[i][3] + boxs[i][1]) / 2

                min_l2_distance = (cx2-cx1)**2 + (cy2-cy1)**2
                
            elif found and (not pass_elements[i]) and (human_id == human_ids[i]) and (class_name == class_names[i]):
                
                cx2 = (boxs[i][2]+boxs[i][0])/2
                cy2 = (boxs[i][3]+boxs[i][1])/2

                l2_distance = (cx2-cx1)**2 + (cy2-cy1)**2

                if min_l2_distance > l2_distance:
                    min_l2_distance = l2_distance
                    index = i
        
        if index == -1:
            return index, 100000
        else:
            return index, min_l2_distance**0.5

    # ***********************************************************************************
    def predict(self, image, frame_index):
        """Propagate track state distributions one time step forward.

        This function should be called once every time step, before `update`.
        """
        for track in self.tracks:
            if (not track.is_deleted()):
                track.predict(image, frame_index)

    # ***********************************************************************************
    def predict_visualization(self, draw_image, scale):
        track: fast_track.FastTrack

        for track in self.tracks:
            bbox = None
            color = None
            color_2 = (0, 255, 255)
            if not track.is_deleted():
                if track.time_since_predict == 0:
                    bbox = track.root_bbox
                    color = (0, 255, 0)
                elif track.match_level2:
                    bbox = track.bbox_predict_fail
                    color = (255, 0, 0)

                if bbox is not None:
                    cv2.rectangle(draw_image, (int(bbox[0] * scale), int(bbox[1] * scale)),
                                  (int(bbox[2] * scale), int(bbox[3] * scale)), color, 2)
                    cv2.putText(draw_image, str(track.track_id), (int(bbox[0] * scale), int(bbox[3] * scale)), 0,
                                5e-3 * 250, color, 3, cv2.LINE_AA)

                if track.predict_box is not None:
                    cv2.circle(draw_image, (int(track.predict_pos[0] * scale), int(track.predict_pos[1] * scale)), 15, color_2, 2)
                    cv2.rectangle(draw_image, (int(track.predict_box[0] * scale), int(track.predict_box[1] * scale)),
                                  (int(track.predict_box[2] * scale), int(track.predict_box[3] * scale)), color_2, 2)
                    cv2.putText(draw_image, "P " + str(track.track_id),
                                (int(track.predict_box[2] * scale), int(track.predict_box[3] * scale)), 0, 5e-3 * 250,
                                color_2, 3, cv2.LINE_AA)

    # ***********************************************************************************
    def find_max_iou_invert(self, det_box, track_update_processed, boxs_track):

        max_iou = 0
        index = -1
        Len_tracks = len(self.tracks)
        for track_index in range(Len_tracks):
            if not track_update_processed[track_index]:

                iou = graphic_utils.iou(det_box, boxs_track[track_index])
                if (max_iou < iou):
                    max_iou = iou
                    index = track_index

        return index, max_iou

    # ***********************************************************************************
    def get_key_value(self, track:fast_track.FastTrack):
        return track.score_predict_normed

    # ***********************************************************************************
    def sort_by_score_predict_normed(self, descending_order=False):

        self.tracks.sort(key=self.get_key_value, reverse=descending_order)

    # ***********************************************************************************
    def set_last_update_is_success(self, value, set_list):
        for track_index in range(len(self.tracks)):
            if set_list[track_index]:
                self.tracks[track_index].last_update_is_success = value

    # ***********************************************************************************
    def get_list_to_update(self, pass_list, only_live_track=True):
        boxs_track = []
        class_names_track = []
        boxs_track_match_level2 = []
        time_since_updates = []
        track_update_processed = []

        for track_index in range(len(self.tracks)):
            track: fast_track.FastTrack = self.tracks[track_index]
            if track.is_deleted() or pass_list[track_index] or \
                    (only_live_track and ((not track.last_update_is_success) and (track.time_since_predict > 0))):
                track_update_processed.append(True)  # Pass element
                boxs_track.append([])
                boxs_track_match_level2.append(False)

            elif track.time_since_predict == 0:  # Predict success
                track_update_processed.append(False)
                boxs_track.append(track.root_bbox.copy())
                boxs_track_match_level2.append(False)

            elif track.match_level2 == True:
                track_update_processed.append(False)
                # boxs_track.append(track.bbox_predict_fail.copy())
                boxs_track.append(track.root_bbox.copy())
                boxs_track_match_level2.append(True)
            else:
                track_update_processed.append(False)  # don't pass element
                boxs_track.append(track.root_bbox.copy())
                boxs_track_match_level2.append(False)

            class_names_track.append(track.class_name)
            time_since_updates.append(track.time_since_update)

        ret_inf = (boxs_track, class_names_track, boxs_track_match_level2, time_since_updates,
                   track_update_processed)
        return ret_inf

    # ***********************************************************************************
    def update_detected_objects(self, head_mask_infor, image, frame_index, image_draw):

        bboxes, mask_ids, scores = head_mask_infor

        self.sort_by_score_predict_normed(descending_order=True)


        factor = 1.0

        # only for debug
        # self.put_stamp(detected_face_infor_list)

        Len = len(bboxes)

        match = [False] * Len

        Len_tracks = len(self.tracks)
        pass_list = [False]*Len_tracks

        cnt_match = 0

        for step in range(2):
            live_track = True
            if step == 1:
                live_track = False

            (boxs_track, class_names_track, boxs_track_match_level2, time_since_updates,
             track_update_processed) = self.get_list_to_update(pass_list, only_live_track=live_track)

            # update box from bbox into tracks, first time
            for track_index in range(Len_tracks):

                if (track_update_processed[track_index]):
                    continue

                track = self.tracks[track_index]

                ref_box = None
                if track.time_since_predict == 0:  # Predict success
                    ref_box = track.root_bbox.copy()
                elif track.match_level2 == True:
                    # ref_box = track.bbox_predict_fail.copy()
                    ref_box = track.root_bbox.copy()
                else:   # Predict un-success
                    ref_box = track.root_bbox.copy()

                if track.is_confirmed() and (ref_box is not None):

                    index, max_iou = self.find_max_iou(ref_box, bboxes, match)
                    if index >= 0:

                        # invert check
                        index_invert, max_iou_invert = self.find_max_iou_invert(bboxes[index], track_update_processed, boxs_track)

                        if (index_invert != track_index) and (index_invert >= 0):
                            ref_box_2 = self.tracks[index_invert].root_bbox.copy()
                            index_2, max_iou_2 = self.find_max_iou(ref_box_2, bboxes, match)
                            if index_2 == index:
                                continue

                        if ((index_invert == track_index) and (max_iou > 0.3)) or \
                                ((max_iou >= 0.75) and
                                 (self.tracks[track_index].time_since_predict >= self.tracks[index_invert].time_since_predict) and
                                 (self.tracks[track_index].time_since_update > self.tracks[index_invert].time_since_update)):

                            detection_inf = [bboxes[index], mask_ids[index], scores[index]]
                            update_result = track.update(detection_inf, image, frame_index)
                            if update_result == 0:
                                match[index] = True
                                cnt_match += 1

                                track_update_processed[track_index] = True
                                pass_list[track_index] = True

        self.set_last_update_is_success(False, [not pass_vale for pass_vale in pass_list])

        # remove Unknown track can't update and have large overlap width other self.tracks
        # self.delete_track_have_large_overlap()

        # self.delete_or_join_large_overlap_or_same_name_track()

        deleted_list = []
        for idx in range(Len_tracks):
            if self.tracks[idx].is_deleted():
                deleted_list.append(idx)

        Len_deleted = len(deleted_list)

        cnt = 0
        for i in range(Len):
            if (not match[i]) and (
                    min(bboxes[i][2] - bboxes[i][0], bboxes[i][3] - bboxes[i][1]) > self.min_size_threshold_to_init_track):

                fasttrack = fast_track.FastTrack(bboxes[i], self._next_id, "Person", mask_ids[i], self.max_age_init,
                                                 self.max_age, self.max_update_pass_init, image, frame_index,
                                                 self.camera_index)

                # detection_inf = [boxes[index], names[index], scores[index]]
                #
                # fasttrack.update_detection_infor(detection_inf, frame_index, image.shape[1], image.shape[0])

                self._next_id += 1

                if cnt < Len_deleted:
                    self.tracks[deleted_list[cnt]] = fasttrack
                else:
                    self.tracks.append(fasttrack)

                cnt += 1

        # remove Unknown track can't update and have large overlap width other self.tracks
        # self.delete_track_have_large_overlap()

        # self.join_same_name_track()

        # Delete if there are too many deleted track
        if (cnt < Len_deleted) and (Len_deleted - cnt > 0):
            track: fast_track.FastTrack
            down_index = len(self.tracks) - 1
            while down_index >= 0:
                if self.tracks[down_index].is_deleted():
                    del self.tracks[down_index]
                    print("$"*50, "deleted track at index : ", down_index)
                down_index -= 1

    # ***********************************************************************************
    def delete_older(self):

        track: fast_track.FastTrack
        for track in self.tracks:
            track.delete_older()

    # ***********************************************************************************
    def export_alldata_for_destroy(self):
        track: fast_track.FastTrack

        for track in self.tracks:
            track.set_delete()

    # ***********************************************************************************
    def delete_track_have_large_overlap(self, overlap_threshold=0.7):

        # large_overlap processing
        Len = len(self.tracks)

        list_ref_box = []
        list_ref_index = []
        list_pass = []
        for track_index in range(Len):
            track = self.tracks[track_index]
            if (not track.is_deleted()):  # Predict or Update success
                list_ref_box.append(track.root_bbox.copy())
                list_ref_index.append(track_index)
                list_pass.append(False)

        Len_list = len(list_ref_box)
        # for i in range(Len_list - 1):
        #     if (not list_pass[i]) and (self.tracks[list_ref_index[i]].time_since_update == 0):  # Have Update
        #         for k in range(Len_list):
        #             if (i != k) and (not list_pass[k]) and (
        #                     self.tracks[list_ref_index[k]].time_since_update != 0):  # Have not Update, only Predict
        #                 overlap_percen = graphic_utils.overlap_percen(list_ref_box[k], list_ref_box[i])
        #                 if (overlap_percen >= overlap_threshold):
        #                     self.tracks[list_ref_index[k]].set_delete()
        #                     list_pass[k] = True
        for i in range(Len_list - 1):
            if not list_pass[i]:
                for k in range(Len_list):
                    if (i != k) and (not list_pass[k]):
                        overlap1, overlap2 = graphic_utils.overlap(list_ref_box[k], list_ref_box[i])
                        if (overlap1 > overlap2) and (overlap1 >= overlap_threshold):
                            self.tracks[list_ref_index[k]].set_delete()
                            list_pass[k] = True
                        elif (overlap2 >= overlap1) and (overlap2 >= overlap_threshold):
                            self.tracks[list_ref_index[i]].set_delete()
                            list_pass[i] = True

    # ***********************************************************************************
    def join_same_name_track(self):
        
        # same name processing
        Len = len(self.tracks)
        for i in range(Len - 1):
            if (not self.tracks[i].is_deleted()) and (self.tracks[i].current_human_id >= 0):
                for k in range(i + 1, Len):
                    if (not self.tracks[k].is_deleted()) and (self.tracks[i].current_human_id == self.tracks[k].current_human_id):
                        if (self.tracks[i].is_past_life(self.tracks[k])):
                            self.tracks[i].join_with(self.tracks[k])
                            self.tracks[k].set_delete(export_data = False)

                        elif (self.tracks[k].is_past_life(self.tracks[i])):
                            self.tracks[k].join_with(self.tracks[i])
                            self.tracks[i].set_delete(export_data = False)

        Len = len(self.tracks)
        
        # # large_overlap processing
        # iou_threshold = 0.7

        # list_ref_box = []
        # list_ref_index = []
        # list_pass = []
        # for track_index in range(Len):
        #     track = self.tracks[track_index]
        #     if (not track.is_deleted()) and ((track.time_since_predict == 0) or (track.time_since_update == 0)) : # Predict or Update success
        #         list_ref_box.append(track.root_bbox.copy())
        #         list_ref_index.append(track_index)
        #         list_pass.append(False)
        
        # Len_list = len(list_ref_box)
        # for i in range(Len_list -1):
        #     if (not list_pass[i]) and (self.tracks[list_ref_index[i]].time_since_update == 0): # Have Update
        #         for k in range(i+1,Len_list):
        #             if (not list_pass[k]) and (self.tracks[list_ref_index[k]].time_since_update != 0): # Have not Update, only Predict
        #                 iou = graphic_utils.iou(list_ref_box[i], list_ref_box[k])
        #                 if (iou >= iou_threshold):
                            
        #                     self.tracks[list_ref_index[i]].join_with(self.tracks[list_ref_index[k]])
        #                     self.tracks[list_ref_index[k]].set_delete()
        #                     list_pass[k] = True
        #                     break

    # ***********************************************************************************
    def get_face_infor_for_recognition(self, quota_face_num):
        
        list_face_infor_for_recognition = []
        
        Len_tracks = len(self.tracks)
        # (1) get list face that had not recognized yet
        list_1 = []
        track: fast_track.FastTrack
        for track_index in range(Len_tracks):
            track = self.tracks[track_index]
            if track.front_face_inf is not None:
                list_1.append((track.face_recognized_number, -track.time_since_recognized, track_index))

        list_1.sort(key=itemgetter(0, 1))  # sort by track.face_recognized_number then by track.time_since_recognized

        # print("list_1 : ", list_1)
        min_num = quota_face_num if len(list_1) > quota_face_num else len(list_1)
        
        for i in range(min_num):
            track_index = list_1[i][2]
            track = self.tracks[track_index]
            list_face_infor_for_recognition.append([track.front_face_inf, track.track_id])
            track.front_face_inf = None  # Very Importance
            track.time_since_recognized = 0

        # quota_face_num -= min_num

        return list_face_infor_for_recognition   # => [ [face_inf, track_id],....]

        # ***********************************************************************************
    def get_body_infor_for_send(self, quota_body_num):

        list_body_infor_for_send = []

        Len_tracks = len(self.tracks)
        # (1) get list face that had not recognized yet
        list_1 = []
        track: fast_track.FastTrack
        for track_index in range(Len_tracks):
            track = self.tracks[track_index]
            if track.body_inf is not None:
                list_1.append((track.body_sent_number, -track.time_since_body_sent, track_index))

        list_1.sort(key=itemgetter(0, 1))  # sort by track.body_sent_number then by track.time_since_body_sent

        # print("list_1 : ", list_1)
        min_num = quota_body_num if len(list_1) > quota_body_num else len(list_1)

        for i in range(min_num):
            track_index = list_1[i][2]
            track = self.tracks[track_index]

            list_body_infor_for_send.append([track.camera_id, track.track_id, track.body_inf.copy()])
            # print("abc"*50, "len = ", len([track.camera_id, track.track_id, track.body_inf.copy()]))
            track.body_inf = None  # Very Importance
            track.time_since_body_sent = 0
            track.body_sent_number += 1


        # quota_body_num -= min_num


        return list_body_infor_for_send  # => [ [camera_id, track_id, body_inf],....]

    # ***********************************************************************************
    def update_face_recognition(self, list_face_recognized_infor):
        # list_face_recognized_infor -> list of [face_infor, person_id, min_distance, track_ID, vector]

        track: fast_track.FastTrack
        for track in self.tracks:
            if track.is_deleted():
                continue
            found = False
            for i in range(len(list_face_recognized_infor)):
                front_face, data_infor = list_face_recognized_infor[i]
                if front_face:
                    # [True, [face_infor, int(person_id), min_distance, track_ID, vector]]
                    if (track.track_id == data_infor[3]):
                        found = True
                        track.update_human_id_have_unknown(data_infor)
                        break
                else:
                    # [False, [face_infor, track_ID, vector]]
                    if (track.track_id == data_infor[1]):
                        found = True
                        track.update_frontless_facial_vector(data_infor)
                        break

    # ***********************************************************************************
    def get_infor(self, update_view=False):

        boxs = []
        names = []
        colors = []
        tails = []
        
        track: fast_track.FastTrack

        for track in self.tracks:

            if not update_view:
                if track.is_deleted() or not ((track.time_since_update == 0) or (track.time_since_predict == 0)):
                    continue
            else:
                if track.is_deleted() or (track.time_since_update != 0):
                    continue

            # if track.is_deleted() or not ((track.time_since_update == 0)):
            #     continue

            # if track.is_deleted() or not (track.time_since_update == 0):
            #     continue

            # if (track.current_human_id <0) or (track.current_human_factor < 5):
            #     continue

            boxs.append(track.root_bbox.copy())
            names.append("id: " + str(track.track_id))
            # names.append("id: " + str(track.track_id) + " (" + str(track.face_recognized_number) +":"+ str(track.time_since_recognized) + ")")
            # names.append(str(track.track_id))

            # fsharp_st = ""
            # if (len(track.detection_inf_list) > 0):
            #     fsharp = track.detection_inf_list[-1][-1]
            #     if fsharp is not None:
            #         fsharp_st = str(int(fsharp*10)/10)


            # names.append(" -> " + str(track.face_recognized_number) +" : "+ str(track.time_since_recognized) + " - " + str(track.track_id))
            # human_ids.append([track.current_human_id, track.current_human_factor])

            # if track.time_since_id_update == 1:
            #     human_ids.append([track.current_human_id, track.current_human_factor])
            # else:
            #     human_ids.append([track.current_human_id, None])

            # if (track.time_since_predict != 0) and (track.time_since_update != 0):
            #     colors.append((0,0,255))
            # elif (track.time_since_predict == 0) and (track.time_since_update != 0):
            #     colors.append((255,0,0))
            # elif (track.time_since_predict != 0) and (track.time_since_update == 0):
            #     colors.append((0,255,0))
            # elif (track.time_since_predict == 0) and (track.time_since_update == 0):
            #     colors.append((255,255,255))
            # else:
            #     colors.append((0, 0, 0))

            # old for head-body
            if track.counted:
                colors.append((0, 255, 0))
            else:
                colors.append((255, 255, 255))

            # # new for face-mask
            # if (1 in track.dic_mask_id) and (track.dic_mask_id[1] >= 3):
            #     colors.append((0, 0, 255))
            # elif track.counted:
            #     colors.append((0, 255, 0))
            # else:
            #     colors.append((255, 255, 255))

            # colors.append((255, 255, 255))
            
            tails.append(track.moving_list.copy())

        return boxs, names, colors, tails


    # ***********************************************************************************
    def counter(self, count_regions, counting_dictionaries, image, index):
        if len(self.tracks) == 0:
            return

        # update red light
        count_region: region_util.Region
        for count_region in count_regions:
            if count_region.have_red_lines:
                for red_line in count_region.red_lines:
                    red_line.red_light.update_red_light(image, index)


        track: fast_track.FastTrack
        for track in self.tracks:

            if track.is_deleted() or (len(track.moving_list) < 4):
                continue

            track_checked = False
            start_point, end_point = track.get_start_end_points()
            near_end_point, end_point = track.get_last_line()
            # index = self._Wanted2Index[track.class_name]


            count_region: region_util.Region
            for region_index, count_region in enumerate(count_regions):
                if count_region.is_inside(end_point):
                    check_count = not track.counted
                    check_yellow = False  # not track.violation.get_lane_violation()
                    check_red_light = False  # not track.violation.get_red_light_violation()
                    count, yellow_count, red_count = count_region.check_gate(check_count, check_yellow, check_red_light,
                                                                             start_point, near_end_point, end_point)
                    if count or yellow_count or red_count:
                        track_checked = True

                        # list_counts[region_index][index] += 1
                        if count:
                            track.counted = count
                            if track.class_name in counting_dictionaries[0]:  # list_dic_counts[0] for traffic counting
                                counting_dictionaries[0][track.class_name] += 1
                            else:
                                counting_dictionaries[0][track.class_name] = 1

                        if yellow_count:
                            track.violation.set_lane_violation(True)
                            if track.class_name in counting_dictionaries[1]:  # list_dic_counts[1] for yellow traffic counting
                                counting_dictionaries[1][track.class_name] += 1
                            else:
                                counting_dictionaries[1][track.class_name] = 1

                        if red_count:
                            track.violation.set_red_light_violation(True)
                            if track.class_name in counting_dictionaries[2]:  # list_dic_counts[1] for yellow traffic counting
                                counting_dictionaries[2][track.class_name] += 1
                            else:
                                counting_dictionaries[2][track.class_name] = 1

                        break

    # ***********************************************************************************
    def delete_outside(self, list_regions, draw_image):
        
                
        for i in range(len(self.tracks)):
            
            if (self.tracks[i].is_deleted()):
                continue

            tail_point = self.tracks[i].get_tail_point()

            inside = False
            for k in range(len(list_regions)):
                if (list_regions[k].is_inside(tail_point)):
                    inside = True
                    break

            if (inside == False):
                self.tracks[i].set_delete()

    # ***********************************************************************************
    def pass_count_line(self, list_regions, list_count_line):
        for reg, line in zip(list_regions, list_count_line):
            for track in self.tracks:
                # track.
                i=0

    # ***********************************************************************************
    def draw(self,image_RGB):
        """
        """
        for track in self.tracks:
            if (track.is_deleted() == False):
                track.draw(image_RGB)

    # ***********************************************************************************
    def max_overlap(self, bbox, wantedLabels_group):
        max1 = 0
        max2 = 0
        for track in self.tracks:
            if (track.is_deleted() == False) and (track.class_name in wantedLabels_group):
                ref_box = track.root_bbox
                v1 = graphic_utils.overlap_percen(bbox, ref_box)
                v2 = graphic_utils.overlap_percen(ref_box, bbox)
                if (max1 < v1):
                    max1 = v1
                if (max2 < v2):
                    max2 = v2
        return max1, max2

    # ***********************************************************************************
    def max_iou(self, bbox):
        max = 0
        for track in self.tracks:
            if (track.is_deleted() == False):
                ref_box = track.root_bbox
                iou = track.iou(ref_box, bbox)
                if (max < iou):
                    max = iou
        return max

    # ***********************************************************************************
    def to_tlbr(self, bbox):
        # bbox is tlwh
        box = bbox.copy()
        box[2] += box[0]
        box[3] += box[1]
        return box

    # ***********************************************************************************
    # def remove_overlap(self, boxs, class_names, scores):

    #     boxs_fix = []
    #     class_names_fix = []
    #     scores_fix = []

    #     for box, name, score in zip(boxs, class_names, scores):
    #         bbox = self.to_tlbr(box)
    #         max = 0
    #         for track in self.tracks:
    #             if (track.is_confirmed() == True):
    #                 ref_box = track.root_bbox
    #                 v = track.overlap_percen(bbox, ref_box)
    #                 if (max < v):
    #                     max = v
            
    #         if not (max > self.remove_overlap_threshold):
    #             boxs_fix.append(bbox)
    #             class_names_fix.append(name)
    #             scores_fix.append(score)

    #     return boxs_fix, class_names_fix, scores_fix

    # ***********************************************************************************
    # def count_callback(self, class_name):
    #     idx = self._Wanted2Index[class_name]
    #     self.objcounts[idx] += 1
    #     self.current_objcounts[idx] += 1

    #     print('-------------------------------------- parking_tracker callback: ', class_name)
    #     print(self.current_objcounts)

    # ***********************************************************************************
    # def subtruct_callback(self, class_name):
    #     idx = self._Wanted2Index[class_name]
    #     self.current_objcounts[idx] -= 1

    #     print('-------------------------------------- parking_tracker callback: ', class_name)
    #     print(self.current_objcounts)
