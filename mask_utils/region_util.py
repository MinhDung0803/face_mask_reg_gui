import cv2
import numpy as np
from _datetime import datetime
from mask_utils import graphic_utils as GraU



# class RegionBox:
#     def __init__(self, box):
#         #boxs is (left, top, right ,bottom)
#         self.x1 = box[0]
#         self.y1 = box[1]
#         self.x2 = box[2]
#         self.y2 = box[3]
#
#     def get_crop_image(self, image):
#
#         height = image.shape[0]
#         width = image.shape[1]
#         if (self.x1<0) or (self.y1<0) or (self.x2+1 >width) or (self.y2+1 >height):
#             print("width, heigh : ", width, ' x ', height)
#             print("Box (x1,y1,x2,y2) : ", self.x1, ' ', self.y1, ' ', self.x2, ' ', self.y2)
#             print("Box is out of image...!")
#
#         img_crop = image[self.y1:self.y2+1, self.x1: self.x2+1, : ]
#
#
#         return img_crop
#
#     def offset_tlwh(self, boxs):
#         #boxs is (left, top ,w,h)
#         for i in range(len(boxs)):
#             boxs[i][0] +=self.x1
#             boxs[i][1] +=self.y1
#             # boxs[i][2] +=self.x1
#             # boxs[i][3] +=self.y1
#
#     def draw_boxregion(self, img, color, thickness):
#         cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color, thickness, cv2.LINE_AA)
#
#
#     def make_scale(self, scale):
#
#         self.x1 = int(self.x1*scale)
#         self.y1 = int(self.y1*scale)
#         self.x2 = int(self.x2*scale)
#         self.y2 = int(self.y2*scale)

class RegionBox:
    def __init__(self, box, caption="", show_point=None):
        # boxs is (left, top, right ,bottom)
        self.x1 = box[0]
        self.y1 = box[1]
        self.x2 = box[2]
        self.y2 = box[3]
        self.caption = caption
        self.show_point = show_point

    def get_crop_image(self, image):

        height = image.shape[0]
        width = image.shape[1]
        if (self.x1 < 0) or (self.y1 < 0) or (self.x2 > width) or (self.y2 > height):
            print("width, heigh : ", width, ' x ', height)
            print("Box (x1,y1,x2,y2) : ", self.x1, ' ', self.y1, ' ', self.x2, ' ', self.y2)
            print("Box is out of image...!")

        img_crop = image[self.y1:self.y2, self.x1: self.x2]

        return img_crop

    def offset_tlwh(self, boxs):
        # boxs is (left, top ,w,h)
        for i in range(len(boxs)):
            boxs[i][0] += self.x1
            boxs[i][1] += self.y1
            # boxs[i][2] +=self.x1
            # boxs[i][3] +=self.y1

    def draw_boxregion(self, img, color, thickness, scale=1, show_caption=False):
        cv2.rectangle(img, (int(self.x1 * scale), int(self.y1 * scale)), (int(self.x2 * scale), int(self.y2 * scale)),
                      color, thickness)
        if show_caption and (self.caption != ""):
            cv2.putText(img, self.caption, (int(self.show_point[0] * scale), int(self.show_point[1] * scale)),
                        0, 5e-3 * 150, color, 2)

    def make_scale(self, scale):

        self.x1 = int(self.x1 * scale)
        self.y1 = int(self.y1 * scale)
        self.x2 = int(self.x2 * scale)
        self.y2 = int(self.y2 * scale)
        if (self.show_point is not None):
            self.show_point = [int(self.show_point[0] ** scale), int(self.show_point[1] ** scale)]


def create_regionboxs(regionboxs_data):
    regionbox_list = []
    for item in regionboxs_data:
        caption = item["caption"]
        box = item["box"]
        show_point = item["show_point"]
        new_regionbox = RegionBox(box, caption, show_point)
        regionbox_list.append(new_regionbox)

    return regionbox_list

class GateLine:
    def __init__(self, x1, y1, x2, y2, two_side=False, direction_point=None):

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        # self._a_ = 0
        # self._b_ = 0
        # self._c_ = 0
        self._a_, self._b_, self._c_ = self.get_abc_factor_of_line()

        # print("self._a_ = {}, self._b_ = {}, self._c_ = {}".format(self._a_, self._b_, self._c_))

        self.two_side = two_side
        self.direction_point = direction_point
        if not self.two_side:
            assert (self.direction_point is not None)

        self.arrow_start, self.arrow_end = None, None
        if self.direction_point is not None:
            self.arrow_start, self.arrow_end = GraU.get_a_line_perpendicular_to_another_line(self.x1, self.y1, self.x2,
                                                                                             self.y2,
                                                                                             self.direction_point, 50)
            self.direction_vector = (self.arrow_end[0] - self.arrow_start[0], self.arrow_end[1] - self.arrow_start[1])


    def get_abc_factor_of_line(self):
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1

        a, b, c = 0, 0, 0

        if dx == 0:  # line formula : x = xa
            a = 1
            b = 0
            c = - self.x1
        elif dy == 0:  # line formula : y = ya
            a = 0
            b = 1
            c = - self.y1
        else:  # line formula : y = mx + c
            a = dy/dx
            b = -1
            c = -a*self.x1 + self.y1

        return a, b, c

    def is_same_size(self, x1, y1, x2, y2):
        f1 = self._a_ * x1 + self._b_ * y1 + self._c_
        f2 = self._a_ * x2 + self._b_ * y2 + self._c_
        same_size = (f1*f2 >= 0)
        return same_size

    def is_same_direction(self, direction_vector):
        return (self.direction_vector[0]*direction_vector[0] + self.direction_vector[1]*direction_vector[1]) > 0


    def check_in(self, start_point, end_point, direction_vector):
        have_inter, inter_point, line_inside = GraU.get_intersection_inside_line(self.x1, self.y1, self.x2, self.y2,
                                                start_point[0], start_point[1], end_point[0], end_point[1])


        if (have_inter == True) and (line_inside == True):
            if self.two_side:
                return True
            else:
                # return self.is_same_size(self.direction_point[0], self.direction_point[1], end_point[0], end_point[1])
                return self.is_same_direction(direction_vector)
        else:
            return False

    def make_scale(self, scale):
        self.x1 = int(self.x1*scale)
        self.y1 = int(self.y1*scale)
        self.x2 = int(self.x2*scale)
        self.y2 = int(self.y2*scale)
        self._a_, self._b_, self._c_ = self.get_abc_factor_of_line()
        if self.direction_point is not None:
            self.direction_point = [int(self.direction_point[0]*scale), int(self.direction_point[1]*scale)]
            self.arrow_start = [int(self.arrow_start[0]*scale), int(self.arrow_start[1]*scale)]
            self.arrow_end = [int(self.arrow_end[0] * scale), int(self.arrow_end[1] * scale)]


class RedLight:
    def __init__(self, red_point, radius, red_on_delay=0):
        self.red_point = red_point
        self.radius = radius
        self.red_light_on = False
        self.red_light_start_time = None
        self.red_light_stop_time = None
        self.red_on_delay = red_on_delay

        self.duration_seconds = 0
        self.start_frame_index = None
        self.stop_frame_index = None

    def update_red_light(self, image, frame_index):

        h, w = image.shape[0:2]
        x, y = self.red_point
        x1, y1 = x - self.radius, y - self.radius
        x2, y2 = x + self.radius + 1, y + self.radius + 1

        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > w:
            x2 = w
        if y2 > h:
            y2 = h

        red_light_img = image[y1:y2, x1:x2, :]

        hsv_img = cv2.cvtColor(red_light_img, cv2.COLOR_BGR2HSV)
        threshold_img = cv2.inRange(hsv_img, (0, 50, 50), (30, 255, 255))

        # print("threshold_img.shape = ", threshold_img.shape)
        # print("threshold_img = ", threshold_img)

        # sum = np.sum(threshold_img)
        cnt = np.count_nonzero(threshold_img)
        threshold_img = cv2.inRange(hsv_img, (165, 50, 100), (180, 255, 255))

        # sum += np.sum(threshold_img)
        cnt += np.count_nonzero(threshold_img)
        # ave = sum/cnt
        element_percent = cnt/(4*(self.radius**2))

        on = True if (element_percent >= 0.2) else False

        if self.red_light_on != on:
            self.red_light_on = on
            if on:
                self.red_light_start_time = datetime.now()
                self.red_light_stop_time = None
                self.start_frame_index = frame_index
                self.stop_frame_index = None
            else:
                self.red_light_stop_time = datetime.now()
                self.stop_frame_index = frame_index
                self.duration_seconds = 0

        elif self.red_light_on:
            self.duration_seconds = (datetime.now() - self.red_light_start_time).seconds

    def is_red_light_on(self):
        return self.red_light_on and (self.duration_seconds >= self.red_on_delay)

    def make_scale(self, scale):

        self.red_point = [int(self.red_point[0]*scale), int(self.red_point[1]*scale)]
        self.radius = int(self.radius*scale)

    def draw_region(self, img, color, thickness, scale=1):
        cv2.circle(img, (int(self.red_point[0]*scale), int(self.red_point[1]*scale)), int(self.radius*scale), color, thickness)


class PolyGateLine:
    def __init__(self, id_string, xy_list, two_side=False, direction_point=None, red_point=None, radius=5):

        self.id_string = id_string
        length = len(xy_list)
        assert ((length >= 4) and (length % 2 == 0))
        self.gate_lines = []
        for i in range(0, length-2, 2):
            gate_line = GateLine(xy_list[i], xy_list[i + 1], xy_list[i + 2], xy_list[i + 3], two_side,
                                      direction_point)

            self.gate_lines.append(gate_line)

        self.red_light: RedLight = None

        if red_point is not None:
            if radius is None:
                radius = 5
            self.red_light = RedLight(red_point, radius)

    def check_in(self, start_point, near_end_point, end_point):

        for gate_line in self.gate_lines:
            if gate_line.check_in(start_point, near_end_point, end_point):
                return True

        return False

    def make_scale(self, scale):

        for item in self.gate_lines:
            item.make_scale(scale)

        if self.red_light is not None:
            self.red_light.make_scale(scale)

    def draw_region(self, img, color, thickness, scale=1, show_caption=False, hor_aligement=1, ver_aligement=1):

        for violation_line in self.gate_lines:
            cv2.line(img, (int(violation_line.x1*scale), int(violation_line.y1*scale)), (int(violation_line.x2*scale), int(violation_line.y2*scale)), color, thickness)
            cv2.circle(img, (int(violation_line.x1*scale), int(violation_line.y1*scale)), 10, color, thickness)
            cv2.circle(img, (int(violation_line.x2 * scale), int(violation_line.y2 * scale)), 10, color, thickness)
            if violation_line.direction_point is not None:
                GraU.arrow_line(img, violation_line.arrow_start[0] * scale, violation_line.arrow_start[1] * scale,
                                violation_line.arrow_end[0] * scale, violation_line.arrow_end[1] * scale, 7, color,
                                thickness, cv2.LINE_AA)

        if show_caption:
            cv2.putText(img, self.id_string, (int(self.gate_lines[0].x1 * scale), int(self.gate_lines[0].y1 * scale) - 10),
                        0, 5e-3 * 150, color, 2, cv2.LINE_AA)

        if self.red_light is not None:
            self.red_light.draw_region(img, color, thickness, scale)


def create_trap_lines(trap_lines_data):
    """
    "trap_lines_data": {
                "unlimited_counts": [
                  {"id": "Counting-1", "points": [101, 433, 505, 444], "direction_point": [707, 500]},
                  {"id": "C-2", "points": [505, 444, 910, 456], "direction_point": [303, 400]}
                ],

                "yellow_lines": [
                  {"id": "Yellow-1", "points": [387, 718, 467, 449]}
                ],

                "red_lines": [
                  {"id": "Red-1", "points": [469, 451, 908, 460], "direction_point": [676, 414], "red_point": [784, 52], "radius": 10}
                ]
              }
    """
    unlimited_counts = []
    yellow_lines = []
    red_lines = []

    if "unlimited_counts" in trap_lines_data:
        unlimited_counts_data = trap_lines_data["unlimited_counts"]
        for item in unlimited_counts_data:
            id = item["id"]
            points = item["points"]
            if "direction_point" in item:
                direction_point = item["direction_point"]
                count_line = PolyGateLine(id, points, two_side=False, direction_point=direction_point)
            else:
                count_line = PolyGateLine(id, points, two_side=True)

            unlimited_counts.append(count_line)

    if "yellow_lines" in trap_lines_data:
        yellow_lines_data = trap_lines_data["yellow_lines"]
        for item in yellow_lines_data:
            id = item["id"]
            points = item["points"]
            if "direction_point" in item:
                direction_point = item["direction_point"]
                count_line = PolyGateLine(id, points, two_side=False, direction_point=direction_point)
            else:
                count_line = PolyGateLine(id, points, two_side=True)

            yellow_lines.append(count_line)

    if "red_lines" in trap_lines_data:
        red_lines_data = trap_lines_data["red_lines"]
        for item in red_lines_data:
            id = item["id"]
            points = item["points"]
            red_point = item["red_point"]
            radius = item["radius"]

            if "direction_point" in item:
                direction_point = item["direction_point"]

            else:
                direction_point = red_point.copy()

            count_line = PolyGateLine(id, points, two_side=False, direction_point=direction_point, red_point=red_point,
                                      radius=radius)

            red_lines.append(count_line)

    return unlimited_counts, yellow_lines, red_lines


class Region:
    def __init__(self, string_id, list_point, id_show_point, unlimited_counts: [PolyGateLine], yellow_lines: [PolyGateLine],
                 red_lines: [PolyGateLine]):
        """
        list_point is [x1,y1,x2,y2,....]
        """
        self.string_id = string_id
        self.list_point = list_point.copy()
        x_min, y_min, x_max, y_max = self._get_bbox_tlbr()
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.id_show_point = id_show_point
        self.have_unlimited_counts = (unlimited_counts is not None) and (len(unlimited_counts) > 0)
        self.unlimited_counts = unlimited_counts
        self.have_yellow_lines = (yellow_lines is not None) and (len(yellow_lines) > 0)
        self.yellow_lines = yellow_lines
        self.have_red_lines = (red_lines is not None) and (len(red_lines) > 0)
        self.red_lines = red_lines

        self.motor_area_sum = 0.0
        self.motor_count = 0.0
        self.motor_area_ave = 0.0

    def cal_motor_ave_size(self):
        if (self.motor_count >= 10):
            self.motor_area_ave = self.motor_area_sum / self.motor_count

            if (self.motor_count >= 1000000000):  # reset
                self.motor_area_sum = 0.0
                self.motor_count = 0.0

            # print('-------------------------------------------------------------------------------------self.motor_area_ave = ', self.motor_area_ave)

    def _get_bbox_tlbr(self):
        L = len(self.list_point)
        x_min, y_min = self.list_point[0:2]
        x_max = x_min
        y_max = y_min

        for i in range(2, L, 2):
            x = self.list_point[i]
            y = self.list_point[i + 1]

            if (x_min > x):
                x_min = x
            elif (x_max < x):
                x_max = x

            if (y_min > y):
                y_min = y
            elif (y_max < y):
                y_max = y

        return [x_min, y_min, x_max, y_max]

    def get_bbox_tlbr(self):

        return [self.x_min, self.y_min, self.x_max, self.y_max]

    def get_crop_image(self, image):

        height = image.shape[0]
        width = image.shape[1]
        x_min, y_min, x_max, y_max = self.get_bbox_tlbr()

        if (x_min < 0) or (y_min < 0) or (x_max + 1 > width) or (y_max + 1 > height):
            print("width, heigh : ", width, ' x ', height)
            print("Box (x1,y1,x2,y2) : ", x_min, y_min, x_max, y_max)
            print("Box is out of image...!")

        img_crop = image[y_min:y_max + 1, x_min:x_max + 1, :]

        return img_crop

    def make_scale(self, scale):
        for i in range(len(self.list_point)):
            self.list_point[i] = int(self.list_point[i] * scale)

        x_min, y_min, x_max, y_max = self._get_bbox_tlbr()
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

        self.id_show_point = [int(self.id_show_point[0] * scale), int(self.id_show_point[1] * scale)]


        if self.have_unlimited_counts:
            for item in self.unlimited_counts:
                item.make_scale(scale)

        if self.have_yellow_lines:
            for item in self.yellow_lines:
                item.make_scale(scale)

        if self.have_red_lines:
            for item in self.red_lines:
                item.make_scale(scale)


    def offset_tlwh(self, boxs):
        # boxs is (left, top ,w,h)
        for i in range(len(boxs)):
            boxs[i][0] += self.x_min
            boxs[i][1] += self.y_min

    def offset_tlbr(self, boxs):
        # boxs is (left, top, right ,bottom)
        for i in range(len(boxs)):
            boxs[i][0] += self.x_min
            boxs[i][1] += self.y_min
            boxs[i][2] += self.x_min
            boxs[i][3] += self.y_min

    def is_inside(self, point2d):
        # point2d is [x , y]
        return GraU.is_inside(point2d, self.list_point)

    def get_bottom_mid_box_inside_indexs(self, list_box_tlwh):

        list_point = GraU.get_list_bottom_mid_of_box_tlwh(list_box_tlwh)

        inside_indexs = GraU.get_list_index_inside(list_point, self.list_point)

        return inside_indexs

    def get_inside_boxs_zip(self, boxs_tlwh, names, scores):

        re_boxs_tlwh = []
        re_names = []
        re_scores = []
        inside_indexs = self.get_bottom_mid_box_inside_indexs(boxs_tlwh)

        for i in range(len(boxs_tlwh)):
            if inside_indexs[i]:
                re_boxs_tlwh.append(boxs_tlwh[i])
                re_names.append(names[i])
                re_scores.append(scores[i])

        return re_boxs_tlwh, re_names, re_scores

    def check_gate(self, check_count, check_yellow, check_red_light, start_point, near_end_point, end_point):

        count = False
        yellow_count = False
        red_count = False
        direction_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
        if check_count and self.have_unlimited_counts:
            poly_gate_line: PolyGateLine
            for poly_gate_line in self.unlimited_counts:
                if poly_gate_line.check_in(near_end_point, end_point, direction_vector):
                    count = True
                    break

        if check_yellow and self.have_yellow_lines:
            poly_gate_line: PolyGateLine
            for poly_gate_line in self.yellow_lines:
                if poly_gate_line.check_in(near_end_point, end_point, direction_vector):
                    yellow_count = True
                    break

        if check_red_light and self.have_red_lines:
            poly_gate_line: PolyGateLine
            for poly_gate_line in self.red_lines:

                if poly_gate_line.red_light.is_red_light_on() and poly_gate_line.check_in(near_end_point, end_point, direction_vector):
                    red_count = True
                    break

        return count, yellow_count, red_count

    def draw_region(self, img, color, thickness, scale=1, show_caption=False, hor_aligement=1, ver_aligement=1):
        GraU.draw_polygon(self.list_point, img, color, thickness, scale)

        if (show_caption == True):
            cv2.putText(img, self.string_id, (int(self.id_show_point[0] * scale), int(self.id_show_point[1] * scale)),
                        0, 5e-3 * 150, color, 2, cv2.LINE_AA)
            # if hor_aligement == 0:
            #     x = self.x_min
            # elif hor_aligement == 1:
            #     x = (self.x_min + self.x_max) // 2
            # else:
            #     x = self.x_max
            #
            # if ver_aligement == 0:
            #     y = self.y_min - 5
            # elif ver_aligement == 1:
            #     y = (self.y_min + self.y_max) // 2
            # else:
            #     y = self.y_max + 5
            #
            # cv2.putText(img, self.string_id, (int(x * scale), int(y * scale)), 0, 5e-3 * 150, color, 2, cv2.LINE_AA)

        if self.have_unlimited_counts:
            for item in self.unlimited_counts:
                item.draw_region(img, (0, 255, 0), thickness, scale, show_caption, hor_aligement, ver_aligement)

        if self.have_yellow_lines:
            for item in self.yellow_lines:
                item.draw_region(img, (0, 255, 255), thickness, scale, show_caption, hor_aligement, ver_aligement)

        if self.have_red_lines:
            for item in self.red_lines:
                item.draw_region(img, (0, 0, 255), thickness, scale, show_caption, hor_aligement, ver_aligement)


def create_tracking_regions(tracking_regions_data):
    tracking_region_list = []
    for item in tracking_regions_data:
        string_id = item["id"]
        points = item["points"]
        id_show_point = item["id_show_point"]
        unlimited_counts, yellow_lines, red_lines = [], [], []
        if "trap_lines" in item:
            trap_lines_data = item["trap_lines"]
            unlimited_counts, yellow_lines, red_lines = create_trap_lines(trap_lines_data)

        new_region = Region(string_id, points, id_show_point, unlimited_counts, yellow_lines, red_lines)
        tracking_region_list.append(new_region)

    return tracking_region_list


