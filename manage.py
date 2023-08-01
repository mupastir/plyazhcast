import json
import shutil
from datetime import datetime
from functools import reduce

import click
import pytz
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.datamodels import Episode

TIME_FORMAT = "%a, %d %b %Y %H:%M:%S %z"

tz = pytz.timezone("Europe/Kyiv")
jinja_env = Environment(
    loader=FileSystemLoader("./app/templates"), autoescape=select_autoescape()
)


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


@click.group()
def cli():
    pass


@cli.command("add_new_episode")
@click.option("--title", help="Episode title", default="")
@click.option("--cover_impage_path", help="Cover image path", default="")
@click.option("--mp3_file_path", help="Audio file path", default="")
@click.option("--themes", help="Themes", default="")
def add_episode(title="", cover_impage_path="", mp3_file_path="", themes=""):
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**load_date(row)) for row in episodes_loaded]
    new_episode_number = len(episodes) + 1
    cover_image_name = "podcast-{new_episode_number}-cover.jpg"
    audio_name = "podcast-{new_episode_number}-audio.mp3"
    shutil.copy2(cover_impage_path, f"./docs/images/{cover_image_name}")
    shutil.copy2(mp3_file_path, f"./docs/files/{audio_name}")
    themes = themes.split("\n")
    new_episode = Episode(
        title=title,
        number=new_episode_number,
        cover_url=f"images/{cover_image_name}",
        mp3_url=f"files/{audio_name}",
        themes=themes,
        date_created=datetime.now(tz),
    )
    episodes.append(new_episode)
    episodes_dumped = [dump_date(episode.model_dump()) for episode in episodes]
    with open("./episodes.json", "w") as episodes_db:
        json.dump(episodes_dumped, episodes_db)


@cli.command("rebuild_main_page")
def rebuild_main_page():
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**make_date(row)) for row in episodes_loaded][:10]
    main_page_template = jinja_env.get_template("index.html")
    with open("./docs/index.html", "w") as main_page:
        main_page.write(
            main_page_template.render(episodes=episodes, year=datetime.now().year)
        )


if __name__ == "__main__":
    cli()
