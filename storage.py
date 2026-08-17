import sqlite3

from datetime import datetime

from config import (
    DATABASE_FILE,
    MONTHS_PER_YEAR
)


# =========================================================
# CONEXIÓN
# =========================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CARGAR ACTIVIDADES
# =========================================================

def load_activities():
    """
    Carga las actividades junto con su meta anual.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nombre,
                meta_minutos
            FROM actividades
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        activities = []

        for row in rows:

            activities.append(
                {
                    "id": row["id"],
                    "name": row["nombre"],
                    "goal_minutes": (
                        row["meta_minutos"]
                        or 0
                    )
                }
            )

        return activities

    finally:

        connection.close()


# =========================================================
# GUARDAR REGISTRO
# =========================================================

def save_time_record(
    activity,
    minutes
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO registros (
                actividad_id,
                minutos,
                fecha
            )
            VALUES (?, ?, ?)
            """,
            (
                activity["id"],
                minutes,
                now.isoformat(
                    timespec="seconds"
                )
            )
        )

        connection.commit()

        print(
            "Registro guardado:",
            activity["name"],
            minutes,
            "minutos"
        )

    finally:

        connection.close()


# =========================================================
# MINUTOS DEL AÑO
# =========================================================

def get_year_minutes(
    activity_id
):
    """
    Suma todos los minutos de la actividad
    desde el 1 de enero hasta el 31 de diciembre
    del año actual.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        current_year = (
            datetime.now().year
        )

        start_date = (
            f"{current_year}-01-01"
        )

        end_date = (
            f"{current_year + 1}-01-01"
        )

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(minutos),
                    0
                ) AS total
            FROM registros
            WHERE actividad_id = ?
            AND fecha >= ?
            AND fecha < ?
            """,
            (
                activity_id,
                start_date,
                end_date
            )
        )

        row = cursor.fetchone()

        return row["total"]

    finally:

        connection.close()


# =========================================================
# MINUTOS DEL MES
# =========================================================

def get_month_minutes(
    activity_id
):
    """
    Suma los minutos realizados durante
    el mes actual.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        now = datetime.now()

        year = now.year
        month = now.month

        start_date = (
            f"{year}-{month:02d}-01"
        )

        if month == 12:

            end_date = (
                f"{year + 1}-01-01"
            )

        else:

            end_date = (
                f"{year}-{month + 1:02d}-01"
            )

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(minutos),
                    0
                ) AS total
            FROM registros
            WHERE actividad_id = ?
            AND fecha >= ?
            AND fecha < ?
            """,
            (
                activity_id,
                start_date,
                end_date
            )
        )

        row = cursor.fetchone()

        return row["total"]

    finally:

        connection.close()


# =========================================================
# CALCULAR PROGRESO
# =========================================================

def get_activity_progress(
    activity
):
    """
    Devuelve el progreso anual y mensual
    de una actividad.
    """

    annual_goal = activity.get(
        "goal_minutes",
        0
    )

    year_minutes = (
        get_year_minutes(
            activity["id"]
        )
    )

    month_minutes = (
        get_month_minutes(
            activity["id"]
        )
    )


    # -----------------------------------------------------
    # Si no existe meta
    # -----------------------------------------------------

    if annual_goal <= 0:

        return {
            "year_minutes": year_minutes,
            "annual_goal": 0,
            "year_percentage": 0,

            "month_minutes": month_minutes,
            "monthly_goal": 0,
            "month_percentage": 0
        }


    # -----------------------------------------------------
    # Meta mensual estimada
    # -----------------------------------------------------

    monthly_goal = (
        annual_goal
        / MONTHS_PER_YEAR
    )


    # -----------------------------------------------------
    # Porcentaje anual
    # -----------------------------------------------------

    year_percentage = (
        year_minutes
        / annual_goal
        * 100
    )


    # -----------------------------------------------------
    # Porcentaje mensual
    # -----------------------------------------------------

    month_percentage = (
        month_minutes
        / monthly_goal
        * 100
    )


    return {
        "year_minutes": year_minutes,

        "annual_goal": annual_goal,

        "year_percentage": round(
            year_percentage
        ),

        "month_minutes": month_minutes,

        "monthly_goal": round(
            monthly_goal
        ),

        "month_percentage": round(
            month_percentage
        )
    }