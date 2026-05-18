import flet as ft

# 📦 패키지 모듈 불러오기
from database.db_manager import init_db
from views.checklist_view import ChecklistView
from views.history_view import HistoryView

# 🌟 [신규 추가] 새로 만든 3개의 화면 패키지 상단에 모두 불러오기!
from views.worker_view import WorkerView
from views.stats_view import StatsView
from views.settings_view import SettingsView

def main(page: ft.Page):
    # ==========================================
    # 1. 앱 초기 세팅 및 DB 초기화
    # ==========================================
    init_db()  # 앱이 켜질 때 SQLite 데이터베이스 파일과 테이블을 준비합니다.

    page.title = "DTRO 안전보건"
    page.window_width = 450
    page.window_height = 800

    # 🎨 테마 설정 (스마트폰 저장소에 기억된 테마 불러오기)
    saved_theme = page.client_storage.get("theme")
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT

    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE_800)
    page.padding = 0  # 전체 여백을 없애고 각 화면(View)에서 여백을 관리합니다.

    # ==========================================
    # 2. UI 컴포넌트 구성 (상단바, 메인화면, 하단바)
    # ==========================================

    # 📱 상단 헤더(AppBar) 추가: 스마트폰 앱의 상단 고정 영역
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.SHIELD_OUTLINED, color=ft.colors.WHITE),
        leading_width=40,
        title=ft.Text("안전보건 체크리스트", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=ft.colors.BLUE_800,
        center_title=False,
    )

    # 📺 화면이 교체될 메인 컨테이너 (앱 실행 시 기본 화면: 체크리스트)
    main_container = ft.Container(
        expand=True,
        content=ChecklistView(page)
    )

    # 🔄 하단 메뉴 클릭 시 화면 전환 로직 (5개 메뉴 완전체 연결!)
    def change_tab(e):
        selected_index = e.control.selected_index

        if selected_index == 0:
            main_container.content = ChecklistView(page)
        elif selected_index == 1:
            main_container.content = HistoryView(page)
        elif selected_index == 2:
            main_container.content = WorkerView(page)   # 🌟 임시 컨테이너 지우고 진짜 작업자 화면 연결!
        elif selected_index == 3:
            main_container.content = StatsView(page)     # 🌟 임시 컨테이너 지우고 진짜 통계 화면 연결!
        elif selected_index == 4:
            main_container.content = SettingsView(page)  # 🌟 임시 컨테이너 지우고 진짜 설정 화면 연결!

        page.update()  # 화면 새로고침

    # 🖱️ 하단 네비게이션 바
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

    # ==========================================
    # 3. 화면에 최종 배치
    # ==========================================
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