from config import (
    ITEMS_PER_PAGE
)


def is_next_button(
    x,
    y
):
    return (
        97 < x < 119
        and
        57 < y < 78
    )


def is_home_button(
    x,
    y
):
    return (
        97 < x < 119
        and
        113 < y < 136
    )


def is_previous_button(
    x,
    y
):
    return (
        97 < x < 119
        and
        169 < y < 190
    )


def is_refresh_button(
    x,
    y
):
    return (
        97 < x < 119
        and
        220 < y < 242
    )


def is_activity_area(
    x,
    y
):
    return (
        2 < x < 90
        and
        2 < y < 248
    )


def get_selected_activity(
    touch_x,
    touch_y,
    page,
    activities
):
    """
    Devuelve la actividad correspondiente
    a las coordenadas tocadas.
    """

    if touch_x < 46:
        column = 0
    else:
        column = 1

    if touch_y < 124:
        row = 0
    else:
        row = 1

    position = (
        column * 2
        + row
    )

    index = (
        page * ITEMS_PER_PAGE
        + position
    )

    if index >= len(
        activities
    ):
        return None

    return activities[
        index
    ]