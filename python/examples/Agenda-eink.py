#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
import threading
import math

from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------
# Carpetas
# ---------------------------------------------------------

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "pic/2in13"
)

fontdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "pic"
)

libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    "lib"
)

if os.path.exists(libdir):
    sys.path.append(libdir)


# ---------------------------------------------------------
# Librerías Waveshare
# ---------------------------------------------------------

from TP_lib import gt1151
from TP_lib import epd2in13_V3


logging.basicConfig(level=logging.DEBUG)

flag_t = 1


# ---------------------------------------------------------
# Archivo donde están las palabras
# ---------------------------------------------------------

WORDS_FILE = os.path.join(
    picdir,
    "words.txt"
)


# ---------------------------------------------------------
# Cargar palabras desde archivo
# ---------------------------------------------------------

def Load_Words():
    """
    Lee words.txt.

    Cada línea representa una palabra.

    Ejemplo:

    Ejercicio
    Agua
    Comida
    Descanso
    """

    words = []

    try:
        with open(WORDS_FILE, "r", encoding="utf-8") as file:
            for line in file:
                word = line.strip()

                # Ignorar líneas vacías
                if word:
                    words.append(word)

    except FileNotFoundError:
        print("ERROR: No se encontró:")
        print(WORDS_FILE)

    return words


# ---------------------------------------------------------
# Touch thread
# ---------------------------------------------------------

def pthread_irq():

    print("pthread running")

    while flag_t == 1:

        if gt.digital_read(gt.INT) == 0:
            GT_Dev.Touch = 1
        else:
            GT_Dev.Touch = 0

        time.sleep(0.01)

    print("thread: exit")


# ---------------------------------------------------------
# Leer una imagen BMP
# ---------------------------------------------------------

def Read_BMP(image, filename, x, y):

    newimage = Image.open(
        os.path.join(
            picdir,
            filename
        )
    ).convert("1")

    image.paste(
        newimage,
        (x, y)
    )


# ---------------------------------------------------------
# Crear una palabra vertical
# ---------------------------------------------------------

def Create_Vertical_Word(text):

    """
    Crea una imagen horizontal de 122 x 43.

    Escribe la palabra centrada.

    Después rota la imagen 90 grados.

    Resultado:
        43 x 122
    """

    word_image = Image.new(
        "1",
        (122, 43),
        255
    )

    word_draw = ImageDraw.Draw(
        word_image
    )

    bbox = word_draw.textbbox(
        (0, 0),
        text,
        font=font15
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    text_x = (
        122 - text_width
    ) // 2

    text_y = (
        43 - text_height
    ) // 2

    word_draw.text(
        (text_x, text_y),
        text,
        font=font15,
        fill=0
    )

    word_image = word_image.rotate(
        90,
        expand=True
    )

    return word_image


# ---------------------------------------------------------
# Número de páginas
# ---------------------------------------------------------

def Get_Total_Pages():

    """
    Cada página muestra 4 palabras.
    """

    if len(Words_S) == 0:
        return 1

    return math.ceil(
        len(Words_S) / 4
    )


# ---------------------------------------------------------
# Mostrar palabras
# ---------------------------------------------------------

def Show_Words(image, page):

    """
    Muestra máximo 4 palabras por página.

    Página 0:
        palabras 0 - 3

    Página 1:
        palabras 4 - 7

    Página 2:
        palabras 8 - 11

    etc.
    """

    # -----------------------------------------------------
    # Primero cargar el fondo con los botones
    # -----------------------------------------------------

    Read_BMP(
        image,
        "Photo_1.bmp",
        0,
        0
    )

    # -----------------------------------------------------
    # Limpiar zona donde aparecen las palabras
    # -----------------------------------------------------

    draw = ImageDraw.Draw(
        image
    )

    draw.rectangle(
        (2, 2, 90, 248),
        fill=255
    )

    # Primera palabra de esta página
    first_index = page * 4

    # -----------------------------------------------------
    # Mostrar máximo cuatro palabras
    # -----------------------------------------------------

    for position in range(4):

        word_index = (
            first_index + position
        )

        if word_index >= len(Words_S):
            continue

        # -----------------------------------------------
        # Calcular posición
        # -----------------------------------------------

        column = position // 2
        row = position % 2

        x = column * 45 + 2
        y = row * 124 + 2

        # -----------------------------------------------
        # Crear palabra
        # -----------------------------------------------

        word_image = Create_Vertical_Word(
            Words_S[word_index]
        )

        # -----------------------------------------------
        # Pegar palabra
        # -----------------------------------------------

        image.paste(
            word_image,
            (x, y)
        )


# ---------------------------------------------------------
# Saber qué palabra se tocó
# ---------------------------------------------------------

def Get_Selected_Word(
    touch_x,
    touch_y,
    page
):

    """
    Convierte coordenadas táctiles en índice
    de una palabra.
    """

    # Zona izquierda/derecha
    if touch_x < 46:
        column = 0
    else:
        column = 1

    # Zona superior/inferior
    if touch_y < 124:
        row = 0
    else:
        row = 1

    position = (
        column * 2
        + row
    )

    word_index = (
        page * 4
        + position
    )

    if word_index >= len(Words_S):
        return None

    return word_index


# ---------------------------------------------------------
# Programa principal
# ---------------------------------------------------------

try:

    logging.info(
        "epd2in13_V3 Dynamic Words"
    )


    # -----------------------------------------------------
    # Inicializar pantalla y touch
    # -----------------------------------------------------

    epd = epd2in13_V3.EPD()

    gt = gt1151.GT1151()

    GT_Dev = gt1151.GT_Development()

    GT_Old = gt1151.GT_Development()


    epd.init(
        epd.FULL_UPDATE
    )

    gt.GT_Init()

    epd.Clear(
        0xFF
    )


    # -----------------------------------------------------
    # Thread táctil
    # -----------------------------------------------------

    t = threading.Thread(
        target=pthread_irq
    )

    t.daemon = True

    t.start()


    # -----------------------------------------------------
    # Fuente
    # -----------------------------------------------------

    font15 = ImageFont.truetype(
        os.path.join(
            fontdir,
            "Font.ttc"
        ),
        15
    )


    # -----------------------------------------------------
    # Leer palabras desde archivo
    # -----------------------------------------------------

    Words_S = Load_Words()


    print("")
    print("Palabras cargadas:")
    print(Words_S)
    print("")


    # -----------------------------------------------------
    # Número de páginas
    # -----------------------------------------------------

    Total_Pages = Get_Total_Pages()


    print(
        "Total palabras:",
        len(Words_S)
    )

    print(
        "Total páginas:",
        Total_Pages
    )


    # -----------------------------------------------------
    # Página inicial
    # -----------------------------------------------------

    Current_Page = 0


    # -----------------------------------------------------
    # Crear imagen inicial
    # -----------------------------------------------------

    image = Image.open(
        os.path.join(
            picdir,
            "Photo_1.bmp"
        )
    ).convert("1")


    # Dibujar primera página
    Show_Words(
        image,
        Current_Page
    )


    # Mostrar pantalla
    epd.displayPartBaseImage(
        epd.getbuffer(
            image
        )
    )


    epd.init(
        epd.PART_UPDATE
    )


    # -----------------------------------------------------
    # Variables de actualización
    # -----------------------------------------------------

    Refresh_Count = 0

    ReFlag = 0

    SelfFlag = 0


    # =====================================================
    # LOOP PRINCIPAL
    # =====================================================

    while True:


        # -------------------------------------------------
        # Refresh parcial
        # -------------------------------------------------

        if ReFlag == 1:

            epd.displayPartial_Wait(
                epd.getbuffer(
                    image
                )
            )

            Refresh_Count += 1

            ReFlag = 0

            print(
                "*** Screen refresh ***"
            )


        # -------------------------------------------------
        # Refresh completo periódico
        # -------------------------------------------------

        elif (
            Refresh_Count > 50
            or SelfFlag == 1
        ):

            SelfFlag = 0

            Refresh_Count = 0

            epd.init(
                epd.FULL_UPDATE
            )

            epd.displayPartBaseImage(
                epd.getbuffer(
                    image
                )
            )

            epd.init(
                epd.PART_UPDATE
            )

            print(
                "--- Full refresh ---"
            )


        # -------------------------------------------------
        # Leer touch
        # -------------------------------------------------

        gt.GT_Scan(
            GT_Dev,
            GT_Old
        )


        # -------------------------------------------------
        # Si no cambió el toque
        # -------------------------------------------------

        if (
            GT_Old.X[0] == GT_Dev.X[0]
            and
            GT_Old.Y[0] == GT_Dev.Y[0]
            and
            GT_Old.S[0] == GT_Dev.S[0]
        ):
            continue


        # -------------------------------------------------
        # Si no hay toque
        # -------------------------------------------------

        if not GT_Dev.TouchpointFlag:
            continue


        GT_Dev.TouchpointFlag = 0


        touch_x = GT_Dev.X[0]

        touch_y = GT_Dev.Y[0]


        print(
            "Touch:",
            touch_x,
            touch_y
        )


        # =================================================
        # BOTÓN NEXT
        # =================================================

        if (
            touch_x > 97
            and touch_x < 119
            and touch_y > 57
            and touch_y < 78
        ):

            print(
                "Next page"
            )


            Current_Page += 1


            # Si estamos después de la última página
            # volver a la primera
            if Current_Page >= Total_Pages:

                Current_Page = 0


            Show_Words(
                image,
                Current_Page
            )


            ReFlag = 1


        # =================================================
        # BOTÓN HOME
        #
        # Ahora simplemente vuelve a la página 0
        # =================================================

        elif (
            touch_x > 97
            and touch_x < 119
            and touch_y > 113
            and touch_y < 136
        ):

            print(
                "First page"
            )


            Current_Page = 0


            Show_Words(
                image,
                Current_Page
            )


            ReFlag = 1


        # =================================================
        # BOTÓN PREVIOUS
        # =================================================

        elif (
            touch_x > 97
            and touch_x < 119
            and touch_y > 169
            and touch_y < 190
        ):

            print(
                "Previous page"
            )


            Current_Page -= 1


            # Si estamos antes de la primera
            # ir a la última
            if Current_Page < 0:

                Current_Page = (
                    Total_Pages - 1
                )


            Show_Words(
                image,
                Current_Page
            )


            ReFlag = 1


        # =================================================
        # BOTÓN REFRESH
        # =================================================

        elif (
            touch_x > 97
            and touch_x < 119
            and touch_y > 220
            and touch_y < 242
        ):

            print(
                "Refresh"
            )


            # ---------------------------------------------
            # Volver a leer words.txt
            #
            # Esto permite modificar el archivo mientras
            # el programa está funcionando.
            # ---------------------------------------------

            Words_S = Load_Words()

            Total_Pages = Get_Total_Pages()


            # Si al eliminar palabras la página actual
            # ya no existe, volver a la primera
            if Current_Page >= Total_Pages:

                Current_Page = 0


            Show_Words(
                image,
                Current_Page
            )


            SelfFlag = 1

            ReFlag = 1


        # =================================================
        # TOCAR UNA PALABRA
        # =================================================

        elif (
            touch_x > 2
            and touch_x < 90
            and touch_y > 2
            and touch_y < 248
        ):

            selected_index = Get_Selected_Word(
                touch_x,
                touch_y,
                Current_Page
            )


            if selected_index is not None:

                selected_word = (
                    Words_S[selected_index]
                )


                print(
                    "Selected:",
                    selected_word
                )


                # Aquí después podemos hacer algo
                # según la palabra seleccionada.
                #
                # Por ejemplo:
                #
                # if selected_word == "Ejercicio":
                #     ...
                #
                # if selected_word == "Agua":
                #     ...


except IOError as error:

    logging.info(
        error
    )


except KeyboardInterrupt:

    logging.info(
        "ctrl + c"
    )

    flag_t = 0

    epd.sleep()

    time.sleep(
        2
    )

    t.join()

    epd.Dev_exit()

    sys.exit()