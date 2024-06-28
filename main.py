import subprocess
import json
from get_airquality_api import AirQualityChecker
from api_to_db import DataBaseManager
from datetime import datetime

def read_and_parse_crontab_cmds():
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.returncode != 0:
        print("No crontab entries found or unable to read crontab")
        return None
    return result.stdout.splitlines()

def filter_cron_entries(entries):
    arr = [entry for entry in entries if entry.strip() and "taeyong" in entry.strip()]
    return arr

def process_timestamp(air_quality_data):
    date_format = "%Y-%m-%d %H:%M"
    timestamp_dt = datetime.now()
    print("\n======================================================== Timestamp 처리 ========================================================")
    print(f"BATCH PERIOD: 1 minute\n")
    print(f"===> timestamp_dt: {timestamp_dt} ({type(timestamp_dt)})")
    print(f"===> Before update: {air_quality_data[0]['Timestamp']} ({type(air_quality_data[0]['Timestamp'])})")
    air_quality_data[0]['Timestamp'] = timestamp_dt.strftime(date_format)
    print(f"===> After update: {air_quality_data[0]['Timestamp']} ({type(air_quality_data[0]['Timestamp'])})")
    print("================================================================================================================================\n")

def main():
    with open('./config.json', 'r') as config_file:
        config = json.load(config_file)
    cron_entries = read_and_parse_crontab_cmds()
    filtered_entries = filter_cron_entries(cron_entries)
    air_quality_checker = AirQualityChecker(config)
    db_manager = DataBaseManager(config)
    
    for entry in filtered_entries:
        air_quality_checker.parse_cron_entries([entry])
        air_quality_data = air_quality_checker.main()
        flag = air_quality_checker.CRON_JSON['uniqueFlag']
        print(f"uniqueFlag: {flag}")
        #uniqueFlag=True -----> 기상청 API 조회 후 새로운 공기질 정보가 갱신되면 INSERT 진행 
        if air_quality_checker.CRON_JSON['uniqueFlag']: # uniq
            db_manager.api_to_db(air_quality_data, flag)
        #uniqueFlag=False -----> 현재 삽입할 Record Timestamp가 마지막 삽입된 Record Timestamp과 동일해도 동일한 Record로 INSERT 진행 (Timestamp만 현재 시간으로 갱신)
        else: 
            process_timestamp(air_quality_data) 
            db_manager.api_to_db(air_quality_data, flag)

if __name__ == "__main__":
    main()
