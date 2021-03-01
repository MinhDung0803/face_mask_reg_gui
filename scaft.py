# import pandas as pd
# import matplotlib.pyplot as plt
# import datetime
# import os
# import shutil
# import sqlite3

# read data from csv file
# data = pd.read_csv('data.csv')
# print(data)
# a = data["Country_ID"]

# a = {"T1": 4, "T2": 5, "T3": 8, "T4": 9, "T5": 4}
# names = list(a.keys())
# values = list(a.values())
# #tick_label does the some work as plt.xticks()
# plt.bar(range(len(a)),values,tick_label=names)
# plt.savefig('bar.png')
# plt.show()

# plt.bar(*zip(*a.items()))
# plt.savefig('figure2.png')
# plt.show()

# x = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
# y = [3, 4, 5, 6, 7, 4, 4, 7, 4, 9, 2, 2]
#
# plt.figure(figsize=(10, 5))
# plt.bar(x, y)
# plt.xlabel('Month')
# plt.ylabel('Number of No Face-Mask')
# for index, value in enumerate(y):
#     plt.text(index, value, str(value), color ="red", size='xx-large')
# plt.savefig('bar.png')
# plt.show()

# x = ["M%d" % i for i in range(1, 13, 1)]
# print(x)

# if os.path.exists("figure1.png"):
#     print("True")
#     shutil.rmtree("./figure1.png")
# else:
#     print("False")

# even_month = [i for i in range(1, 13, 2)]
# print(even_month)
# old_month = [i for i in range(2, 13, 2)]
# print(old_month)
# camera_name_input = "A"
# year_input = 2020
#
# conn = sqlite3.connect('./database/Face_Mask_Recognition_DataBase.db')
# c = conn.cursor()
#
# query = f"SELECT * FROM DATA WHERE Camera_name = '{camera_name_input}' " \
#                 f"and Year = {year_input}"
# c.execute(query)
# return_data = c.fetchall()
# df = DataFrame(return_data, columns=["Camera name", "Minute", "Hour", "Day", "Month", "Year"])
# df.to_csv('./export_data/export_data_example.csv')
# print(df)

# import sys
# sys.path.append(("/home/gg-greenlab/Desktop/Project/dungpm/face_mask_reg_gui/face_mask_detection.py"))
# import detection_module

# os.system("python face_mask_detection.py ./configs/Cam_PTZ.yml")

# import json
# import yaml
#
#
# json_file = 'Camera_PTZ.json'
# f = open(json_file)
# json_data = json.load(f)
# f.close()
# data = json_data["data"]
#
# data[0]["url"] = "a"
#
# with open(json_file, "w") as outfile:
#     json.dump(data, outfile)
#
# print(data)

# print("A"*150)
#
# from playsound import playsound
# playsound('police.mp3')

# import pyglet
#
# music = pyglet.resource.media('police.mp3')
# music.play()
# pyglet.app.run()

# list_test = [1, 2, 3, 4, 5, 6, 7, 8]
# for i in range(0, len(list_test), 2):
#     if i+3 > len(list_test):
#         print("first point: ", (list_test[i], list_test[i+1]), "second point: ", (list_test[0], list_test[1]))
#     else:
#         print("first point: ", (list_test[i], list_test[i+1]), "second point: ", (list_test[i+2], list_test[i+3]))


# name = "camera1"
# data = datetime.datetime.now()
# data_form = {"Camera_name": name,
#              "Minute": int(data.minute),
#              "Hour": int(data.hour),
#              "Day": int(data.day),
#              "Month": int(data.month),
#              "Year": int(data.year)}
# print(data_form)
# data_form_add = pd.DataFrame.from_dict([data_form])
# print(data_form_add)


from pydub import AudioSegment
from pydub.playback import play
import threading


def play_audio(file):
    # Input an existing wav filename
    wavFile = "police.mp3"
    # load the file into pydub
    sound = AudioSegment.from_file(wavFile)
    print("Playing wav file...")
    # play the file
    play(sound)


def play_audio_by_threading(file):
    t = threading.Thread(target = play_audio, args = [file])
    t.start()


if __name__ == "__main__":
    # Input an existing wav filename
    wavFile = "./sound_alarm/police.mp3"
    play_audio_by_threading(wavFile)
