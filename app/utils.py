from app.constants import TIME_FORMAT


def load_date(episode: dict):
    date_created = episode.get("date_created", None)
    if date_created:
        date_created = datetime.strptime(date_created, TIME_FORMAT)
        episode["date_created"] = date_created
    return episode


def dump_date(episode: dict):
    date_created = episode.get("date_created", None)
    if date_created:
        episode["date_created"] = date_created.strftime(TIME_FORMAT)
    return episode
