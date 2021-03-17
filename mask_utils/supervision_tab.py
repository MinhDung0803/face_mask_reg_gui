import pandas as pd
import sqlite3
import json
import requests
import datetime

# variable
number_of_limited_records = 500

# load host and port in configuration file
configuration_file = "./configs/configuration.json"
with open(configuration_file) as json_file_configuration:
    json_data_configuration = json.load(json_file_configuration)
json_file_configuration.close()
host = json_data_configuration["host"]
port = json_data_configuration["port"]
token = json_data_configuration["token"]


def inset_data_into_database(data_in, time_minute, time_hour, time_day, time_month, time_year):
    # # connect to sql database
    conn_display = sqlite3.connect('./database/final_data_base.db')
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


def update_data_to_report_server(json_data, update_data_queue):
    global number_of_limited_records, host, port, token

    # # connect to sql database
    conn = sqlite3.connect('./database/final_data_base.db')
    c = conn.cursor()
    # update data to Report Server before run main loop
    check_latest_time_form = {
        "object_id": int(json_data["object_id"]),
    }
    # send request to API
    check_time_server_url = f"{host}:{port}/api/objects/get_latest_result_sync"
    api_path = f"http://{check_time_server_url}"
    headers = {"token": token}
    response = requests.request("POST", api_path, json=check_latest_time_form, headers=headers)
    check_latest_time_data = response.json()

    if check_latest_time_data["status"] == 200:
        print('[INFO]-- Latest time from Report Server', check_latest_time_data)

        for item in check_latest_time_data["data"]:
            if item is not None:
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

                # print("from_time: ", from_time)
                # print("to_time: ", to_time)

                query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
                             f"camera_id = '{camera_id}' AND " \
                             f"(substr(year,1,4)||substr(substr('00'||month,-2),1,2)||substr(substr('00'||day,-2),1,2)||" \
                             f"substr(substr('00'||hour,-2),1,2)||substr(substr('00'||minute,-2),1,2)) " \
                             f"BETWEEN '{from_time}' AND '{to_time}'"

                # # query for test
                # query_test = f"SELECT num_in, num_mask, num_no_mask, minute, hour, day, month, year FROM DATA WHERE " \
                #              f"camera_id = '{camera_id}'"

                # query data
                c.execute(query_test)
                updated_data = c.fetchall()  # get all result data from query
                print('[INFO]-- Query data to update', updated_data)
                sending_data = []

                if (len(updated_data) > 0) and (len(updated_data) < 500):
                    for i in range(len(updated_data)):
                        if i != 0:
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
                        print('[INFO]-- Data at Report Server was updated')
                elif len(updated_data) > 500:
                    total_number_data = len(updated_data)
                    div_lay_du = total_number_data % number_of_limited_records
                    div_lay_nguyen = total_number_data // number_of_limited_records
                    for i in range(div_lay_nguyen + 1):
                        sending_data_500 = []
                        if i == 0:
                            item_data = updated_data[1:number_of_limited_records]
                        elif 0 < i < div_lay_nguyen + 1:
                            item_data = updated_data[number_of_limited_records * i:
                                                     number_of_limited_records * i + number_of_limited_records]
                        elif i == div_lay_nguyen + 1:
                            item_data = updated_data[number_of_limited_records * i:number_of_limited_records * i + div_lay_du]

                        for j in range(len(item_data)):
                            if j != 0:
                                item = str(item_data[j])
                                item = item.replace("(", "")
                                item = item.replace(")", "")
                                sending_data_500.append(item)
                        if len(sending_data_500) > 0:
                            # forming data and put into queue
                            insert_data = {
                                "camera_id": camera_id,
                                "data": sending_data_500
                            }
                            data_form = {
                                "object_id": int(json_data["object_id"]),
                                "data": [insert_data]
                            }
                            # put data into queue for updating
                            update_data_queue.put(data_form)
                        else:
                            print('[INFO]-- Data at Report Server was updated')
                else:
                    print('[INFO]-- Data at Report Server was updated')
            else:
                print('[INFO]-- No response about latest time from Report Server')
