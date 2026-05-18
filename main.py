import flet as ft

# 📦 패키지 모듈 불러오기
from database.db_manager import init_db
from views.checklist_view import ChecklistView


# (나중에 만들 화면들도 여기에 추가될 예정입니다)
from views.history_view import HistoryView

def main(page: ft.Page):
    # ==========================================
    # 1. 앱 초기 세팅 및 DB 초기화
    # ==========================================
    init_db()  # 앱이 켜질 때 SQLite 데이터베이스 파일과 테이블을 준비합니다.

    page.title = "DTRO 안전보건"
    page.window_width = 450
    page.window_height = 800

    # 🎨 테마 설정 (DTRO에 어울리는 신뢰감 있는 블루 톤)
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

    # 📺 화면이 교체될 메인 컨테이너 (여기에 메뉴별 화면이 들어갑니다)
    main_container = ft.Container(
        expand=True,
        content=ChecklistView(page)  # 앱 실행 시 기본 화면 설정
    )

    # 🔄 하단 메뉴 클릭 시 화면 전환 로직
    def change_tab(e):
        selected_index = e.control.selected_index

        if selected_index == 0:
            main_container.content = ChecklistView(page)
        elif selected_index == 1:
            # TODO: 나중에 HistoryView(page)로 교체할 부분입니다.
            main_container.content = HistoryView(page)

        elif selected_index == 2:
            main_container.content = ft.Container(content=ft.Text("작업자 관리 메뉴"), alignment=ft.alignment.center)
        elif selected_index == 3:
            main_container.content = ft.Container(content=ft.Text("통계 메뉴"), alignment=ft.alignment.center)
        elif selected_index == 4:
            main_container.content = ft.Container(content=ft.Text("환경 설정"), alignment=ft.alignment.center)

        page.update()  # 화면 새로고침

    # 🖱️ 하단 네비게이션 바
    # 🖱️ 하단 네비게이션 바 (수정됨)
    bottom_nav = ft.NavigationBar(
        selected_index=0,
        on_change=change_tab,
        destinations=[
            ft.NavigationDestination(icon=ft.icons.FACT_CHECK_OUTLINED, selected_icon=ft.icons.FACT_CHECK,
                                     label="체크리스트"),
            ft.NavigationDestination(icon=ft.icons.HISTORY_OUTLINED, selected_icon=ft.icons.HISTORY, label="기록조회"),
            ft.NavigationDestination(icon=ft.icons.PEOPLE_OUTLINE, selected_icon=ft.icons.PEOPLE, label="작업자"),
            ft.NavigationDestination(icon=ft.icons.BAR_CHART_OUTLINED, selected_icon=ft.icons.INSERT_CHART,
                                     label="통계"),
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
