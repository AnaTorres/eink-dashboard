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
# Palabras que aparecerán en el menú
# ---------------------------------------------------------

Words_S = [
    "Ejercicio",
    "Agua",
    "Comida",
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
# Páginas del programa
#
# Page 0 = menú principal
# Page 1 = menú de palabras
# Page 2 = imagen grande
# ---------------------------------------------------------

PagePath = [
    "Menu.bmp",
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
# Abrir una imagen BMP
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
    Crea el texto horizontalmente sobre una imagen de 122 x 43
    y después lo rota 90 grados.

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

    # Rotación vertical
    word_image = word_image.rotate(
        90,
        expand=True
    )

    return word_image


# ---------------------------------------------------------
# Mostrar cuatro palabras pequeñas
# ---------------------------------------------------------

def Show_Photo_Small(image, page):
    """
    Muestra cuatro palabras por página.

    Página 0:
        Ejercicio, Agua, Comida, Descanso

    Página 1:
        Comida, Descanso, Peso, Pasos

    Página 2:
        Peso, Pasos
    """

    first_index = page * 2

    # Limpiar el espacio donde aparecen las palabras.
    # No se limpia la barra lateral de botones.
    draw = ImageDraw.Draw(image)

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

        # Dibujar el fondo de cada espacio
        draw.rectangle(
            (x, y, x + 42, y + 121),
            fill=255
        )

        if word_index >= len(Words_S):
            continue

        text = Words_S[word_index]

        word_image = Create_Vertical_Word(text)

        image.paste(
            word_image,
            (x, y)
        )


# ---------------------------------------------------------
# Mostrar una imagen grande
# ---------------------------------------------------------

def Show_Photo_Large(image, large):
    """
    Muestra la imagen grande correspondiente a la palabra
    seleccionada.
    """

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
# Convertir coordenadas táctiles en número de elemento
# ---------------------------------------------------------

def Get_Selected_Item(touch_x, touch_y, page):
    """
    Devuelve un número entre 1 y 6.

    Distribución del menú:

        superior izquierda
        inferior izquierda
        superior derecha
        inferior derecha
    """

    column = 0 if touch_x < 46 else 1
    row = 0 if touch_y < 124 else 1

    position = column * 2 + row

    item_index = page * 2 + position

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

    # Cargar menú inicial
    image = Image.open(
        os.path.join(picdir, "Menu.bmp")
    ).convert("1")

    epd.displayPartBaseImage(
        epd.getbuffer(image)
    )

    epd.init(epd.PART_UPDATE)

    # Variables
    i = 0
    j = 0

    ReFlag = 0
    SelfFlag = 0

    Page = 0
    Photo_L = 1
    Photo_S = 0

    while True:

        # -------------------------------------------------
        # Actualizar la pantalla después de un cambio
        # -------------------------------------------------

        if ReFlag == 1:
            epd.displayPartial_Wait(
                epd.getbuffer(image)
            )

            i = 0
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
        # Leer la pantalla táctil
        # -------------------------------------------------

        gt.GT_Scan(
            GT_Dev,
            GT_Old
        )

        # Si las coordenadas no cambiaron, no hacer nada
        if (
            GT_Old.X[0] == GT_Dev.X[0]
            and GT_Old.Y[0] == GT_Dev.Y[0]
            and GT_Old.S[0] == GT_Dev.S[0]
        ):
            continue

        if not GT_Dev.TouchpointFlag:
            continue

        GT_Dev.TouchpointFlag = 0
        i += 1

        touch_x = GT_Dev.X[0]
        touch_y = GT_Dev.Y[0]

        print(
            "Touch:",
            touch_x,
            touch_y
        )

        # =================================================
        # PAGE 0: MENÚ PRINCIPAL
        # =================================================

        if Page == 0 and ReFlag == 0:

            # Botón superior del menú
            if (
                touch_x > 29
                and touch_x < 92
                and touch_y > 56
                and touch_y < 95
            ):
                print("Words menu")

                Page = 1
                Photo_S = 0

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                Show_Photo_Small(
                    image,
                    Photo_S
                )

                ReFlag = 1

        # =================================================
        # PAGE 1: MENÚ DE PALABRAS
        # =================================================

        elif Page == 1 and ReFlag == 0:

            # Botón Home
            if (
                touch_x > 97
                and touch_x < 119
                and touch_y > 113
                and touch_y < 136
            ):
                print("Home")

                Page = 0

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                ReFlag = 1

            # Botón siguiente página
            elif (
                touch_x > 97
                and touch_x < 119
                and touch_y > 57
                and touch_y < 78
            ):
                print("Next page")

                Photo_S += 1

                if Photo_S > 2:
                    Photo_S = 0

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                Show_Photo_Small(
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
                print("Previous page")

                if Photo_S > 0:
                    Photo_S -= 1
                else:
                    Photo_S = 2

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                Show_Photo_Small(
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
                print("Refresh")

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
                    Page = 2

                    Read_BMP(
                        image,
                        PagePath[Page],
                        0,
                        0
                    )

                    Show_Photo_Large(
                        image,
                        Photo_L
                    )

                    ReFlag = 1

        # =================================================
        # PAGE 2: IMAGEN GRANDE
        # =================================================

        elif Page == 2 and ReFlag == 0:

            # Volver al menú de palabras
            if (
                touch_x > 96
                and touch_x < 117
                and touch_y > 4
                and touch_y < 25
            ):
                print("Words menu")

                Page = 1

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                Show_Photo_Small(
                    image,
                    Photo_S
                )

                ReFlag = 1

            # Imagen siguiente
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 57
                and touch_y < 78
            ):
                print("Next item")

                Photo_L += 1

                if Photo_L > 6:
                    Photo_L = 1

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                Show_Photo_Large(
                    image,
                    Photo_L
                )

                ReFlag = 1

            # Volver al inicio
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 113
                and touch_y < 136
            ):
                print("Home")

                Page = 0

                Read_BMP(
                    image,
                    PagePath[Page],
                    0,
                    0
                )

                ReFlag = 1

            # Imagen anterior
            elif (
                touch_x > 96
                and touch_x < 117
                and touch_y > 169
                and touch_y < 190
            ):
                print("Previous item")

                Photo_L -= 1

                if Photo_L < 1:
                    Photo_L = 6

                Read_BMP(
                    image,
                    PagePath[Page],
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
