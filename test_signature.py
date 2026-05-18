import flet as ft
import flet.canvas as cv


def main(page: ft.Page):
    page.title = "전자 서명 테스트"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 서명할 때 그려진 선(좌표)들을 저장할 리스트
    strokes = []
    current_stroke = []

    # 1. 서명 팝업창용 그림판
    signature_canvas = cv.Canvas(shapes=[], expand=True)

    # 2. 메인 화면용 그림판 (결과 보여주기 용도)
    result_canvas = cv.Canvas(shapes=[], expand=True)

    # 🌟 헬퍼 함수: 좌표(strokes)를 받아서 지정한 도화지에 새로 그려주는 함수
    def draw_on_canvas(canvas_obj):
        elements = []
        for stroke in strokes:
            if not stroke: continue
            path_elements = [cv.Path.MoveTo(stroke[0][0], stroke[0][1])]
            for x, y in stroke[1:]:
                path_elements.append(cv.Path.LineTo(x, y))

            elements.append(
                cv.Path(
                    elements=path_elements,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        color=ft.colors.BLACK,
                        stroke_width=3,
                        stroke_cap=ft.StrokeCap.ROUND,
                        stroke_join=ft.StrokeJoin.ROUND,
                    )
                )
            )
        canvas_obj.shapes = elements
        canvas_obj.update()

    # 손가락이 닿았을 때
    def pan_start(e: ft.DragStartEvent):
        nonlocal current_stroke
        current_stroke = [(e.local_x, e.local_y)]
        strokes.append(current_stroke)

    # 손가락이 움직일 때
    def pan_update(e: ft.DragUpdateEvent):
        current_stroke.append((e.local_x, e.local_y))
        # 팝업창 캔버스에 실시간으로 그리기
        draw_on_canvas(signature_canvas)

    # 서명 지우기
    def clear_signature(e):
        strokes.clear()
        signature_canvas.shapes.clear()
        signature_canvas.update()

    # 서명 저장
    def save_signature(e):
        if not strokes:
            page.snack_bar = ft.SnackBar(ft.Text("서명을 입력해주세요!"))
            page.snack_bar.open = True
            page.update()
            return

        # 🌟 핵심 수정: 메인 화면 캔버스에 새로운 선들을 만들어서 그려줌!
        draw_on_canvas(result_canvas)

        # 메인 화면의 서명 액자를 보이게 켜기
        signature_result_box.visible = True

        # 버튼 이름은 '다시 서명하기'로 변경
        btn_signature.text = "다시 서명하기"
        btn_signature.icon = ft.icons.REFRESH

        # 팝업창 닫기
        page.dialog.open = False
        page.update()

    # 팝업창 디자인
    signature_dialog = ft.AlertDialog(
        title=ft.Text("작업책임자 서명"),
        content=ft.Container(
            width=300,
            height=150,
            bgcolor=ft.colors.WHITE,
            border=ft.border.all(2, ft.colors.BLUE_200),
            border_radius=5,
            content=ft.GestureDetector(
                on_pan_start=pan_start,
                on_pan_update=pan_update,
                drag_interval=10,
                content=signature_canvas,
            )
        ),
        actions=[
            ft.TextButton("지우기", on_click=clear_signature),
            ft.ElevatedButton("저장", on_click=save_signature, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_signature_pad(e):
        page.dialog = signature_dialog
        signature_dialog.open = True
        page.update()

    # --- 메인 화면 UI 구성 ---

    # 서명 버튼
    btn_signature = ft.ElevatedButton(
        text="✍️ 서명하기",
        on_click=open_signature_pad
    )

    # 🌟 완료된 서명이 보여질 네모난 액자 (처음엔 숨겨둠)
    signature_result_box = ft.Container(
        width=300,
        height=150,
        bgcolor=ft.colors.WHITE,
        border=ft.border.all(1, ft.colors.BLACK26),
        border_radius=5,
        content=result_canvas,
        visible=False  # 서명 전에는 안 보임
    )

    # 화면에 요소들 배치
    page.add(
        ft.Text("안전 보건 점검표", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row(
            controls=[
                ft.Text("작업책임자:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("홍길동", size=16),
                btn_signature
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        signature_result_box
    )


ft.app(target=main)