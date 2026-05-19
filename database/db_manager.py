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

    # 1. 점검 기록 테이블
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
            signature_data TEXT,                   -- 서명 좌표 데이터 (JSON)
            created_at TIMESTAMP                   -- 저장 시간
        )
    ''')

    # 2. 🌟 [신규] 작업자 명단 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            phone TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_checklist(task_name, task_date, task_time, location, manager_name, work_type, check_results_dict,
                   signature_strokes):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    results_json = json.dumps(check_results_dict, ensure_ascii=False)
    signature_json = json.dumps(signature_strokes)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM checklist_records ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_record(record_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checklist_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()


def delete_all_records():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM checklist_records")
    conn.commit()
    conn.close()


# ==========================================
# 🌟 [신규] 작업자 데이터 관리 기능 함수들
# ==========================================
def add_worker(name, department, phone):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO workers (name, department, phone) VALUES (?, ?, ?)", (name, department, phone))
    conn.commit()
    conn.close()


def get_all_workers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workers ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_worker(worker_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
    conn.commit()
    conn.close()


def get_records_by_manager(manager_name):
    """특정 작업책임자가 과거에 참여했던 안전점검 기록만 뽑아옵니다."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checklist_records WHERE manager_name = ? ORDER BY id DESC", (manager_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows