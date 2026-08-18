from config import (
    ITEMS_PER_PAGE
)


# =========================================================
# COORDENADAS BOTONES
# =========================================================
#
# Deben coincidir con display.py
#
# =========================================================

BUTTON_X1 = 94
BUTTON_X2 = 124

PLUS_Y1 = 10
PLUS_Y2 = 50

SAVE_Y1 = 72
SAVE_Y2 = 112

MINUS_Y1 = 134
MINUS_Y2 = 174

BACK_Y1 = 196
BACK_Y2 = 240


# =========================================================
# FUNCIÓN AUXILIAR
# =========================================================

def is_inside(
    x,
    y,
    x1,
    y1,
    x2,
    y2
):
    """
    Devuelve True si el touch está dentro
    del rectángulo indicado.
    """

    return (
        x >= x1
        and
        x <= x2
        and
        y >= y1
        and
        y <= y2
    )


# =========================================================
# BOTÓN +
# =========================================================

def is_next_button(
    x,
    y
):

    return is_inside(
        x,
        y,
        BUTTON_X1,
        PLUS_Y1,
        BUTTON_X2,
        PLUS_Y2
    )


# =========================================================
# BOTÓN GUARDAR
# =========================================================

def is_save_button(
    x,
    y
):

    return is_inside(
        x,
        y,
        BUTTON_X1,
        SAVE_Y1,
        BUTTON_X2,
        SAVE_Y2
    )


# =========================================================
# BOTÓN -
# =========================================================

def is_previous_button(
    x,
    y
):

    return is_inside(
        x,
        y,
        BUTTON_X1,
        MINUS_Y1,
        BUTTON_X2,
        MINUS_Y2
    )


# =========================================================
# BOTÓN VOLVER
# =========================================================

def is_bottom_button(
    x,
    y
):

    return is_inside(
        x,
        y,
        BUTTON_X1,
        BACK_Y1,
        BUTTON_X2,
        BACK_Y2
    )


# =========================================================
# ÁREA DE ACTIVIDADES
# =========================================================

def is_activity_area(
    x,
    y
):
    """
    Zona donde aparecen las actividades.
    """

    return (
        x >= 2
        and
        x <= 90
        and
        y >= 2
        and
        y <= 242
    )


# =========================================================
# OBTENER ACTIVIDAD SELECCIONADA
# =========================================================

def get_selected_activity(
    x,
    y,
    current_page,
    activities
):

    if not is_activity_area(
        x,
        y
    ):
        return None


    # Cada actividad ocupa aproximadamente 60 px
    position = (
        y
        // 60
    )


    if position < 0:
        return None


    if position >= ITEMS_PER_PAGE:
        return None


    index = (
        current_page
        * ITEMS_PER_PAGE
        + position
    )


    if index >= len(
        activities
    ):
        return None


    return activities[index]