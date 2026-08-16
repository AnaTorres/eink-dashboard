#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import math
import logging
import threading


# =========================================================
# LIBRERÍA WAVESHARE
# =========================================================

libdir = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__)
        )
    ),
    "lib"
)

if os.path.exists(
    libdir
):
    sys.path.append(
        libdir
    )


from TP_lib import gt1151
from TP_lib import epd2in13_V3


# =========================================================
# MÓDULOS PROPIOS
# =========================================================

from config import (
    ITEMS_PER_PAGE,
    DEFAULT_MINUTES,
    MINUTES_STEP,
    MIN_MINUTES,
    PAGE_ACTIVITY_LIST,
    PAGE_DURATION
)

from storage import (
    load_activities,
    save_time_record
)

from display import (
    create_blank_image,
    show_activities,
    show_duration_screen
)

from touch import (
    is_next_button,
    is_home_button,
    is_previous_button,
    is_refresh_button,
    is_activity_area,
    get_selected_activity
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

logging.basicConfig(
    level=logging.DEBUG
)


flag_t = 1


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
# TOTAL PÁGINAS
# =========================================================

def get_total_pages(
    activities
):

    if len(
        activities
    ) == 0:

        return 1

    return math.ceil(
        len(
            activities
        )
        / ITEMS_PER_PAGE
    )


# =========================================================
# MAIN
# =========================================================

try:

    logging.info(
        "Activity Tracker"
    )


    # -----------------------------------------------------
    # Waveshare
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


    # -----------------------------------------------------
    # Inicialización
    # -----------------------------------------------------

    epd.init(
        epd.FULL_UPDATE
    )

    gt.GT_Init()

    epd.Clear(
        0xFF
    )


    # -----------------------------------------------------
    # Touch thread
    # -----------------------------------------------------

    t = threading.Thread(
        target=pthread_irq
    )

    t.daemon = True

    t.start()


    # -----------------------------------------------------
    # Datos
    # -----------------------------------------------------

    activities = (
        load_activities()
    )

    total_pages = (
        get_total_pages(
            activities
        )
    )


    print(
        "Actividades:",
        len(
            activities
        )
    )

    print(
        "Páginas:",
        total_pages
    )


    # -----------------------------------------------------
    # Estado aplicación
    # -----------------------------------------------------

    current_page = 0

    current_screen = (
        PAGE_ACTIVITY_LIST
    )

    selected_activity = None

    selected_minutes = (
        DEFAULT_MINUTES
    )


    # -----------------------------------------------------
    # Imagen inicial
    # -----------------------------------------------------

    image = (
        create_blank_image()
    )

    show_activities(
        image,
        activities,
        current_page
    )


    epd.displayPartBaseImage(
        epd.getbuffer(
            image
        )
    )

    epd.init(
        epd.PART_UPDATE
    )


    refresh_count = 0

    refresh_required = False

    full_refresh_required = False


    # =====================================================
    # LOOP PRINCIPAL
    # =====================================================

    while True:


        # -------------------------------------------------
        # Refresh parcial
        # -------------------------------------------------

        if refresh_required:

            epd.displayPartial_Wait(
                epd.getbuffer(
                    image
                )
            )

            refresh_count += 1

            refresh_required = False


        # -------------------------------------------------
        # Refresh completo
        # -------------------------------------------------

        elif (
            refresh_count > 40
            or
            full_refresh_required
        ):

            refresh_count = 0

            full_refresh_required = False


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
        # Leer touch
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


        if not (
            GT_Dev.TouchpointFlag
        ):

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
            current_screen
            == PAGE_ACTIVITY_LIST
        ):


            # ---------------------------------------------
            # NEXT
            # ---------------------------------------------

            if is_next_button(
                touch_x,
                touch_y
            ):

                current_page += 1


                if (
                    current_page
                    >= total_pages
                ):

                    current_page = 0


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


            # ---------------------------------------------
            # HOME
            # ---------------------------------------------

            elif is_home_button(
                touch_x,
                touch_y
            ):

                current_page = 0


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


            # ---------------------------------------------
            # PREVIOUS
            # ---------------------------------------------

            elif is_previous_button(
                touch_x,
                touch_y
            ):

                current_page -= 1


                if (
                    current_page < 0
                ):

                    current_page = (
                        total_pages
                        - 1
                    )


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


            # ---------------------------------------------
            # RELOAD ACTIVITIES
            # ---------------------------------------------

            elif is_refresh_button(
                touch_x,
                touch_y
            ):

                print(
                    "Reload activities"
                )


                activities = (
                    load_activities()
                )


                total_pages = (
                    get_total_pages(
                        activities
                    )
                )


                if (
                    current_page
                    >= total_pages
                ):

                    current_page = 0


                show_activities(
                    image,
                    activities,
                    current_page
                )


                full_refresh_required = True

                refresh_required = True


            # ---------------------------------------------
            # ACTIVIDAD
            # ---------------------------------------------

            elif is_activity_area(
                touch_x,
                touch_y
            ):

                selected_activity = (
                    get_selected_activity(
                        touch_x,
                        touch_y,
                        current_page,
                        activities
                    )
                )


                if (
                    selected_activity
                    is not None
                ):

                    print(
                        "Actividad:",
                        selected_activity[
                            "name"
                        ]
                    )


                    selected_minutes = (
                        DEFAULT_MINUTES
                    )


                    current_screen = (
                        PAGE_DURATION
                    )


                    show_duration_screen(
                        image,
                        selected_activity,
                        selected_minutes
                    )


                    refresh_required = True


        # =================================================
        # DURACIÓN
        # =================================================

        elif (
            current_screen
            == PAGE_DURATION
        ):


            # ---------------------------------------------
            # + MINUTOS
            # ---------------------------------------------

            if is_next_button(
                touch_x,
                touch_y
            ):

                selected_minutes += (
                    MINUTES_STEP
                )


                show_duration_screen(
                    image,
                    selected_activity,
                    selected_minutes
                )


                refresh_required = True


            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            elif is_home_button(
                touch_x,
                touch_y
            ):

                save_time_record(
                    selected_activity,
                    selected_minutes
                )


                current_screen = (
                    PAGE_ACTIVITY_LIST
                )


                selected_activity = None


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


            # ---------------------------------------------
            # - MINUTOS
            # ---------------------------------------------

            elif is_previous_button(
                touch_x,
                touch_y
            ):

                selected_minutes -= (
                    MINUTES_STEP
                )


                if (
                    selected_minutes
                    < MIN_MINUTES
                ):

                    selected_minutes = (
                        MIN_MINUTES
                    )


                show_duration_screen(
                    image,
                    selected_activity,
                    selected_minutes
                )


                refresh_required = True


            # ---------------------------------------------
            # BACK
            # ---------------------------------------------

            elif is_refresh_button(
                touch_x,
                touch_y
            ):

                current_screen = (
                    PAGE_ACTIVITY_LIST
                )


                selected_activity = None


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


# =========================================================
# ERROR
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