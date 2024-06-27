# get_airquality_api.py

import json
import re 
import requests

class AirQualityChecker:
    def __init__(self, config):
        self.api_keys = config["API_KEYS"]
        self.CRON_JSON = {
            "schedules": "",
            "city": "",
            "dong": "",
            "timeFrame": "",
            "venv_path": "",
            "script_path": "",
            "cronlog_path": "",
            "uniqueFlag": "",
            "nearby_count": "",
            "TM_X": "",
            "TM_Y": "",
            "address": "",
            "stnName": "",
            "tm_distance": "",
            "API_Fetch_Period": "",
            "Last_DB_WriteTime": ""
        }
    def extract_period(self, input_str):
        # Regex pattern to match digits
        match = re.search(r'\d+', input_str)
        # Return the matched number or 1 if no match found
        return int(match.group()) if match else 1
    
    def parse_cron_entries(self, CMD):
        print("======================================================== 0. READ AND PARSE CRONTAB COMMANDS ========================================================\n")
        print("PRE_PARSED CRONTAB COMMANDS", CMD)
        cron_arr = CMD[0].split(" ")
        schedules = " ".join(cron_arr[0:5])
        cron_arr = [schedules] + cron_arr[5:]
        # print("INSIDE CMD_PARSED", cron_arr)
        print("\n........................................   Parsing Cron Tab Entries Array   .........................................\n")
        for i in range(len(cron_arr)):
            print("---------------------------------->    ", i, cron_arr[i])
        
        self.CRON_JSON['schedules'] = schedules
        self.CRON_JSON['venv_path'] = cron_arr[4]
        self.CRON_JSON['script_path'] = cron_arr[3][0:-1] + "/" + cron_arr[5]
        self.CRON_JSON['city'] = cron_arr[6]
        self.CRON_JSON['dong'] = cron_arr[7]
        self.CRON_JSON['timeFrame'] = cron_arr[8]
        self.CRON_JSON['uniqueFlag'] = "True" in cron_arr[9]
        self.CRON_JSON['cronlog_path'] = cron_arr[10]
        # pretty = json.dumps(self.CRON_JSON, indent=4, ensure_ascii=False)
        # print(pretty)
    def find_tm(self):
        URL = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt'
        params = {
            'serviceKey': self.api_keys['encodeKey'],
            'returnType': 'json',
            'numOfRows': '10000',
            'pageNo': '1',
            'umdName': self.CRON_JSON['dong']
        }

        response = requests.get(URL, params=params)
        print(f"\n ------> 소재지 TM 좌표 조회 Status Code: {response.status_code}")

        response = response.json()
        pretty_json = json.dumps(response, indent=4, ensure_ascii=False)
        print("===============================================================================================================")
        print("1. 소재지 기준 TM 좌표 찾기")
        print("================================================================================================================")
        print(pretty_json)

        self.CRON_JSON['TM_X'] = response['response']['body']['items'][0]['tmX']
        self.CRON_JSON['TM_Y'] = response['response']['body']['items'][0]['tmY']

        return pretty_json

    def 근접측정소정보(self):
        URL = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList'
        params = {
            'serviceKey': self.api_keys['encodeKey'],
            'returnType': 'json',
            "tmX": self.CRON_JSON['TM_X'],
            "tmY": self.CRON_JSON['TM_Y'],
            'ver': 1.1
        }

        res = requests.get(URL, params=params)
        response = res.json()
        arr = response['response']['body']['items']
        self.CRON_JSON['nearby_count'] = len(arr)
        self.CRON_JSON['address'] = arr[0]['addr']
        self.CRON_JSON['stnName'] = arr[0]['stationName']
        self.CRON_JSON['tm_distance'] = arr[0]['tm']

        # 제일 가까운 측정소 기준 정렬
        stations = sorted(arr, key=lambda d: d['tm'])
        print("=====================================================   API 결과 처리 및 PARSING 후 JSON에 저장완료   ==============================================================================\n")
        print(self.CRON_JSON)
        print(f"------> 근접측정소정보 Status Code: {res.status_code}\n")

        print("===============================================================================================================================================\n\n")
        print("2. 근접 측정소 조회")
        print("============================================================================================================================================\n\n")
        pretty_json = json.dumps(response, indent=4, ensure_ascii=False)
        print(pretty_json)

        return stations

    def 대기오염통계(self, stations):
        final_data = []
        URL = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getCtprvnMesureSidoLIst'
        params = {
            'serviceKey': self.api_keys['encodeKey'],
            'returnType': 'JSON',
            'numOfRows': '100',
            'searchCondition': self.CRON_JSON['timeFrame'],
            'pageNo': '1'
        }
        for station in stations:
            input_sido = station['addr'].split(" ")[0]
            input_district = station['addr'].split(" ")[1]
            params['sidoName'] = input_sido
            try:
                response = requests.get(URL, params=params)
                print("\n\n\n================================================================================================================")
                print(f"\n 3. 대기오염통계 for {station['addr']} API Status Code: {response.status_code}\n")
                print("================================================================================================================\n\n")
                response.raise_for_status()

                try:
                    response_json = response.json()
                    print(self.CRON_JSON)
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", response_json)
                    for item in response_json['response']['body']['items']:
                        if item['cityName'] == input_district:
                            if item['pm25Value'] and item['khaiValue'] and item['so2Value'] and item['pm10Value']:
                                row = {
                                    'Timestamp': item['dataTime'],
                                    'District_Name': item['cityName'],
                                    'Station_Address': station['addr'],
                                    'Station_Code': station['stationCode'],
                                    'Station_TM': station['tm'],
                                    'PM25_Value': item['pm25Value'],
                                    'Khai_Value': item['khaiValue'],
                                    'SO2_Value': item['so2Value'],
                                    'CO_Value': item['coValue'],
                                    'PM10_Value': item['pm10Value'],
                                    'NO2_Value': item['no2Value'],
                                    'O3_Value': item['o3Value']
                                }
                                final_data.append(row)
                                break

                    if final_data:
                        break

                except json.JSONDecodeError:
                    print("Error decoding JSON. Response content:")
                    print(response.text)

            except requests.exceptions.RequestException as e:
                print(f"HTTP request failed: {e}")

        pretty_final = json.dumps(final_data, indent=4, ensure_ascii=False)
        print("================================================================================================================")
        print("기록된 JSON 데이터:")
        print(pretty_final)

        return final_data

    def main(self):
        self.find_tm()
        stations = self.근접측정소정보()
        air_quality_data = self.대기오염통계(stations)
        return air_quality_data