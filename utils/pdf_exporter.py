from fpdf import FPDF
import os


class SafetyPDF(FPDF):
    def header(self):
        # 상단 타이틀 폰트 설정
        self.set_font("KoreanFont", "B", 16)

    def footer(self):
        # 하단 페이지 번호 폰트 설정
        self.set_y(-15)
        self.set_font("KoreanFont", "", 8)
        self.cell(0, 10, f"페이지 {self.page_no()}/{{nb}} - DTRO 안전보건 시스템", align="C")


def export_to_pdf(data_dict, target_path):
    """
    target_path: FilePicker를 통해 사용자가 선택한 실제 저장 경로 (파일명 포함)
    """
    pdf = SafetyPDF()
    pdf.alias_nb_pages()

    font_path = os.path.join("assets", "fonts", "korean.ttf")
    if not os.path.exists(font_path):
        return False, "assets/fonts/ 경로에 korean.ttf 파일이 없습니다!"

    pdf.add_font("KoreanFont", "", font_path)
    pdf.add_font("KoreanFont", "B", font_path)
    pdf.add_page()

    # 2. 타이틀 영역
    pdf.set_font("KoreanFont", "B", 18)
    pdf.cell(0, 15, f"[{data_dict['work_type']}] 안전보건 체크리스트", ln=True, align="C")
    pdf.ln(5)

    # =========================================================================
    # 3. 기본 정보 테이블 (가로 총합 190mm)
    # =========================================================================
    pdf.set_font("KoreanFont", "B", 13)
    pdf.set_fill_color(240, 240, 240)  # 연회색 배경

    # --- 첫 번째 줄: 제목(30) + 값(75) + 제목(30) + 값(55) = 총 190mm ---
    pdf.cell(30, 10, "작업명", border=1, fill=True, align="C")
    pdf.set_font("KoreanFont", "", 13)
    pdf.cell(75, 10, data_dict.get("task_name", ""), border=1)

    pdf.set_font("KoreanFont", "B", 13)
    pdf.cell(30, 10, "작업장소", border=1, fill=True, align="C")
    pdf.set_font("KoreanFont", "", 13)
    pdf.cell(55, 10, data_dict.get("location", ""), border=1, ln=True)

    # --- 두 번째 줄: 제목(30) + 값(35) + 제목(30) + 값(30) + 제목(30) + 값(35) = 총 190mm ---
    pdf.set_font("KoreanFont", "B", 13)
    pdf.cell(30, 10, "작업일자", border=1, fill=True, align="C")
    pdf.set_font("KoreanFont", "", 13)
    pdf.cell(35, 10, data_dict.get("task_date", ""), border=1, align="C")

    pdf.set_font("KoreanFont", "B", 13)
    pdf.cell(30, 10, "작업시간", border=1, fill=True, align="C")
    pdf.set_font("KoreanFont", "", 13)
    pdf.cell(30, 10, data_dict.get("task_time", ""), border=1, align="C")

    pdf.set_font("KoreanFont", "B", 13)
    pdf.cell(30, 10, "작업책임자", border=1, fill=True, align="C")
    pdf.set_font("KoreanFont", "", 13)
    pdf.cell(35, 10, data_dict.get("manager_name", ""), border=1, align="C", ln=True)

    pdf.ln(10)

    # 4. 체크리스트 테이블 헤더
    pdf.set_font("KoreanFont", "B", 13)
    pdf.cell(150, 14, "주요 점검 항목", border=1, align="C", fill=True)
    pdf.cell(40, 14, "결과", border=1, align="C", fill=True, ln=True)

    # 5. 체크리스트 데이터
    pdf.set_font("KoreanFont", "", 11)
    for item, result in data_dict["check_results"].items():
        x = pdf.get_x()
        y = pdf.get_y()

        # 폰트 깨짐 방지를 위해 동그라미(•)를 빼기(-) 기호로 치환
        safe_item_text = item.replace("•", "-")

        pdf.multi_cell(150, 10, safe_item_text, border=1)
        new_y = pdf.get_y()
        pdf.set_xy(x + 150, y)
        pdf.cell(40, new_y - y, result, border=1, align="C", ln=True)

    # =========================================================================
    # 🌟 6. 서명 데이터 (PDF에 직접 그리기)
    # =========================================================================
    signature_strokes = data_dict.get("signature", [])

    if signature_strokes:
        pdf.ln(10)

        # 결재란(액자)의 크기와 위치 설정 (가로 60mm, 세로 30mm)
        box_w = 60
        box_h = 30

        # 페이지 우측 하단에 배치하기 위한 X, Y 좌표 계산
        start_x = 200 - box_w  # 우측 여백 10mm 남기고 배치
        start_y = pdf.get_y()

        # 공간이 부족하면 다음 페이지로 넘김
        if start_y + box_h + 15 > 280:
            pdf.add_page()
            start_y = pdf.get_y()

        # 책임자 이름 출력
        pdf.set_xy(start_x, start_y)
        pdf.set_font("KoreanFont", "B", 12)
        pdf.cell(box_w, 10, f"작업책임자 : {data_dict.get('manager_name', '')}", align="C")

        start_y += 10  # 네모난 박스를 이름 밑에 그리기 위해 10mm 내림

        # 1. 투명한 테두리 박스 그리기
        pdf.rect(start_x, start_y, box_w, box_h)

        # 2. 비율 축소 (앱 화면의 Canvas는 300x150 이었으므로 이를 60x30 크기에 맞춤)
        scale_x = box_w / 300.0
        scale_y = box_h / 150.0

        # 3. 펜 굵기 설정 (서명이 잘 보이도록 약간 굵게)
        pdf.set_line_width(0.6)

        # 4. 좌표를 따라 PDF 캔버스 위에 선 그리기
        for stroke in signature_strokes:
            if not stroke or len(stroke) < 2:
                continue

            # 시작점 잡기
            prev_x = start_x + (stroke[0][0] * scale_x)
            prev_y = start_y + (stroke[0][1] * scale_y)

            # 이어지는 점들로 선 긋기
            for point in stroke[1:]:
                curr_x = start_x + (point[0] * scale_x)
                curr_y = start_y + (point[1] * scale_y)
                pdf.line(prev_x, prev_y, curr_x, curr_y)

                prev_x = curr_x
                prev_y = curr_y

        # 펜 굵기를 다시 원래대로 돌려놓음
        pdf.set_line_width(0.2)
        pdf.set_y(start_y + box_h + 10)

    # 7. 하단 안내 문구
    pdf.ln(5)
    pdf.set_font("KoreanFont", "", 9)
    pdf.multi_cell(0, 5, "이 체크리스트는 관련 법규를 준수하여 작성되었습니다.\n작업 전 반드시 해당 항목을 직접 확인하시기 바랍니다.", align="C")

    # 최종 저장
    pdf.output(target_path)
    return True, os.path.basename(target_path)