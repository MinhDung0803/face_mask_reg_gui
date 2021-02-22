
import cv2
import numpy as np

class Grid_View:

    """

    Parameters
    ----------


    Attributes
    ----------

    """


    #-------------------------------------------------------------------------
    def __init__(self, window_name, view_width, view_height, grid_row, grid_col, border_line_width, border_line_color, cam_id_list, text_color, direct_show=True):
    
        self.window_name = window_name
        self.view_width = int(view_width)
        self.view_height = int(view_height)
        self.grid_row = int(grid_row)
        self.grid_col = int(grid_col)
        self.border_line_width = border_line_width
        self.border_line_color = border_line_color
        self.cam_id_list = cam_id_list
        self.text_color = text_color
        self.direct_show = direct_show
        print("[1]", "-"*50)
        if self.direct_show:
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
            # cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
            print("[2]", "-"*50)
            # cv2.setMouseCallback(self.window_name, self.mouse_callback_this)
        print("[3]", "-"*50)
        self.left_mouse_down = False

        self.main_img = np.zeros((self.view_height, self.view_width, 3), dtype = "uint8")
        self.main_img.fill(255)

        self.cell_width = int(self.view_width/self.grid_col)
        self.cell_height = int(self.view_height/self.grid_row)
        print("[4]", "-"*50)
    #-------------------------------------------------------------------------
    def mouse_callback_this(self, event, x, y, flags, param):
        # x = int(x/self.scale)
        # y = int(y/self.scale)
        
        
        if (event == cv2.EVENT_LBUTTONDOWN) and (self.left_mouse_down == False):
            self.left_mouse_down = True

        elif event == cv2.EVENT_LBUTTONUP and self.left_mouse_down:
            self.left_mouse_down = False


    #-------------------------------------------------------------------------
    def set_direct_show(self, value):
        if self.direct_show:
            if value: # show on
                return
            else: # show off
                cv2.destroyWindow(self.window_name) 
                self.direct_show = value
        else:
            if value: # show on
                self.direct_show = value
                # cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
                # cv2.setMouseCallback(self.window_name, self.mouse_callback_this)
            else: # show off
                return
            
    #-------------------------------------------------------------------------
    def release(self):
        if self.direct_show:
            cv2.destroyWindow(self.window_name)
            # cv2.destroyAllWindows()

            print("cv2.destroyWindow({0})".format(self.window_name))

    #-------------------------------------------------------------------------

    def set_cell_image(self, img, cel_index):
        h,w,_ = img.shape

        scale = min(self.cell_width/w, self.cell_height/h)
        new_w = int(w * scale) - self.border_line_width
        new_h = int(h * scale) - self.border_line_width

        cell_img = cv2.resize(img, (new_w,new_h))
        # cell_img = cv2.resize(img, (0,0), fx=scale, fy=scale)

        cel_row_index = cel_index//self.grid_col
        cel_col_index = cel_index - cel_row_index*self.grid_col

        x_offset = (self.cell_width - new_w)//2
        y_offset = (self.cell_height - new_h)//2

        x1 = cel_col_index*self.cell_width + x_offset
        x2 = x1 + new_w

        y1 = cel_row_index*self.cell_height + y_offset
        y2 = y1 + new_h

        self.main_img[y1:y2, x1:x2, :] = cell_img

        self.draw_cam_id_text(cel_index, x1 - x_offset + 20, y1 - y_offset + 30, (0,0,0), 120)
        self.draw_cam_id_text(cel_index, x1 - x_offset + 22, y1 - y_offset + 28, self.text_color, 120)


    def show(self, delay_time):
        if self.direct_show is False:
            print("Called to Show")
            return 0

        self.draw_grid()
        cv2.imshow(self.window_name, self.main_img)

        char = cv2.waitKeyEx(delay_time)
        return char

    def draw_grid(self):

        # draw row
        for i in range(1, self.grid_row):
            y = i*self.cell_height
            cv2.line(self.main_img, (0, y), (self.view_width, y), self.border_line_color, self.border_line_width)
        # draw col
        for i in range(1, self.grid_col):
            x = i*self.cell_width
            cv2.line(self.main_img, (x, 0), (x, self.view_height), self.border_line_color, self.border_line_width)

    def draw_cam_id_text(self, cel_index, x, y, color, small_size):
        cv2.putText(self.main_img, self.cam_id_list[cel_index], (x, y), 0, 5e-3 * small_size, color, 2, cv2.LINE_AA)

    def get_windows_size(self):
        return (int(self.main_img.shape[1]), int(self.main_img.shape[0]))

    def get_capture_image(self):
        return self.main_img.copy()
        


