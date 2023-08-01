from datetime import datetime

from flask import Blueprint, current_app, make_response, render_template, request
from werkzeug.exceptions import NotFound

from app.models import Episode

podcast_bp = Blueprint("podcast", __name__)


@podcast_bp.route("/", methods=("GET",))
def main_page():
    page = int(request.args.get("page", 1))
    episodes = Episode.objects.paginate(page=page, per_page=10)
    return render_template("index.html", episodes=episodes, year=datetime.now().year)


@podcast_bp.route(
    "/p/<int:year>/<int:month>/<int:day>/podcast-<int:episode_number>", methods=("GET",)
)
def episode_page(year, month, day, episode_number):
    try:
        episode = Episode.objects(number=episode_number).get()
    except Episode.DoesNotExist:
        raise NotFound
    if not (
        episode.date_created.year == year
        and episode.date_created.month == month
        and episode.date_created.day == day
    ):
        raise NotFound
    return render_template("episode.html", episode=episode)


@podcast_bp.route("/info", methods=("GET",))
def info_page():
    return render_template("info.html")


@podcast_bp.route("/feed", methods=("GET",))
def rss_feed():
    episodes = Episode.objects.paginate(page=1, per_page=10)
    template = render_template(
        "rss-feed.xml",
        episodes=episodes,
        title=current_app.config["TITLE"],
        host=current_app.config["HOST"],
    )
    response = make_response(template)
    response.headers["Content-Type"] = "application/xml"
    return response
