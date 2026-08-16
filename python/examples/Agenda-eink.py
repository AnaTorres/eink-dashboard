#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import logging
import threading
import math
import json

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
# Archivo JSON
# ---------------------------------------------------------

ITEMS_FILE = os.path.join(
    picdir,
    "words.json"
)


# ---------------------------------------------------------
# Cargar elementos desde JSON
# ---------------------------------------------------------

def Load_Items():
    """
    Lee los elementos desde words.json.

    Formato esperado:

    [
        {
            "id": 1,
            "name": "Ejercicio"
        },
        {
            "id": 2,
            "name": "Agua"
        }
    ]
    """

    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Validar que el JSON contenga una lista
        if not isinstance(data, list):
            print("ERROR: words.json debe contener una lista")
            return []

        items = []

        for item in data:

            # Ignorar valores que no sean objetos
            if not isinstance(item, dict):
                continue

            # Ignorar elementos sin name
            if "name" not in item:
                continue

            name = str(item["name"]).strip()

            if not name:
                continue

            items.append(item)

        return items

    except FileNotFoundError:
        print("ERROR: No se encontró el archivo:")
        print(ITEMS_FILE)

        return []

    except json.JSONDecodeError as error:
        print("ERROR: El archivo JSON no es válido")
        print(error)

        return []


# ---------------------------------------------------------
# Hilo para detectar touch
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
# Leer imagen BMP
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
# Crear texto vertical
# ---------------------------------------------------------

def Create_Vertical_Word(text):
    """
    Crea una palabra en una imagen de 122 x 43
    y después la rota 90 grados.

    Resultado final:
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
# Calcular total de páginas
# ---------------------------------------------------------

def Get_Total_Pages():
    """
    Cada página muestra cuatro elementos.
    """

    if len(Items) == 0:
        return 1

    return math.ceil(
        len(Items) / 4
    )


# ---------------------------------------------------------
# Mostrar una página de palabras
# ---------------------------------------------------------

def Show_Items(image, page):
    """
    Muestra máximo cuatro elementos por página.

    Ejemplo:

    Página 0:
        Items 0 - 3

    Página 1:
        Items 4 - 7

    Página 2:
        Items 8 - 11
    """

    # -----------------------------------------------------
    # Cargar fondo
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


    # -----------------------------------------------------
    # Primer elemento de esta página
    # -----------------------------------------------------

    first_index = (
        page * 4
    )


    # -----------------------------------------------------
    # Máximo cuatro elementos
    # -----------------------------------------------------

    for position in range(4):

        item_index = (
            first_index
            + position
        )


        if item_index >= len(Items):
            continue


        # -------------------------------------------------
        # Obtener nombre
        # -------------------------------------------------

        text = str(
            Items[item_index]["name"]
        )


        # -------------------------------------------------
        # Calcular posición en pantalla
        # -------------------------------------------------

        column = position // 2

        row = position % 2


        x = (
            column * 45
            + 2
        )

        y = (
            row * 124
            + 2
        )


        # -------------------------------------------------
        # Crear palabra
        # -------------------------------------------------

        word_image = Create_Vertical_Word(
            text
        )


        # -------------------------------------------------
        # Pegar palabra
        # -------------------------------------------------

        image.paste(
            word_image,
            (x, y)
        )


# ---------------------------------------------------------
# Detectar qué elemento se tocó
# ---------------------------------------------------------

def Get_Selected_Item(
    touch_x,
    touch_y,
    page
):

    """
    Convierte las coordenadas táctiles
    en el índice correspondiente de Items.
    """

    # -----------------------------------------------------
    # Columna
    # -----------------------------------------------------

    if touch_x < 46:
        column = 0
    else:
        column = 1


    # -----------------------------------------------------
    # Fila
    # -----------------------------------------------------

    if touch_y < 124:
        row = 0
    else:
        row = 1


    # -----------------------------------------------------
    # Posición dentro de la página
    # -----------------------------------------------------

    position = (
        column * 2
        + row
    )


    # -----------------------------------------------------
    # Índice dentro de Items
    # -----------------------------------------------------

    item_index = (
        page * 4
        + position
    )


    if item_index >= len(Items):
        return None


    return item_index


# ---------------------------------------------------------
# Mostrar información del elemento seleccionado
# ---------------------------------------------------------

def On_Item_Selected(item):
    """
    Esta función se ejecuta cuando el usuario
    toca una palabra.

    Aquí podrás añadir después:
    - guardar algo en DB
    - cambiar de pantalla
    - ejecutar una acción
    - llamar a una API
    """

    print("------------------------")

    print(
        "ID:",
        item.get("id")
    )

    print(
        "Nombre:",
        item.get("name")
    )

    print("------------------------")


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

try:

    logging.info(
        "epd2in13_V3 JSON Menu"
    )


    # -----------------------------------------------------
    # Inicializar pantalla
    # -----------------------------------------------------

    epd = epd2in13_V3.EPD()


    # -----------------------------------------------------
    # Inicializar touch
    # -----------------------------------------------------

    gt = gt1151.GT1151()

    GT_Dev = gt1151.GT_Development()

    GT_Old = gt1151.GT_Development()


    # -----------------------------------------------------
    # Inicialización completa
    # -----------------------------------------------------

    epd.init(
        epd.FULL_UPDATE
    )

    gt.GT_Init()

    epd.Clear(
        0xFF
    )


    # -----------------------------------------------------
    # Iniciar thread táctil
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
    # Cargar Items desde JSON
    # -----------------------------------------------------

    Items = Load_Items()


    print("")
    print("------------------------")
    print("Elementos cargados")
    print("------------------------")


    for item in Items:

        print(
            item.get("id"),
            "-",
            item.get("name")
        )


    print("------------------------")
    print("")


    # -----------------------------------------------------
    # Calcular páginas
    # -----------------------------------------------------

    Total_Pages = Get_Total_Pages()


    print(
        "Total elementos:",
        len(Items)
    )

    print(
        "Total páginas:",
        Total_Pages
    )


    # -----------------------------------------------------
    # Página actual
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


    # -----------------------------------------------------
    # Mostrar primera página
    # -----------------------------------------------------

    Show_Items(
        image,
        Current_Page
    )


    # -----------------------------------------------------
    # Mostrar en pantalla
    # -----------------------------------------------------

    epd.displayPartBaseImage(
        epd.getbuffer(
            image
        )
    )


    epd.init(
        epd.PART_UPDATE
    )


    # -----------------------------------------------------
    # Variables de refresh
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
        # Refresh completo
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
        # Ignorar si no cambió
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
        # Si no existe touch
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
            and
            touch_y > 57
            and touch_y < 78
        ):

            Current_Page += 1


            if Current_Page >= Total_Pages:

                Current_Page = 0


            print(
                "Next page:",
                Current_Page + 1,
                "/",
                Total_Pages
            )


            Show_Items(
                image,
                Current_Page
            )


            ReFlag = 1


        # =================================================
        # BOTÓN HOME
        #
        # Vuelve a la primera página
        # =================================================

        elif (
            touch_x > 97
            and touch_x < 119
            and
            touch_y > 113
            and touch_y < 136
        ):

            Current_Page = 0


            print(
                "First page"
            )


            Show_Items(
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
            and
            touch_y > 169
            and touch_y < 190
        ):

            Current_Page -= 1


            if Current_Page < 0:

                Current_Page = (
                    Total_Pages - 1
                )


            print(
                "Previous page:",
                Current_Page + 1,
                "/",
                Total_Pages
            )


            Show_Items(
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
            and
            touch_y > 220
            and touch_y < 242
        ):

            print(
                "Reload JSON"
            )


            # ---------------------------------------------
            # Volver a leer words.json
            # ---------------------------------------------

            Items = Load_Items()


            # ---------------------------------------------
            # Recalcular páginas
            # ---------------------------------------------

            Total_Pages = Get_Total_Pages()


            print(
                "Total elementos:",
                len(Items)
            )

            print(
                "Total páginas:",
                Total_Pages
            )


            # ---------------------------------------------
            # Si la página actual ya no existe
            # ---------------------------------------------

            if Current_Page >= Total_Pages:

                Current_Page = 0


            # ---------------------------------------------
            # Mostrar nuevos datos
            # ---------------------------------------------

            Show_Items(
                image,
                Current_Page
            )


            SelfFlag = 1

            ReFlag = 1


        # =================================================
        # SELECCIONAR PALABRA
        # =================================================

        elif (
            touch_x > 2
            and touch_x < 90
            and
            touch_y > 2
            and touch_y < 248
        ):

            selected_index = Get_Selected_Item(
                touch_x,
                touch_y,
                Current_Page
            )


            if selected_index is not None:

                selected_item = (
                    Items[selected_index]
                )


                On_Item_Selected(
                    selected_item
                )


# =========================================================
# ERROR DE ARCHIVO
# =========================================================

except IOError as error:

    logging.info(
        error
    )


# =========================================================
# CTRL + C
# =========================================================

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