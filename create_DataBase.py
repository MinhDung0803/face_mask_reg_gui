import sqlite3
import os


def create_db(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    # Create table - DATA - with 6 features
    c.execute('''CREATE TABLE DATA
                     ([Camera_name] text, 
                     [Hour] integer, 
                     [Minute] integer, 
                     [Day] integer, 
                     [Month] integer, 
                     [Year] integer)''')
    conn.commit()


def final_create_db(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    # Create table - DATA - with 6 features
    c.execute('''CREATE TABLE DATA
                     ([object_id] text,
                     [camera_name] text,
                     [camera_id] text,
                     [num_in] integer,
                     [num_mask] integer,
                     [num_no_mask] integer,
                     [minute] integer, 
                     [hour] integer, 
                     [day] integer, 
                     [month] integer, 
                     [year] integer)''')
    conn.commit()


# def create_db_test():
#     conn = sqlite3.connect("TestDB.db")
#     c = conn.cursor()
#     # Create table - DATA - with 6 features
#     c.execute('''CREATE TABLE DATA
#                      ([Camera_name] text,
#                      [Hour] integer,
#                      [Minute] integer,
#                      [Day] integer,
#                      [Month] integer,
#                      [Year] integer)''')
#     conn.commit()
#
# def create_db_test_cl():
#     conn = sqlite3.connect("TestDB.db")
#     c = conn.cursor()
#     # Create table - DATA - with 6 features
#     c.execute('''CREATE TABLE DATA
#                          ([Camera_name] text,
#                          [Hour] integer,
#                          [Minute] integer,
#                          [Day] integer,
#                          [Month] integer,
#                          [Year] integer)''')
#     conn.commit()


if __name__ == "__main__":
    # # for test
    # db_test_name = "./database/Face_Mask_Recognition_DataBase.db"
    # create_db(db_test_name)

    # final
    data_base_name = "./database/final_data_base.db"
    final_create_db(data_base_name)
