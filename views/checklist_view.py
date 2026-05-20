import flet as ft
import flet.canvas as cv
from database.db_manager import save_checklist, get_all_workers
import components.styles as style
from utils.report_generator import generate_html_report


def ChecklistView(page: ft.Page):
    # ==========================================
    # 🌟 1. 상태 변수 및 기본 설정
    # ==========================================
    signature_strokes = []
    current_stroke = []
    signature_canvas = cv.Canvas(shapes=[], expand=True)

    # ==========================================
    # 🌟 2. 서명 패드 (팝업 및 캔버스)
    # ==========================================
    def draw_on_canvas(canvas_obj):
        elements = []
        for stroke in signature_strokes:
            if not stroke: continue
            path_elements = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
            for x, y in stroke[1:]:
                path_elements.append(cv.Path.LineTo(x, y))
            elements.append(cv.Path(elements=path_elements,
                                    paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.Colors.BLACK, stroke_width=3,
                                                   stroke_cap=ft.StrokeCap.ROUND, stroke_join=ft.StrokeJoin.ROUND)))
        canvas_obj.shapes = elements
        canvas_obj.update()

    def pan_start(e):
        nonlocal current_stroke
        current_stroke = [(e.local_x, e.local_y)]
        signature_strokes.append(current_stroke)

    def pan_update(e):
        current_stroke.append((e.local_x, e.local_y))
        draw_on_canvas(signature_canvas)

    def clear_signature(e):
        signature_strokes.clear()
        signature_canvas.shapes.clear()
        signature_canvas.update()

    def save_signature(e):
        if not signature_strokes:
            page.snack_bar = ft.SnackBar(ft.Text("서명을 입력해주세요!"), bgcolor=ft.Colors.RED_ACCENT)
            page.snack_bar.open = True;
            page.update();
            return

        # ✅ 서명 완료 시 2열의 서명 버튼 상태 연동 업데이트
        sign_text.value = "서명완료"
        sign_text.color = ft.Colors.GREEN_700
        sign_icon.name = ft.Icons.CHECK_CIRCLE
        sign_icon.color = ft.Colors.GREEN_700
        sign_btn.border = ft.Border(top=ft.BorderSide(2, ft.Colors.GREEN_500),
                                    bottom=ft.BorderSide(2, ft.Colors.GREEN_500),
                                    left=ft.BorderSide(2, ft.Colors.GREEN_500),
                                    right=ft.BorderSide(2, ft.Colors.GREEN_500))
        sign_btn.bgcolor = ft.Colors.GREEN_50
        sign_btn.update()

        signature_dialog.open = False
        page.update()

    signature_dialog = ft.AlertDialog(
        title=ft.Text("작업자 서명", weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=350, height=200, bgcolor=ft.Colors.WHITE,
            border=ft.Border(top=ft.BorderSide(2, style.AppColors.PRIMARY),
                             bottom=ft.BorderSide(2, style.AppColors.PRIMARY),
                             left=ft.BorderSide(2, style.AppColors.PRIMARY),
                             right=ft.BorderSide(2, style.AppColors.PRIMARY)),
            border_radius=5,
            content=ft.GestureDetector(on_pan_start=pan_start, on_pan_update=pan_update, drag_interval=10,
                                       content=signature_canvas)
        ),
        actions=[ft.TextButton("지우기", on_click=clear_signature),
                 ft.ElevatedButton(content=ft.Text("저장", color=ft.Colors.WHITE), on_click=save_signature,
                                   bgcolor=style.AppColors.PRIMARY)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_signature_pad(e):
        page.dialog = signature_dialog
        signature_dialog.open = True
        page.update()

    # ==========================================
    # 🌟 3. 작업책임자 팝업
    # ==========================================
    def open_worker_select_popup(e):
        workers = get_all_workers()
        select_content = ft.Column(scroll=ft.ScrollMode.AUTO, height=300, width=300, spacing=5)
        select_content.controls.append(ft.Text("작업자 선택", weight=ft.FontWeight.BOLD, size=15))
        select_content.controls.append(ft.Divider(height=1))

        if not workers:
            select_content.controls.append(ft.Text("등록된 작업자가 없습니다.", color=ft.Colors.RED_400, size=13))
        else:
            for w in workers:
                w_name = w[1]
                w_dept = w[2]

                def make_select_cell_func(name):
                    def cell_click(cp_e):
                        manager_text.value = name
                        manager_text.color = ft.Colors.BLACK
                        manager_btn.data = name
                        manager_btn.update()
                        select_dlg.open = False
                        page.update()

                    return cell_click

                select_content.controls.append(ft.ListTile(title=ft.Text(w_name, weight=ft.FontWeight.W_600),
                                                           subtitle=ft.Text(f"소속: {w_dept}", size=12),
                                                           on_click=make_select_cell_func(w_name)))

        def close_select_dlg(e):
            select_dlg.open = False
            page.update()

        select_dlg = ft.AlertDialog(content=select_content, actions=[ft.TextButton("닫기", on_click=close_select_dlg)],
                                    actions_alignment=ft.MainAxisAlignment.END)
        page.dialog = select_dlg
        select_dlg.open = True
        page.update()

    # ==========================================
    # 🌟 4. 날짜/시간 선택 팝업 (가장 안전한 호출 방식)
    # ==========================================
    def on_date_change(e):
        if e.control.value:
            date_text.value = e.control.value.strftime("%m.%d")
            date_text.color = ft.Colors.BLACK
            date_btn.update()

    def on_time_change(e):
        if e.control.value:
            time_text.value = e.control.value.strftime("%H:%M")
            time_text.color = ft.Colors.BLACK
            time_btn.update()

    date_picker = ft.DatePicker(on_change=on_date_change)
    time_picker = ft.TimePicker(on_change=on_time_change)

    page.overlay.extend([date_picker, time_picker])

    # ✅ 가장 확실하게 동작하는 Picker 오픈 로직 (버그 원천 차단)
    def open_date_picker(e):
        date_picker.open = True
        page.update()

    def open_time_picker(e):
        time_picker.open = True
        page.update()

    # ==========================================
    # 🌟 5. 스마트폰 최적화 모바일 레이아웃 (6:4 비율 및 4등분 비율)
    # ==========================================

    # --- [1열] 작업명 / 작업장소 (비율 6 : 4 지정) ---
    task_name_input = ft.TextField(label="작업명", height=45, expand=6, border_radius=8,
                                   content_padding=ft.Padding(10, 5, 10, 5), text_size=13,
                                   border_color=ft.Colors.BLACK26)
    location_input = ft.TextField(label="작업장소", height=45, expand=4, border_radius=8,
                                  content_padding=ft.Padding(10, 5, 10, 5), text_size=13,
                                  border_color=ft.Colors.BLACK26)
    row_1 = ft.Row([task_name_input, location_input], spacing=8)

    # --- [2열] 일자 / 시간 / 작업자 / 서명 (1 : 1 : 1 : 1 지정) ---
    date_text = ft.Text("일자", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    time_text = ft.Text("시간", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    manager_text = ft.Text("작업자", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    sign_text = ft.Text("서명", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    sign_icon = ft.Icon(ft.Icons.DRAW, size=20, color=style.AppColors.PRIMARY)

    def create_compact_btn(icon_obj, text_obj, click_event):
        return ft.Container(
            content=ft.Column([icon_obj, text_obj], alignment=ft.MainAxisAlignment.CENTER, spacing=2,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=click_event, expand=1, height=60, ink=True, border_radius=8,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.BLACK26), bottom=ft.BorderSide(1, ft.Colors.BLACK26),
                             left=ft.BorderSide(1, ft.Colors.BLACK26), right=ft.BorderSide(1, ft.Colors.BLACK26))
        )

    # 수정된 안전한 팝업 호출 함수 연동
    date_btn = create_compact_btn(ft.Icon(ft.Icons.CALENDAR_MONTH, size=20, color=style.AppColors.PRIMARY), date_text,
                                  open_date_picker)
    time_btn = create_compact_btn(ft.Icon(ft.Icons.ACCESS_TIME, size=20, color=style.AppColors.PRIMARY), time_text,
                                  open_time_picker)
    manager_btn = create_compact_btn(ft.Icon(ft.Icons.PERSON_SEARCH, size=20, color=style.AppColors.PRIMARY),
                                     manager_text, open_worker_select_popup)
    manager_btn.data = ""
    sign_btn = create_compact_btn(sign_icon, sign_text, open_signature_pad)

    row_2 = ft.Row([date_btn, time_btn, manager_btn, sign_btn], spacing=8)

    # 기본정보 카드 조립
    custom_card_style = style.card_style()
    custom_card_style["margin"] = ft.Margin(0, 0, 0, 0)

    info_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.EDIT_NOTE, color=style.AppColors.PRIMARY, size=20),
                    ft.Text("현장 작업 기본정보", size=16, weight=ft.FontWeight.BOLD, color=style.AppColors.PRIMARY)]),
            row_1,
            row_2
        ], spacing=10),
        **custom_card_style
    )

    # ==========================================
    # 🌟 6. 체크리스트 데이터 구성
    # ==========================================
    work_types_list = ["아크용접", "가스용접", "플라즈마", "테르밋용접", "그라인더/금속절단기"]
    controls_dict_map = {k: {} for k in work_types_list}
    active_tab = {"work_type": work_types_list[0]}

    def make_check_item(text, work_type):
        radio_group = ft.RadioGroup(content=ft.Row(
            [ft.Radio(value="확인", label="확인", fill_color=style.RADIO_THEME["confirm"]),
             ft.Radio(value="해당없음", label="해당없음", fill_color=style.RADIO_THEME["none"])], spacing=20))
        controls_dict_map[work_type][text] = radio_group
        return ft.Container(
            content=ft.Column([ft.Text(text, weight=ft.FontWeight.W_600, color=style.AppColors.TEXT_MAIN), radio_group],
                              spacing=5), padding=15, bgcolor=ft.Colors.BLUE_GREY_50, border_radius=12)

    common_items = ["• 안전작업허가서 발급 및 승인 여부 확인", "• 작업 반경 11m 이내 가연물 제거 또는 방호 조치", "• 화재감시자 지정 및 배치 (연장 및 야간작업 포함)",
                    "• 작업장 인근 소화기구 비치 및 소화전 사용 가능 여부", "• 용접방화포(성능인증 제품) 사용 및 개구부 차단", "• 작업 종료 후 최소 30분 이상 잔불 및 훈소 감시"]
    health_items = ["• 용접 흄 제거 단말기 또는 환기 조치", "• 밀폐공간 작업 시 산소 및 가스 농도 측정 등 안전조치",
                    "• 개인보호구(방진마스크, 용접면, 보안경, 장갑 등) 지급/착용"]
    specific_items = {
        "아크용접": ["• 자동전격방지기 설치 및 정상 작동 여부 확인", "• 홀더의 절연커버 파손 여부 및 규격품 사용 확인", "• 용접 케이블 피복의 손상이나 충전부 노출 확인",
                 "• 작업 중단/종료 시 홀더에서 용접봉 제거 여부", "• 젖은 장갑, 옷, 신발 등 습윤한 상태 작업 여부"],
        "가스용접": ["• 취관(토치) 및 분기관에 역화방지기(안전기) 설치", "• 가스 용기는 40℃ 이하 보관 및 전도 방지 조치", "• 아세틸렌 용기는 반드시 세워서 사용",
                 "• 호스 및 접속부 가스 누설 여부 점검(비눗물 등)", "• 아세틸렌 사용 압력은 0.1 MPa 이하로 유지", "• 산소 밸브 및 조정기에 기름/그ريس 접촉 금지"],
        "플라즈마": ["• 냉각 장치의 누수 여부 점검 (절연 성능 저하 방지)", "• 용접기 외함 접지 및 케이블 피복 손상 여부 확인", "• 자동화 설비의 경우 긴급 정지 장치 작동 상태 점검",
                 "• 전원 연결 및 분리 시 반드시 전문가가 수행/전원 차단 확인"],
        "테르밋용접": ["• 고온의 용융 금속 비산 방지용 불연성 덮개 설치 여부", "• 반응 용기 및 모재 예열 시 주변 가연물 점화 방지 조치",
                  "• 테르밋 반응 후 냉각 시까지 작업자 접근 통제/화상 방지", "• 점화 시 스파크가 주변 인화성 물질에 닿지 않도록 격리",
                  "• 반응이 끝난 후 슬래그 등을 안전하게 처리할 장소 확보"],
        "그라인더/금속절단기": ["• 마찰열이나 스파크가 인근 가연성 물질의 점화원이 되지 않도록 격리했는가?"]
    }

    # ==========================================
    # 🌟 7. DB 저장 및 HTML 발행 (데이터 연동)
    # ==========================================
    def on_save_click(e):
        if date_text.value == "일자" or time_text.value == "시간":
            page.snack_bar = ft.SnackBar(ft.Text("작업 일자와 시간을 선택하세요."), bgcolor=ft.Colors.RED_ACCENT);
            page.snack_bar.open = True;
            page.update();
            return
        if not manager_btn.data or manager_btn.data == "":
            page.snack_bar = ft.SnackBar(ft.Text("작업자를 선택하세요."), bgcolor=ft.Colors.RED_ACCENT);
            page.snack_bar.open = True;
            page.update();
            return
        if not signature_strokes:
            page.snack_bar = ft.SnackBar(ft.Text("작업자의 서명이 누락되었습니다!"), bgcolor=ft.Colors.RED_ACCENT);
            page.snack_bar.open = True;
            page.update();
            return

        current_work = active_tab["work_type"]
        results = {}
        for item_text, radio in controls_dict_map[current_work].items():
            if not radio.value:
                page.snack_bar = ft.SnackBar(ft.Text(f"⚠️ 점검 결과가 누락되었습니다.\n{item_text}"), bgcolor=ft.Colors.RED_700);
                page.snack_bar.open = True;
                page.update();
                return
            results[item_text] = radio.value

        save_checklist(task_name_input.value, date_text.value, time_text.value, location_input.value, manager_btn.data,
                       current_work, results, signature_strokes)
        page.snack_bar = ft.SnackBar(ft.Text(f"[{current_work}] 저장 완료!"), bgcolor=style.AppColors.SECONDARY)
        page.snack_bar.open = True;
        page.update()

    async def on_html_report_click(e):
        if not manager_btn.data or not signature_strokes:
            page.snack_bar = ft.SnackBar(ft.Text("모든 항목(날짜/시간/작업자/서명)을 입력해주세요."), bgcolor=ft.Colors.RED_ACCENT);
            page.snack_bar.open = True;
            page.update();
            return
        current_work = active_tab["work_type"]
        for item_text, radio in controls_dict_map[current_work].items():
            if not radio.value:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ 체크되지 않은 항목이 있습니다."), bgcolor=ft.Colors.RED_700);
                page.snack_bar.open = True;
                page.update();
                return

        safe_work_type = current_work.replace("/", "_")
        default_name = f"Safety_Report_{manager_btn.data}_{safe_work_type}.html"

        data = {"task_name": task_name_input.value, "task_date": date_text.value, "task_time": time_text.value,
                "location": location_input.value, "manager_name": manager_btn.data,
                "work_type": current_work,
                "check_results": {k: v.value for k, v in controls_dict_map[current_work].items()},
                "signature": signature_strokes}

        if page.platform == ft.PagePlatform.ANDROID:
            success, msg = generate_html_report(data)
            if success:
                page.snack_bar = ft.SnackBar(ft.Text("🎉 다운로드 폴더에 보고서가 발행되었습니다!"), bgcolor=style.AppColors.PRIMARY)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ 오류: {msg}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True;
            page.update()
        else:
            save_path = await ft.FilePicker().save_file(file_name=default_name, allowed_extensions=["html"])
            if save_path:
                success, msg = generate_html_report(data, save_path)
                if success:
                    page.snack_bar = ft.SnackBar(ft.Text("🎉 HTML 성공적으로 저장됨!"), bgcolor=style.AppColors.PRIMARY)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"❌ 오류: {msg}"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True;
                page.update()

    # ==========================================
    # 🌟 8. 체크리스트 탭 구성
    # ==========================================
    def create_section(title, icon, items, work_type, color):
        return ft.Container(content=ft.Column(
            [ft.Row([ft.Icon(icon, color=color), ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=color)]),
             *[make_check_item(i, work_type) for i in items]], spacing=12), **style.card_style())

    def create_tab_content(work_type):
        save_btn = ft.Container(content=ft.ElevatedButton(content=ft.Text("체크리스트 DB 저장", color=style.AppColors.WHITE),
                                                          on_click=on_save_click, icon=ft.Icons.SAVE,
                                                          style=ft.ButtonStyle(bgcolor=ft.Colors.TRANSPARENT,
                                                                               shadow_color=ft.Colors.TRANSPARENT),
                                                          width=float('inf'), height=55),
                                gradient=style.SAVE_BUTTON_GRADIENT, border_radius=12, shadow=style.COMMON_SHADOW,
                                margin=ft.Margin(left=0, top=10, right=0, bottom=0))
        html_btn = ft.Container(content=ft.ElevatedButton(content=ft.Text("보고서 발행 (HTML)", color=style.AppColors.WHITE),
                                                          on_click=on_html_report_click, icon=ft.Icons.WEB,
                                                          style=ft.ButtonStyle(bgcolor=ft.Colors.TRANSPARENT,
                                                                               shadow_color=ft.Colors.TRANSPARENT),
                                                          width=float('inf'), height=55),
                                gradient=style.PDF_BUTTON_GRADIENT, border_radius=12, shadow=style.COMMON_SHADOW,
                                margin=ft.Margin(left=0, top=0, right=0, bottom=20))
        return ft.ListView(expand=True, spacing=10, padding=20, controls=[
            create_section("공통 안전점검", ft.Icons.FACT_CHECK, common_items, work_type, style.AppColors.PRIMARY),
            create_section(f"{work_type} 특화점검", ft.Icons.GAVEL, specific_items[work_type], work_type,
                           style.AppColors.SECONDARY),
            create_section("보건/위생관리", ft.Icons.HEALTH_AND_SAFETY, health_items, work_type, ft.Colors.GREEN_800),
            save_btn, html_btn])

    tab_content_view = ft.Container(expand=True, content=create_tab_content(work_types_list[0]))

    def on_tab_change(e):
        selected_type = e.control.data
        active_tab["work_type"] = selected_type
        for c in tab_row.controls:
            if c.data == selected_type:
                c.border = ft.Border(bottom=ft.BorderSide(3,
                                                          style.AppColors.PRIMARY)); c.content.color = style.AppColors.PRIMARY; c.content.weight = ft.FontWeight.BOLD
            else:
                c.border = None; c.content.color = style.AppColors.TEXT_SUB; c.content.weight = ft.FontWeight.NORMAL
        tab_content_view.content = create_tab_content(selected_type)
        tab_row.update();
        tab_content_view.update()

    tab_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=0, controls=[ft.Container(data=wt, content=ft.Text(wt, size=15,
                                                                                                           weight=ft.FontWeight.BOLD if wt ==
                                                                                                                                        work_types_list[
                                                                                                                                            0] else ft.FontWeight.NORMAL,
                                                                                                           color=style.AppColors.PRIMARY if wt ==
                                                                                                                                            work_types_list[
                                                                                                                                                0] else style.AppColors.TEXT_SUB),
                                                                                  padding=ft.Padding(15, 12, 15, 12),
                                                                                  border=ft.Border(
                                                                                      bottom=ft.BorderSide(3,
                                                                                                           style.AppColors.PRIMARY)) if wt ==
                                                                                                                                        work_types_list[
                                                                                                                                            0] else None,
                                                                                  on_click=on_tab_change, ink=True) for
                                                                     wt in work_types_list])
    tabs_container = ft.Column(
        [ft.Container(content=tab_row, bgcolor=ft.Colors.WHITE, shadow=style.COMMON_SHADOW), tab_content_view],
        expand=True, spacing=0)

    return ft.Column([
        ft.Container(content=info_card, padding=ft.Padding(left=15, top=5, right=15, bottom=0)),
        ft.Container(content=tabs_container, expand=True, margin=ft.Margin(left=0, top=-5, right=0, bottom=0))
    ], expand=True, spacing=0)