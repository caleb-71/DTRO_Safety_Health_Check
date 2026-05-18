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
    # 3. 기본 정보 테이블 (🌟 가로 총합 190mm)
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
    pdf.cell(55, 10, data_dict.get("location", ""), border=1, ln=True)  # ln=True로 줄바꿈

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
    pdf.set_font("KoreanFont", "B", 14)
    pdf.cell(150, 15, "주요 점검 항목", border=1, align="C", fill=True)
    pdf.cell(40, 15, "결과", border=1, align="C", fill=True, ln=True)

    # 5. 체크리스트 데이터
    pdf.set_font("KoreanFont", "", 11)
    for item, result in data_dict["check_results"].items():
        x = pdf.get_x()
        y = pdf.get_y()

        # 🌟 폰트 깨짐 방지를 위해 동그라미(•)를 빼기(-) 기호로 치환
        safe_item_text = item.replace("•", "-")

        pdf.multi_cell(150, 12, safe_item_text, border=1)
        new_y = pdf.get_y()
        pdf.set_xy(x + 150, y)
        pdf.cell(40, new_y - y, result, border=1, align="C", ln=True)

    # 6. 하단 안내 문구
    pdf.ln(10)
    pdf.set_font("KoreanFont", "", 9)
    pdf.multi_cell(0, 5, "이 체크리스트는 관련 법규를 준수하여 작성되었습니다.\n작업 전 반드시 해당 항목을 직접 확인하시기 바랍니다.", align="C")

    # 🌟 핵심: 사용자가 FilePicker로 지정한 경로(target_path)에 저장합니다.
    pdf.output(target_path)
    return True, os.path.basename(target_path)