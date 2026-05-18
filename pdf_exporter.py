from fpdf import FPDF
import os


class SafetyPDF(FPDF):
    def header(self):
        # 상단 타이틀 (한글 폰트 설정 후 호출됨)
        self.set_font("NanumGothic", "B", 16)

    def footer(self):
        self.set_y(-15)
        self.set_font("NanumGothic", "", 8)
        self.cell(0, 10, f"페이지 {self.page_no()}/{{nb}} - DTRO 안전보건 시스템", align="C")


def export_to_pdf(data_dict):
    """
    data_dict 예시: {
        "task_name": "...", "task_date": "...", "manager_name": "...",
        "work_type": "아크용접", "check_results": {"항목": "확인", ...}
    }
    """
    pdf = SafetyPDF()
    pdf.alias_nb_pages()

    # 1. 한글 폰트 등록 (파일이 assets/fonts/에 있어야 함)
    font_path = os.path.join("assets", "fonts", "NanumGothic.ttf")
    # 폰트 파일이 없을 경우를 대비한 예외 처리
    if not os.path.exists(font_path):
        return False, "폰트 파일(NanumGothic.ttf)을 찾을 수 없습니다."

    pdf.add_font("NanumGothic", "", font_path)
    pdf.add_font("NanumGothic", "B", font_path)
    pdf.add_page()

    # 2. 타이틀 영역
    pdf.set_font("NanumGothic", "B", 18)
    pdf.cell(0, 15, f"[{data_dict['work_type']}] 안전보건 체크리스트", ln=True, align="C")
    pdf.ln(5)

    # 3. 기본 정보 테이블
    pdf.set_font("NanumGothic", "B", 10)
    pdf.set_fill_color(240, 240, 240)

    col_width = 38
    pdf.cell(col_width, 10, "작업명", border=1, fill=True)
    pdf.set_font("NanumGothic", "", 10)
    pdf.cell(col_width * 4, 10, data_dict["task_name"], border=1, ln=True)

    pdf.set_font("NanumGothic", "B", 10)
    pdf.cell(col_width, 10, "작업일자", border=1, fill=True)
    pdf.set_font("NanumGothic", "", 10)
    pdf.cell(col_width, 10, data_dict["task_date"], border=1)

    pdf.set_font("NanumGothic", "B", 10)
    pdf.cell(col_width, 10, "작업책임자", border=1, fill=True)
    pdf.set_font("NanumGothic", "", 10)
    pdf.cell(col_width, 10, data_dict["manager_name"], border=1, ln=True)

    pdf.ln(10)

    # 4. 체크리스트 테이블 헤더
    pdf.set_font("NanumGothic", "B", 11)
    pdf.cell(150, 10, "주요 점검 항목", border=1, align="C", fill=True)
    pdf.cell(40, 10, "결과", border=1, align="C", fill=True, ln=True)

    # 5. 체크리스트 데이터
    pdf.set_font("NanumGothic", "", 9)
    for item, result in data_dict["check_results"].items():
        # 항목 내용이 길 경우 자동 줄바꿈을 위해 multi_cell 사용 고민 가능하지만 여기선 cell 사용
        # 항목 텍스트가 너무 길면 잘릴 수 있으므로 멀티셀 처리
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(150, 8, item, border=1)
        new_y = pdf.get_y()
        pdf.set_xy(x + 150, y)
        pdf.cell(40, new_y - y, result, border=1, align="C", ln=True)

    # 6. 하단 안내 및 저장
    pdf.ln(10)
    pdf.set_font("NanumGothic", "", 9)
    pdf.multi_cell(0, 5, "이 체크리스트는 관련 법규를 준수하여 작성되었습니다.\n작업 전 반드시 해당 항목을 직접 확인하시기 바랍니다.", align="C")

    # 파일 저장 (현재 폴더에 '보고서_시간.pdf' 형태로 저장)
    filename = f"Safety_Report_{data_dict['manager_name']}_{data_dict['work_type']}.pdf"
    pdf.output(filename)
    return True, filename