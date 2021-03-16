import pandas as pd
import sqlite3
import json
import requests
import datetime

# variable
number_of_limited_records = 500


def inset_data_into_database(data_in, time_minute, time_hour, time_day, time_month, time_year):
    # # connect to sql database
    conn_display = sqlite3.connect(
        '/home/gg-greenlab/Desktop/Project/dungpm/face_mask_reg_gui/database/final_data_base.db')
    c_display = conn_display.cursor()

    data_form_add = pd.DataFrame.from_dict([data_in])
    data_form_add.to_sql('DATA', conn_display, if_exists='append', index=False)
    print("[INFO]-- Inserted data into Database")
    conn_display.commit()
    data_in["num_in"] = 0
    data_in["num_mask"] = 0
    data_in["num_no_mask"] = 0
    data_in["minute"] = time_minute
    data_in["hour"] = time_hour
    data_in["day"] = time_day
    data_in["month"] = time_month
    data_in["year"] = time_year
    return data_in


def update_data_to_report_server(json_data, token, update_data_queue):
    global number_of_limited_records

    # # connect to sql database
    conn = sqlite3.connect(
        '/home/gg-greenlab/Desktop/Project/dungpm/face_mask_reg_gui/database/final_data_base.db')
    c = conn.cursor()
    # update data to Report Server before run main loop
    check_latest_time_form = {
        "object_id": int(json_data["object_id"]),
    }
    # send request to API
    check_time_server_url = "192.168.111.182:9000/api/objects/get_latest_result_sync"
    api_path = f"http://{check_time_server_url}"
    headers = {"token": token}
    response = requests.request("POST", api_path, json=check_latest_time_form, headers=headers)
    check_latest_time_data = response.json()
    print(check_latest_time_data)

    for item in check_latest_time_data["data"]:
        # prepare information
        camera_id = item["camera_id"]
        now = datetime.datetime.now()
        data_lst = (str(item["year"]),
                    str(item["month"]).zfill(2),
                    str(item["date"]).zfill(2),
                    str(item["hours"]).zfill(2),
                    str(item["minutes"]).zfill(2))

        to_time = now.strftime("%Y%m%d%H%M")
        from_time = "".join(data_lst)

        query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
                     f"camera_id = '{camera_id}' AND " \
                     f"(substr(year,1,4)||substr(substr('00'||month,-2),1,2)||substr(substr('00'||day,-2),1,2)||" \
                     f"substr(substr('00'||hour,-2),1,2)||substr(substr('00'||minute,-2),1,2)) " \
                     f"BETWEEN '{from_time}' AND '{to_time}'"

        # query data
        c.execute(query_test)
        updated_data = c.fetchall() # get all result data from query

        sending_data = []

        if (len(updated_data) > 0) and (len(updated_data) < 500):
            for i in range(len(updated_data)):
                item = str(updated_data[i])
                item = item.replace("(", "")
                item = item.replace(")", "")
                sending_data.append(item)
            if len(sending_data) > 0:
                # forming data and put into queue
                insert_data = {
                    "camera_id": camera_id,
                    "data": sending_data
                }
                data_form = {
                    "object_id": int(json_data["object_id"]),
                    "data": [insert_data]
                }
                # put into update data queue
                update_data_queue.put(data_form)
            else:
                print('[INFO]-- Problem on preprocessing data before updating to Report Server')
        elif len(updated_data) > 500:
            total_number_data = len(updated_data)
            div_lay_du = total_number_data % number_of_limited_records
            div_lay_nguyen = total_number_data // number_of_limited_records
            for i in range(div_lay_nguyen + 1):
                if i == 0:
                    item_data = updated_data[0:number_of_limited_records]
                elif 0 < i < div_lay_nguyen + 1:
                    item_data = updated_data[number_of_limited_records * i:
                                             number_of_limited_records * i + number_of_limited_records]
                elif i == div_lay_nguyen + 1:
                    item_data = updated_data[number_of_limited_records * i:number_of_limited_records * i + div_lay_du]

                # forming data and put into queue
                insert_data = {
                    "camera_id": camera_id,
                    "data": item_data
                }
                data_form = {
                    "object_id": int(json_data["object_id"]),
                    "data": [insert_data]
                }
                # put data into queue for updating
                update_data_queue.put(data_form)
        else:
            print('[INFO]-- Data at Report Server was updated')
