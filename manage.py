import json
import os
import shutil
from datetime import datetime
from functools import reduce

import click
import pytz
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Episode
from app.utils import dump_date, get_s3_resource, load_date

tz = pytz.timezone("Europe/Kyiv")
jinja_env = Environment(
    loader=FileSystemLoader("./app/templates"), autoescape=select_autoescape()
)
load_dotenv()


def build_main_page(episodes: list[Episode]):
    main_page_template = jinja_env.get_template("index.html")
    with open("./docs/index.html", "w") as main_page:
        main_page.write(
            main_page_template.render(episodes=episodes, year=datetime.now().year)
        )


def build_rss_feed(episodes: list[Episode]):
    rss_feed_template = jinja_env.get_template("rss-feed.xml")
    with open("./docs/feed.xml", "w") as rss_page:
        rss_page.write(rss_feed_template.render(episodes=episodes))


@click.group()
def cli():
    pass


@cli.command("add_new_episode")
@click.option("--title", help="Episode title", default="")
@click.option("--cover_image_path", help="Cover image path", default="")
@click.option("--themes", help="Themes", default="")
def add_episode(title="", cover_image_path="", themes=""):
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**load_date(row)) for row in episodes_loaded]
    new_episode_number = len(episodes) + 2
    cover_image_name = f"podcast-{new_episode_number}-cover.jpeg"
    mp3_url = f"https://cdn.plyazhcast.org.ua/podcast-{new_episode_number}-audio.mp3"
    shutil.copy2(cover_image_path, f"./docs/images/{cover_image_name}")
    themes = themes.split("\n")
    new_episode = Episode(
        title=title,
        number=new_episode_number,
        cover_url=f"images/{cover_image_name}",
        mp3_url=mp3_url,
        themes=themes,
        date_created=datetime.now(tz),
    )
    episodes.append(new_episode)
    episode_link_path = f"./docs/p/{new_episode.date_created.year}/{new_episode.date_created.month}/{new_episode.date_created.day}"
    if not os.path.isdir(episode_link_path):
        os.makedirs(episode_link_path)

    episode_template = jinja_env.get_template("episode.html")
    with open(
        f"{episode_link_path}/podcast-{new_episode_number}.html", "w"
    ) as new_podcast_file:
        new_podcast_file.write(episode_template.render(episode=new_episode))

    build_main_page(episodes[:-11:-1])
    build_rss_feed(episodes[:-11:-1])
    episodes_dumped = [dump_date(episode.model_dump()) for episode in episodes]
    with open("./episodes.json", "w") as episodes_db:
        json.dump(episodes_dumped, episodes_db)


@cli.command("rebuild_info_page")
def rebuild_info_page():
    info_page_template = jinja_env.get_template("info.html")
    with open("./docs/info.html", "w") as info_page:
        info_page.write(info_page_template.render(year=datetime.now().year))


@cli.command("rebuild_license_page")
def rebuild_license_page():
    license_page_template = jinja_env.get_template("license.html")
    with open("./docs/license.html", "w") as license_page:
        license_page.write(license_page_template.render(year=datetime.now().year))


@cli.command("rebuild_main_page")
def rebuild_main_page():
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**load_date(row)) for row in episodes_loaded][:-11:-1]
    build_main_page(episodes)


@cli.command("rebuild_rss_feed")
def rebuild_rss_feed():
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**load_date(row)) for row in episodes_loaded][:-11:-1]
    build_rss_feed(episodes)


@cli.command("upload_audio")
@click.option("--episode_number", help="Episode number", type=int)
@click.option("--mp3_file_path", help="Audio file path", default="")
def upload_audio(episode_number: int, mp3_file_path: str):
    aws_access_key_id = os.environ.get("AWS_KEY_ID_S3")
    aws_secret_access_key = os.environ.get("AWS_SECRET_KEY_S3")
    bucket_name = os.environ.get("AWS_BUCKET_NAME")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

    resource = get_s3_resource(account_id, aws_access_key_id, aws_secret_access_key)
    bucket = resource.Bucket(bucket_name)
    audio_name = f"podcast-{episode_number}-audio.mp3"
    with open(mp3_file_path, "rb") as mp3_file:
        bucket.upload_fileobj(
            mp3_file, audio_name, ExtraArgs={"ContentType": "audio/mpeg"}
        )


if __name__ == "__main__":
    cli()
