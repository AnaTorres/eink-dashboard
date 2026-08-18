from config import (
    ITEMS_PER_PAGE
)


# =========================================================
# COORDENADAS GENERALES
# =========================================================

BUTTON_X1 = 94
BUTTON_X2 = 124


# =========================================================
# BOTONES PANTALLA PRINCIPAL
# =========================================================

MAIN_NEXT_Y1 = 65
MAIN_NEXT_Y2 = 105

MAIN_PREVIOUS_Y1 = 145
MAIN_PREVIOUS_Y2 = 185


# =========================================================
# BOTONES PANTALLA DURACIÓN
# =========================================================

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
        and x <= x2
        and y >= y1
        and y <= y2
    )


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================

def is_activity_next_button(
    x,
    y
):
    """
    Botón para avanzar de página
    en la lista de actividades.
    """

    return is_inside(
        x,
        y,
        BUTTON_X1,
        MAIN_NEXT_Y1,
        BUTTON_X2,
        MAIN_NEXT_Y2
    )


def is_activity_previous_button(
    x,
    y
):
    """
    Botón para retroceder de página
    en la lista de actividades.
    """

    return is_inside(
        x,
        y,
        BUTTON_X1,
        MAIN_PREVIOUS_Y1,
        BUTTON_X2,
        MAIN_PREVIOUS_Y2
    )


# =========================================================
# PANTALLA DURACIÓN
# =========================================================

def is_next_button(
    x,
    y
):
    """
    Botón + minutos.
    """

    return is_inside(
        x,
        y,
        BUTTON_X1,
        PLUS_Y1,
        BUTTON_X2,
        PLUS_Y2
    )


def is_save_button(
    x,
    y
):
    """
    Botón guardar.
    """

    return is_inside(
        x,
        y,
        BUTTON_X1,
        SAVE_Y1,
        BUTTON_X2,
        SAVE_Y2
    )


def is_previous_button(
    x,
    y
):
    """
    Botón - minutos.
    """

    return is_inside(
        x,
        y,
        BUTTON_X1,
        MINUS_Y1,
        BUTTON_X2,
        MINUS_Y2
    )


def is_bottom_button(
    x,
    y
):
    """
    Botón volver.
    """

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

    return (
        x >= 2
        and x <= 90
        and y >= 2
        and y <= 242
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