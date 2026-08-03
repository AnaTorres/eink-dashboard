#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
import threading

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
# Palabras del menú
# ---------------------------------------------------------

Words_S = [
    "Ejercicio",
    "Estudio",
    "Organizacion",
    "Descanso",
    "Peso",
    "Pasos",
]


# ---------------------------------------------------------
# Imágenes grandes asociadas a cada palabra
# ---------------------------------------------------------

PhotoPath_L = [
    "Photo_2_0.bmp",
    "Photo_2_1.bmp",
    "Photo_2_2.bmp",
    "Photo_2_3.bmp",
    "Photo_2_4.bmp",
    "Photo_2_5.bmp",
    "Photo_2_6.bmp",
]


# ---------------------------------------------------------
# Páginas
#
# Page 0 = lista de palabras
# Page 1 = imagen grande
# ---------------------------------------------------------

PagePath = [
    "Photo_1.bmp",
    "Photo_2.bmp",
]


# ---------------------------------------------------------
# Lectura del controlador táctil
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
# Abrir y pegar una imagen BMP
# ---------------------------------------------------------

def Read_BMP(image, filename, x, y):
    newimage = Image.open(
        os.path.join(picdir, filename)
    ).convert("1")

    image.paste(newimage, (x, y))


# ---------------------------------------------------------
# Crear una palabra vertical
# ---------------------------------------------------------

def Create_Vertical_Word(text):
    """
    Crea una palabra horizontal en una imagen de 122 x 43
    y después la rota 90 grados.

    El resultado final mide 43 x 122 píxeles.
    """

    word_image = Image.new(
        "1",
        (122, 43),
        255
    )

    word_draw = ImageDraw.Draw(word_image)

    bbox = word_draw.textbbox(
        (0, 0),
        text,
        font=font15
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (122 - text_width) // 2
    text_y = (43 - text_height) // 2

    word_draw.text(
        (text_x, text_y),
        text,
        font=font15,
        fill=0
    )

    return word_image.rotate(
        90,
        expand=True
    )


# ---------------------------------------------------------
# Mostrar palabras 
# ---------------------------------------------------------

def Show_words(image, page):
    """
    Muestra cuatro palabras por página.

    Página 0:
        Ejercicio
        Agua
        Comida
        Descanso

    Página 1:
        Comida
        Descanso
        Peso
        Pasos

    Página 2:
        Peso
        Pasos
    """

    first_index = page * 2

    draw = ImageDraw.Draw(image)

    # Limpiar solamente la zona de palabras.
    # La barra lateral de botones se conserva.
    draw.rectangle(
        (2, 2, 90, 248),
        fill=255
    )

    for position in range(4):
        word_index = first_index + position

        column = position // 2
        row = position % 2

        x = column * 45 + 2
        y = row * 124 + 2

        # Limpiar el espacio de la palabra
        draw.rectangle(
            (x, y, x + 42, y + 121),
            fill=255
        )

        if word_index >= len(Words_S):
            continue

        word_image = Create_Vertical_Word(
            Words_S[word_index]
        )

        image.paste(
            word_image,
            (x, y)
        )


# ---------------------------------------------------------
# Mostrar la página de palabras
# ---------------------------------------------------------

def Show_Words_Page(image, words_page):
    Read_BMP(
        image,
        PagePath[0],
        0,
        0
    )

    Show_words(
        image,
        words_page
    )


# ---------------------------------------------------------
# Mostrar una imagen grande
# ---------------------------------------------------------

def Show_Photo_Large(image, large):
    if large < 1 or large > 6:
        large = 1

    newimage = Image.open(
        os.path.join(
            picdir,
            PhotoPath_L[large]
        )
    ).convert("1")

    image.paste(
        newimage,
        (2, 2)
    )


# ---------------------------------------------------------
# Obtener la palabra seleccionada
# ---------------------------------------------------------

def Get_Selected_Item(touch_x, touch_y, words_page):
    """
    Convierte la posición tocada en un elemento de la lista.

    Distribución:

        superior izquierda
        inferior izquierda
        superior derecha
        inferior derecha
    """

    if touch_x < 46:
        column = 0
    else:
        column = 1

    if touch_y < 124:
        row = 0
    else:
        row = 1

    position = column * 2 + row

    item_index = words_page * 2 + position

    if item_index >= len(Words_S):
        return None

    return item_index + 1


# ---------------------------------------------------------
# Programa principal
# ---------------------------------------------------------

try:
    logging.info("epd2in13_V3 Touch Demo")

    epd = epd2in13_V3.EPD()
    gt = gt1151.GT1151()

    GT_Dev = gt1151.GT_Development()
    GT_Old = gt1151.GT_Development()

    logging.info("init and clear")

    epd.init(epd.FULL_UPDATE)
    gt.GT_Init()
    epd.Clear(0xFF)

    # Iniciar hilo táctil
    t = threading.Thread(
        target=pthread_irq
    )

    t.daemon = True
    t.start()

    # Fuentes
    font15 = ImageFont.truetype(
        os.path.join(fontdir, "Font.ttc"),
        15
    )

    font24 = ImageFont.truetype(
        os.path.join(fontdir, "Font.ttc"),
        24
    )

    # -----------------------------------------------------
    # Empezar directamente en la lista de palabras
    # -----------------------------------------------------

    Page = 0
    Photo_S = 0
    Photo_L = 1

    image = Image.open(
        os.path.join(
            picdir,
            PagePath[0]
        )
    ).convert("1")

    Show_words(
        image,
        Photo_S
    )

    epd.displayPartBaseImage(
        epd.getbuffer(image)
    )

    epd.init(epd.PART_UPDATE)

    j = 0
    ReFlag = 0
    SelfFlag = 0

    while True:

        # -------------------------------------------------
        # Actualización parcial
        # -------------------------------------------------

        if ReFlag == 1:
            epd.displayPartial_Wait(
                epd.getbuffer(image)
            )

            j += 1
            ReFlag = 0

            print("*** Screen refresh ***")

        # -------------------------------------------------
        # Actualización completa periódica
        # -------------------------------------------------

        elif j > 50 or SelfFlag == 1:
            SelfFlag = 0
            j = 0

            epd.init(epd.FULL_UPDATE)

            epd.displayPartBaseImage(
                epd.getbuffer(image)
            )

            epd.init(epd.PART_UPDATE)

            print("--- Full refresh ---")

        # -------------------------------------------------
        # Leer pantalla táctil
        # -------------------------------------------------

        gt.GT_Scan(
            GT_Dev,
            GT_Old
        )

        if (
            GT_Old.X[0] == GT_Dev.X[0]
            and GT_Old.Y[0] == GT_Dev.Y[0]
            and GT_Old.S[0] == GT_Dev.S[0]
        ):
            continue

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
        # PAGE 0: LISTA DE PALABRAS
        # =================================================

        if Page == 0 and ReFlag == 0:

            # Botón siguiente página
            if (
                touch_x > 97
                and touch_x < 119
                and touch_y > 57
                and touch_y < 78
            ):
                print("Next words page")

                Photo_S += 1

                if Photo_S > 2:
                    Photo_S = 0

                Show_Words_Page(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Botón central:
            # volver a la primera página de palabras
            elif (
                touch_x > 97
                and touch_x < 119
                and touch_y > 113
                and touch_y < 136
            ):
                print("First words page")

                Photo_S = 0

                Show_Words_Page(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Botón página anterior
            elif (
                touch_x > 97
                and touch_x < 119
                and touch_y > 169
                and touch_y < 190
            ):
                print("Previous words page")

                Photo_S -= 1

                if Photo_S < 0:
                    Photo_S = 2

                Show_Words_Page(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Botón refrescar
            elif (
                touch_x > 97
                and touch_x < 119
                and touch_y > 220
                and touch_y < 242
            ):
                print("Refresh words")

                SelfFlag = 1
                ReFlag = 1

            # Seleccionar una palabra
            elif (
                touch_x > 2
                and touch_x < 90
                and touch_y > 2
                and touch_y < 248
            ):
                selected_item = Get_Selected_Item(
                    touch_x,
                    touch_y,
                    Photo_S
                )

                if selected_item is not None:
                    print(
                        "Selected:",
                        Words_S[selected_item - 1]
                    )

                    Photo_L = selected_item
                    Page = 1

                    Read_BMP(
                        image,
                        PagePath[1],
                        0,
                        0
                    )

                    Show_Photo_Large(
                        image,
                        Photo_L
                    )

                    ReFlag = 1

        # =================================================
        # PAGE 1: IMAGEN GRANDE
        # =================================================

        elif Page == 1 and ReFlag == 0:

            # Volver a la lista de palabras actual
            if (
                touch_x > 96
                and touch_x < 117
                and touch_y > 4
                and touch_y < 25
            ):
                print("Back to words")

                Page = 0

                Show_Words_Page(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Elemento siguiente
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 57
                and touch_y < 78
            ):
                print("Next item")

                Photo_L += 1

                if Photo_L > len(Words_S):
                    Photo_L = 1

                Read_BMP(
                    image,
                    PagePath[1],
                    0,
                    0
                )

                Show_Photo_Large(
                    image,
                    Photo_L
                )

                ReFlag = 1

            # Volver a la primera página de palabras
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 113
                and touch_y < 136
            ):
                print("First words page")

                Page = 0
                Photo_S = 0

                Show_Words_Page(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Elemento anterior
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 169
                and touch_y < 190
            ):
                print("Previous item")

                Photo_L -= 1

                if Photo_L < 1:
                    Photo_L = len(Words_S)

                Read_BMP(
                    image,
                    PagePath[1],
                    0,
                    0
                )

                Show_Photo_Large(
                    image,
                    Photo_L
                )

                ReFlag = 1

            # Refrescar
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 220
                and touch_y < 242
            ):
                print("Refresh item")

                SelfFlag = 1
                ReFlag = 1


except IOError as error:
    logging.info(error)


except KeyboardInterrupt:
    logging.info("ctrl + c")

    flag_t = 0

    epd.sleep()

    time.sleep(2)

    t.join()

    epd.Dev_exit()

    sys.exit()