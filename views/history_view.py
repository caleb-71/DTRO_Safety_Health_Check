import flet as ft
import json

# 📦 DB에서 데이터 불러오는 함수 가져오기
from database.db_manager import get_all_records


def HistoryView(page: ft.Page):
    # 1. DB에서 모든 기록 가져오기 (가장 최근 기록이 먼저 옴)
    records = get_all_records()

    # 2. 목록을 담을 스크롤 가능한 뷰 (ListView)
    list_view = ft.ListView(expand=True, spacing=10, padding=20)

    # 데이터가 없을 때 보여줄 화면
    if not records:
        list_view.controls.append(
            ft.Container(
                content=ft.Text("저장된 점검 기록이 없습니다.", size=16, color=ft.colors.GREY_500),
                alignment=ft.alignment.center,
                padding=50
            )
        )
    else:
        # 데이터가 있으면 하나씩 카드로 만들어서 리스트에 추가
        for row in records:
            # DB의 컬럼 순서대로 변수에 저장
            record_id = row[0]
            task_name = row[1]
            task_date = row[2]
            # task_time = row[3] (목록에서는 생략)
            # location = row[4] (목록에서는 생략)
            manager_name = row[5]
            work_type = row[6]
            check_results_json = row[7]  # JSON 보따리
            created_at = row[8]

            # 카드를 클릭했을 때 상세 팝업창을 띄우는 함수 (클로저 활용)
            def create_show_detail_func(t_name, t_date, m_name, w_type, results_json, c_at):
                def show_detail(e):
                    # JSON 문자열을 파이썬 딕셔너리로 다시 변환
                    try:
                        results_dict = json.loads(results_json)
                    except:
                        results_dict = {"오류": "데이터를 해독할 수 없습니다."}

                    # 상세 내용을 담을 텍스트 기둥(Column)
                    detail_content = ft.Column(scroll=ft.ScrollMode.AUTO, height=400, spacing=10)

                    # 기본 정보 헤더
                    detail_content.controls.append(ft.Text(f"📋 {t_name}", size=20, weight=ft.FontWeight.BOLD))
                    detail_content.controls.append(ft.Text(f"• 책임자: {m_name}\n• 작업일자: {t_date}\n• 저장시간: {c_at}"))
                    detail_content.controls.append(ft.Divider(height=1, color=ft.colors.GREY_300))
                    detail_content.controls.append(
                        ft.Text(f"[{w_type}] 체크 결과", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700))

                    # 딕셔너리를 돌면서 체크 항목 텍스트 생성
                    for item_text, result in results_dict.items():
                        # 결과값에 따라 글자색 다르게 표시
                        if result == "확인":
                            color = ft.colors.GREEN_700
                        elif result == "해당없음":
                            color = ft.colors.GREY_700
                        else:
                            color = ft.colors.RED_700  # 미확인일 경우 빨간색

                        detail_content.controls.append(
                            ft.Text(f"{item_text} : {result}", color=color)
                        )

                    # 팝업창 닫기 함수
                    def close_dlg(e):
                        dlg.open = False
                        page.update()

                    # 팝업창(AlertDialog) 객체 생성
                    dlg = ft.AlertDialog(
                        content=detail_content,
                        actions=[ft.TextButton("닫기", on_click=close_dlg)],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )

                    # 화면에 팝업창 띄우기
                    page.dialog = dlg
                    dlg.open = True
                    page.update()

                return show_detail

            # Flet의 ListTile을 사용하면 카카오톡 목록처럼 깔끔한 UI를 만들 수 있습니다.
            card = ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.ASSIGNMENT, color=ft.colors.BLUE_700, size=30),
                    title=ft.Text(f"[{work_type}] {task_name}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"책임자: {manager_name} | 일자: {task_date}\n기록: {created_at}"),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=create_show_detail_func(task_name, task_date, manager_name, work_type, check_results_json,
                                                     created_at)
                )
            )
            list_view.controls.append(card)

    # 3. 최종 화면 조립
    return ft.Column([
        ft.Container(
            content=ft.Text("기록 조회", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(left=20, top=20, bottom=10)
        ),
        list_view
    ], expand=True)