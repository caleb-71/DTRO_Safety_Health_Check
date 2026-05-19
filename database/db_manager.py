import sqlite3
import json
from datetime import datetime

# DB 파일 이름 설정 (앱이 실행되는 폴더에 생성됩니다)
DB_FILE = "dtro_safety.db"


def init_db():
    """
    앱이 처음 실행될 때 데이터베이스와 테이블(엑셀 시트)을 만드는 함수입니다.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # checklist_records 라는 이름의 테이블 생성 (SQL 명령어 사용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklist_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 고유 번호
            task_name TEXT,                        -- 작업명
            task_date TEXT,                        -- 작업일자
            task_time TEXT,                        -- 작업시간
            location TEXT,                         -- 작업장소
            manager_name TEXT,                     -- 작업책임자
            work_type TEXT,                        -- 취급작업 종류
            check_results TEXT,                    -- 체크리스트 결과 (JSON)
            signature_data TEXT,                   -- 🌟 [신규] 서명 좌표 데이터 (JSON)
            created_at TIMESTAMP                   -- 저장 시간
        )
    ''')
    conn.commit()
    conn.close()


# 🌟 파라미터 맨 끝에 signature_strokes 가 추가되었습니다!
def save_checklist(task_name, task_date, task_time, location, manager_name, work_type, check_results_dict,
                   signature_strokes):
    """
    화면(View)에서 입력받은 데이터를 DB에 한 줄(Row) 추가하는 함수입니다.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 파이썬의 딕셔너리(사전) 형태를 문자열 보따리(JSON)로 변환
    results_json = json.dumps(check_results_dict, ensure_ascii=False)

    # 🌟 서명 좌표 리스트(strokes)를 문자로 압축 (JSON 형태)
    signature_json = json.dumps(signature_strokes)

    # 현재 시간 기록
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 🌟 INSERT 명령어에 signature_data 항목과 물음표(?) 1개를 추가로 뚫어줍니다.
    cursor.execute('''
        INSERT INTO checklist_records 
        (task_name, task_date, task_time, location, manager_name, work_type, check_results, signature_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (task_name, task_date, task_time, location, manager_name, work_type, results_json, signature_json,
          current_time))

    conn.commit()
    conn.close()
    print(f"[{current_time}] 데이터 및 서명 저장 완료! (책임자: {manager_name}, 종류: {work_type})")


def get_all_records():
    """
    저장된 모든 기록을 불러오는 함수입니다.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 최신 기록이 맨 위로 오도록 내림차순(DESC) 정렬
    cursor.execute('SELECT * FROM checklist_records ORDER BY id DESC')
    rows = cursor.fetchall()

    conn.close()
    return rows


def delete_record(record_id):
    """
    기록 조회 화면에서 선택한 ID의 점검 데이터를 SQLite DB에서 완벽하게 지우는 함수
    """
    # 🌟 상단에 선언해둔 DB_FILE 변수를 깔끔하게 재활용합니다!
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 🌟 진짜 테이블 이름인 'checklist_records'로 완벽하게 수정!
    cursor.execute("DELETE FROM checklist_records WHERE id = ?", (record_id,))

    conn.commit()
    conn.close()