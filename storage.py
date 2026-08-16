import json

from datetime import datetime

from config import (
    ACTIVITIES_FILE,
    RECORDS_FILE
)


def load_activities():
    """
    Carga las actividades desde activities.json.
    """

    try:
        with open(
            ACTIVITIES_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            print(
                "ERROR: activities.json debe contener una lista"
            )
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

            activities.append(
                item
            )

        return activities

    except FileNotFoundError:

        print(
            "ERROR: No se encontró activities.json"
        )

        return []

    except json.JSONDecodeError as error:

        print(
            "ERROR: activities.json no es válido"
        )

        print(
            error
        )

        return []


def load_records():
    """
    Carga los registros existentes.
    """

    try:
        with open(
            RECORDS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            records = json.load(
                file
            )

        if not isinstance(
            records,
            list
        ):
            return []

        return records

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return []


def save_time_record(
    activity,
    minutes
):
    """
    Guarda un nuevo registro en time_records.json.
    """

    records = load_records()

    now = datetime.now()

    record = {
        "activity_id": activity.get(
            "id"
        ),
        "activity_name": activity.get(
            "name"
        ),
        "minutes": minutes,
        "date": now.strftime(
            "%Y-%m-%d"
        ),
        "created_at": now.isoformat(
            timespec="seconds"
        )
    }

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

    print(
        "Registro guardado:",
        activity.get("name"),
        minutes,
        "minutos"
    )