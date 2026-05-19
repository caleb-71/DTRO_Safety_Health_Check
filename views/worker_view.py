import flet as ft

def WorkerView(page: ft.Page):
    # 1. 스마트폰 저장소에서 기존 명단 불러오기 (없으면 기본값 세팅)
    saved_workers = page.client_storage.get("workers")
    workers_list = saved_workers if saved_workers else ["홍길동", "김철수", "이영희"]

    # 명단이 그려질 시각적 리스트
    worker_list_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    # 2. 화면에 명단 그리기 함수
    def update_worker_list():
        worker_list_ui.controls.clear()
        for w in workers_list:
            worker_list_ui.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON, color=ft.colors.BLUE_700),
                        title=ft.Text(w, weight=ft.FontWeight.BOLD),
                        # 삭제 버튼
                        trailing=ft.IconButton(
                            icon=ft.icons.DELETE_OUTLINE,
                            icon_color=ft.colors.RED_500,
                            data=w, # 버튼에 삭제할 이름 달아두기
                            on_click=delete_worker
                        )
                    )
                )
            )
        page.update()

    # 3. 추가/삭제 기능
    def add_worker(e):
        if new_worker_field.value:
            workers_list.append(new_worker_field.value)
            page.client_storage.set("workers", workers_list) # 스마트폰에 저장
            new_worker_field.value = ""
            update_worker_list()

    def delete_worker(e):
        target_name = e.control.data
        if target_name in workers_list:
            workers_list.remove(target_name)
            page.client_storage.set("workers", workers_list) # 스마트폰에 업데이트
            update_worker_list()

    # 4. 입력 필드 및 UI 조립
    new_worker_field = ft.TextField(label="새 작업자 이름 입력", expand=True, height=50)
    add_btn = ft.ElevatedButton("추가", on_click=add_worker, icon=ft.icons.PERSON_ADD, height=50, bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE)

    # 화면 진입 시 최초 1회 그리기
    update_worker_list()

    return ft.Column([
        ft.Container(
            content=ft.Text("작업자 명단 관리", size=20, weight=ft.FontWeight.BOLD),
            padding=ft.padding.only(left=20, top=20, bottom=10)
        ),
        # 🌟 수정된 부분: ft.Row를 ft.Container로 한 번 감싸서 padding을 주었습니다!
        ft.Container(
            content=ft.Row([new_worker_field, add_btn]),
            padding=ft.padding.symmetric(horizontal=20)
        ),
        ft.Divider(),
        ft.Container(content=worker_list_ui, padding=20, expand=True)
    ], expand=True)