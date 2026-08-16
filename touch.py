from config import ITEMS_PER_PAGE


# =========================================================
# BOTÓN SIGUIENTE
# =========================================================

def is_next_button(x, y):
    return (
        97 < x < 119
        and
        57 < y < 78
    )


# =========================================================
# BOTÓN ANTERIOR
# =========================================================

def is_previous_button(x, y):
    return (
        97 < x < 119
        and
        169 < y < 190
    )


# =========================================================
# BOTÓN VOLVER
# =========================================================


def is_bottom_button(x, y):
    return (
        97 < x < 119
        and
        220 < y < 242
    )



# =========================================================
# ZONA DE ACTIVIDADES
# =========================================================

def is_activity_area(x, y):
    """
    Zona izquierda de la pantalla donde
    aparecen las cuatro actividades.
    """

    return (
        2 < x < 90
        and
        2 < y < 242
    )


# =========================================================
# OBTENER ACTIVIDAD SELECCIONADA
# =========================================================

def get_selected_activity(
    touch_x,
    touch_y,
    page,
    activities
):
    """
    Devuelve la actividad correspondiente
    a la fila tocada.

    Cada actividad ocupa aproximadamente
    60 píxeles de alto.

    0 - 59     -> actividad 1
    60 - 119   -> actividad 2
    120 - 179  -> actividad 3
    180 - 239  -> actividad 4
    """

    if not is_activity_area(
        touch_x,
        touch_y
    ):
        return None

    item_height = 60

    position = (
        touch_y // item_height
    )

    if (
        position < 0
        or
        position >= ITEMS_PER_PAGE
    ):
        return None

    index = (
        page * ITEMS_PER_PAGE
        + position
    )

    if index >= len(activities):
        return None

    return activities[index]