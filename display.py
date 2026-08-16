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
    """
    Crea una imagen blanca del tamaño de la pantalla.
    """

    return Image.new(
        "1",
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        255
    )


def create_vertical_text(
    text,
    width=122,
    height=43,
    font=font15
):
    """
    Crea texto horizontal y luego lo rota 90 grados.
    """

    image = Image.new(
        "1",
        (
            width,
            height
        ),
        255
    )

    draw = ImageDraw.Draw(
        image
    )

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

    x = (
        width
        - text_width
    ) // 2

    y = (
        height
        - text_height
    ) // 2

    draw.text(
        (
            x,
            y
        ),
        text,
        font=font,
        fill=0
    )

    return image.rotate(
        90,
        expand=True
    )


def show_activities(
    image,
    activities,
    page
):
    """
    Dibuja las actividades de una página.
    """

    draw = ImageDraw.Draw(
        image
    )

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
            activities[
                index
            ]
        )

        text = str(
            activity["name"]
        )

        column = (
            position // 2
        )

        row = (
            position % 2
        )

        x = (
            column * 45
            + 2
        )

        y = (
            row * 124
            + 2
        )

        word_image = (
            create_vertical_text(
                text
            )
        )

        image.paste(
            word_image,
            (
                x,
                y
            )
        )

    draw = ImageDraw.Draw(
        image
    )

    # Botón siguiente
    draw.text(
        (
            100,
            60
        ),
        ">",
        font=font15,
        fill=0
    )

    # Primera página
    draw.text(
        (
            100,
            115
        ),
        "H",
        font=font15,
        fill=0
    )

    # Página anterior
    draw.text(
        (
            100,
            170
        ),
        "<",
        font=font15,
        fill=0
    )

    # Recargar actividades
    draw.text(
        (
            100,
            220
        ),
        "R",
        font=font15,
        fill=0
    )


def show_duration_screen(
    image,
    activity,
    minutes
):
    """
    Pantalla para modificar y guardar el tiempo.
    """

    draw = ImageDraw.Draw(
        image
    )

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
    # Nombre actividad
    # -----------------------------------------------------

    activity_image = (
        create_vertical_text(
            str(
                activity["name"]
            ),
            width=190,
            height=30,
            font=font15
        )
    )

    image.paste(
        activity_image,
        (
            5,
            25
        )
    )

    # -----------------------------------------------------
    # Duración
    # -----------------------------------------------------

    minutes_text = (
        str(minutes)
        + " min"
    )

    time_image = (
        create_vertical_text(
            minutes_text,
            width=110,
            height=35,
            font=font24
        )
    )

    image.paste(
        time_image,
        (
            50,
            70
        )
    )

    draw = ImageDraw.Draw(
        image
    )

    # +15
    draw.text(
        (
            100,
            60
        ),
        "+",
        font=font24,
        fill=0
    )

    # Save
    draw.text(
        (
            100,
            115
        ),
        "S",
        font=font15,
        fill=0
    )

    # -15
    draw.text(
        (
            100,
            170
        ),
        "-",
        font=font24,
        fill=0
    )

    # Back
    draw.text(
        (
            100,
            220
        ),
        "B",
        font=font15,
        fill=0
    )