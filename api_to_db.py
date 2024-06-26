# api_to_db.py

import json
import mysql.connector
from datetime import datetime

class DataBaseManager:
    def __init__(self, config):
        self.db_config = config["DB_KEYS"]

    def INSERT_DATA(self, data):
        print("\n\n======================================================== INSERTING DATA ========================================================")

        pretty_final = json.dumps(data, indent=4, ensure_ascii=False)
        print(pretty_final)
        print("================================================================================================================")

        sql_query = """
        INSERT INTO air_quality_history_final
        (Timestamp, District_Name, Station_Address, Station_Code, Station_TM, PM25_Value, Khai_Value, SO2_Value, CO_Value, PM10_Value, NO2_Value, O3_Value)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        District_Name = VALUES(District_Name), 
        Station_Address = VALUES(Station_Address), 
        Station_Code = VALUES(Station_Code), 
        Station_TM = VALUES(Station_TM), 
        PM25_Value = VALUES(PM25_Value), 
        Khai_Value = VALUES(Khai_Value), 
        SO2_Value = VALUES(SO2_Value), 
        CO_Value = VALUES(CO_Value), 
        PM10_Value = VALUES(PM10_Value), 
        NO2_Value = VALUES(NO2_Value), 
        O3_Value = VALUES(O3_Value)
        """

        values = (
            data[0]["Timestamp"],
            data[0]["District_Name"],
            data[0]['Station_Address'],
            data[0]['Station_Code'],
            data[0]['Station_TM'],
            data[0]['PM25_Value'],
            data[0]['Khai_Value'],
            data[0]['SO2_Value'],
            data[0]['CO_Value'],
            data[0]['PM10_Value'],
            data[0]['NO2_Value'],
            data[0]['O3_Value']
        )

        print(f"Constructed SQL Query: {sql_query}")
        print(f"Values to be inserted: {values}")

        return sql_query, values

    def API_TO_DB(self, json_data):
        print("======================================================== DB CONNECTION ========================================================\n")
        print(f"DB Name: {self.db_config['DBNAME']}, Database user: {self.db_config['USERNAME']}, Host: {self.db_config['HOST']}, Port: {self.db_config['PORT']}\n\n")
        
        CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS air_quality_history_final (
            Timestamp DATETIME PRIMARY KEY,  
            District_Name VARCHAR(100),
            Station_Address VARCHAR(255),
            Station_Code VARCHAR(10), 
            Station_TM FLOAT,
            PM25_Value FLOAT,
            Khai_Value FLOAT,
            SO2_Value FLOAT,
            CO_Value FLOAT,
            PM10_Value FLOAT,
            NO2_Value FLOAT,            
            O3_Value FLOAT
        )
        """

        try:
            connection = mysql.connector.connect(
                host=self.db_config["HOST"],
                user=self.db_config["USERNAME"],
                password=self.db_config["PASSWORD"],
                database=self.db_config["DBNAME"],
                port=self.db_config["PORT"]
            )

            if connection.is_connected():
                print('==> Connected to MySQL database\n\n')
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'air_quality_history_final'")
            result = cursor.fetchone()
            print("======================================================== CREATING TABLE ========================================================")
            if result:
                print("==> Table 'air_quality_history_final' already exists. Skipping creation.")
            else:
                cursor.execute(CREATE_TABLE)
                connection.commit()
                print("=========> Table 'air_quality_history_final' created successfully.")
            print("================================================================================================================================\n")
   
            insert_query, values = self.INSERT_DATA(json_data)
            cursor.execute(insert_query, values)
            connection.commit()
        
            print(f"\n ==== DB INSERT ===> {len(json_data)} records inserted successfully into air_quality_history table at timestamp {datetime.now()}\n\n")

        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL database: {error}")

        except Exception as error:
            print(f"Error inserting data: {error}")

        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")

