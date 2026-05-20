import flet as ft

# =====================================================
# 🛡️ [버전 호환 패치] - 반드시 다른 import보다 먼저 실행
# 최신 Flet은 ft.Colors / ft.Icons (대문자)를 사용
# 구버전 코드(ft.colors / ft.icons 소문자)와 호환되도록 처리
# =====================================================
if hasattr(ft, 'Colors') and not hasattr(ft, 'colors'):
    ft.colors = ft.Colors
if hasattr(ft, 'Icons') and not hasattr(ft, 'icons'):
    ft.icons = ft.Icons

# =====================================================
# 이 아래부터 나머지 import
# =====================================================
from database.db_manager import init_db
from views.checklist_view import ChecklistView
from views.history_view import HistoryView
from views.worker_view import WorkerView
from views.stats_view import StatsView
from views.settings_view import SettingsView


def main(page: ft.Page):
    init_db()

    page.title = "DTRO 안전보건"
    page.window_width = 450
    page.window_height = 800

    saved_theme = page.client_storage.get("theme")
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_800 if hasattr(ft, 'Colors') else ft.colors.BLUE_800)
    page.padding = 0

    _icons = ft.Icons if hasattr(ft, 'Icons') else ft.icons
    _colors = ft.Colors if hasattr(ft, 'Colors') else ft.colors

    page.appbar = ft.AppBar(
        leading=ft.Icon(_icons.SHIELD_OUTLINED, color=_colors.WHITE),
        leading_width=40,
        title=ft.Text("안전보건 체크리스트", color=_colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=_colors.BLUE_800,
        center_title=False,
    )

    main_container = ft.Container(
        expand=True,
        content=ChecklistView(page)
    )

    def change_tab(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            main_container.content = ChecklistView(page)
        elif selected_index == 1:
            main_container.content = HistoryView(page)
        elif selected_index == 2:
            main_container.content = WorkerView(page)
        elif selected_index == 3:
            main_container.content = StatsView(page)
        elif selected_index == 4:
            main_container.content = SettingsView(page)
        page.update()

    bottom_nav = ft.NavigationBar(
        selected_index=0,
        on_change=change_tab,
        destinations=[
            ft.NavigationDestination(icon=_icons.FACT_CHECK_OUTLINED,  selected_icon=_icons.FACT_CHECK,    label="체크리스트"),
            ft.NavigationDestination(icon=_icons.HISTORY_OUTLINED,      selected_icon=_icons.HISTORY,       label="기록조회"),
            ft.NavigationDestination(icon=_icons.PEOPLE_OUTLINE,        selected_icon=_icons.PEOPLE,        label="작업자"),
            ft.NavigationDestination(icon=_icons.BAR_CHART_OUTLINED,    selected_icon=_icons.INSERT_CHART,  label="통계"),
            ft.NavigationDestination(icon=_icons.SETTINGS_OUTLINED,     selected_icon=_icons.SETTINGS,      label="설정"),
        ]
    )

    page.add(
        ft.Column(
            [main_container],
            expand=True
        )
    )
    page.navigation_bar = bottom_nav
    page.update()


if __name__ == "__main__":
    ft.app(target=main)