import flet as ft

# 🌈 브랜드 컬러 정의
class AppColors:
    PRIMARY = ft.colors.BLUE_800
    PRIMARY_LIGHT = ft.colors.BLUE_50
    SECONDARY = ft.colors.TEAL_700
    ACCENT = ft.colors.DEEP_ORANGE_600
    BACKGROUND = ft.colors.GREY_100
    WHITE = ft.colors.WHITE
    TEXT_MAIN = ft.colors.BLUE_GREY_900
    TEXT_SUB = ft.colors.BLUE_GREY_400

# ✨ 그림자(Shadow) 설정
COMMON_SHADOW = ft.BoxShadow(
    spread_radius=1,
    blur_radius=12,
    color=ft.colors.with_opacity(0.15, ft.colors.BLACK),
    offset=ft.Offset(0, 5)
)

# 🌊 그라데이션 버튼 스타일
SAVE_BUTTON_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=[ft.colors.BLUE_700, ft.colors.INDIGO_800]
)

PDF_BUTTON_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=[ft.colors.ORANGE_700, ft.colors.RED_700]
)

# 📦 카드 스타일 정의
def card_style():
    return {
        "padding": 20,
        "bgcolor": AppColors.WHITE,
        "border_radius": 18,
        "margin": ft.padding.only(bottom=15),
        "shadow": COMMON_SHADOW
    }

# 🔘 라디오 버튼 스타일
RADIO_THEME = {
    "confirm": ft.colors.TEAL_500,
    "none": ft.colors.AMBER_700
}