**공기질 API 데이터 관리 시스템**
**개요**
이 프로젝트는 한국 기상청 API로부터 대기질 데이터를 자동으로 검색하여 MySQL 데이터베이스에 저장하는 기능을 제공합니다. API 요청, 데이터베이스 상호작용 및 주기적 데이터 업데이트를 위한 cron 작업 스케줄링을 처리하는 모듈을 포함하고 있습니다.

**프로그램 흐름**
중개서버에 기상청 공기질 API 조회하여 매 10분마다 회사 데이터서버 air_quality_history 테이블에 공기질 데이터 INSERT하는 프로그램 
1. Read and Parse Cron Tab Command (Crontab 명령어로 1. 도시 2. 동명 3. 주기 4. uniqueFlag=True/uniqueFlag=False ==> Parsing 후 명시된 주기로 API GET 조회) 
2. (동별) 소재지 기준 TM 좌표 찾기 --> 기상청 API Endpoint: 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt'
3. TM_X, TM_Y 좌표 기준 근접측정소 정보 리스트 조회 후 TM 좌표 기준 가장 가까운 측정소 기준 정렬 --> 기상청 API Endpoint: 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList'
4. 소재지와 가장 가까운 측정소로 기상청 공기질 데이터 조회 (실시간 갱신)--> 기상청 API Endpoint: 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getCtprvnMesureSidoLIst'
5. MySQL DB 연결
6. air_quality_history_final 테이블의 스키마를 정의하고, 테이블이 없는 경우에만 생성합니다.
7. SQL의 ON DUPLICATE KEY UPDATE를 (Timestamp) 사용하여 중복 항목을 처리하고 새로운 대기질 데이터를 데이터베이스에 삽입합니다.
8. uniqueFlag=True/uniqueFlag=False 에 따란 lastWriteDB Timestamp 와 Current Record Timestamp 비교하여 데이터 삽입 

**프로젝트 파일**

**1. main.py**

데이터 검색 및 데이터베이스 삽입 프로세스를 조정하는 진입점 스크립트입니다.
시스템에서 cron 작업을 파싱하고, get_airquality_api.py를 통해 대기질 데이터를 검색하며, api_to_db.py를 통해 데이터베이스 상호작용을 관리합니다.
API 검색 빈도와 타임스탬프 고유성에 따라 중복 레코드를 처리하는 옵션을 제공합니다.

**2. api_to_db.py**

데이터베이스 연결 및 작업을 관리합니다.
air_quality_history_final 테이블의 스키마를 정의하고, 테이블이 없는 경우에만 생성합니다.
SQL의 ON DUPLICATE KEY UPDATE를 사용하여 중복 항목을 처리하고 새로운 대기질 데이터를 데이터베이스에 삽입합니다.

**3. get_airquality_api.py**

한국 기상청 API에서 대기질 데이터를 검색하는 함수를 제공합니다.
JSON 형식으로 데이터를 반환하며, 이후 api_to_db.py에서 데이터 처리 및 데이터베이스 삽입을 처리합니다.
설정

**4. config.json: 데이터베이스 자격 증명 (DB_KEYS) 및 기타 설정을 포함한 구성 파일입니다.**
- air_quality_history_final 테이블 Columns 
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
참고: 보안 및 개인 정보 문제로 인해 이 저장소에 config.json 파일이 포함되어 있지 않습니다. 사용자는 이 파일을 로컬에 생성하고 적절한 자격 증명을 설정해야 합니다.


**5. cron 작업 설정**
주기적인 업데이트를 위해 다음 crontab 항목을 추가합니다:

"* * * * *  cd /home/asicentralcity3/Workspace/air_quality_data; /home/asicentralcity3/myenv/bin/python main.py arg1 arg2 arg3 arg4 >> /home/asicentralcity3/Workspace/air_quality_data/cronlogs.log 2>&1; cd"

- 원하는 도시 및 구역을 선택하고, 타임프레임 (HOUR 또는 DAILY), 필요에 따라 unique=True를 조정합니다.


"Ex) * * * * *  cd /home/asicentralcity3/Workspace/air_quality_data; /home/asicentralcity3/myenv/bin/python main.py 서울 반포동 HOUR unique=True>> /home/asicentralcity3/Workspace/air_quality_data/cronlogs.log 2>&1; cd"

- arg1 = 도시
- arg2= 동명
- arg3 = Timeframe (HOUR, DAILY)
- arg4 = uniqueFlag=True, uniqueFlag=False
- uniqueFlag=False --> crontab 주기별로 기상청 API 조회하여 현재 Record Timestamp가 마지막 Record Timestamp과 동일해도 INSERT 진행 (Timestamp만 현재 시간으로 갱신)
- uniqueFlag=True --> crontab 주기별로 기상청 API 조회하여 현재 Timestamp가 다를 경우에만 INSERT 진행

**6. 데이터베이스 정보**
데이터베이스: main_centralcity
데이터베이스 사용자: centralcity_collector
호스트: 218.50.4.180
포트: 3306
Password: N/A 
새로운 테이블: air_quality_history_final

**7. 설치**
저장소를 클론합니다:
bash
코드 복사
git clone https://github.com/your/repository.git
cd repository
Dependency를 설치합니다 (Python 및 pip이 설치되어 있어야 합니다):
bash
코드 복사
pip install -r requirements.txt
config.json 파일을 자신의 데이터베이스 자격 증명 및 설정으로 구성합니다.

**8. 사용법**
main.py를 실행하여 데이터 검색 및 데이터베이스 삽입을 시작합니다:
bash
코드 복사
python main.py
예약된 작업의 출력 및 오류를 확인하기 위해 /home/asicentralcity3/Workspace/air_quality_data/cronlogs.log의 cron 작업 로그를 모니터링합니다.

**9. 기여자**
- nkty26



* 이 README는 프로젝트의 목적, 기능, 설정 지침 및 사용 지침에 대한 개요를 제공합니다. 사용자가 대기질 데이터 관리 시스템을 효과적으로 설정하고 실행하고 유지할 수 있도록 도움을 줍니다.
