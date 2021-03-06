import threading
import requests
import json
import queue
import time

# load host and port in configuration file
configuration_file = "./configs/configuration.json"
with open(configuration_file) as json_file:
    json_data = json.load(json_file)
json_file.close()
host = json_data["host"]
port = json_data["port"]
token = json_data["token"]


def update_data_to_server(update_data_queue, forward_message, backward_message, wait_stop, no_job_sleep_time):
    global host, port, token

    print("(5)--- Running Insert Data to Report Server Threading")

    pausing = False

    # update data config
    setting_server_url = f"{host}:{port}/api/objects/sync"
    headers = {"token": token}
    api_path = f"http://{setting_server_url}"

    while True:
        if forward_message.empty() is False:
            event_message = forward_message.get()
            if event_message == "stop":
                print("[INFO]-- Insert Data to Report Server is waiting to stop")
                wait_stop.wait()
                print("(5)--- Stopped Insert Data to Report Server Threading")
                return
            elif event_message == "pause/unpause":
                pausing = not pausing

        if pausing:
            time.sleep(no_job_sleep_time)
            continue

        have_no_job = True

        if not update_data_queue.empty():
            have_no_job = False

            data = update_data_queue.get()

            # print("check data in queue: ", data)

            # sending data to Report Server
            response = requests.request("POST", api_path, json=data, headers=headers)
            insert_data = response.json()
            print("[INFO]-- ", insert_data)
            if insert_data["status"] == 200:
                print("[INFO]-- Insert Data to Report Server is successful")
            else:
                print("[INFO]-- Insert Data to Report Server has problems, check again !")

        elif have_no_job:
            time.sleep(no_job_sleep_time)

    print("(5)--- Stopped Insert Data to Report Server Threading")


def update_data_by_threading(update_data_queue, forward_message, backward_message, wait_stop, no_job_sleep_time):
    t = threading.Thread(target=update_data_to_server, args=[update_data_queue, forward_message, backward_message,
                                                             wait_stop, no_job_sleep_time])
    t.start()
