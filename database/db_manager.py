import sqlite3
import json
import os
from datetime import datetime

# ✅ DB 파일 위치 — Windows/Android 공통 안전 경로
# Windows  : 프로젝트 루트 폴더에 생성 (main.py 옆)
# Android  : APK 실행 시 Flet이 CWD를 앱 전용 쓰기 가능 폴더로 설정해주므로
#            os.getcwd() 가 가장 안전한 기준점
import platform as _platform

if _platform.system() == "Windows":
    # 개발 환경: database/ 폴더 한 단계 위(프로젝트 루트)에 생성
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
else:
    # Android APK: Flet이 설정한 앱 전용 쓰기 가능 CWD 사용
    _BASE_DIR = os.getcwd()

DB_FILE = os.path.join(_BASE_DIR, "dtro_safety.db")


def init_db():
    """앱 최초 실행 시 DB 파일과 테이블을 생성합니다."""
    # ✅ with 문으로 커넥션 자동 close 보장
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # 점검 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklist_records (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name     TEXT,
                task_date     TEXT,
                task_time     TEXT,
                location      TEXT,
                manager_name  TEXT,
                work_type     TEXT,
                check_results TEXT,
                signature_data TEXT,
                created_at    TIMESTAMP
            )
        ''')

        # 작업자 명단 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                department TEXT,
                phone      TEXT
            )
        ''')

        conn.commit()


def save_checklist(task_name, task_date, task_time, location,
                   manager_name, work_type, check_results_dict, signature_strokes):
    results_json   = json.dumps(check_results_dict, ensure_ascii=False)
    signature_json = json.dumps(signature_strokes)
    current_time   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ✅ with 문 + 예외 처리로 안전한 저장
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('''
                INSERT INTO checklist_records
                (task_name, task_date, task_time, location,
                 manager_name, work_type, check_results, signature_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task_name, task_date, task_time, location,
                  manager_name, work_type, results_json, signature_json, current_time))
            conn.commit()
        print(f"[{current_time}] 저장 완료 (책임자: {manager_name}, 종류: {work_type})")
    except sqlite3.Error as ex:
        print(f"[DB 오류] save_checklist: {ex}")
        raise   # checklist_view.py의 try/except로 전달


def get_all_records():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute(
                'SELECT * FROM checklist_records ORDER BY id DESC'
            )
            return cursor.fetchall()
    except sqlite3.Error as ex:
        print(f"[DB 오류] get_all_records: {ex}")
        return []


def delete_record(record_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "DELETE FROM checklist_records WHERE id = ?", (record_id,)
            )
            conn.commit()
    except sqlite3.Error as ex:
        print(f"[DB 오류] delete_record: {ex}")


def delete_all_records():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM checklist_records")
            conn.commit()
    except sqlite3.Error as ex:
        print(f"[DB 오류] delete_all_records: {ex}")
        raise   # settings_view.py의 try/except로 전달


def add_worker(name, department, phone):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO workers (name, department, phone) VALUES (?, ?, ?)",
                (name, department, phone)
            )
            conn.commit()
    except sqlite3.Error as ex:
        print(f"[DB 오류] add_worker: {ex}")


def get_all_workers():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute(
                "SELECT * FROM workers ORDER BY name ASC"
            )
            return cursor.fetchall()
    except sqlite3.Error as ex:
        print(f"[DB 오류] get_all_workers: {ex}")
        return []


def delete_worker(worker_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "DELETE FROM workers WHERE id = ?", (worker_id,)
            )
            conn.commit()
    except sqlite3.Error as ex:
        print(f"[DB 오류] delete_worker: {ex}")


def get_records_by_manager(manager_name):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.execute(
                "SELECT * FROM checklist_records WHERE manager_name = ? ORDER BY id DESC",
                (manager_name,)
            )
            return cursor.fetchall()
    except sqlite3.Error as ex:
        print(f"[DB 오류] get_records_by_manager: {ex}")
        return []