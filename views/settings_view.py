import flet as ft
from database.db_manager import delete_all_records


def SettingsView(page: ft.Page):

    # ==========================================
    # 🌟 1. 데이터 초기화 확인 BottomSheet
    #   page.overlay 등록 BottomSheet 방식
    # ==========================================
    def _cancel_reset(e):
        reset_sheet.open = False
        page.update()

    def _confirm_reset(e):
        reset_sheet.open = False
        try:
            delete_all_records()
            page.snack_bar = ft.SnackBar(
                ft.Text("모든 점검 데이터가 초기화되었습니다."),
                bgcolor=ft.Colors.RED_700,
            )
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"초기화 실패: {ex}"),
                bgcolor=ft.Colors.RED_ACCENT,
            )
        page.snack_bar.open = True
        page.update()

    reset_sheet = ft.BottomSheet(
        open=False,
        content=ft.Container(
            padding=ft.Padding(24, 24, 24, 36),
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED,
                                color=ft.Colors.RED_600, size=24),
                        ft.Text(
                            "데이터 초기화 경고",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED_600,
                        ),
                    ], spacing=8),
                    ft.Text(
                        "정말로 모든 점검 기록을 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다!",
                        size=14, color=ft.Colors.BLUE_GREY_700,
                    ),
                    ft.Row([
                        ft.OutlinedButton(
                            content=ft.Text("취소"),
                            on_click=_cancel_reset,
                            expand=1,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text("전체 삭제", color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED_700,
                            on_click=_confirm_reset,
                            expand=1,
                            height=46,
                        ),
                    ], spacing=12),
                ],
            ),
        ),
    )

    page.overlay.append(reset_sheet)

    def open_reset_sheet(e):
        reset_sheet.open = True
        page.update()

    # ==========================================
    # 🌟 2. 테마 설정 (async — SharedPreferences)
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
    # 🌟 3. UI 화면 조립
    # ==========================================
    current_is_dark = (page.theme_mode == ft.ThemeMode.DARK)
    theme_switch = ft.Switch(
        value=current_is_dark,
        on_change=theme_changed,
        active_color=ft.Colors.BLUE_500,
    )

    return ft.Column([
        ft.Container(
            content=ft.Text("환경 설정", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.Padding(20, 20, 0, 10),
        ),
        ft.Container(
            expand=True,
            padding=ft.Padding(10, 0, 10, 0),
            content=ft.ListView(
                spacing=5,
                controls=[
                    # 다크 모드
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DARK_MODE,
                                        color=ft.Colors.BLUE_GREY_500),
                        title=ft.Text("어두운 배경 (다크 모드)",
                                      weight=ft.FontWeight.BOLD, size=15),
                        subtitle=ft.Text("화면 테마를 밝게 하거나 어둡게 전환합니다.",
                                         size=13),
                        trailing=theme_switch,
                        toggle_inputs=True,
                    ),
                    ft.Divider(height=20, color=ft.Colors.BLACK12),

                    # 앱 정보
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.INFO_OUTLINE,
                                        color=ft.Colors.BLUE_GREY_500),
                        title=ft.Text("앱 정보",
                                      weight=ft.FontWeight.BOLD, size=15),
                        subtitle=ft.Text("버전: 1.0.0\n개발: DTRO 안전계획팀",
                                         size=13),
                    ),
                    ft.Divider(height=20, color=ft.Colors.BLACK12),

                    # 데이터 초기화
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.WARNING_AMBER,
                                        color=ft.Colors.RED_400),
                        title=ft.Text("데이터 초기화",
                                      color=ft.Colors.RED_500,
                                      weight=ft.FontWeight.BOLD, size=15),
                        subtitle=ft.Text("모든 점검 기록과 설정을 삭제합니다.",
                                         size=13),
                        on_click=open_reset_sheet,   # ✅ BottomSheet 호출
                    ),
                ],
            ),
        ),
    ], expand=True)