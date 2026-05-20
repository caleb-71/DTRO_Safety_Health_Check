import flet as ft

# =====================================================
# 🛡️ Flet 버전 호환 패치
# ft.colors / ft.Colors 두 버전 모두 안전하게 처리
# =====================================================
_C = ft.Colors if hasattr(ft, 'Colors') else ft.colors
_I = ft.Icons if hasattr(ft, 'Icons') else ft.icons


# 🌈 브랜드 컬러 정의
class AppColors:
    PRIMARY       = _C.BLUE_800
    PRIMARY_LIGHT = _C.BLUE_50
    SECONDARY     = _C.TEAL_700
    ACCENT        = _C.DEEP_ORANGE_600
    BACKGROUND    = _C.GREY_100
    WHITE         = _C.WHITE
    TEXT_MAIN     = _C.BLUE_GREY_900
    TEXT_SUB      = _C.BLUE_GREY_400


# ✨ 그림자(Shadow) 설정
COMMON_SHADOW = ft.BoxShadow(
    spread_radius=1,
    blur_radius=12,
    color=ft.Colors.with_opacity(0.15, _C.BLACK) if hasattr(ft, 'Colors') else ft.colors.with_opacity(0.15, _C.BLACK),
    offset=ft.Offset(0, 5)
)

# 🌊 그라데이션 버튼 스타일
SAVE_BUTTON_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=[_C.BLUE_700, _C.INDIGO_800]
)

PDF_BUTTON_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=[_C.ORANGE_700, _C.RED_700]
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
    "confirm": _C.TEAL_500,
    "none":    _C.AMBER_700
}