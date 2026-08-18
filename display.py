from PIL import (
    Image,
    ImageDraw,
    ImageFont
)

from config import (
    FONT_FILE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ITEMS_PER_PAGE
)


# =========================================================
# FUENTES
# =========================================================

font15 = ImageFont.truetype(
    FONT_FILE,
    15
)

font24 = ImageFont.truetype(
    FONT_FILE,
    24
)


# =========================================================
# CREAR IMAGEN VACÍA
# =========================================================

def create_blank_image():

    return Image.new(
        "1",
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        255
    )


# =========================================================
# BARRA DE PROGRESO
# =========================================================

def draw_progress_bar(
    draw,
    x,
    y,
    width,
    height,
    percentage
):
    """
    Dibuja una barra de progreso monocromática.
    """

    visual_percentage = max(
        0,
        min(
            percentage,
            100
        )
    )

    # Borde
    draw.rectangle(
        (
            x,
            y,
            x + width,
            y + height
        ),
        outline=0,
        fill=255
    )

    filled_width = int(
        width
        * visual_percentage
        / 100
    )

    if filled_width > 0:

        draw.rectangle(
            (
                x,
                y,
                x + filled_width,
                y + height
            ),
            fill=0
        )


# =========================================================
# TEXTO CENTRADO
# =========================================================

def draw_centered_text(
    draw,
    box,
    text,
    font
):
    """
    Dibuja texto centrado dentro de un rectángulo.

    Si contiene varias palabras y no cabe,
    intenta dividirlo en dos líneas.
    """

    x1, y1, x2, y2 = box

    max_width = (
        x2
        - x1
    )


    # -----------------------------------------------------
    # Medir texto
    # -----------------------------------------------------

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2]
        - bbox[0]
    )


    # -----------------------------------------------------
    # Cabe en una sola línea
    # -----------------------------------------------------

    if text_width <= max_width - 6:

        text_height = (
            bbox[3]
            - bbox[1]
        )

        x = x1 + (
            max_width
            - text_width
        ) // 2

        y = y1 + (
            (
                y2
                - y1
                - text_height
            )
            // 2
        )

        draw.text(
            (x, y),
            text,
            font=font,
            fill=0
        )

        return


    # -----------------------------------------------------
    # Dividir en varias líneas
    # -----------------------------------------------------

    words = text.split()

    if len(words) >= 2:

        middle = (
            len(words)
            // 2
        )

        line1 = " ".join(
            words[:middle]
        )

        line2 = " ".join(
            words[middle:]
        )

        lines = [
            line1,
            line2
        ]

    else:

        lines = [
            text
        ]


    line_height = 17

    total_height = (
        len(lines)
        * line_height
    )

    y = y1 + (
        (
            y2
            - y1
            - total_height
        )
        // 2
    )


    for line in lines:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        width = (
            bbox[2]
            - bbox[0]
        )

        x = x1 + (
            max_width
            - width
        ) // 2

        draw.text(
            (x, y),
            line,
            font=font,
            fill=0
        )

        y += line_height


# =========================================================
# BOTÓN NEGRO
# =========================================================

def draw_button(
    draw,
    box,
    text,
    font
):
    """
    Dibuja un botón negro con texto blanco centrado.
    """

    x1, y1, x2, y2 = box


    # -----------------------------------------------------
    # Fondo negro
    # -----------------------------------------------------

    draw.rectangle(
        box,
        outline=0,
        fill=0
    )


    # -----------------------------------------------------
    # Medir símbolo
    # -----------------------------------------------------

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2]
        - bbox[0]
    )

    text_height = (
        bbox[3]
        - bbox[1]
    )


    # -----------------------------------------------------
    # Posición centrada
    # -----------------------------------------------------

    x = x1 + (
        (
            x2
            - x1
            - text_width
        )
        // 2
    )

    y = y1 + (
        (
            y2
            - y1
            - text_height
        )
        // 2
    ) - bbox[1]


    # -----------------------------------------------------
    # Texto blanco
    # -----------------------------------------------------

    draw.text(
        (x, y),
        text,
        font=font,
        fill=255
    )


# =========================================================
# PANTALLA ACTIVIDADES
# =========================================================

def show_activities(
    image,
    activities,
    page
):
    """
    Muestra cuatro actividades.
    """

    draw = ImageDraw.Draw(
        image
    )


    # -----------------------------------------------------
    # Limpiar pantalla
    # -----------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            SCREEN_WIDTH - 1,
            SCREEN_HEIGHT - 1
        ),
        fill=255
    )


    first_index = (
        page
        * ITEMS_PER_PAGE
    )

    item_height = 60


    # -----------------------------------------------------
    # Actividades
    # -----------------------------------------------------

    for position in range(
        ITEMS_PER_PAGE
    ):

        index = (
            first_index
            + position
        )

        if index >= len(
            activities
        ):
            continue


        activity = (
            activities[index]
        )

        text = str(
            activity["name"]
        )


        y1 = (
            position
            * item_height
            + 2
        )

        y2 = (
            y1
            + item_height
            - 4
        )


        box = (
            2,
            y1,
            90,
            y2
        )


        draw.rectangle(
            box,
            outline=0
        )


        draw_centered_text(
            draw,
            box,
            text,
            font15
        )


    # -----------------------------------------------------
    # Botón siguiente
    # -----------------------------------------------------

    draw.text(
        (
            100,
            60
        ),
        "▶",
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Botón anterior
    # -----------------------------------------------------

    draw.text(
        (
            100,
            170
        ),
        "◀",
        font=font15,
        fill=0
    )


# =========================================================
# PANTALLA DURACIÓN
# =========================================================

def show_duration_screen(
    image,
    activity,
    minutes,
    progress
):

    draw = ImageDraw.Draw(
        image
    )


    # -----------------------------------------------------
    # Limpiar pantalla
    # -----------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            SCREEN_WIDTH - 1,
            SCREEN_HEIGHT - 1
        ),
        fill=255
    )


    # =====================================================
    # ACTIVIDAD
    # =====================================================

    draw_centered_text(
        draw,
        (
            3,
            7,
            90,
            37
        ),
        str(
            activity["name"]
        ),
        font15
    )


    # =====================================================
    # TIEMPO A REGISTRAR
    # =====================================================

    draw_centered_text(
        draw,
        (
            3,
            47,
            90,
            83
        ),
        str(minutes) + " min",
        font24
    )


    # =====================================================
    # PROGRESO MENSUAL
    # =====================================================

    month_minutes = (
        progress["month_minutes"]
    )

    monthly_goal = (
        progress["monthly_goal"]
    )

    month_percentage = (
        progress["month_percentage"]
    )


    # -----------------------------------------------------
    # Mes
    # -----------------------------------------------------

    draw.text(
        (
            5,
            110
        ),
        "Mes",
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Porcentaje mes
    # -----------------------------------------------------

    percentage_text = (
        f"{month_percentage}%"
    )

    bbox = draw.textbbox(
        (0, 0),
        percentage_text,
        font=font15
    )

    percentage_width = (
        bbox[2]
        - bbox[0]
    )

    draw.text(
        (
            85
            - percentage_width,
            110
        ),
        percentage_text,
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Minutos / meta mensual
    # -----------------------------------------------------

    month_text = (
        f"{month_minutes}/{monthly_goal}"
    )

    draw.text(
        (
            5,
            130
        ),
        month_text,
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Barra mensual
    # -----------------------------------------------------

    draw_progress_bar(
        draw,
        5,
        153,
        80,
        8,
        month_percentage
    )


    # =====================================================
    # PROGRESO ANUAL
    # =====================================================

    year_minutes = (
        progress["year_minutes"]
    )

    annual_goal = (
        progress["annual_goal"]
    )

    year_percentage = (
        progress["year_percentage"]
    )


    # -----------------------------------------------------
    # Año
    # -----------------------------------------------------

    draw.text(
        (
            5,
            190
        ),
        "Año",
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Porcentaje año
    # -----------------------------------------------------

    percentage_text = (
        f"{year_percentage}%"
    )

    bbox = draw.textbbox(
        (0, 0),
        percentage_text,
        font=font15
    )

    percentage_width = (
        bbox[2]
        - bbox[0]
    )

    draw.text(
        (
            85
            - percentage_width,
            190
        ),
        percentage_text,
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Minutos / meta anual
    # -----------------------------------------------------

    year_text = (
        f"{year_minutes}/{annual_goal}"
    )

    draw.text(
        (
            5,
            210
        ),
        year_text,
        font=font15,
        fill=0
    )


    # -----------------------------------------------------
    # Barra anual
    # -----------------------------------------------------

    draw_progress_bar(
        draw,
        5,
        230,
        80,
        8,
        year_percentage
    )


    # =====================================================
    # BOTONES LATERALES
    # =====================================================

    # -----------------------------------------------------
    # + minutos
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            94,
            35,
            124,
            80
        ),
        "+",
        font24
    )


    # -----------------------------------------------------
    # Guardar
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            94,
            95,
            124,
            140
        ),
        "S",
        font24
    )


    # -----------------------------------------------------
    # - minutos
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            94,
            155,
            124,
            200
        ),
        "-",
        font24
    )


    # -----------------------------------------------------
    # Volver
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            94,
            210,
            124,
            248
        ),
        "B",
        font15
    )


# =========================================================
# PANTALLA TIEMPO GUARDADO
# =========================================================

def show_saved_screen(
    image
):

    draw = ImageDraw.Draw(
        image
    )


    # -----------------------------------------------------
    # Limpiar pantalla
    # -----------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            SCREEN_WIDTH - 1,
            SCREEN_HEIGHT - 1
        ),
        fill=255
    )


    # -----------------------------------------------------
    # Mensaje centrado
    # -----------------------------------------------------

    draw_centered_text(
        draw,
        (
            5,
            75,
            SCREEN_WIDTH - 5,
            175
        ),
        "Tiempo guardado",
        font24
    )