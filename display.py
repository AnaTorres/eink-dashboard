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

    # Limitar visualmente entre 0 y 100
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
    Dibuja el texto centrado.

    Si contiene varias palabras y no cabe horizontalmente,
    intenta dividirlo en dos líneas.
    """

    x1, y1, x2, y2 = box

    max_width = x2 - x1


    # -----------------------------------------------------
    # Medir texto completo
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
    # Si cabe en una sola línea
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
    # Intentar dividir en dos líneas
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


    # -----------------------------------------------------
    # Calcular altura total
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Dibujar cada línea
    # -----------------------------------------------------

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
# BOTÓN
# =========================================================

def draw_button(
    draw,
    box,
    text,
    font
):
    """
    Dibuja un botón rectangular con borde
    y texto centrado.
    """

    draw.rectangle(
        box,
        outline=0,
        fill=255
    )

    draw_centered_text(
        draw,
        box,
        text,
        font
    )


# =========================================================
# PANTALLA DE ACTIVIDADES
# =========================================================

def show_activities(
    image,
    activities,
    page
):
    """
    Muestra cuatro actividades.

    La zona izquierda:
        x = 2 ... 90

    se divide en cuatro filas.
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


    # Alto aproximado de cada actividad
    item_height = 60


    # -----------------------------------------------------
    # Dibujar actividades
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


        # Rectángulo alrededor de actividad
        draw.rectangle(
            box,
            outline=0
        )


        # Texto centrado
        draw_centered_text(
            draw,
            box,
            text,
            font15
        )


    # -----------------------------------------------------
    # Botones laterales
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
# PANTALLA DE DURACIÓN
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
    # Título Mes
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
    # Porcentaje mensual
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
    # Título Año
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
    # Porcentaje anual
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
    # BOTONES
    # =====================================================

    # -----------------------------------------------------
    # + minutos
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            96,
            42,
            122,
            82
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
            96,
            98,
            122,
            138
        ),
        "OK",
        font15
    )


    # -----------------------------------------------------
    # - minutos
    # -----------------------------------------------------

    draw_button(
        draw,
        (
            96,
            154,
            122,
            194
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
            96,
            210,
            122,
            248
        ),
        "<",
        font24
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
    # Mensaje
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