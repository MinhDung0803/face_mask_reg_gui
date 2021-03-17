import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os
import time
from mask_utils import app_warning_function


def plot_save_export(name_of_figure,
                     color,
                     camera_name_input,
                     statistics_type,
                     date,
                     save_figure_flag,
                     export_data_flag):
    # connect to sql database
    conn = sqlite3.connect('/home/gg-greenlab/Desktop/Project/dungpm/face_mask_reg_gui/database/final_data_base.db')
    c = conn.cursor()
    return_data = []

    # get camera_id of camera_name_input
    query_id = f"SELECT camera_id FROM DATA WHERE camera_name = '{camera_name_input}'"
    c.execute(query_id)
    # id_data = c.fetchall()
    # if len(c.fetchall()) > 0:
    #     print(c.fetchall())
    id_data = c.fetchall()

    if len(id_data) == 0:
        app_warning_function.query_camera_id_warning()
    else:

        camera_id = id_data[0][0]

        if statistics_type == "Thống kê theo Ngày":
            year_input = date[-4:]
            day_input = date[0:2]
            month_input = date[3:5]

            query = f"SELECT camera_name,num_in,num_mask,num_no_mask,minute,hour,day,month,year " \
                    f"FROM DATA WHERE camera_id = '{camera_id}' and year = {year_input} and day = {day_input} " \
                    f"and month = {month_input} "
            c.execute(query)
            return_data = c.fetchall()
            if export_data_flag:
                df = pd.DataFrame(return_data, columns=["Tên camera", "SL vào", "SL có KT", "SL không KT",
                                                        "Phút", "Giờ", "Ngày", "Tháng", "Năm"])
                file_name_export = "Dữ liệu thống kê " + str(camera_name_input) + "-" + str(day_input) + "-" + \
                                   str(month_input) + "-" + str(year_input) + "-" + ".csv"
                df.to_csv('./export_data/' + file_name_export)
            else:
                x = ["%d" % i for i in range(1, 25, 1)]
                y_in = [0 for i in range(1, 25, 1)]
                y_mask = [0 for i in range(1, 25, 1)]
                y_no_mask = [0 for i in range(1, 25, 1)]
                for elem in return_data:
                    for i in range(len(y_in)):
                        if elem[5] - 1 == i:
                            y_in[i] = y_in[i] + elem[1]
                            y_mask[i] = y_mask[i] + elem[2]
                            y_no_mask[i] = y_no_mask[i] + elem[3]
                plt.figure(figsize=(10, 5))
                plt.plot(x, y_in, label="Tổng số người vào")
                plt.plot(x, y_mask, label="Tổng số người có khẩu trang")
                plt.plot(x, y_no_mask, label="Tổng số người không khẩu trang")
                plt.title("Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                          + str(day_input) + "-"
                          + str(month_input) + "-"
                          + str(year_input) + " "
                          + "tại " + str(camera_name_input))
                plt.xlabel('Giờ trong ngày')
                plt.ylabel('Số lượng trong ngày')
                plt.legend()
                for i in range(len(y_in)):
                    if y_in[i] != 0:
                        plt.text(i - 0.2, y_in[i], str(y_in[i]), color=color, size='large')
                    if y_mask[i] != 0:
                        plt.text(i - 0.2, y_mask[i], str(y_mask[i]), color=color, size='large')
                    if y_no_mask[i] != 0:
                        plt.text(i - 0.2, y_no_mask[i], str(y_no_mask[i]), color=color, size='large')
                if not save_figure_flag:
                    if os.path.exists("./figure/" + name_of_figure):
                        os.remove("./figure/" + name_of_figure)
                    plt.savefig("./figure/" + name_of_figure)
                    plt.close()
                else:
                    plt.savefig("./figure/" + "Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                                + str(day_input) + "-"
                                + str(month_input) + "-"
                                + str(year_input) + " "
                                + "tại " + str(camera_name_input))
                    plt.close()
            time.sleep(0.5)
        elif statistics_type == "Thống kê theo Tháng":
            year_input = date[-4:]
            month_input = date[0:2]

            query = f"SELECT camera_name,num_in,num_mask,num_no_mask,minute,hour,day,month,year " \
                    f"FROM DATA WHERE camera_id = '{camera_id}' and year = {year_input} and month = {month_input} "
            c.execute(query)
            return_data = c.fetchall()
            if export_data_flag:
                df = pd.DataFrame(return_data, columns=["Tên camera", "SL vào", "SL có KT", "SL không KT",
                                                        "Phút", "Giờ", "Ngày", "Tháng", "Năm"])
                file_name_export = "Dữ liệu thống kê " + str(camera_name_input) + "-" + "-" + str(month_input) + "-" \
                                   + str(year_input) + "-" + ".csv"
                df.to_csv('./export_data/' + file_name_export)
            else:
                x = ["%d" % i for i in range(1, 32, 1)]
                y_in = [0 for i in range(1, 32, 1)]
                y_mask = [0 for i in range(1, 32, 1)]
                y_no_mask = [0 for i in range(1, 32, 1)]
                for elem in return_data:
                    for i in range(len(y_in)):
                        if elem[6] - 1 == i:
                            y_in[i] = y_in[i] + elem[1]
                            y_mask[i] = y_mask[i] + elem[2]
                            y_no_mask[i] = y_no_mask[i] + elem[3]
                plt.figure(figsize=(10, 5))
                plt.plot(x, y_in, label="Tổng số người vào")
                plt.plot(x, y_mask, label="Tổng số người có khẩu trang")
                plt.plot(x, y_no_mask, label="Tổng số người không khẩu trang")
                plt.title("Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                          + str(month_input) + "-"
                          + str(year_input) + " "
                          + "tại " + str(camera_name_input))
                plt.xlabel('Ngày trong tháng')
                plt.ylabel('Số lượng trong tháng')
                plt.legend()
                for i in range(len(y_in)):
                    if y_in[i] != 0:
                        plt.text(i - 0.3, y_in[i], str(y_in[i]), color=color, size='large')
                    if y_mask[i] != 0:
                        plt.text(i - 0.3, y_mask[i], str(y_mask[i]), color=color, size='large')
                    if y_no_mask[i] != 0:
                        plt.text(i - 0.3, y_no_mask[i], str(y_no_mask[i]), color=color, size='large')
                if not save_figure_flag:
                    if os.path.exists("./figure/" + name_of_figure):
                        os.remove("./figure/" + name_of_figure)
                    plt.savefig("./figure/" + name_of_figure)
                    plt.close()
                else:
                    plt.savefig("./figure/" + "Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                                + str(month_input) + "-"
                                + str(year_input) + " "
                                + "tại " + str(camera_name_input))
                    plt.close()
            time.sleep(0.5)
        elif statistics_type == "Thống kê theo Năm":
            year_input = date
            query = f"SELECT camera_name,num_in,num_mask,num_no_mask,minute,hour,day,month,year " \
                    f"FROM DATA WHERE camera_id = '{camera_id}' and year = {year_input}"
            c.execute(query)
            return_data = c.fetchall()
            if export_data_flag:
                df = pd.DataFrame(return_data, columns=["Tên camera", "SL vào", "SL có KT", "SL không KT",
                                                        "Phút", "Giờ", "Ngày", "Tháng", "Năm"])
                file_name_export = "Dữ liệu thống kê " + str(camera_name_input) + "-" + str(year_input) \
                                   + "-" + ".csv"
                df.to_csv('./export_data/' + file_name_export)
            else:
                x = ["%d" % i for i in range(1, 13, 1)]
                y_in = [0 for i in range(1, 13, 1)]
                y_mask = [0 for i in range(1, 13, 1)]
                y_no_mask = [0 for i in range(1, 13, 1)]
                for elem in return_data:
                    for i in range(len(y_in)):
                        if elem[7] - 1 == i:
                            y_in[i] = y_in[i] + elem[1]
                            y_mask[i] = y_mask[i] + elem[2]
                            y_no_mask[i] = y_no_mask[i] + elem[3]
                plt.figure(figsize=(10, 5))
                plt.plot(x, y_in, label="Tổng số người vào")
                plt.plot(x, y_mask, label="Tổng số người có khẩu trang")
                plt.plot(x, y_no_mask, label="Tổng số người không khẩu trang")
                plt.title("Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                          + str(year_input) + " "
                          + "tại " + str(camera_name_input))
                plt.xlabel('Tháng trong năm')
                plt.ylabel('Số lượng trong năm')
                plt.legend()
                for i in range(len(y_in)):
                    if y_in[i] != 0:
                        plt.text(i - 0.3, y_in[i], str(y_in[i]), color=color, size='large')
                    if y_mask[i] != 0:
                        plt.text(i - 0.3, y_mask[i], str(y_mask[i]), color=color, size='large')
                    if y_no_mask[i] != 0:
                        plt.text(i - 0.3, y_no_mask[i], str(y_no_mask[i]), color=color, size='large')
                if not save_figure_flag:
                    if os.path.exists("./figure/" + name_of_figure):
                        os.remove("./figure/" + name_of_figure)
                    plt.savefig("./figure/" + name_of_figure)
                    plt.close()
                else:
                    plt.savefig("./figure/" + "Biểu đồ thống kê tổng số lượng người vào, có KT, không KT "
                                + str(year_input) + " "
                                + "tại " + str(camera_name_input))
                    plt.close()
                time.sleep(0.5)
        # commit database
        conn.commit()

    return return_data
