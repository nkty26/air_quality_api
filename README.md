**공기질 API 데이터 관리 시스템**
**개요**
이 프로젝트는 한국 기상청 API로부터 대기질 데이터를 자동으로 검색하여 MySQL 데이터베이스에 저장하는 기능을 제공합니다. API 요청, 데이터베이스 상호작용 및 주기적 데이터 업데이트를 위한 cron 작업 스케줄링을 처리하는 모듈을 포함하고 있습니다.

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
참고: 보안 및 개인 정보 문제로 인해 이 저장소에 config.json 파일이 포함되어 있지 않습니다. 사용자는 이 파일을 로컬에 생성하고 적절한 자격 증명을 설정해야 합니다.


**5. cron 작업 설정**
주기적인 업데이트를 위해 다음 crontab 항목을 추가합니다:
bash
코드 복사
* * * * *  cd /home/asicentralcity3/Workspace/air_quality_data; /home/asicentralcity3/myenv/bin/python main.py 서울 반포동 HOUR unique=True >> /home/asicentralcity3/Workspace/air_quality_data/cronlogs.log 2>&1; cd
원하는 도시 및 구역을 선택하고, 타임프레임 (HOUR 또는 DAILY), 필요에 따라 unique=True를 조정합니다.

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
이 README는 프로젝트의 목적, 기능, 설정 지침 및 사용 지침에 대한 개요를 제공합니다. 사용자가 대기질 데이터 관리 시스템을 효과적으로 설정하고 실행하고 유지할 수 있도록 도움을 줍니다.
