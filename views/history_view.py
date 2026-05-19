import flet as ft
import flet.canvas as cv
import json

from database.db_manager import get_all_records, delete_record
from utils.report_generator import generate_html_report


def HistoryView(page: ft.Page):
    # 화면을 새로고침하는 내부 함수
    def refresh_data():
        records = get_all_records()
        list_view.controls.clear()

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
                record_id = row[0]
                task_name = row[1]
                task_date = row[2]
                task_time = row[3] if len(row) > 3 else ""
                location = row[4] if len(row) > 4 else ""
                manager_name = row[5]
                work_type = row[6]
                check_results_json = row[7]
                signature_json = row[8]
                created_at = row[9]

                def create_show_detail_func(r_id, t_name, t_date, t_time, loc, m_name, w_type, results_json, sig_json,
                                            c_at):
                    def show_detail(e):
                        try:
                            results_dict = json.loads(results_json)
                        except:
                            results_dict = {"오류": "데이터를 해독할 수 없습니다."}

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
                            color = ft.colors.GREEN_700 if result == "확인" else (
                                ft.colors.GREY_700 if result == "해당없음" else ft.colors.RED_700)
                            detail_content.controls.append(ft.Text(f"{item_text} : {result}", color=color))

                        # 서명 도화지 복원
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

                            sig_canvas = cv.Canvas(shapes=elements, width=300, height=150)
                            detail_content.controls.append(
                                ft.Container(content=sig_canvas, border=ft.border.all(1, ft.colors.BLACK26),
                                             border_radius=5, bgcolor=ft.colors.WHITE)
                            )

                        # ==========================================
                        # 🌟 버튼 기능 함수 정의 (무조건 dlg 조립보다 위에 있어야 합니다!)
                        # ==========================================
                        def close_dlg(e):
                            dlg.open = False
                            page.update()

                        def print_html_report(e):
                            report_data = {
                                "task_name": t_name,
                                "task_date": t_date,
                                "task_time": t_time,
                                "location": loc,
                                "manager_name": m_name,
                                "work_type": w_type,
                                "check_results": results_dict,
                                "signature": signature_strokes
                            }

                            success, msg = generate_html_report(report_data)

                            if success:
                                page.snack_bar = ft.SnackBar(ft.Text("🎉 다운로드 폴더에 보고서가 발행되었습니다!"),
                                                             bgcolor=ft.colors.BLUE_800)
                            else:
                                page.snack_bar = ft.SnackBar(ft.Text(f"❌ 발행 실패: {msg}"), bgcolor=ft.colors.RED_700)
                            page.snack_bar.open = True
                            dlg.open = False
                            page.update()

                        def remove_record(e):
                            def confirm_delete(cp_e):
                                delete_record(r_id)  # DB에서 삭제
                                confirm_dlg.open = False
                                dlg.open = False
                                refresh_data()  # 리스트 새로고침
                                page.snack_bar = ft.SnackBar(ft.Text("🗑️ 기록이 성공적으로 삭제되었습니다."),
                                                             bgcolor=ft.colors.GREY_700)
                                page.snack_bar.open = True
                                page.update()

                            def cancel_delete(cp_e):
                                confirm_dlg.open = False
                                page.update()

                            confirm_dlg = ft.AlertDialog(
                                title=ft.Text("기록 삭제"),
                                content=ft.Text("정말로 이 점검 기록을 영구 삭제하시겠습니까?"),
                                actions=[
                                    ft.TextButton("취소", on_click=cancel_delete),
                                    ft.ElevatedButton("삭제", on_click=confirm_delete, bgcolor=ft.colors.RED_700,
                                                      color=ft.colors.WHITE)
                                ]
                            )
                            page.dialog = confirm_dlg
                            confirm_dlg.open = True
                            page.update()

                        # ==========================================
                        # 🌟 팝업창 조립 (함수를 다 읽은 후 가장 마지막에 조립합니다)
                        # ==========================================
                        dlg = ft.AlertDialog(
                            content=detail_content,
                            actions=[
                                ft.IconButton(icon=ft.icons.PICTURE_AS_PDF, icon_color=ft.colors.BLUE_800,
                                              tooltip="HTML 보고서 발행", on_click=print_html_report),
                                ft.IconButton(icon=ft.icons.DELETE_FOREVER, icon_color=ft.colors.RED_600,
                                              tooltip="기록 삭제", on_click=remove_record),
                                ft.TextButton("닫기", on_click=close_dlg)
                            ]
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
                        on_click=create_show_detail_func(record_id, task_name, task_date, task_time, location,
                                                         manager_name, work_type, check_results_json,
                                                         signature_json, created_at)
                    )
                )
                list_view.controls.append(card)
        page.update()

    # 최초 화면 진입 시 데이터 로드
    list_view = ft.ListView(expand=True, spacing=10, padding=20)
    refresh_data()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Text("과거 점검 기록", size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda _: refresh_data(), tooltip="새로고침")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(left=20, top=20, bottom=10, right=20)
        ),
        list_view
    ], expand=True)