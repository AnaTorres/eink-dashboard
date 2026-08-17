import sqlite3
from datetime import datetime

from config import DATABASE_FILE


# =========================================================
# CONEXIÓN
# =========================================================

def get_connection():
    """
    Abre una conexión a SQLite.
    """

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
    Lee las actividades desde SQLite.

    Devuelve una lista como:

    [
        {
            "id": 1,
            "name": "Ejercicio"
        },
        {
            "id": 2,
            "name": "Leer"
        }
    ]
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nombre
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
                    "name": row["nombre"]
                }
            )

        return activities

    finally:

        connection.close()


# =========================================================
# GUARDAR TIEMPO
# =========================================================

def save_time_record(
    activity,
    minutes
):
    """
    Guarda el tiempo asociado a una actividad.
    """

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
# OBTENER REGISTROS
# =========================================================

def load_records():
    """
    Devuelve todos los registros junto
    con el nombre de la actividad.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                registros.id,
                actividades.nombre,
                registros.minutos,
                registros.fecha
            FROM registros
            JOIN actividades
                ON actividades.id = registros.actividad_id
            ORDER BY registros.fecha DESC
            """
        )

        rows = cursor.fetchall()

        records = []

        for row in rows:

            records.append(
                {
                    "id": row["id"],
                    "activity_name": row["nombre"],
                    "minutes": row["minutos"],
                    "date": row["fecha"]
                }
            )

        return records

    finally:

        connection.close()