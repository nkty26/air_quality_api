# main.py

import subprocess
import json
from get_airquality_api import AirQualityChecker
from api_to_db import DataBaseManager
from datetime import datetime
import re 

def read_and_parse_crontab_cmds():
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode != 0:
        print("No crontab entries found or unable to read crontab")
        return None
    return result.stdout.splitlines()

def filter_cron_entries(entries):
    # Filter out lines that are comments or empty
    arr = [entry for entry in entries if entry.strip() and "taeyong" in entry.strip()]
    return arr

def main():
    with open('./config.json', 'r') as config_file:
        config = json.load(config_file)

    cron_entries = read_and_parse_crontab_cmds()
    # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", cron_entries)
    filtered_entries = filter_cron_entries(cron_entries)

    air_quality_checker = AirQualityChecker(config)
    db_manager = DataBaseManager(config)

    for entry in filtered_entries:
        # print("ENTRY ENTRY ENTRY", entry)
        air_quality_checker.parse_cron_entries([entry])
        air_quality_data = air_quality_checker.main()
        
        # Manually updating timestamp in final JSON array before inserting record into DB
        print("======================================================== Timestamp 처리 ========================================================\n")
        schedule = air_quality_checker.CRON_JSON['schedules'].split(" ")[0]
        period = air_quality_checker.extract_period(schedule)
        batch_period = period * 60
        print("BATCH PERIOD: ", period, " minutes")
        date_format = "%Y-%m-%d %H:%M"
        timestamp_dt = datetime.now()
        print("  ======>   timestamp_dt  ", timestamp_dt, type(timestamp_dt))
        print("  ======>   before update json  ", air_quality_data[0]['Timestamp'], type(air_quality_data[0]['Timestamp']))
        
        air_quality_data[0]['Timestamp'] = timestamp_dt.strftime(date_format)
        print("  ======>   after update json  ", air_quality_data[0]['Timestamp'], type(air_quality_data[0]['Timestamp']))
        print("================================================================================================================================\n")
        
        db_manager.API_TO_DB(air_quality_data)

if __name__ == "__main__":
    main()
