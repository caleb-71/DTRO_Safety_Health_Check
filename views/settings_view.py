import flet as ft
from database.db_manager import delete_all_records  # 🌟 DB 초기화 함수 불러오기


def SettingsView(page: ft.Page):
    # 테마 스위치를 껐다 켤 때 작동하는 함수
    def theme_changed(e):
        is_dark = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.client_storage.set("theme", "dark" if is_dark else "light")
        page.update()

    # ==========================================
    # 🌟 [신규 기능] 데이터 초기화 마법의 함수 구역
    # ==========================================
    def reset_data_click(e):
        # 2. 팝업창에서 '전체 삭제'를 실제로 눌렀을 때 실행
        def confirm_reset(cp_e):
            try:
                delete_all_records()  # DB의 모든 기록 날리기
                confirm_dlg.open = False

                # 안정성이 검증된 순정 알림창 문법 적용
                page.snack_bar = ft.SnackBar(
                    ft.Text("🗑️ 모든 점검 데이터가 완전 초기화되었습니다."),
                    bgcolor=ft.colors.RED_700
                )
            except Exception as ex:
                confirm_dlg.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"❌ 초기화 실패: {str(ex)}"),
                    bgcolor=ft.colors.RED_ACCENT
                )

            page.snack_bar.open = True
            page.update()

        # 3. 팝업창에서 '취소'를 눌렀을 때 실행
        def cancel_reset(cp_e):
            confirm_dlg.open = False
            page.update()

        # 1. 초기화 버튼 클릭 시 "진짜 지울 거냐"고 물어보는 2중 안전 팝업창 조립
        confirm_dlg = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.icons.WARNING, color=ft.colors.RED_700),
                ft.Text("데이터 초기화 경고", weight=ft.FontWeight.BOLD)
            ], spacing=10),
            content=ft.Text("정말로 모든 점검 기록을 영구 삭제하시겠습니까?\n이 작업은 절대 되돌릴 수 없습니다!"),
            actions=[
                ft.TextButton("취소", on_click=cancel_reset),
                ft.ElevatedButton(
                    "전체 삭제",
                    on_click=confirm_reset,
                    bgcolor=ft.colors.RED_700,
                    color=ft.colors.WHITE
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = confirm_dlg
        confirm_dlg.open = True
        page.update()

    # 앱 켤 때 스마트폰이 기억하던 테마 상태 가져오기
    current_theme = page.client_storage.get("theme") or "light"

    # 스위치 디자인 설정
    theme_switch = ft.Switch(
        value=(current_theme == "dark"),
        on_change=theme_changed,
        active_color=ft.colors.BLUE_500
    )

    return ft.Column([
        ft.Container(
            content=ft.Text("환경 설정", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(left=20, top=20, bottom=10)
        ),
        ft.Container(
            content=ft.ListView([
                # 테마 변경 레이아웃
                ft.ListTile(
                    leading=ft.Icon(ft.icons.DARK_MODE, color=ft.colors.BLUE_GREY_500),
                    title=ft.Text("어두운 배경 (다크 모드)", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("화면 테마를 밝게 하거나 어둡게 전환합니다.", size=13),
                    trailing=theme_switch,
                    toggle_inputs=True
                ),
                ft.Divider(height=20, color=ft.colors.BLACK12),

                # 앱 정보 구역
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE_GREY_500),
                    title=ft.Text("앱 정보", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("버전: 1.0.0\n개발: DTRO 안전계획팀", size=13)
                ),
                ft.Divider(height=20, color=ft.colors.BLACK12),

                # 🌟 [생명 주입] 데이터 초기화 구역 (on_click 이벤트 바인딩)
                ft.ListTile(
                    leading=ft.Icon(ft.icons.WARNING_AMBER, color=ft.colors.RED_400),
                    title=ft.Text("데이터 초기화", color=ft.colors.RED_500, weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("모든 점검 기록과 설정을 삭제합니다.", size=13),
                    on_click=reset_data_click  # ➔ 마우스나 손가락으로 누르면 경고 함수가 발동합니다!
                )
            ], spacing=5),
            padding=ft.padding.symmetric(horizontal=10),
            expand=True
        )
    ], expand=True)