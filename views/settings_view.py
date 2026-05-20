import flet as ft
from database.db_manager import delete_all_records


def SettingsView(page: ft.Page):
    # ==========================================
    # 1. 테마 설정 (비동기)
    # ==========================================
    async def theme_changed(e):
        is_dark = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT

        for s in page.services:
            if isinstance(s, ft.SharedPreferences):
                await s.set("theme", "dark" if is_dark else "light")
                break

        page.update()

    # ==========================================
    # 2. 팝업창 기능 함수 (미리 정의)
    # ==========================================
    def cancel_reset(e):
        confirm_dlg.open = False
        page.update()

    def confirm_reset(e):
        try:
            delete_all_records()
            confirm_dlg.open = False
            page.snack_bar = ft.SnackBar(
                ft.Text("🗑️ 모든 점검 데이터가 완전 초기화되었습니다."),
                bgcolor=ft.Colors.RED_700
            )
        except Exception as ex:
            confirm_dlg.open = False
            page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ 초기화 실패: {str(ex)}"),
                bgcolor=ft.Colors.RED_ACCENT
            )
        page.snack_bar.open = True
        page.update()

    # ==========================================
    # 3. 🌟 핵심 해결 포인트: 팝업창을 이벤트 밖에서 '미리' 조립해 둡니다.
    # 이렇게 해야 클릭 시 Flet 엔진이 팝업을 잃어버리지 않고 100% 띄웁니다.
    # ==========================================
    confirm_dlg = ft.AlertDialog(
        title=ft.Text("⚠️ 데이터 초기화 경고", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
        content=ft.Text("정말로 모든 점검 기록을 영구 삭제하시겠습니까?\n이 작업은 절대 되돌릴 수 없습니다!"),
        actions=[
            ft.TextButton("취소", on_click=cancel_reset),
            ft.ElevatedButton(
                content=ft.Text("전체 삭제", color=ft.Colors.WHITE),
                on_click=confirm_reset,
                bgcolor=ft.Colors.RED_700
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # 4. 버튼 클릭 시 미리 만들어둔 팝업창을 화면에 호출만 합니다.
    def open_reset_dlg(e):
        page.dialog = confirm_dlg
        confirm_dlg.open = True
        page.update()

    # ==========================================
    # 5. UI 화면 조립
    # ==========================================
    current_is_dark = (page.theme_mode == ft.ThemeMode.DARK)
    theme_switch = ft.Switch(
        value=current_is_dark,
        on_change=theme_changed,
        active_color=ft.Colors.BLUE_500
    )

    return ft.Column([
        ft.Container(
            content=ft.Text("환경 설정", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.Padding(20, 20, 0, 10)
        ),
        ft.Container(
            content=ft.ListView([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DARK_MODE, color=ft.Colors.BLUE_GREY_500),
                    title=ft.Text("어두운 배경 (다크 모드)", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("화면 테마를 밝게 하거나 어둡게 전환합니다.", size=13),
                    trailing=theme_switch,
                    toggle_inputs=True
                ),
                ft.Divider(height=20, color=ft.Colors.BLACK12),

                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_GREY_500),
                    title=ft.Text("앱 정보", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("버전: 1.0.0\n개발: DTRO 안전계획팀", size=13)
                ),
                ft.Divider(height=20, color=ft.Colors.BLACK12),

                # 🌟 선생님이 기획하셨던 깔끔한 원본 디자인 완벽 복구
                # 누락 방지 처리된 팝업 호출 함수(open_reset_dlg) 연결 완료!
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED_400),
                    title=ft.Text("데이터 초기화", color=ft.Colors.RED_500, weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("모든 점검 기록과 설정을 삭제합니다.", size=13),
                    on_click=open_reset_dlg
                )
            ], spacing=5),
            padding=ft.Padding(10, 0, 10, 0),
            expand=True
        )
    ], expand=True)