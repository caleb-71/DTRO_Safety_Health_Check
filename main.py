import flet as ft

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

    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE_800)
    page.padding = 0

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.SHIELD_OUTLINED, color=ft.colors.WHITE),
        leading_width=40,
        title=ft.Text("안전보건 체크리스트", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.BLUE_800,
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
            ft.NavigationDestination(icon=ft.icons.FACT_CHECK_OUTLINED, selected_icon=ft.icons.FACT_CHECK, label="체크리스트"),
            ft.NavigationDestination(icon=ft.icons.HISTORY_OUTLINED, selected_icon=ft.icons.HISTORY, label="기록조회"),
            ft.NavigationDestination(icon=ft.icons.PEOPLE_OUTLINE, selected_icon=ft.icons.PEOPLE, label="작업자"),
            ft.NavigationDestination(icon=ft.icons.BAR_CHART_OUTLINED, selected_icon=ft.icons.INSERT_CHART, label="통계"),
            ft.NavigationDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="설정"),
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