import flet as ft
import datetime
import os
from database.db_manager import save_checklist
from utils.pdf_exporter import export_to_pdf
import components.styles as style


def ChecklistView(page: ft.Page):
    # ==========================================
    # 1. 입력 필드 생성
    # ==========================================
    task_name_input = ft.TextField(label="작업명", height=40, border_radius=10)
    task_date_input = ft.TextField(label="작업일자", height=40, expand=1, border_radius=10, read_only=True,
                                   hint_text="달력 클릭 ➔")
    task_time_input = ft.TextField(label="작업시간", height=40, expand=1, border_radius=10, read_only=True,
                                   hint_text="시계 클릭 ➔")
    location_input = ft.TextField(label="작업장소", height=40, expand=1, border_radius=10)
    manager_input = ft.TextField(label="작업책임자", height=40, expand=1, border_radius=10)

    # ==========================================
    # 2. 날짜/시간 선택 이벤트 로직
    # ==========================================
    def on_date_change(e):
        if e.control.value:
            task_date_input.value = e.control.value.strftime("%Y-%m-%d")
            task_date_input.update()

    def on_time_change(e):
        if e.control.value:
            task_time_input.value = e.control.value.strftime("%H:%M")
            task_time_input.update()

    date_picker = ft.DatePicker(on_change=on_date_change, help_text="작업 일자를 선택하세요")
    time_picker = ft.TimePicker(on_change=on_time_change, help_text="작업 시간을 선택하세요")

    # ==========================================
    # 🌟 3. FilePicker (파일 저장 팝업) 설정
    # ==========================================
    def on_file_save_result(e: ft.FilePickerResultEvent):
        """사용자가 팝업에서 저장 위치와 이름을 지정하고 '저장'을 눌렀을 때 실행"""
        if not e.path:
            return  # 사용자가 취소를 눌렀다면 아무 동작 안 함

        current_work = list(controls_dict_map.keys())[tabs.selected_index]
        results = {k: v.value for k, v in controls_dict_map[current_work].items()}

        data = {
            "task_name": task_name_input.value,
            "task_date": task_date_input.value,
            "task_time": task_time_input.value,
            "location": location_input.value,
            "manager_name": manager_input.value,
            "work_type": current_work,
            "check_results": results
        }

        # 선택한 절대 경로(e.path)를 PDF 생성기에 전달!
        success, msg = export_to_pdf(data, e.path)

        if success:
            page.snack_bar = ft.SnackBar(ft.Text(f"🎉 PDF 성공적으로 저장됨: {msg}"), bgcolor=style.AppColors.PRIMARY)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ 오류 발생: {msg}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_save_result)

    # 오버레이에 픽커들 추가
    page.overlay.extend([date_picker, time_picker, file_picker])

    date_btn = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, icon_color=style.AppColors.PRIMARY,
                             on_click=lambda _: date_picker.pick_date())
    time_btn = ft.IconButton(icon=ft.icons.ACCESS_TIME, icon_color=style.AppColors.PRIMARY,
                             on_click=lambda _: time_picker.pick_time())

    # 기본 정보 카드 조립
    info_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.EDIT_NOTE, color=style.AppColors.PRIMARY),
                ft.Text("현장 작업 기본정보", size=18, weight=ft.FontWeight.BOLD, color=style.AppColors.PRIMARY)
            ]),
            ft.Divider(height=10, color=ft.colors.TRANSPARENT),
            task_name_input,
            ft.Row([
                ft.Row([task_date_input, date_btn], expand=1, spacing=0),
                ft.Row([task_time_input, time_btn], expand=1, spacing=0)
            ], spacing=10),
            ft.Row([location_input, manager_input]),
        ]),
        **style.card_style()
    )

    # ==========================================
    # 4. 체크리스트 데이터 (유지)
    # ==========================================
    controls_dict_map = {k: {} for k in ["아크용접", "가스용접", "플라즈마", "테르밋용접", "그라인더/금속절단기"]}

    def make_check_item(text, work_type):
        radio_group = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="확인", label="확인", fill_color=style.RADIO_THEME["confirm"]),
                ft.Radio(value="해당없음", label="해당없음", fill_color=style.RADIO_THEME["none"]),
            ], spacing=20)
        )
        controls_dict_map[work_type][text] = radio_group

        return ft.Container(
            content=ft.Column([
                ft.Text(text, weight=ft.FontWeight.W_600, color=style.AppColors.TEXT_MAIN),
                radio_group,
            ], spacing=5),
            padding=15, bgcolor=ft.colors.BLUE_GREY_50, border_radius=12,
        )

    common_items = ["• 안전작업허가서 발급 및 승인 여부 확인", "• 작업 반경 11m 이내 가연물 제거 또는 방호 조치", "• 화재감시자 지정 및 배치 (연장 및 야간작업 포함)",
                    "• 작업장 인근 소화기구 비치 및 소화전 사용 가능 여부", "• 용접방화포(성능인증 제품) 사용 및 개구부 차단", "• 작업 종료 후 최소 30분 이상 잔불 및 훈소 감시"]
    health_items = ["• 용접 흄 제거를 위한 국소배기장치 또는 환기 조치", "• 밀폐공간 작업 시 산소 및 가스 농도 측정 등 안전조치",
                    "• 개인보호구(방진마스크, 용접면, 보안경, 장갑 등) 지급/착용"]
    specific_items = {
        "아크용접": ["• 자동전격방지기 설치 및 정상 작동 여부 확인", "• 홀더의 절연커버 파손 여부 및 규격품 사용 확인", "• 용접 케이블 피복의 손상이나 충전부 노출 확인",
                 "• 작업 중단/종료 시 홀더에서 용접봉 제거 여부", "• 젖은 장갑, 옷, 신발 등 습윤한 상태 작업 여부"],
        "가스용접": ["• 취관(토치) 및 분기관에 역화방지기(안전기) 설치", "• 가스 용기는 40℃ 이하 보관 및 전도 방지 조치", "• 아세틸렌 용기는 반드시 세워서 사용",
                 "• 호스 및 접속부 가스 누설 여부 점검(비눗물 등)", "• 아세틸렌 사용 압력은 0.1 MPa 이하로 유지", "• 산소 밸브 및 조정기에 기름/그리스 접촉 금지"],
        "플라즈마": ["• 냉각 장치의 누수 여부 점검 (절연 성능 저하 방지)", "• 용접기 외함 접지 및 케이블 피복 손상 여부 확인", "• 자동화 설비의 경우 긴급 정지 장치 작동 상태 점검",
                 "• 전원 연결 및 분리 시 반드시 전문가가 수행/전원 차단 확인"],
        "테르밋용접": ["• 고온의 용융 금속 비산 방지용 불연성 덮개 설치 여부", "• 반응 용기 및 모재 예열 시 주변 가연물 점화 방지 조치",
                  "• 테르밋 반응 후 냉각 시까지 작업자 접근 통제/화상 방지", "• 점화 시 스파크가 주변 인화성 물질에 닿지 않도록 격리",
                  "• 반응이 끝난 후 슬래그 등을 안전하게 처리할 장소 확보"],
        "그라인더/금속절단기": ["• 마찰열이나 스파크가 인근 가연성 물질의 점화원이 되지 않도록 격리했는가?"]
    }

    # ==========================================
    # 5. 버튼 이벤트 (저장/PDF)
    # ==========================================
    def on_save_click(e):
        if not manager_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("작업책임자 실명을 입력하세요."), bgcolor=ft.colors.RED_ACCENT)
            page.snack_bar.open = True
            page.update()
            return

        current_work = list(controls_dict_map.keys())[tabs.selected_index]
        results = {}
        for item_text, radio in controls_dict_map[current_work].items():
            if not radio.value:
                page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ 아래 항목의 점검 결과가 누락되었습니다.\n{item_text}"),
                                             bgcolor=ft.colors.RED_700, duration=4000)
                page.snack_bar.open = True
                page.update()
                return
            results[item_text] = radio.value

        save_checklist(task_name_input.value, task_date_input.value, task_time_input.value, location_input.value,
                       manager_input.value, current_work, results)
        page.snack_bar = ft.SnackBar(ft.Text(f"[{current_work}] 저장 완료!"), bgcolor=style.AppColors.SECONDARY)
        page.snack_bar.open = True
        page.update()

    def on_pdf_click(e):
        if not manager_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("작업책임자 실명을 입력하세요."), bgcolor=ft.colors.RED_ACCENT)
            page.snack_bar.open = True
            page.update()
            return

        current_work = list(controls_dict_map.keys())[tabs.selected_index]
        for item_text, radio in controls_dict_map[current_work].items():
            if not radio.value:
                page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ 체크되지 않은 항목이 있어 PDF를 생성할 수 없습니다.\n{item_text}"),
                                             bgcolor=ft.colors.RED_700, duration=4000)
                page.snack_bar.open = True
                page.update()
                return

                # 🌟 디폴트 파일명 미리 생성 (슬래시 제거)
        safe_work_type = current_work.replace("/", "_")
        default_name = f"Safety_Report_{manager_input.value}_{safe_work_type}.pdf"

        # 🌟 PDF를 바로 만들지 않고, 저장 탐색기(FilePicker)를 먼저 호출합니다.
        # 🌟 PDF를 바로 만들지 않고, 저장 탐색기(FilePicker)를 먼저 호출합니다.
        file_picker.save_file(
            file_name=default_name,
            allowed_extensions=["pdf"]
        )

    # ==========================================
    # 6. 각 탭 뷰 구성
    # ==========================================
    def create_section(title, icon, items, work_type, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=color), ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=color)]),
                *[make_check_item(i, work_type) for i in items]
            ], spacing=12),
            **style.card_style()
        )

    def create_tab_content(work_type):
        save_btn = ft.Container(
            content=ft.ElevatedButton(f"체크리스트 DB 저장", on_click=on_save_click, icon=ft.icons.SAVE,
                                      style=ft.ButtonStyle(color=style.AppColors.WHITE, bgcolor=ft.colors.TRANSPARENT,
                                                           shadow_color=ft.colors.TRANSPARENT), width=float('inf'),
                                      height=55),
            gradient=style.SAVE_BUTTON_GRADIENT, border_radius=12, shadow=style.COMMON_SHADOW,
            margin=ft.padding.only(top=10)
        )
        pdf_btn = ft.Container(
            content=ft.ElevatedButton("PDF 보고서 발행", on_click=on_pdf_click, icon=ft.icons.PICTURE_AS_PDF,
                                      style=ft.ButtonStyle(color=style.AppColors.WHITE, bgcolor=ft.colors.TRANSPARENT,
                                                           shadow_color=ft.colors.TRANSPARENT), width=float('inf'),
                                      height=55),
            gradient=style.PDF_BUTTON_GRADIENT, border_radius=12, shadow=style.COMMON_SHADOW,
            margin=ft.padding.only(bottom=20)
        )
        return ft.ListView(
            expand=True, spacing=10, padding=20,
            controls=[
                create_section("공통 안전점검", ft.icons.FACT_CHECK, common_items, work_type, style.AppColors.PRIMARY),
                create_section(f"{work_type} 특화점검", ft.icons.GAVEL, specific_items[work_type], work_type,
                               style.AppColors.SECONDARY),
                create_section("보건/위생관리", ft.icons.HEALTH_AND_SAFETY, health_items, work_type, ft.colors.GREEN_800),
                save_btn, pdf_btn
            ]
        )

    def custom_tab(title):
        return ft.Tab(
            tab_content=ft.Container(content=ft.Text(title, size=15, weight=ft.FontWeight.BOLD),
                                     padding=ft.padding.symmetric(horizontal=5, vertical=10)),
            content=create_tab_content(title)
        )

    tabs = ft.Tabs(
        selected_index=0, scrollable=True, expand=1,
        indicator_color=style.AppColors.PRIMARY, label_color=style.AppColors.PRIMARY,
        unselected_label_color=style.AppColors.TEXT_SUB,
        tabs=[custom_tab("아크용접"), custom_tab("가스용접"), custom_tab("플라즈마"), custom_tab("테르밋용접"), custom_tab("그라인더/금속절단기")]
    )

    # ==========================================
    # 7. 최종 화면 조립
    # ==========================================
    return ft.Column([
        ft.Container(content=info_card, padding=ft.padding.only(left=20, right=20, top=20)),
        tabs
    ], expand=True)