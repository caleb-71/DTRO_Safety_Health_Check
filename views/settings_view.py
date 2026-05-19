import flet as ft


def SettingsView(page: ft.Page):
    # 테마 스위치를 껐다 켤 때 작동하는 함수
    def theme_changed(e):
        is_dark = e.control.value
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.client_storage.set("theme", "dark" if is_dark else "light")
        page.update()

    # 앱 켤 때 스마트폰이 기억하던 테마 상태 가져오기
    current_theme = page.client_storage.get("theme") or "light"

    # 🌟 수정 포인트 1: 스위치 내부의 긴 label을 지우고 덩치를 슬림하게 압축!
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
                # 🌟 수정 포인트 2: ListTile 구조를 가로로 완벽하게 배치
                ft.ListTile(
                    leading=ft.Icon(ft.icons.DARK_MODE, color=ft.colors.BLUE_GREY_500),
                    title=ft.Text("어두운 배경 (다크 모드)", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("화면 테마를 밝게 하거나 어둡게 전환합니다.", size=13),
                    trailing=theme_switch,  # 슬림해진 스위치가 우측 끝에 쏙 들어갑니다.
                    toggle_inputs=True  # 항목 전체를 눌러도 스위치가 딸깍 켜지도록 편리함 추가
                ),
                ft.Divider(height=20, color=ft.colors.BLACK12),

                # 앱 정보 구역
                ft.ListTile(
                    leading=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE_GREY_500),
                    title=ft.Text("앱 정보", weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("버전: 1.0.0\n개발: DTRO 안전계획팀", size=13)
                ),
                ft.Divider(height=20, color=ft.colors.BLACK12),

                # 데이터 초기화 구역
                ft.ListTile(
                    leading=ft.Icon(ft.icons.WARNING_AMBER, color=ft.colors.RED_400),
                    title=ft.Text("데이터 초기화", color=ft.colors.RED_500, weight=ft.FontWeight.BOLD, size=15),
                    subtitle=ft.Text("모든 점검 기록과 설정을 삭제합니다.", size=13),
                )
            ], spacing=5),
            padding=ft.padding.symmetric(horizontal=10),
            expand=True
        )
    ], expand=True)