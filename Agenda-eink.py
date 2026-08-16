#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import json
import math
import logging
import threading

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# =========================================================
# RUTAS
# =========================================================

scriptdir = os.path.dirname(
    os.path.realpath(__file__)
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


# =========================================================
# LIBRERÍAS WAVESHARE
# =========================================================

from TP_lib import gt1151
from TP_lib import epd2in13_V3


logging.basicConfig(level=logging.DEBUG)

flag_t = 1


# =========================================================
# ARCHIVOS
# =========================================================

ACTIVITIES_FILE = os.path.join(
    scriptdir,
    "activities.json"
)

RECORDS_FILE = os.path.join(
    scriptdir,
    "time_records.json"
)


# =========================================================
# PÁGINAS
# =========================================================

PAGE_ACTIVITY_LIST = 0
PAGE_DURATION = 1


# =========================================================
# CARGAR ACTIVIDADES
# =========================================================

def Load_Activities():

    try:
        with open(
            ACTIVITIES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            print("ERROR: activities.json debe contener una lista")
            return []

        activities = []

        for item in data:

            if not isinstance(item, dict):
                continue

            if "name" not in item:
                continue

            name = str(
                item["name"]
            ).strip()

            if not name:
                continue

            activities.append(item)

        return activities

    except FileNotFoundError:

        print(
            "ERROR: no se encontró:",
            ACTIVITIES_FILE
        )

        return []

    except json.JSONDecodeError as error:

        print(
            "ERROR JSON:",
            error
        )

        return []


# =========================================================
# GUARDAR REGISTRO DE TIEMPO
# =========================================================

def Save_Time_Record(activity, minutes):

    now = datetime.now()

    record = {
        "activity_id": activity.get("id"),
        "activity_name": activity.get("name"),
        "minutes": minutes,
        "date": now.strftime("%Y-%m-%d"),
        "created_at": now.isoformat(
            timespec="seconds"
        )
    }

    try:

        with open(
            RECORDS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            records = json.load(file)

        if not isinstance(records, list):
            records = []

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        records = []


    records.append(
        record
    )


    with open(
        RECORDS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=2
        )


    print("")
    print("-----------------------")
    print("REGISTRO GUARDADO")
    print("Actividad:", activity.get("name"))
    print("Minutos:", minutes)
    print("-----------------------")
    print("")


# =========================================================
# TOUCH THREAD
# =========================================================

def pthread_irq():

    print(
        "pthread running"
    )

    while flag_t == 1:

        if gt.digital_read(
            gt.INT
        ) == 0:

            GT_Dev.Touch = 1

        else:

            GT_Dev.Touch = 0

        time.sleep(
            0.01
        )

    print(
        "thread exit"
    )


# =========================================================
# CREAR PALABRA VERTICAL
# =========================================================

def Create_Vertical_Word(text):

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
        (
            text_x,
            text_y
        ),
        text,
        font=font15,
        fill=0
    )


    return word_image.rotate(
        90,
        expand=True
    )


# =========================================================
# TOTAL DE PÁGINAS
# =========================================================

def Get_Total_Pages():

    if len(Activities) == 0:
        return 1

    return math.ceil(
        len(Activities) / 4
    )


# =========================================================
# MOSTRAR LISTA DE ACTIVIDADES
# =========================================================

def Show_Activities(image, page):

    # Limpiar pantalla
    draw = ImageDraw.Draw(
        image
    )

    draw.rectangle(
        (0, 0, 121, 249),
        fill=255
    )


    first_index = (
        page * 4
    )


    for position in range(4):

        activity_index = (
            first_index
            + position
        )


        if activity_index >= len(Activities):
            continue


        activity = (
            Activities[
                activity_index
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
            Create_Vertical_Word(
                text
            )
        )


        image.paste(
            word_image,
            (x, y)
        )


    # -----------------------------------------------------
    # Dibujar zona lateral
    # -----------------------------------------------------

    draw = ImageDraw.Draw(
        image
    )


    # NEXT
    draw.text(
        (100, 60),
        ">",
        font=font15,
        fill=0
    )


    # HOME / FIRST PAGE
    draw.text(
        (100, 115),
        "H",
        font=font15,
        fill=0
    )


    # PREVIOUS
    draw.text(
        (100, 170),
        "<",
        font=font15,
        fill=0
    )


    # REFRESH
    draw.text(
        (100, 220),
        "R",
        font=font15,
        fill=0
    )


# =========================================================
# OBTENER ACTIVIDAD TOCADA
# =========================================================

def Get_Selected_Activity(
    touch_x,
    touch_y,
    page
):

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


    activity_index = (
        page * 4
        + position
    )


    if activity_index >= len(
        Activities
    ):
        return None


    return Activities[
        activity_index
    ]


# =========================================================
# MOSTRAR PANTALLA DE DURACIÓN
# =========================================================

def Show_Duration_Screen(
    image,
    activity,
    minutes
):

    draw = ImageDraw.Draw(
        image
    )


    # Limpiar pantalla
    draw.rectangle(
        (0, 0, 121, 249),
        fill=255
    )


    # -----------------------------------------------------
    # Crear nombre vertical
    # -----------------------------------------------------

    activity_image = Image.new(
        "1",
        (200, 30),
        255
    )

    activity_draw = ImageDraw.Draw(
        activity_image
    )


    name = str(
        activity["name"]
    )


    bbox = activity_draw.textbbox(
        (0, 0),
        name,
        font=font15
    )


    width = (
        bbox[2] - bbox[0]
    )


    activity_draw.text(
        (
            (200 - width) // 2,
            5
        ),
        name,
        font=font15,
        fill=0
    )


    activity_image = (
        activity_image.rotate(
            90,
            expand=True
        )
    )


    image.paste(
        activity_image,
        (5, 25)
    )


    # -----------------------------------------------------
    # Minutos
    # -----------------------------------------------------

    minutes_text = (
        str(minutes)
        + " min"
    )


    time_image = Image.new(
        "1",
        (100, 35),
        255
    )

    time_draw = ImageDraw.Draw(
        time_image
    )


    bbox = time_draw.textbbox(
        (0, 0),
        minutes_text,
        font=font24
    )


    width = (
        bbox[2] - bbox[0]
    )


    time_draw.text(
        (
            (100 - width) // 2,
            3
        ),
        minutes_text,
        font=font24,
        fill=0
    )


    time_image = (
        time_image.rotate(
            90,
            expand=True
        )
    )


    image.paste(
        time_image,
        (50, 75)
    )


    # -----------------------------------------------------
    # Botones laterales
    #
    # Y 57    -> +15
    # Y 113   -> GUARDAR
    # Y 169   -> -15
    # Y 220   -> VOLVER
    # -----------------------------------------------------

    draw.text(
        (100, 60),
        "+",
        font=font24,
        fill=0
    )

    draw.text(
        (100, 115),
        "S",
        font=font15,
        fill=0
    )

    draw.text(
        (100, 170),
        "-",
        font=font24,
        fill=0
    )

    draw.text(
        (100, 220),
        "B",
        font=font15,
        fill=0
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

try:

    logging.info(
        "Activity Time Tracker"
    )


    # -----------------------------------------------------
    # Inicializar pantalla
    # -----------------------------------------------------

    epd = (
        epd2in13_V3.EPD()
    )


    gt = (
        gt1151.GT1151()
    )


    GT_Dev = (
        gt1151.GT_Development()
    )


    GT_Old = (
        gt1151.GT_Development()
    )


    epd.init(
        epd.FULL_UPDATE
    )


    gt.GT_Init()


    epd.Clear(
        0xFF
    )


    # -----------------------------------------------------
    # Thread touch
    # -----------------------------------------------------

    t = threading.Thread(
        target=pthread_irq
    )


    t.daemon = True

    t.start()


    # -----------------------------------------------------
    # Fuentes
    # -----------------------------------------------------

    font15 = (
        ImageFont.truetype(
            os.path.join(
                fontdir,
                "Font.ttc"
            ),
            15
        )
    )


    font24 = (
        ImageFont.truetype(
            os.path.join(
                fontdir,
                "Font.ttc"
            ),
            24
        )
    )


    # -----------------------------------------------------
    # Cargar actividades
    # -----------------------------------------------------

    Activities = (
        Load_Activities()
    )


    Total_Pages = (
        Get_Total_Pages()
    )


    print(
        "Actividades:",
        len(Activities)
    )


    print(
        "Páginas:",
        Total_Pages
    )


    # -----------------------------------------------------
    # Estado
    # -----------------------------------------------------

    Current_Page = 0

    Current_Screen = (
        PAGE_ACTIVITY_LIST
    )

    Selected_Activity = None

    Selected_Minutes = 30


    # -----------------------------------------------------
    # Imagen base
    # -----------------------------------------------------

    image = Image.new(
        "1",
        (122, 250),
        255
    )


    Show_Activities(
        image,
        Current_Page
    )


    epd.displayPartBaseImage(
        epd.getbuffer(
            image
        )
    )


    epd.init(
        epd.PART_UPDATE
    )


    Refresh_Count = 0

    ReFlag = 0

    SelfFlag = 0


    # =====================================================
    # LOOP
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


        # -------------------------------------------------
        # Refresh completo
        # -------------------------------------------------

        elif (
            Refresh_Count > 40
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


        # -------------------------------------------------
        # Leer Touch
        # -------------------------------------------------

        gt.GT_Scan(
            GT_Dev,
            GT_Old
        )


        if (
            GT_Old.X[0]
            == GT_Dev.X[0]

            and

            GT_Old.Y[0]
            == GT_Dev.Y[0]

            and

            GT_Old.S[0]
            == GT_Dev.S[0]
        ):

            continue


        if not GT_Dev.TouchpointFlag:

            continue


        GT_Dev.TouchpointFlag = 0


        touch_x = (
            GT_Dev.X[0]
        )

        touch_y = (
            GT_Dev.Y[0]
        )


        print(
            "Touch:",
            touch_x,
            touch_y
        )


        # =================================================
        # LISTA DE ACTIVIDADES
        # =================================================

        if (
            Current_Screen
            == PAGE_ACTIVITY_LIST
        ):


            # ---------------------------------------------
            # NEXT
            # ---------------------------------------------

            if (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 57
                and touch_y < 78
            ):

                Current_Page += 1


                if (
                    Current_Page
                    >= Total_Pages
                ):

                    Current_Page = 0


                Show_Activities(
                    image,
                    Current_Page
                )


                ReFlag = 1


            # ---------------------------------------------
            # PRIMERA PÁGINA
            # ---------------------------------------------

            elif (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 113
                and touch_y < 136
            ):

                Current_Page = 0


                Show_Activities(
                    image,
                    Current_Page
                )


                ReFlag = 1


            # ---------------------------------------------
            # PREVIOUS
            # ---------------------------------------------

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


                Show_Activities(
                    image,
                    Current_Page
                )


                ReFlag = 1


            # ---------------------------------------------
            # REFRESH ACTIVIDADES
            # ---------------------------------------------

            elif (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 220
                and touch_y < 242
            ):

                Activities = (
                    Load_Activities()
                )


                Total_Pages = (
                    Get_Total_Pages()
                )


                if (
                    Current_Page
                    >= Total_Pages
                ):

                    Current_Page = 0


                Show_Activities(
                    image,
                    Current_Page
                )


                SelfFlag = 1

                ReFlag = 1


            # ---------------------------------------------
            # SELECCIONAR ACTIVIDAD
            # ---------------------------------------------

            elif (
                touch_x > 2
                and touch_x < 90

                and

                touch_y > 2
                and touch_y < 248
            ):

                Selected_Activity = (
                    Get_Selected_Activity(
                        touch_x,
                        touch_y,
                        Current_Page
                    )
                )


                if (
                    Selected_Activity
                    is not None
                ):

                    print(
                        "Seleccionada:",
                        Selected_Activity[
                            "name"
                        ]
                    )


                    Selected_Minutes = 30


                    Current_Screen = (
                        PAGE_DURATION
                    )


                    Show_Duration_Screen(
                        image,
                        Selected_Activity,
                        Selected_Minutes
                    )


                    ReFlag = 1


        # =================================================
        # SELECCIÓN DE DURACIÓN
        # =================================================

        elif (
            Current_Screen
            == PAGE_DURATION
        ):


            # ---------------------------------------------
            # +15 MIN
            # ---------------------------------------------

            if (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 57
                and touch_y < 78
            ):

                Selected_Minutes += 15


                Show_Duration_Screen(
                    image,
                    Selected_Activity,
                    Selected_Minutes
                )


                ReFlag = 1


            # ---------------------------------------------
            # GUARDAR
            # ---------------------------------------------

            elif (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 113
                and touch_y < 136
            ):

                Save_Time_Record(
                    Selected_Activity,
                    Selected_Minutes
                )


                Current_Screen = (
                    PAGE_ACTIVITY_LIST
                )


                Selected_Activity = None


                Show_Activities(
                    image,
                    Current_Page
                )


                ReFlag = 1


            # ---------------------------------------------
            # -15 MIN
            # ---------------------------------------------

            elif (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 169
                and touch_y < 190
            ):

                Selected_Minutes -= 15


                if Selected_Minutes < 15:

                    Selected_Minutes = 15


                Show_Duration_Screen(
                    image,
                    Selected_Activity,
                    Selected_Minutes
                )


                ReFlag = 1


            # ---------------------------------------------
            # VOLVER SIN GUARDAR
            # ---------------------------------------------

            elif (
                touch_x > 97
                and touch_x < 119

                and

                touch_y > 220
                and touch_y < 242
            ):

                Current_Screen = (
                    PAGE_ACTIVITY_LIST
                )


                Selected_Activity = None


                Show_Activities(
                    image,
                    Current_Page
                )


                ReFlag = 1


# =========================================================
# ERRORES
# =========================================================

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