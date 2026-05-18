import flet as ft
import flet.canvas as cv  # 🌟 캔버스 그리기용
import json

from database.db_manager import get_all_records


def HistoryView(page: ft.Page):
    records = get_all_records()
    list_view = ft.ListView(expand=True, spacing=10, padding=20)

    if not records:
        list_view.controls.append(
            ft.Container(
                content=ft.Text("저장된 점검 기록이 없습니다.", size=16, color=ft.colors.GREY_500),
                alignment=ft.alignment.center,
                padding=50
            )
        )
    else:
        for row in records:
            # 🌟 DB 구조 변경으로 인한 인덱스 조정 완료
            record_id = row[0]
            task_name = row[1]
            task_date = row[2]
            manager_name = row[5]
            work_type = row[6]
            check_results_json = row[7]
            signature_json = row[8]  # 🌟 [신규] 서명 데이터
            created_at = row[9]  # 🌟 [밀림] 8 -> 9로 변경됨

            def create_show_detail_func(t_name, t_date, m_name, w_type, results_json, sig_json, c_at):
                def show_detail(e):
                    try:
                        results_dict = json.loads(results_json)
                    except:
                        results_dict = {"오류": "데이터를 해독할 수 없습니다."}

                    # 서명 좌표 해독
                    try:
                        signature_strokes = json.loads(sig_json) if sig_json else []
                    except:
                        signature_strokes = []

                    # 팝업창 세로 스크롤 허용 및 높이 조절
                    detail_content = ft.Column(scroll=ft.ScrollMode.AUTO, height=500, spacing=10)

                    detail_content.controls.append(ft.Text(f"📋 {t_name}", size=20, weight=ft.FontWeight.BOLD))
                    detail_content.controls.append(ft.Text(f"• 책임자: {m_name}\n• 작업일자: {t_date}\n• 저장시간: {c_at}"))
                    detail_content.controls.append(ft.Divider(height=1, color=ft.colors.GREY_300))
                    detail_content.controls.append(
                        ft.Text(f"[{w_type}] 체크 결과", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700))

                    for item_text, result in results_dict.items():
                        if result == "확인":
                            color = ft.colors.GREEN_700
                        elif result == "해당없음":
                            color = ft.colors.GREY_700
                        else:
                            color = ft.colors.RED_700
                        detail_content.controls.append(ft.Text(f"{item_text} : {result}", color=color))

                    # 🌟 팝업창 하단에 서명 도화지 다시 그리기
                    if signature_strokes:
                        detail_content.controls.append(ft.Divider(height=1, color=ft.colors.GREY_300))
                        detail_content.controls.append(
                            ft.Text("✍️ 작업책임자 서명", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700))

                        elements = []
                        for stroke in signature_strokes:
                            if not stroke: continue
                            path_elements = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
                            for x, y in stroke[1:]:
                                path_elements.append(cv.Path.LineTo(x, y))
                            elements.append(cv.Path(
                                elements=path_elements,
                                paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.BLACK, stroke_width=3,
                                               stroke_cap=ft.StrokeCap.ROUND, stroke_join=ft.StrokeJoin.ROUND)
                            ))

                        # 액자 크기 설정 (원래 서명 패드와 동일한 비율)
                        sig_canvas = cv.Canvas(shapes=elements, width=300, height=150)
                        detail_content.controls.append(
                            ft.Container(content=sig_canvas, border=ft.border.all(1, ft.colors.BLACK26),
                                         border_radius=5, bgcolor=ft.colors.WHITE)
                        )

                    def close_dlg(e):
                        dlg.open = False
                        page.update()

                    dlg = ft.AlertDialog(
                        content=detail_content,
                        actions=[ft.TextButton("닫기", on_click=close_dlg)],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )

                    page.dialog = dlg
                    dlg.open = True
                    page.update()

                return show_detail

            card = ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.ASSIGNMENT, color=ft.colors.BLUE_700, size=30),
                    title=ft.Text(f"[{work_type}] {task_name}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"책임자: {manager_name} | 일자: {task_date}\n기록: {created_at}"),
                    trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                    on_click=create_show_detail_func(task_name, task_date, manager_name, work_type, check_results_json,
                                                     signature_json, created_at)
                )
            )
            list_view.controls.append(card)

    return ft.Column([
        ft.Container(
            content=ft.Text("과거 점검 기록", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(left=20, top=20, bottom=10)
        ),
        list_view
    ], expand=True)