import flet as ft
import flet.canvas as cv
from database.db_manager import save_checklist, get_all_workers
import components.styles as style
from utils.report_generator import generate_html_report


def ChecklistView(page: ft.Page):

    # ==========================================
    # 🌟 1. 상태 변수
    # ==========================================
    signature_strokes = []
    current_stroke    = []

    # ==========================================
    # 🌟 2. 서명 패드 — BottomSheet
    # ==========================================
    sign_hint = ft.Text(
        "✍️  이곳에 마우스(또는 손가락)로 서명하세요",
        color=ft.Colors.BLUE_GREY_300,
        size=12,
        text_align=ft.TextAlign.CENTER,
        visible=True,
    )

    signature_canvas = cv.Canvas(shapes=[], expand=True)

    def _redraw():
        shapes = []
        for stroke in signature_strokes:
            if len(stroke) < 2:
                continue
            pts = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
            for x, y in stroke[1:]:
                pts.append(cv.Path.LineTo(x, y))
            shapes.append(cv.Path(
                elements=pts,
                paint=ft.Paint(
                    style=ft.PaintingStyle.STROKE,
                    color=ft.Colors.BLACK,
                    stroke_width=3,
                    stroke_cap=ft.StrokeCap.ROUND,
                    stroke_join=ft.StrokeJoin.ROUND,
                ),
            ))
        signature_canvas.shapes = shapes
        signature_canvas.update()

    def _pan_start(e: ft.DragStartEvent):
        nonlocal current_stroke
        if sign_hint.visible:
            sign_hint.visible = False
            sign_hint.update()
        current_stroke = [(e.local_position.x, e.local_position.y)]
        signature_strokes.append(current_stroke)

    def _pan_update(e: ft.DragUpdateEvent):
        current_stroke.append((e.local_position.x, e.local_position.y))
        _redraw()

    def _clear_signature(e):
        signature_strokes.clear()
        current_stroke.clear()
        signature_canvas.shapes = []
        signature_canvas.update()
        sign_hint.visible = True
        sign_hint.update()
        _set_sign_btn_state(done=False)

    def _save_signature(e):
        if not signature_strokes:
            _show_snack("서명을 먼저 그려주세요!", ft.Colors.RED_ACCENT)
            return
        _set_sign_btn_state(done=True)
        sign_bottom_sheet.open = False
        page.update()

    def _set_sign_btn_state(done: bool):
        if done:
            sign_text.value  = "서명완료"
            sign_text.color  = ft.Colors.GREEN_700
            sign_icon.name   = ft.Icons.CHECK_CIRCLE
            sign_icon.color  = ft.Colors.GREEN_700
            sign_btn.border  = ft.Border(
                top=ft.BorderSide(2, ft.Colors.GREEN_500),
                bottom=ft.BorderSide(2, ft.Colors.GREEN_500),
                left=ft.BorderSide(2, ft.Colors.GREEN_500),
                right=ft.BorderSide(2, ft.Colors.GREEN_500),
            )
            sign_btn.bgcolor = ft.Colors.GREEN_50
        else:
            sign_text.value  = "서명"
            sign_text.color  = ft.Colors.BLUE_GREY_400
            sign_icon.name   = ft.Icons.DRAW
            sign_icon.color  = style.AppColors.PRIMARY
            sign_btn.border  = ft.Border(
                top=ft.BorderSide(1, ft.Colors.BLACK26),
                bottom=ft.BorderSide(1, ft.Colors.BLACK26),
                left=ft.BorderSide(1, ft.Colors.BLACK26),
                right=ft.BorderSide(1, ft.Colors.BLACK26),
            )
            sign_btn.bgcolor = None
        sign_btn.update()

    sign_bottom_sheet = ft.BottomSheet(
        open=False,
        content=ft.Container(
            padding=ft.Padding(20, 16, 20, 30),
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.DRAW, color=style.AppColors.PRIMARY),
                        ft.Text("작업자 서명", size=17, weight=ft.FontWeight.BOLD,
                                color=style.AppColors.PRIMARY),
                    ], spacing=8),
                    ft.Divider(height=2),
                    sign_hint,
                    ft.GestureDetector(
                        on_pan_start=_pan_start,
                        on_pan_update=_pan_update,
                        drag_interval=8,
                        content=ft.Container(
                            width=float("inf"),
                            height=210,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            border=ft.Border(
                                top=ft.BorderSide(2, style.AppColors.PRIMARY),
                                bottom=ft.BorderSide(2, style.AppColors.PRIMARY),
                                left=ft.BorderSide(2, style.AppColors.PRIMARY),
                                right=ft.BorderSide(2, style.AppColors.PRIMARY),
                            ),
                            content=signature_canvas,
                        ),
                    ),
                    ft.Row([
                        ft.OutlinedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.REFRESH, size=16),
                                ft.Text("지우기"),
                            ], spacing=4, tight=True),
                            on_click=_clear_signature,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, ft.Colors.RED_300),
                                color=ft.Colors.RED_400,
                            ),
                            expand=1,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK, size=16, color=ft.Colors.WHITE),
                                ft.Text("서명 저장", color=ft.Colors.WHITE),
                            ], spacing=4, tight=True),
                            on_click=_save_signature,
                            bgcolor=style.AppColors.PRIMARY,
                            expand=2,
                            height=46,
                        ),
                    ], spacing=10),
                ],
            ),
        ),
    )

    # ==========================================
    # 🌟 3. 작업자 입력 — BottomSheet
    # ==========================================
    worker_name_field = ft.TextField(
        label="작업자 이름 입력",
        hint_text="이름을 입력하고 확인 버튼을 누르세요",
        height=52,
        border_radius=10,
        text_size=16,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        border_color=ft.Colors.BLACK26,
        autofocus=True,
    )
    worker_list_col = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)

    def _apply_worker(name: str):
        manager_text.value   = name
        manager_text.color   = ft.Colors.BLACK
        manager_text.size    = 18
        manager_icon.visible = False
        manager_btn.data     = name
        manager_btn.update()
        worker_bottom_sheet.open = False
        page.update()

    def confirm_worker_name(e):
        name = worker_name_field.value.strip()
        if name:
            _apply_worker(name)

    def build_worker_list():
        worker_list_col.controls.clear()
        workers = get_all_workers()
        if not workers:
            return
        worker_list_col.controls.append(
            ft.Text("👥 등록된 작업자 (탭하면 바로 선택)",
                    size=12, color=style.AppColors.TEXT_SUB)
        )
        for w in workers:
            w_name, w_dept = w[1], w[2]

            def make_tap(n):
                return lambda _: _apply_worker(n)

            worker_list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=style.AppColors.PRIMARY, size=18),
                        ft.Column([
                            ft.Text(w_name, weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"소속: {w_dept}", size=11, color=style.AppColors.TEXT_SUB),
                        ], spacing=1),
                    ], spacing=10),
                    padding=ft.Padding(12, 10, 12, 10),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    on_click=make_tap(w_name),
                    ink=True,
                )
            )

    worker_bottom_sheet = ft.BottomSheet(
        open=False,
        content=ft.Container(
            padding=ft.Padding(20, 20, 20, 30),
            content=ft.Column(
                tight=True,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON_SEARCH, color=style.AppColors.PRIMARY),
                        ft.Text("작업자 입력", size=17, weight=ft.FontWeight.BOLD,
                                color=style.AppColors.PRIMARY),
                    ], spacing=8),
                    ft.Divider(height=4),
                    worker_name_field,
                    ft.ElevatedButton(
                        content=ft.Text("확인", color=ft.Colors.WHITE),
                        bgcolor=style.AppColors.PRIMARY,
                        height=46,
                        width=float("inf"),
                        on_click=confirm_worker_name,
                    ),
                    ft.Divider(height=4),
                    worker_list_col,
                ],
            ),
        ),
    )

    # ==========================================
    # 🌟 4. 날짜 / 시간 선택
    # ==========================================
    def on_date_change(e):
        if e.control.value:
            date_text.value   = e.control.value.strftime("%Y.%m.%d")
            date_text.color   = ft.Colors.BLACK
            date_text.size    = 18
            date_icon.visible = False
            date_btn.update()

    def on_time_change(e):
        if e.control.value:
            time_text.value   = e.control.value.strftime("%H:%M")
            time_text.color   = ft.Colors.BLACK
            time_text.size    = 18
            time_icon.visible = False
            time_btn.update()

    date_picker = ft.DatePicker(on_change=on_date_change)
    time_picker = ft.TimePicker(on_change=on_time_change)

    # ✅ overlay 위젯 등록
    page.overlay.extend([
        sign_bottom_sheet,
        worker_bottom_sheet,
        date_picker,
        time_picker,
    ])

    def open_signature_pad(e):
        sign_hint.visible = not bool(signature_strokes)
        sign_bottom_sheet.open = True
        page.update()

    def open_worker_input(e):
        worker_name_field.value = ""
        build_worker_list()
        worker_bottom_sheet.open = True
        page.update()

    def open_date_picker(e):
        date_picker.open = True
        page.update()

    def open_time_picker(e):
        time_picker.open = True
        page.update()

    # ==========================================
    # 🌟 5. 기본정보 카드 레이아웃
    # ==========================================
    task_name_input = ft.TextField(
        label="작업명", height=45, expand=6, border_radius=8,
        content_padding=ft.Padding(10, 5, 10, 5), text_size=18,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        border_color=ft.Colors.BLACK26, text_align=ft.TextAlign.CENTER,
    )
    location_input = ft.TextField(
        label="작업장소", height=45, expand=4, border_radius=8,
        content_padding=ft.Padding(10, 5, 10, 5), text_size=18,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        border_color=ft.Colors.BLACK26, text_align=ft.TextAlign.CENTER,
    )
    row_1 = ft.Row([task_name_input, location_input], spacing=8)

    date_text    = ft.Text("일자",   size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    time_text    = ft.Text("시간",   size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    manager_text = ft.Text("작업자", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
    sign_text    = ft.Text("서명",   size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)

    date_icon    = ft.Icon(ft.Icons.CALENDAR_MONTH, size=20, color=style.AppColors.PRIMARY)
    time_icon    = ft.Icon(ft.Icons.ACCESS_TIME,    size=20, color=style.AppColors.PRIMARY)
    manager_icon = ft.Icon(ft.Icons.PERSON_SEARCH,  size=20, color=style.AppColors.PRIMARY)
    sign_icon    = ft.Icon(ft.Icons.DRAW,           size=20, color=style.AppColors.PRIMARY)

    def create_compact_btn(icon_obj, text_obj, click_fn):
        return ft.Container(
            content=ft.Column(
                [icon_obj, text_obj],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            on_click=click_fn, expand=1, height=65, ink=True, border_radius=8,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.BLACK26),
                bottom=ft.BorderSide(1, ft.Colors.BLACK26),
                left=ft.BorderSide(1, ft.Colors.BLACK26),
                right=ft.BorderSide(1, ft.Colors.BLACK26),
            ),
        )

    date_btn    = create_compact_btn(date_icon,    date_text,    open_date_picker)
    time_btn    = create_compact_btn(time_icon,    time_text,    open_time_picker)
    manager_btn = create_compact_btn(manager_icon, manager_text, open_worker_input)
    manager_btn.data = ""
    sign_btn    = create_compact_btn(sign_icon,    sign_text,    open_signature_pad)

    row_2 = ft.Row([date_btn, time_btn, manager_btn, sign_btn], spacing=8)

    custom_card_style = style.card_style()
    custom_card_style["margin"] = ft.Margin(0, 0, 0, 0)

    info_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.EDIT_NOTE, color=style.AppColors.PRIMARY, size=20),
                ft.Text("현장 작업 기본정보", size=16, weight=ft.FontWeight.BOLD,
                        color=style.AppColors.PRIMARY),
            ]),
            row_1,
            row_2,
        ], spacing=10),
        **custom_card_style,
    )

    # ==========================================
    # 🌟 6. 체크리스트 데이터
    # ==========================================
    work_types_list   = ["아크용접", "가스용접", "플라즈마", "테르밋용접", "그라인더/금속절단기"]
    controls_dict_map = {k: {} for k in work_types_list}
    active_tab        = {"work_type": work_types_list[0]}

    def make_check_item(text, work_type):
        rg = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="확인",    label="확인",    fill_color=style.RADIO_THEME["confirm"]),
            ft.Radio(value="해당없음", label="해당없음", fill_color=style.RADIO_THEME["none"]),
        ], spacing=20))
        controls_dict_map[work_type][text] = rg
        return ft.Container(
            content=ft.Column([
                ft.Text(text, weight=ft.FontWeight.W_600, color=style.AppColors.TEXT_MAIN),
                rg,
            ], spacing=5),
            padding=15, bgcolor=ft.Colors.BLUE_GREY_50, border_radius=12,
        )

    common_items = [
        "• 안전작업허가서 발급 및 승인 여부 확인",
        "• 작업 반경 11m 이내 가연물 제거 또는 방호 조치",
        "• 화재감시자 지정 및 배치 (연장 및 야간작업 포함)",
        "• 작업장 인근 소화기구 비치 및 소화전 사용 가능 여부",
        "• 용접방화포(성능인증 제품) 사용 및 개구부 차단",
        "• 작업 종료 후 최소 30분 이상 잔불 및 훈소 감시",
    ]
    health_items = [
        "• 용접 흄 제거 단말기 또는 환기 조치",
        "• 밀폐공간 작업 시 산소 및 가스 농도 측정 등 안전조치",
        "• 개인보호구(방진마스크, 용접면, 보안경, 장갑 등) 지급/착용",
    ]
    specific_items = {
        "아크용접": [
            "• 자동전격방지기 설치 및 정상 작동 여부 확인",
            "• 홀더의 절연커버 파손 여부 및 규격품 사용 확인",
            "• 용접 케이블 피복의 손상이나 충전부 노출 확인",
            "• 작업 중단/종료 시 홀더에서 용접봉 제거 여부",
            "• 젖은 장갑, 옷, 신발 등 습윤한 상태 작업 여부",
        ],
        "가스용접": [
            "• 취관(토치) 및 분기관에 역화방지기(안전기) 설치",
            "• 가스 용기는 40℃ 이하 보관 및 전도 방지 조치",
            "• 아세틸렌 용기는 반드시 세워서 사용",
            "• 호스 및 접속부 가스 누설 여부 점검(비눗물 등)",
            "• 아세틸렌 사용 압력은 0.1 MPa 이하로 유지",
            "• 산소 밸브 및 조정기에 기름/그리스 접촉 금지",
        ],
        "플라즈마": [
            "• 냉각 장치의 누수 여부 점검 (절연 성능 저하 방지)",
            "• 용접기 외함 접지 및 케이블 피복 손상 여부 확인",
            "• 자동화 설비의 경우 긴급 정지 장치 작동 상태 점검",
            "• 전원 연결 및 분리 시 반드시 전문가가 수행/전원 차단 확인",
        ],
        "테르밋용접": [
            "• 고온의 용융 금속 비산 방지용 불연성 덮개 설치 여부",
            "• 반응 용기 및 모재 예열 시 주변 가연물 점화 방지 조치",
            "• 테르밋 반응 후 냉각 시까지 작업자 접근 통제/화상 방지",
            "• 점화 시 스파크가 주변 인화성 물질에 닿지 않도록 격리",
            "• 반응이 끝난 후 슬래그 등을 안전하게 처리할 장소 확보",
        ],
        "그라인더/금속절단기": [
            "• 마찰열이나 스파크가 인근 가연성 물질의 점화원이 되지 않도록 격리했는가?",
        ],
    }

    # ==========================================
    # 🌟 7. SnackBar 헬퍼 + 미체크 항목 안내 BottomSheet
    # ==========================================
    def _show_snack(msg: str, color):
        # ✅ Flet 0.85 지원 파라미터만 사용
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    # 미체크 항목 목록을 BottomSheet로 표시
    _unchecked_list_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)

    def _close_unchecked_sheet(e):
        unchecked_bottom_sheet.open = False
        page.update()

    unchecked_bottom_sheet = ft.BottomSheet(
        open=False,
        content=ft.Container(
            padding=ft.Padding(20, 20, 20, 30),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ORANGE_700, size=22),
                        ft.Text(
                            "미체크 항목 안내",
                            size=17, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE_700,
                        ),
                    ], spacing=8),
                    ft.Text(
                        "아래 항목들을 확인 또는 해당없음으로 선택해주세요.",
                        size=13, color=ft.Colors.BLUE_GREY_600,
                    ),
                    ft.Divider(height=4),
                    ft.Container(
                        content=_unchecked_list_col,
                        height=280,
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("확인", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_700,
                        height=46,
                        width=float("inf"),
                        on_click=_close_unchecked_sheet,
                    ),
                ],
            ),
        ),
    )
    page.overlay.append(unchecked_bottom_sheet)

    def _show_unchecked(missing_items: list):
        _unchecked_list_col.controls.clear()
        for i, item in enumerate(missing_items, 1):
            _unchecked_list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(
                                str(i),
                                size=11,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            width=22, height=22,
                            bgcolor=ft.Colors.ORANGE_700,
                            border_radius=11,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(
                            item,
                            size=13,
                            color=ft.Colors.BLUE_GREY_800,
                            expand=True,
                        ),
                    ], spacing=10),
                    padding=ft.Padding(10, 8, 10, 8),
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=8,
                    border=ft.Border(
                        top=ft.BorderSide(1, ft.Colors.ORANGE_200),
                        bottom=ft.BorderSide(1, ft.Colors.ORANGE_200),
                        left=ft.BorderSide(1, ft.Colors.ORANGE_200),
                        right=ft.BorderSide(1, ft.Colors.ORANGE_200),
                    ),
                )
            )
        unchecked_bottom_sheet.open = True
        page.update()

    # ==========================================
    # 🌟 8. DB 저장
    # ==========================================
    def on_save_click(e):
        if date_text.value == "일자":
            _show_snack("작업 일자를 선택하세요.", ft.Colors.RED_ACCENT)
            return
        if time_text.value == "시간":
            _show_snack("작업 시간을 선택하세요.", ft.Colors.RED_ACCENT)
            return
        if not manager_btn.data:
            _show_snack("작업자를 입력하세요.", ft.Colors.RED_ACCENT)
            return
        if not signature_strokes:
            _show_snack("작업자 서명이 누락되었습니다!", ft.Colors.RED_ACCENT)
            return

        current_work = active_tab["work_type"]
        missing = [
            item_text
            for item_text, radio in controls_dict_map[current_work].items()
            if not radio.value
        ]
        if missing:
            _show_unchecked(missing)
            return

        results = {
            item_text: radio.value
            for item_text, radio in controls_dict_map[current_work].items()
        }
        try:
            save_checklist(
                task_name_input.value,
                date_text.value,
                time_text.value,
                location_input.value,
                manager_btn.data,
                current_work,
                results,
                signature_strokes,
            )
            _show_snack(f"[{current_work}] DB 저장 완료!", style.AppColors.SECONDARY)
        except Exception as ex:
            _show_snack(f"저장 오류: {ex}", ft.Colors.RED_700)

    # ==========================================
    # 🌟 9. HTML 보고서 발행
    # ==========================================
    def on_html_report_click(e):
        if date_text.value == "일자":
            _show_snack("작업 일자를 선택하세요.", ft.Colors.RED_ACCENT)
            return
        if time_text.value == "시간":
            _show_snack("작업 시간을 선택하세요.", ft.Colors.RED_ACCENT)
            return
        if not manager_btn.data:
            _show_snack("작업자를 입력하세요.", ft.Colors.RED_ACCENT)
            return
        if not signature_strokes:
            _show_snack("작업자 서명이 누락되었습니다!", ft.Colors.RED_ACCENT)
            return

        current_work = active_tab["work_type"]
        missing = [
            item_text
            for item_text, radio in controls_dict_map[current_work].items()
            if not radio.value
        ]
        if missing:
            _show_unchecked(missing)
            return

        data = {
            "task_name":     task_name_input.value,
            "task_date":     date_text.value,
            "task_time":     time_text.value,
            "location":      location_input.value,
            "manager_name":  manager_btn.data,
            "work_type":     current_work,
            "check_results": {k: v.value for k, v in controls_dict_map[current_work].items()},
            "signature":     signature_strokes,
        }

        # report_generator.py 가 Windows/Android 경로 자동 분기
        try:
            success, msg = generate_html_report(data)
            if success:
                _show_snack("다운로드 폴더에 보고서가 저장되었습니다!", style.AppColors.PRIMARY)
            else:
                _show_snack(f"발행 실패: {msg}", ft.Colors.RED_700)
        except Exception as ex:
            _show_snack(f"오류: {ex}", ft.Colors.RED_700)

    # ==========================================
    # 🌟 10. 체크리스트 탭 구성
    # ==========================================
    def create_section(title, icon, items, work_type, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=color),
                ]),
                *[make_check_item(i, work_type) for i in items],
            ], spacing=12),
            **style.card_style(),
        )

    def create_tab_content(work_type):
        save_btn = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Text("체크리스트 DB 저장", color=style.AppColors.WHITE),
                on_click=on_save_click,
                icon=ft.Icons.SAVE,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TRANSPARENT,
                    shadow_color=ft.Colors.TRANSPARENT,
                ),
                width=float("inf"),
                height=55,
            ),
            gradient=style.SAVE_BUTTON_GRADIENT,
            border_radius=12,
            shadow=style.COMMON_SHADOW,
            margin=ft.Margin(left=0, top=10, right=0, bottom=0),
        )
        html_btn = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Text("보고서 발행 (HTML)", color=style.AppColors.WHITE),
                on_click=on_html_report_click,
                icon=ft.Icons.WEB,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TRANSPARENT,
                    shadow_color=ft.Colors.TRANSPARENT,
                ),
                width=float("inf"),
                height=55,
            ),
            gradient=style.PDF_BUTTON_GRADIENT,
            border_radius=12,
            shadow=style.COMMON_SHADOW,
            margin=ft.Margin(left=0, top=0, right=0, bottom=20),
        )
        return ft.ListView(
            expand=True, spacing=10, padding=20,
            controls=[
                create_section("공통 안전점검",        ft.Icons.FACT_CHECK,        common_items,              work_type, style.AppColors.PRIMARY),
                create_section(f"{work_type} 특화점검", ft.Icons.GAVEL,            specific_items[work_type], work_type, style.AppColors.SECONDARY),
                create_section("보건/위생관리",         ft.Icons.HEALTH_AND_SAFETY, health_items,              work_type, ft.Colors.GREEN_800),
                save_btn,
                html_btn,
            ],
        )

    tab_content_view = ft.Container(expand=True, content=create_tab_content(work_types_list[0]))

    def on_tab_change(e):
        sel = e.control.data
        active_tab["work_type"] = sel
        for c in tab_row.controls:
            if c.data == sel:
                c.border         = ft.Border(bottom=ft.BorderSide(3, style.AppColors.PRIMARY))
                c.content.color  = style.AppColors.PRIMARY
                c.content.weight = ft.FontWeight.BOLD
            else:
                c.border         = None
                c.content.color  = style.AppColors.TEXT_SUB
                c.content.weight = ft.FontWeight.NORMAL
        tab_content_view.content = create_tab_content(sel)
        tab_row.update()
        tab_content_view.update()

    tab_row = ft.Row(
        scroll=ft.ScrollMode.AUTO, spacing=0,
        controls=[
            ft.Container(
                data=wt,
                content=ft.Text(
                    wt, size=15,
                    weight=ft.FontWeight.BOLD if wt == work_types_list[0] else ft.FontWeight.NORMAL,
                    color=style.AppColors.PRIMARY if wt == work_types_list[0] else style.AppColors.TEXT_SUB,
                ),
                padding=ft.Padding(15, 12, 15, 12),
                border=ft.Border(bottom=ft.BorderSide(3, style.AppColors.PRIMARY)) if wt == work_types_list[0] else None,
                on_click=on_tab_change,
                ink=True,
            )
            for wt in work_types_list
        ],
    )

    tabs_container = ft.Column(
        [
            ft.Container(content=tab_row, bgcolor=ft.Colors.WHITE, shadow=style.COMMON_SHADOW),
            tab_content_view,
        ],
        expand=True, spacing=0,
    )

    return ft.Column([
        ft.Container(content=info_card, padding=ft.Padding(left=15, top=5, right=15, bottom=0)),
        ft.Container(content=tabs_container, expand=True, margin=ft.Margin(left=0, top=-5, right=0, bottom=0)),
    ], expand=True, spacing=0)