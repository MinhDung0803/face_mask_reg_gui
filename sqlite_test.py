import sqlite3
import cv2
import pandas as pd
from pandas import DataFrame

conn = sqlite3.connect('Face_Mask_Recognition_DataBase.db')  # You can create a new database by changing the name within the quotes
c = conn.cursor()  # The database will be saved in the location where your 'py' file is saved


width, height = 720, 480
cap = cv2.VideoCapture('rtsp://admin:Admin123@192.168.111.211/1')

# read data from csv file
data = pd.read_csv('data.csv')
data_2 = pd.read_csv('data_2.csv')
print(data)
# print(data_2)


ex = {"Client_Name": ["Pham Minh Dung"], "Country_ID": [1], "Date": ["15022021"]}
add_data = DataFrame.from_dict(ex)
print(add_data)


while True:
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (width, height))
        cv2.imshow("Test DataBase", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("i"):
            print("Insert data into DataBase")
            add_data.to_sql('CLIENTS', conn, if_exists='replace', index=False)
            data.to_sql('CLIENTS', conn, if_exists='replace', index=False)
            data_2.to_sql('COUNTRY', conn, if_exists='replace', index=False)
            conn.commit()
        elif key == ord("e"):
            c.execute('''
                        INSERT INTO DAILY_STATUS (Client_Name,Country_Name,Date)
                        SELECT DISTINCT clt.Client_Name, ctr.Country_Name, clt.Date
                        FROM CLIENTS clt
                        LEFT JOIN COUNTRY ctr ON clt.Country_ID = ctr.Country_ID
                                  ''')

            c.execute('''
                        SELECT DISTINCT *
                        FROM DAILY_STATUS
                        WHERE Date = (SELECT 14012019 FROM DAILY_STATUS)
                                  ''')

            # my_query = "SELECT DISTINCT * FROM DAILY_STATUS WHERE Date = (SELECT (`data_value`) FROM DAILY_STATUS) " \
            #            "VALUES %s"
            # c.execute(my_query, '14012019')
            df = DataFrame(c.fetchall(), columns=['Client_Name', 'Country_ID', 'Date'])
            print(df)
        elif key == ord("t"):
            date = str(15022021)
            query = f"SELECT * FROM CLIENTS WHERE Date = {date}"
            c.execute(query)
            rows = c.fetchall()
            for row in rows:
                print(row)
        elif key == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()