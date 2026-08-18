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
        os.path.realpath(__file__)
    ),
    "lib"
)

if os.path.exists(libdir):
    sys.path.append(libdir)


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
    save_time_record,
    get_activity_progress
)

from display import (
    create_blank_image,
    show_activities,
    show_duration_screen,
    show_saved_screen
)

from touch import (
    is_next_button,
    is_save_button,
    is_previous_button,
    is_bottom_button,
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
# THREAD TOUCH
# =========================================================

def pthread_irq():
    global flag_t

    print("pthread running")

    while flag_t == 1:

        if gt.digital_read(gt.INT) == 0:
            GT_Dev.Touch = 1
        else:
            GT_Dev.Touch = 0

        time.sleep(0.01)

    print("thread exit")


# =========================================================
# TOTAL DE PÁGINAS
# =========================================================

def get_total_pages(activities):

    if len(activities) == 0:
        return 1

    return math.ceil(
        len(activities)
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
    # Inicializar Waveshare
    # -----------------------------------------------------

    epd = epd2in13_V3.EPD()

    gt = gt1151.GT1151()

    GT_Dev = gt1151.GT_Development()

    GT_Old = gt1151.GT_Development()


    # -----------------------------------------------------
    # Inicialización pantalla + touch
    # -----------------------------------------------------

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
    # Cargar actividades desde SQLite
    # -----------------------------------------------------

    activities = load_activities()


    total_pages = get_total_pages(
        activities
    )


    print(
        "Actividades:",
        len(activities)
    )

    print(
        "Páginas:",
        total_pages
    )


    # -----------------------------------------------------
    # Estado de la aplicación
    # -----------------------------------------------------

    current_page = 0

    current_screen = (
        PAGE_ACTIVITY_LIST
    )

    selected_activity = None

    selected_minutes = (
        DEFAULT_MINUTES
    )

    selected_progress = None


    # -----------------------------------------------------
    # Crear imagen inicial
    # -----------------------------------------------------

    image = create_blank_image()


    show_activities(
        image,
        activities,
        current_page
    )


    # -----------------------------------------------------
    # Mostrar primera pantalla
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
    # Control de refresh
    # -----------------------------------------------------

    refresh_count = 0

    refresh_required = False

    full_refresh_required = False


    # =====================================================
    # LOOP PRINCIPAL
    # =====================================================

    while True:


        # -------------------------------------------------
        # REFRESH PARCIAL
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
        # REFRESH COMPLETO
        # -------------------------------------------------

        elif (
            refresh_count > 40
            or full_refresh_required
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
        # LEER TOUCH
        # -------------------------------------------------

        gt.GT_Scan(
            GT_Dev,
            GT_Old
        )


        # -------------------------------------------------
        # Si el toque no cambió, ignorar
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
        # Si no existe un touch válido
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
        # PANTALLA: LISTA DE ACTIVIDADES
        # =================================================

        if (
            current_screen
            == PAGE_ACTIVITY_LIST
        ):


            # ---------------------------------------------
            # NEXT PAGE
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
            # PREVIOUS PAGE
            # ---------------------------------------------

            elif is_previous_button(
                touch_x,
                touch_y
            ):

                current_page -= 1


                if current_page < 0:

                    current_page = (
                        total_pages - 1
                    )


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


            # ---------------------------------------------
            # SELECCIONAR ACTIVIDAD
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


                if selected_activity is not None:

                    print(
                        "Actividad seleccionada:",
                        selected_activity["name"]
                    )


                    # -------------------------------------
                    # Tiempo inicial
                    # -------------------------------------

                    selected_minutes = (
                        DEFAULT_MINUTES
                    )


                    # -------------------------------------
                    # Obtener progreso desde SQLite
                    # -------------------------------------

                    selected_progress = (
                        get_activity_progress(
                            selected_activity
                        )
                    )


                    print(
                        "Progreso:",
                        selected_progress
                    )


                    # -------------------------------------
                    # Cambiar de pantalla
                    # -------------------------------------

                    current_screen = (
                        PAGE_DURATION
                    )


                    show_duration_screen(
                        image,
                        selected_activity,
                        selected_minutes,
                        selected_progress
                    )


                    refresh_required = True


        # =================================================
        # PANTALLA: DURACIÓN Y PROGRESO
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
                    selected_minutes,
                    selected_progress
                )


                refresh_required = True


            # ---------------------------------------------
            # GUARDAR
            # ---------------------------------------------

            elif is_save_button(
                touch_x,
                touch_y
            ):

                save_time_record(
                    selected_activity,
                    selected_minutes
                )

                show_saved_screen(
                    image
                )

                epd.displayPartial_Wait(
                    epd.getbuffer(
                        image
                    )
                )

                time.sleep(1)


                # -----------------------------------------
                # Recalcular progreso después de guardar
                # -----------------------------------------

                selected_progress = (
                    get_activity_progress(
                        selected_activity
                    )
                )


                print(
                    "Nuevo progreso:",
                    selected_progress
                )


                # -----------------------------------------
                # Volver a lista
                # -----------------------------------------

                current_screen = (
                    PAGE_ACTIVITY_LIST
                )


                selected_activity = None

                selected_progress = None


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
                    selected_minutes,
                    selected_progress
                )


                refresh_required = True


            # ---------------------------------------------
            # VOLVER SIN GUARDAR
            # ---------------------------------------------

            elif is_bottom_button(
                touch_x,
                touch_y
            ):

                print(
                    "Cancelado"
                )


                current_screen = (
                    PAGE_ACTIVITY_LIST
                )


                selected_activity = None

                selected_progress = None


                show_activities(
                    image,
                    activities,
                    current_page
                )


                refresh_required = True


# =========================================================
# ERROR DE I/O
# =========================================================

except IOError as error:

    logging.exception(
        "IOError: %s",
        error
    )


# =========================================================
# CUALQUIER OTRO ERROR
# =========================================================

except Exception as error:

    logging.exception(
        "Error inesperado: %s",
        error
    )


    flag_t = 0


    try:

        if "t" in locals():
            t.join(
                timeout=1
            )

    except Exception:
        pass


    try:

        if "epd" in locals():
            epd.sleep()
            epd.Dev_exit()

    except Exception:
        pass


    sys.exit(1)


# =========================================================
# CTRL + C
# =========================================================

except KeyboardInterrupt:

    logging.info(
        "ctrl + c"
    )


    flag_t = 0


    try:

        t.join(
            timeout=1
        )

    except Exception:
        pass


    try:

        epd.sleep()

        time.sleep(
            2
        )

        epd.Dev_exit()

    except Exception:
        pass


    sys.exit()