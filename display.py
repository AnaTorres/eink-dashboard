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


font15 = ImageFont.truetype(
    FONT_FILE,
    15
)

font24 = ImageFont.truetype(
    FONT_FILE,
    24
)


def create_blank_image():
    return Image.new(
        "1",
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        255
    )

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

    # Medir el texto completo
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    # Si cabe, mostrar normalmente
    if text_width <= max_width - 6:

        text_height = bbox[3] - bbox[1]

        x = x1 + (
            max_width - text_width
        ) // 2

        y = y1 + (
            (y2 - y1 - text_height) // 2
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

        middle = len(words) // 2

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
        lines = [text]


    # -----------------------------------------------------
    # Calcular altura total
    # -----------------------------------------------------

    line_height = 17

    total_height = (
        len(lines)
        * line_height
    )

    y = y1 + (
        (y2 - y1 - total_height) // 2
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
            max_width - width
        ) // 2

        draw.text(
            (x, y),
            line,
            font=font,
            fill=0
        )

        y += line_height


def show_activities(
    image,
    activities,
    page
):
    """
    Muestra cuatro actividades horizontalmente.

    La zona izquierda:
        x = 2 ... 90

    se divide en cuatro filas.
    """

    draw = ImageDraw.Draw(
        image
    )

    # Limpiar pantalla
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
        page * ITEMS_PER_PAGE
    )

    # Alto aproximado de cada actividad
    item_height = 60

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

        activity = activities[index]

        text = str(
            activity["name"]
        )

        y1 = (
            position * item_height
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

        # Rectángulo alrededor de la actividad
        draw.rectangle(
            box,
            outline=0
        )

        # Texto horizontal
        draw_centered_text(
            draw,
            box,
            text,
            font15
        )

    # ---------------------------------------------
    # Botones laterales
    # ---------------------------------------------

    draw.text(
        (100, 60),
        "▶",
        font=font15,
        fill=0
    )

    draw.text(
        (100, 170),
        "◀",
        font=font15,
        fill=0
    )



def show_duration_screen(
    image,
    activity,
    minutes,
    progress
):

    draw = ImageDraw.Draw(
        image
    )

    # Limpiar pantalla
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
            5,
            90,
            35
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
            40,
            90,
            74
        ),
        str(minutes) + " min",
        font24
    )


     # =====================================================
    # PROGRESO ANUAL
    # =====================================================

    year_minutes = progress["year_minutes"]
    annual_goal = progress["annual_goal"]
    year_percentage = progress["year_percentage"]

    # Título
    draw.text(
        (5, 105),
        "Año",
        font=font15,
        fill=0
    )

    # Porcentaje a la derecha
    percentage_text = f"{year_percentage}%"

    bbox = draw.textbbox(
        (0, 0),
        percentage_text,
        font=font15
    )

    percentage_width = bbox[2] - bbox[0]

    draw.text(
        (85 - percentage_width, 105),
        percentage_text,
        font=font15,
        fill=0
    )

    # Minutos realizados / meta
    year_text = f"{year_minutes}/{annual_goal}"

    draw.text(
        (5, 125),
        year_text,
        font=font15,
        fill=0
    )

    # Barra anual
    draw_progress_bar(
        draw,
        5,
        148,
        80,
        8,
        year_percentage
    )


    # =====================================================
    # PROGRESO MENSUAL
    # =====================================================

    month_minutes = progress["month_minutes"]
    monthly_goal = progress["monthly_goal"]
    month_percentage = progress["month_percentage"]

    # Título
    draw.text(
        (5, 175),
        "Mes",
        font=font15,
        fill=0
    )

    # Porcentaje a la derecha
    percentage_text = f"{month_percentage}%"

    bbox = draw.textbbox(
        (0, 0),
        percentage_text,
        font=font15
    )

    percentage_width = bbox[2] - bbox[0]

    draw.text(
        (85 - percentage_width, 175),
        percentage_text,
        font=font15,
        fill=0
    )

    # Minutos realizados / meta
    month_text = f"{month_minutes}/{monthly_goal}"

    draw.text(
        (5, 195),
        month_text,
        font=font15,
        fill=0
    )

    # Barra mensual
    draw_progress_bar(
        draw,
        5,
        215,
        80,
        8,
        month_percentage
    )


    # =====================================================
    # BOTONES
    # =====================================================

    # + minutos
    draw.text(
        (
            100,
            60
        ),
        "+",
        font=font24,
        fill=0
    )


    # Guardar
    draw.text(
        (
            100,
            115
        ),
        "S",
        font=font15,
        fill=0
    )


    # - minutos
    draw.text(
        (
            100,
            170
        ),
        "-",
        font=font24,
        fill=0
    )


    # Volver
    draw.text(
        (
            100,
            220
        ),
        "B",
        font=font15,
        fill=0
    )