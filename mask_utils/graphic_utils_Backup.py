import cv2
import numpy as np


def intersection_with_h_line(line2d, point2d):
    """
    Use for checking point inside or outside a polygon

    Cal intersection point of line2d width horizontal line pass through point2d
    line2d : [x1 y1 x2 y2]
    point2d: [x y]    
    """

    if (line2d[1] == line2d[3]): # Horizontal line
            return False, []

    if ((line2d[1] <= point2d[1]) and (point2d[1] <= line2d[3])) or\
       ((line2d[3] <= point2d[1]) and (point2d[1] <= line2d[1])):
       x = (point2d[1] - line2d[1])*(line2d[2]-line2d[0])/(line2d[3]-line2d[1]) + line2d[0]
       return True, [x, point2d[1]]

    return False, []

def is_inside(point, polygon=None):
	"""
	Return True if a point (coordinate (x, y)) is inside a polygon defined by
	a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].
	"""
	if polygon is None:
		return False
	x, y = point
	n = len(polygon)//2
	inside = False
	p1x, p1y = polygon[0], polygon[1]
	for i in range(1, n + 1):
		p2x, p2y = polygon[(i % n) * 2], polygon[(i % n) * 2 +1]
		if y > min(p1y, p2y):
			if y <= max(p1y, p2y):
				if x <= max(p1x, p2x):
					if p1y != p2y:
						xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
					if p1x == p2x or x <= xinters:
						inside = not inside
		p1x, p1y = p2x, p2y
	return inside


# def is_inside(point2d, polygon2d):
#     """

#     """


#     num_point = len(polygon2d)
#     if (num_point < 6): # the polygon have less than 3 point 
#         return False

#     is_close = False
#     if (polygon2d[0] == polygon2d[num_point-2]) and (polygon2d[1] == polygon2d[num_point-1]): # the polygon is close
#         is_close = True
    
#     cnt_left_intersection = 0
#     for i in range(0,num_point-2,2):
#         have_inter,point = intersection_with_h_line(polygon2d[i:i+4], point2d)
#         if have_inter and (point[0] < point2d[0]):
#             cnt_left_intersection +=1

    
#     if (is_close == False):
#         line = polygon2d[0:4].copy()
#         line[2] = polygon2d[num_point-2]
#         line[3] = polygon2d[num_point-1]
#         have_inter,point = intersection_with_h_line(line, point2d)
#         if have_inter and (point[0] < point2d[0]):
#             cnt_left_intersection +=1


#     return ((cnt_left_intersection % 2) == 1)

def get_list_index_inside(list_point2d, polygon2d):
    # list_point2d is [x1, y1, x2, y2, x3, y3,...]
    # return [1 , 3] if (x1, y1) and (x3, y3) inside polygon2d
    Len = len(list_point2d)
    inside_indexs = [False]*(Len//2)

    for i in range(0,Len,2):
        if is_inside(list_point2d[i:i+2], polygon2d):
            inside_indexs[(i+1)//2] = True

    return inside_indexs

def get_list_bottom_mid_of_box_tlwh(boxs):
    # boxs is list of box_tlwh as [x, y, w, h]
    # return [x1, y1, x2, y2, x3, y3]
    Len = len(boxs)
    list_point = [0]*(Len*2)
    for i in range(Len):
        list_point[i*2] = boxs[i][0] + boxs[i][2]/2
        list_point[i*2+1] = boxs[i][1] + boxs[i][3]

    return list_point

def get_list_bottom_mid_of_box_tlbr(boxs):
    # boxs is list of box_tlbr as [x1, y1, x2, y2]
    # return [x1, y1, x2, y2, x3, y3]
    Len = len(boxs)
    list_point = [0]*(Len*2)
    for i in range(Len):
        list_point[i*2] = (boxs[i][0] + boxs[i][2])/2
        list_point[i*2+1] = boxs[i][3]

    return list_point

def change_box_tlwh_2_tlbr_int(boxs):
    
    re_boxs = boxs.copy()
    Len = len(boxs)
    
    for i in range(Len):
        re_boxs[i][0] = int(boxs[i][0])
        re_boxs[i][1] = int(boxs[i][1])
        re_boxs[i][2] = int(boxs[i][0]+ boxs[i][2])
        re_boxs[i][3] = int(boxs[i][1] + boxs[i][3])

    return re_boxs

def draw_polygon(polygon2d, image, color, thickness, scale = 1):
    num_point = len(polygon2d)
    
    is_close = False
    if (polygon2d[0] == polygon2d[num_point-2]) and (polygon2d[1] == polygon2d[num_point-1]): # the polygon is close
        is_close = True
    
    
    for i in range(0,num_point-2,2):
        cv2.line(image,(int(polygon2d[i]*scale),int(polygon2d[i+1]*scale)), (int(polygon2d[i+2]*scale),int(polygon2d[i+3]*scale)), color, thickness)
    
    if (is_close == False):
        cv2.line(image,(int(polygon2d[0]*scale), int(polygon2d[1]*scale)), (int(polygon2d[num_point-2]*scale),int(polygon2d[num_point-1]*scale)), color, thickness)


    # convex polygon




# part 1: bounding box processing
def iou(bbox1, bbox2):
    xmax, xmin = bbox1[0], bbox1[2] # x1, x2
    ymax, ymin = bbox1[1], bbox1[3] # y1, y2

    if (xmax < bbox2[0]): 
        xmax = bbox2[0]
    if (xmin > bbox2[2]):
        xmin = bbox2[2]
    if (ymax < bbox2[1]):
        ymax = bbox2[1]
    if (ymin > bbox2[3]):
        ymin = bbox2[3]
    
    if (xmax <= xmin) and (ymax <= ymin): # have intersection
        w = xmin - xmax
        h = ymin - ymax

        area_intersection = w*h
        area1 = (bbox1[2]-bbox1[0])*(bbox1[3]-bbox1[1]) # (x2-x1)*(y2-y1)
        area2 = (bbox2[2]-bbox2[0])*(bbox2[3]-bbox2[1]) # (s_x2-s_x1)*(s_y2-s_y1)
        
        return area_intersection / (area1 + area2 - area_intersection)
    else:
        return 0

def overlap_percen(bbox, bbox2):
    """
        percen of overlap of bbox intersection width bbox2
    """
    xmax, xmin = bbox[0], bbox[2] # x1, x2
    ymax, ymin = bbox[1], bbox[3] # y1, y2

    if (xmax < bbox2[0]): 
        xmax = bbox2[0]
    if (xmin > bbox2[2]):
        xmin = bbox2[2]
    if (ymax < bbox2[1]):
        ymax = bbox2[1]
    if (ymin > bbox2[3]):
        ymin = bbox2[3]
    
    if (xmax <= xmin) and (ymax <= ymin): # have intersection
        w = xmin - xmax
        h = ymin - ymax

        area_intersection = w*h
        area1 = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])  # (x2-x1)*(y2-y1)
        
        return area_intersection / area1
    else:
        return 0

def overlap(bbox1, bbox2):
        """
            bbox1, bbox2 are bounding box format `(min x, miny, max x, max y)`
        """
        xmax = bbox1[0]  # x1
        xmin = bbox1[2]  # x2
        ymax = bbox1[1]  # y1
        ymin = bbox1[3]  # y2

        if (xmax < bbox2[0]): 
            xmax = bbox2[0]
        if (xmin > bbox2[2]):
            xmin = bbox2[2]
        if (ymax < bbox2[1]):
            ymax = bbox2[1]
        if (ymin > bbox2[3]):
            ymin = bbox2[3]
        
        if (xmax <= xmin) and (ymax <= ymin):  # have intersection
            w = xmin - xmax
            h = ymin - ymax

            area_intersection = float(w*h)
            area1 = (bbox1[2]-bbox1[0])*(bbox1[3]-bbox1[1]) # (x2-x1)*(y2-y1)
            area2 = (bbox2[2]-bbox2[0])*(bbox2[3]-bbox2[1]) # (s_x2-s_x1)*(s_y2-s_y1)

            overlap1 = area_intersection / area1
            overlap2 = area_intersection / area2
            
            # print ("----------------------------------------------------------------------------------------------", overlap1, overlap2)
            return overlap1, overlap2
        else:
            return 0, 0

def remove_overlap_box(boxs, scores, passlist, iou_threshold):
    """
    đánh dấu gỡ bỏ ( = True) đối với những Box có overlap với một box khác nhưng mức độ ưu tiên (score) thấp
    passlist là danh sách các phần tử đã được đánh dấu loại bỏ trước khi vào thực hiện hàm remove_overlap_box
    """
    Len = len(boxs)
    remove_checks = passlist.copy()

    for i in range(Len-1):
        if remove_checks[i] == False:
            for k in range(i+1,Len):
                if remove_checks[k] == False:
                    if (iou(boxs[i],boxs[k]) >= iou_threshold):
                        if (scores[i] > scores[k]):
                            remove_checks[k] = True
                        else:
                            remove_checks[i] = True
                            break

    
    return remove_checks

def get_intersection_inside_line(x1,y1,x2,y2,x3,y3,x4,y4):
    # link: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

    Q = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)

    if (Q==0):
        return False, (0,0), False
    else:
        P = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
        t = P/float(Q)
        firt_line_inside = ((0<= t) and (t<=1))
        u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / float(Q)
        second_line_inside = ((0<= u) and (u<=1))

        return True, (x1 + t*(x2-x1), y1 + t*(y2-y1)), (firt_line_inside and second_line_inside)

def _cal_for_spline(u, Poly, k):
    # poly = [x1 y1 x2 y2 x3 y3....]
    u2 = u*u
    u3 = u2*u
    t = 0
    s = (1-t)/2
    x = int(Poly[k-2]*(-s*u3+2*s*u2-s*u)+Poly[k]*((2-s)*u3+(s-3)*u2+1) +Poly[k+2]*((s-2)*u3+(3-2*s)*u2+s*u)+Poly[k+4]*(s*u3-s*u2) + 0.5)
    y = int(Poly[k-1]*(-s*u3+2*s*u2-s*u)+Poly[k+1]*((2-s)*u3+(s-3)*u2+1) +Poly[k+3]*((s-2)*u3+(3-2*s)*u2+s*u)+Poly[k+5]*(s*u3-s*u2) + 0.5)

    return [x, y]

def _cal_for_spline_float(u, Poly, k):
    # poly = [x1 y1 x2 y2 x3 y3....]
    u2 = u*u
    u3 = u2*u
    t = 0
    s = (1-t)/2
    x = Poly[k-2]*(-s*u3+2*s*u2-s*u)+Poly[k]*((2-s)*u3+(s-3)*u2+1) +Poly[k+2]*((s-2)*u3+(3-2*s)*u2+s*u)+Poly[k+4]*(s*u3-s*u2)
    y = Poly[k-1]*(-s*u3+2*s*u2-s*u)+Poly[k+1]*((2-s)*u3+(s-3)*u2+1) +Poly[k+3]*((s-2)*u3+(3-2*s)*u2+s*u)+Poly[k+5]*(s*u3-s*u2)

    return [x, y]

def spline_interpolation(Poly):
    # poly = [x1 y1 x2 y2 x3 y3....]

    Len = len(Poly)
    x0 = Poly[0]
    y0 = Poly[1]
    xn = Poly[Len -2]
    yn = Poly[Len -1]
    Poly.insert(0, x0)
    Poly.insert(1, y0)
    Poly += [xn, yn, xn, yn]

    Poly_out = []
    for k in range(2, Len+2, 2):
        u = 0
        while (u<=1):
            re_point = _cal_for_spline(u, Poly, k)
            u += 0.1
            Poly_out += re_point


    return Poly_out

def cal_map_u(num_of_step):
    Map_u = ([], [], [], [])

    for i in range(num_of_step+1):
        u = i/num_of_step
        u2 = u*u
        u3 = u2*u
        t = 0
        s = (1-t)/2
        Map_u[0].append(-s*u3+2*s*u2-s*u)
        Map_u[1].append((2-s)*u3+(s-3)*u2+1)
        Map_u[2].append((s-2)*u3+(3-2*s)*u2+s*u)
        Map_u[3].append(s*u3-s*u2)

    return Map_u

def _cal_for_spline_fast(Map_u, step, Poly, k):
    # poly = [x1 y1 x2 y2 x3 y3....]
    
    x = int(Poly[k-2]*Map_u[0][step]+Poly[k]*Map_u[1][step] +Poly[k+2]*Map_u[2][step]+Poly[k+4]*Map_u[3][step] + 0.5)
    y = int(Poly[k-1]*Map_u[0][step]+Poly[k+1]*Map_u[1][step] +Poly[k+3]*Map_u[2][step]+Poly[k+5]*Map_u[3][step] + 0.5)

    return [x, y]

def _cal_for_spline_fast_float(Map_u, step, Poly, k):
    # poly = [x1 y1 x2 y2 x3 y3....]
    
    x = Poly[k-2]*Map_u[0][step]+Poly[k]*Map_u[1][step] +Poly[k+2]*Map_u[2][step]+Poly[k+4]*Map_u[3][step]
    y = Poly[k-1]*Map_u[0][step]+Poly[k+1]*Map_u[1][step] +Poly[k+3]*Map_u[2][step]+Poly[k+5]*Map_u[3][step]

    return [x, y]

def spline_interpolation_fast(Poly, Map_u):
    # poly = [x1 y1 x2 y2 x3 y3....]

    max_step = len(Map_u[0])

    Len = len(Poly)
    x0 = Poly[0]
    y0 = Poly[1]
    xn = Poly[Len -2]
    yn = Poly[Len -1]
    Poly.insert(0, x0)
    Poly.insert(1, y0)
    Poly += [xn, yn, xn, yn]

    Poly_out = []
    for k in range(2, Len+2, 2):
        for step in range(max_step):
            re_point = _cal_for_spline_fast(Map_u, step, Poly, k)
            
            Poly_out += re_point

    return Poly_out

def spline_interpolation_fast_float(Poly, Map_u):
    # poly = [x1 y1 x2 y2 x3 y3....]

    max_step = len(Map_u[0])

    Len = len(Poly)
    x0 = Poly[0]
    y0 = Poly[1]
    xn = Poly[Len -2]
    yn = Poly[Len -1]
    Poly.insert(0, x0)
    Poly.insert(1, y0)
    Poly += [xn, yn, xn, yn]

    Poly_out = []
    for k in range(2, Len+2, 2):
        for step in range(max_step):
            re_point = _cal_for_spline_fast_float(Map_u, step, Poly, k)
            
            Poly_out += re_point

    return Poly_out

    
def filter_mean_1D(list_data, kernel_size):
    fil = [1/kernel_size]*kernel_size
    return np.convolve(list_data, fil, 'valid')


def filter_tail(list_point, kernel_size):
    # list_point = [x1 y1 x2 y2 x3 y3....]
    
    Len = len(list_point)
    padded_data = list_point[0:2]*int((kernel_size/2)) + list_point + list_point[Len-2:Len]*int((kernel_size/2))

    fil = [1/kernel_size]*(kernel_size*2)

    for i in range(1,kernel_size*2,2):
        fil[i] = 0

    filtered_data = list(np.convolve(padded_data, fil, 'same'))

    len_cut = int(kernel_size/2)*2

    valid_filtered_data = filtered_data[len_cut:len(filtered_data)-len_cut]   
    
    return valid_filtered_data


def reduce_size_of_long_tail(list_point):
    """
    downsampling of last half of list_point
    list_point = [x1 y1 x2 y2 x3 y3....]
    """
    Len = len(list_point)
    half = (Len//4)*2
    last_half_tail = list_point[half:Len]
    re_last_half_tail = filter_tail(last_half_tail, 3)
    Len2 = len(re_last_half_tail)

    del list_point[half:Len]
    
    for i in range(0, Len2-1, 4):
        list_point.append(re_last_half_tail[i])
        list_point.append(re_last_half_tail[i+1])
    

# def filter_tail(list_point, kernel_size):
#     # list_point = [x1 y1 x2 y2 x3 y3....]
#     x = list_point[0: len(list_point) :2]
#     y = list_point[1: len(list_point) :2]

#     # Pad data
#     x_pad = [x[0]]*int((kernel_size/2)) + x + [x[len(x)-1]]*int((kernel_size/2))
#     y_pad = [y[0]]*int((kernel_size/2)) + y + [y[len(x)-1]]*int((kernel_size/2))

#     re_x = filter_mean_1D(x_pad, kernel_size)
#     re_y = filter_mean_1D(y_pad, kernel_size)

#     re_list_point = []
#     for i in range(len(re_x)):
#         re_list_point.append(re_x[i])
#         re_list_point.append(re_y[i])
    
#     return re_list_point



def puttext_alignment(image, text, fontFace, fontScale, color, thickness, lineType,\
                    x, y, vertical_alignment, horizontal_alignment):

    textsize, baseline = cv2.getTextSize(text, fontFace, fontScale, thickness)

    
    text_width, text_height = textsize
    
    x_org = x - text_width  # Horizontal-Left alignment
    y_org = y  # Vertical-Top alignment


    if (horizontal_alignment == 1):  # Horizontal-Center alignment
        x_org = x - text_width//2
    elif (horizontal_alignment == 2):  # Horizontal-Right alignment
        x_org = x

    if (vertical_alignment == 1):  # Vertical-Center alignment
        y_org = y + text_height//2
    elif (vertical_alignment == 2):  # Vertical-Bottom alignment
        y_org = y + text_height

    cv2.putText(image, text, (x_org, y_org), fontFace, fontScale,
            color, thickness, lineType)

    bbox = (x_org, y_org, x_org + text_width, y_org + text_height)
    return bbox

