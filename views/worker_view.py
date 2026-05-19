import flet as ft
from database.db_manager import add_worker, get_all_workers, delete_worker, get_records_by_manager


def WorkerView(page: ft.Page):
    # 🌟 연락처 필드 삭제됨
    name_input = ft.TextField(label="이름", expand=1, height=40, border_radius=10)
    dept_input = ft.TextField(label="소속/부서 (선택)", expand=1, height=40, border_radius=10)

    worker_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def update_worker_list():
        worker_list_view.controls.clear()
        workers = get_all_workers()

        if not workers:
            worker_list_view.controls.append(
                ft.Container(
                    content=ft.Text("등록된 작업자가 없습니다. 상단에서 등록해 주세요.", color=ft.colors.GREY_500),
                    alignment=ft.alignment.center, padding=30
                )
            )
        else:
            for w in workers:
                # w_phone 변수는 버립니다
                w_id, w_name, w_dept, _ = w

                def create_click_event(name):
                    return lambda _: show_worker_history(name)

                def create_delete_event(worker_id, name):
                    def delete_click(e):
                        delete_worker(worker_id)
                        update_worker_list()
                        page.snack_bar = ft.SnackBar(ft.Text(f"🗑️ {name} 작업자가 삭제되었습니다."), bgcolor=ft.colors.GREY_700)
                        page.snack_bar.open = True
                        page.update()

                    return delete_click

                worker_list_view.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            leading=ft.CircleAvatar(content=ft.Text(w_name[0] if w_name else "작"),
                                                    bgcolor=ft.colors.BLUE_100, color=ft.colors.BLUE_800),
                            title=ft.Text(w_name, weight=ft.FontWeight.BOLD),
                            # 🌟 연락처 삭제됨
                            subtitle=ft.Text(f"소속: {w_dept}"),
                            trailing=ft.IconButton(icon=ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_400,
                                                   on_click=create_delete_event(w_id, w_name)),
                            on_click=create_click_event(w_name)
                        )
                    )
                )
        page.update()

    def show_worker_history(manager_name):
        history_records = get_records_by_manager(manager_name)

        history_content = ft.Column(scroll=ft.ScrollMode.AUTO, height=400, width=350, spacing=10)
        history_content.controls.append(
            ft.Text(f"👷 [{manager_name}] 안전 점검 이력", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800))
        history_content.controls.append(ft.Divider(height=1))

        if not history_records:
            history_content.controls.append(ft.Text("과거 점검 기록이 없습니다.", color=ft.colors.GREY_500, size=13))
        else:
            for row in history_records:
                task_name = row[1]
                task_date = row[2]
                work_type = row[6]

                history_content.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"[{work_type}] {task_name}", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"일자: {task_date}", size=12, color=ft.colors.GREY_600)
                        ], spacing=3),
                        padding=10, bgcolor=ft.colors.BLUE_GREY_50, border_radius=8
                    )
                )

        def close_history_dlg(e):
            history_dlg.open = False
            page.update()

        history_dlg = ft.AlertDialog(
            content=history_content,
            actions=[ft.TextButton("닫기", on_click=close_history_dlg)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = history_dlg
        history_dlg.open = True
        page.update()

    def add_new_worker(e):
        if not name_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("이름을 입력하세요!"), bgcolor=ft.colors.RED_ACCENT)
            page.snack_bar.open = True
            page.update()
            return

        # 🌟 연락처 자리에는 빈 칸("")을 넘겨주어 DB 구조 변경 없이 호환되게 처리합니다.
        add_worker(name_input.value, dept_input.value or "미지정", "")
        name_input.value = ""
        dept_input.value = ""
        update_worker_list()

    # 화면 진입 시 최초 1회 그리기
    update_worker_list()

    return ft.Column([
        ft.Container(
            content=ft.Text("현장 인력 관리", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(left=20, top=20, bottom=10)
        ),
        # 🌟 연락처 칸이 사라지고 2줄로 슬림하게 압축되었습니다.
        ft.Container(
            content=ft.Column([
                ft.Row([name_input, dept_input], spacing=5),
                ft.ElevatedButton("등록", on_click=add_new_worker, bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE,
                                  height=40, width=float('inf'))
            ], spacing=5),
            padding=15, margin=ft.padding.symmetric(horizontal=20),
            border=ft.border.all(1, ft.colors.BLACK12), border_radius=12, bgcolor=ft.colors.WHITE
        ),
        ft.Divider(),
        ft.Container(content=worker_list_view, padding=ft.padding.symmetric(horizontal=10), expand=True)
    ], expand=True)