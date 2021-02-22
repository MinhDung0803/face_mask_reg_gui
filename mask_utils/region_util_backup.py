import cv2
import numpy as np
from mask_utils import graphic_utils as GraU


class Region:
    def __init__(self, list_point, caption, have_count_line = False, line_point1 = (0, 0), line_point2 = (0, 0)):
        """
        list_point is [x1,y1,x2,y2,....]
        """
        self.list_point = list_point.copy()
        x_min, y_min, x_max, y_max = self._get_bbox_tlbr()
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.caption = caption
        self.have_count_line = have_count_line
        self.line_point1 = (int(line_point1[0]), int(line_point1[1]))
        self.line_point2 = (int(line_point2[0]), int(line_point2[1]))

        self.motor_area_sum = 0.0
        self.motor_count = 0.0
        self.motor_area_ave = 0.0
        
    def cal_motor_ave_size(self):
        if (self.motor_count >= 10):
            self.motor_area_ave = self.motor_area_sum/self.motor_count
            
            if (self.motor_count >= 1000000000): # reset
                self.motor_area_sum = 0.0
                self.motor_count = 0.0

            # print('-------------------------------------------------------------------------------------self.motor_area_ave = ', self.motor_area_ave)

    def _get_bbox_tlbr(self):
        L = len(self.list_point)
        x_min, y_min = self.list_point[0:2]
        x_max = x_min
        y_max = y_min

        for i in range(2,L,2):
            x = self.list_point[i]
            y = self.list_point[i+1]

            if (x_min > x) : 
                x_min = x 
            elif (x_max < x):
                x_max = x
            
            if (y_min > y) : 
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

        if (x_min<0) or (y_min<0) or (x_max+1 >width) or (y_max+1 >height):
            print("width, heigh : ", width, ' x ', height)
            print("Box (x1,y1,x2,y2) : ", x_min, y_min, x_max, y_max)
            print("Box is out of image...!")

        img_crop = image[y_min:y_max+1, x_min:x_max+1, : ]
        
        return img_crop

    def make_scale(self, scale):
        for i in range(len(self.list_point)):
            self.list_point[i] = int(self.list_point[i] * scale)
            
        
        x_min, y_min, x_max, y_max = self._get_bbox_tlbr()
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

        if (self.have_count_line):
            self.line_point1 = (int(self.line_point1[0]*scale), int(self.line_point1[1]*scale))
            self.line_point2 = (int(self.line_point2[0]*scale), int(self.line_point2[1]*scale))
            

    def offset_tlwh(self, boxs):
        #boxs is (left, top ,w,h)
        for i in range(len(boxs)):
            boxs[i][0] +=self.x_min
            boxs[i][1] +=self.y_min
    
    def offset_tlbr(self, boxs):
        #boxs is (left, top, right ,bottom)
        for i in range(len(boxs)):
            boxs[i][0] +=self.x_min
            boxs[i][1] +=self.y_min
            boxs[i][2] +=self.x_min
            boxs[i][3] +=self.y_min
     
    def is_inside(self, point2d):
        # point2d is [x , y]
        return GraU.is_inside(point2d, self.list_point)


    def get_bottom_mid_box_inside_indexs(self, list_box_tlwh):

        list_point = GraU.get_list_bottom_mid_of_box_tlwh(list_box_tlwh)

        inside_indexs = GraU.get_list_index_inside(list_point, self.list_point)
        
        return inside_indexs
    
    def get_inside_boxs_zip(self, boxs_tlwh, names, scores):

        
        re_boxs_tlwh =[]
        re_names =[]
        re_scores =[]
        inside_indexs = self.get_bottom_mid_box_inside_indexs(boxs_tlwh)

        for i in range(len(boxs_tlwh)):
            if inside_indexs[i]:
                re_boxs_tlwh.append(boxs_tlwh[i])
                re_names.append(names[i])
                re_scores.append(scores[i])

        

        return re_boxs_tlwh, re_names, re_scores

    def draw_region(self, img, color, thickness, scale = 1, show_caption = False, hor_aligement = 1, ver_aligement = 1):
        GraU.draw_polygon(self.list_point, img, color, thickness, scale)

        if (show_caption == True):
            if hor_aligement == 0:
                x = self.x_min
            elif hor_aligement == 1:
                x = (self.x_min + self.x_max)//2
            else:
                x = self.x_max

            if ver_aligement == 0:
                y = self.y_min - 5
            elif ver_aligement == 1:
                y = (self.y_min + self.y_max)//2
            else:
                y = self.y_max + 5

            cv2.putText(img, self.caption, (int(x*scale),int(y*scale)), 0, 5e-3 * 150, color,2)
        
        if (self.have_count_line):
            cv2.line(img, (int(self.line_point1[0]*scale), int(self.line_point1[1]*scale)), (int(self.line_point2[0]*scale), int(self.line_point2[1]*scale)), color, thickness)

    def fill_region_of_mark(self, mark_img):

        pts= []
        for i in range(0, len(self.list_point), 2):
            pts.append([self.list_point[i], self.list_point[i+1]])
        
        pts_np = np.array( [pts], dtype=np.int32 )
        
        cv2.fillPoly(mark_img, pts_np,(255,255,255))


class RegionBox:
    def __init__(self, box):
        #boxs is (left, top, right ,bottom)
        self.x1 = box[0]
        self.y1 = box[1]
        self.x2 = box[2]
        self.y2 = box[3]
        # dx = (self.x2-self.x1 + 1) % 32
        # dy = (self.y2-self.y1 + 1) % 32

        # if (dx != 0):
        #     self.x2 += (32-dx)
        
        # if (dy != 0):
        #     self.y2 += (32-dy)
        
    
    def get_crop_image(self, image):

        height = image.shape[0]
        width = image.shape[1]
        if (self.x1<0) or (self.y1<0) or (self.x2+1 >width) or (self.y2+1 >height):
            print("width, heigh : ", width, ' x ', height)
            print("Box (x1,y1,x2,y2) : ", self.x1, ' ', self.y1, ' ', self.x2, ' ', self.y2)
            print("Box is out of image...!")

        img_crop = image[self.y1:self.y2+1, self.x1: self.x2+1, : ]
        

        return img_crop

    def offset_tlwh(self, boxs):
        #boxs is (left, top ,w,h)
        for i in range(len(boxs)):
            boxs[i][0] +=self.x1
            boxs[i][1] +=self.y1
            # boxs[i][2] +=self.x1
            # boxs[i][3] +=self.y1

    def offset_tlbr(self, boxs):
        #boxs is (left, top , bottom, right)
        for i in range(len(boxs)):
            boxs[i][0] +=self.x1
            boxs[i][1] +=self.y1
            boxs[i][2] +=self.x1
            boxs[i][3] +=self.y1


    def draw_boxregion(self, img, color, thickness):
        cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), color, thickness)


    def make_scale(self, scale):
        
        self.x1 = int(self.x1*scale)
        self.y1 = int(self.y1*scale)
        self.x2 = int(self.x2*scale)
        self.y2 = int(self.y2*scale)





