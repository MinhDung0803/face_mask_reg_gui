import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import shutil

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
# plt.bar(x, y)
# plt.xlabel('Month')
# plt.ylabel('Number of No Face-Mask')
# for index, value in enumerate(y):
#     plt.text(index, value, str(value), color ="red")
# plt.show()

# x = ["M%d" % i for i in range(1, 13, 1)]
# print(x)

# if os.path.exists("figure1.png"):
#     print("True")
#     shutil.rmtree("./figure1.png")
# else:
#     print("False")

even_month = [i for i in range(1, 13, 2)]
print(even_month)
old_month = [i for i in range(2, 13, 2)]
print(old_month)