import json
import os
import shutil
from datetime import datetime
from functools import reduce

import asyncio
import click
import pytz
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.episode import Episode
from app.utils import dump_date, get_s3_resource, load_date
from app.settings import settings

tz = pytz.timezone("Europe/Kyiv")
jinja_env = Environment(
    loader=FileSystemLoader("./app/templates"), autoescape=select_autoescape()
)
load_dotenv()


async def generate_episode_image_cover(themes: str, image_path_to_save: str):
    from PIL import Image
    from io import BytesIO
    from app.gateways.openai import OpenAI
    from app.models.openai.response import Answer
    import httpx

    openai = OpenAI(settings.openai_api_key, model=settings.openai_model)

    promt = f"""Обкладинка для подкасту про пляжний волейбол за наступними шоунотами:
        {themes}
    """

    response: Answer = await openai.image_generate(promt)
    url = response.data[0].url
    async with httpx.AsyncClient(timeout=180) as client:
        image_response = await client.get(str(url))

    image = Image.open(BytesIO(image_response.content)).convert('RGB')
    image.save(image_path_to_save)


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
@click.option("--themes", help="Themes", default="")
def add_episode(title="", themes=""):
    with open("./episodes.json", "r") as episodes_db:
        episodes_loaded = json.load(episodes_db)

    episodes = [Episode(**load_date(row)) for row in episodes_loaded]
    new_episode_number = len(episodes) + 2
    cover_image_name = f"podcast-{new_episode_number}-cover.jpeg"
    mp3_url = f"https://cdn.plyazhcast.org.ua/podcast-{new_episode_number}-audio.mp3"
    cover_image_path = f"./docs/images/{cover_image_name}"
    asyncio.run(generate_episode_image_cover(themes, cover_image_path))
    themes = themes.split("\n")
    new_episode = Episode(
        title=title,
        number=new_episode_number,
        cover_url=f"images/{cover_image_name}",
        mp3_url=mp3_url,
        themes=themes,
        date_created=datetime(year=2024, day=9, month=9, tzinfo=tz),
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
    resource = get_s3_resource(settings.cloudflare_account_id, settings.aws_key_id_s3, settings.aws_secret_key_s3)
    bucket = resource.Bucket(settings.aws_bucket_name)
    audio_name = f"podcast-{episode_number}-audio.mp3"
    with open(mp3_file_path, "rb") as mp3_file:
        bucket.upload_fileobj(
            mp3_file, audio_name, ExtraArgs={"ContentType": "audio/mpeg"}
        )
    print(f"Audio file uploaded to {bucket_name}/{audio_name}")


if __name__ == "__main__":
    cli()
