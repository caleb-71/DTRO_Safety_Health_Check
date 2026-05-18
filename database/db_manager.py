import sqlite3
import json
from datetime import datetime

# DB 파일 이름 설정 (앱이 실행되는 폴더에 생성됩니다)
DB_FILE = "dtro_safety.db"


def init_db():
    """
    앱이 처음 실행될 때 데이터베이스와 테이블(엑셀 시트)을 만드는 함수입니다.
    이미 만들어져 있다면 기존 것을 그대로 사용합니다.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # checklist_records 라는 이름의 테이블 생성 (SQL 명령어 사용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklist_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 고유 번호 (자동으로 1, 2, 3... 부여)
            task_name TEXT,                        -- 작업명
            task_date TEXT,                        -- 작업일자
            task_time TEXT,                        -- 작업시간
            location TEXT,                         -- 작업장소
            manager_name TEXT,                     -- 작업책임자
            work_type TEXT,                        -- 취급작업 종류 (아크용접, 가스용접 등)
            check_results TEXT,                    -- 체크리스트 결과 (JSON 형태의 보따리로 저장)
            created_at TIMESTAMP                   -- 실제 저장 버튼을 누른 시간
        )
    ''')
    conn.commit()  # 변경사항 저장 (엑셀의 Ctrl+S와 같음)
    conn.close()  # 파일 닫기


def save_checklist(task_name, task_date, task_time, location, manager_name, work_type, check_results_dict):
    """
    화면(View)에서 입력받은 데이터를 DB에 한 줄(Row) 추가하는 함수입니다.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 파이썬의 딕셔너리(사전) 형태를 문자열 보따리(JSON)로 변환
    results_json = json.dumps(check_results_dict, ensure_ascii=False)

    # 현재 시간 기록
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 엑셀의 빈 줄에 데이터를 채워 넣는 SQL 명령어
    cursor.execute('''
        INSERT INTO checklist_records 
        (task_name, task_date, task_time, location, manager_name, work_type, check_results, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (task_name, task_date, task_time, location, manager_name, work_type, results_json, current_time))

    conn.commit()
    conn.close()
    print(f"[{current_time}] 데이터 저장 완료! (책임자: {manager_name}, 종류: {work_type})")


def get_all_records():
    """
    저장된 모든 기록을 불러오는 함수입니다. (나중에 '기록 조회' 화면에서 사용)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM checklist_records ORDER BY id DESC')  # 최근 기록부터 가져오기
    rows = cursor.fetchall()  # 모든 줄 가져오기

    conn.close()
    return rows