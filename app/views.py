from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app.models import Episode

podcast_bp = Blueprint("podcast", __name__)


@podcast_bp.route("/", methods=("GET",))
def main_page():
    page = int(request.args.get('page', 1))
    episodes = Episode.objects.paginate(page=page, per_page=10)
    return render_template("index.html", episodes=episodes)
