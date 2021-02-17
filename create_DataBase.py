import sqlite3
import os


def create_db(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    # Create table - DATA - with 6 features
    c.execute('''CREATE TABLE DATA
                     ([generated_id] INTEGER PRIMARY KEY,
                     [Camera_name] text, [Hour] integer, 
                     [Minute] integer, 
                     [Day] integer, 
                     [Month] integer, 
                     [Year] integer, 
                     [Image] text)''')
    conn.commit()


def create_db_test():
    conn = sqlite3.connect("TestDB.db")
    c = conn.cursor()
    # Create table - DATA - with 6 features
    c.execute('''CREATE TABLE DATA
                     ([generated_id] INTEGER PRIMARY KEY,
                     [Camera_name] text, [Hour] integer, 
                     [Minute] integer, 
                     [Day] integer, 
                     [Month] integer, 
                     [Year] integer, 
                     [Image] text)''')
    conn.commit()

# def insert_data(data):
#     for item in data:
#
#     print("checked")


# db_test_name = "Face_Mask_Recognition_DataBase.db"
# create_db(db_test_name)

create_db_test()
