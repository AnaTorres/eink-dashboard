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
# BOTÓN HOME / PRIMERA PÁGINA
# =========================================================

def is_home_button(x, y):
    return (
        97 < x < 119
        and
        113 < y < 136
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
# BOTÓN REFRESH / BACK
# =========================================================

def is_refresh_button(x, y):
    return (
        97 < x < 119
        and
        220 < y < 242
    )


# =========================================================
# ZONA DONDE ESTÁN LAS ACTIVIDADES
# =========================================================

def is_activity_area(x, y):
    """
    Devuelve True si el toque está dentro
    de la zona donde se muestran las actividades.

    La barra lateral empieza aproximadamente
    en x = 97, así que dejamos las actividades
    entre x = 2 y x = 90.
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
    Devuelve la actividad tocada.

    La pantalla muestra 4 actividades en vertical:

        posición 0 -> y 0 - 59
        posición 1 -> y 60 - 119
        posición 2 -> y 120 - 179
        posición 3 -> y 180 - 239

    Cada página contiene 4 actividades.
    """

    # -----------------------------------------------------
    # Verificar que el toque esté en la zona correcta
    # -----------------------------------------------------

    if not is_activity_area(
        touch_x,
        touch_y
    ):
        return None


    # -----------------------------------------------------
    # Cada actividad ocupa 60 píxeles de alto
    # -----------------------------------------------------

    item_height = 60


    # -----------------------------------------------------
    # Calcular qué fila se tocó
    #
    # Ejemplo:
    #
    # y = 20  -> 0
    # y = 80  -> 1
    # y = 140 -> 2
    # y = 210 -> 3
    # -----------------------------------------------------

    position = (
        touch_y // item_height
    )


    # -----------------------------------------------------
    # Solo tenemos 4 posiciones por página
    # -----------------------------------------------------

    if (
        position < 0
        or
        position >= ITEMS_PER_PAGE
    ):
        return None


    # -----------------------------------------------------
    # Calcular índice real dentro de activities
    #
    # Página 0:
    #   0 1 2 3
    #
    # Página 1:
    #   4 5 6 7
    #
    # Página 2:
    #   8 9 10 11
    # -----------------------------------------------------

    index = (
        page * ITEMS_PER_PAGE
        + position
    )


    # -----------------------------------------------------
    # Comprobar que existe la actividad
    # -----------------------------------------------------

    if index >= len(
        activities
    ):
        return None


    # -----------------------------------------------------
    # Devolver actividad
    # -----------------------------------------------------

    return activities[
        index
    ]