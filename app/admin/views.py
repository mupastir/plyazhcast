import functools
from datetime import datetime

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from app.admin.forms import AdminLoginForm, EpisodeUploadForm
from app.admin.uploader import FileTypes, LocalFileUploader
from app.models import AdminUser, Episode
from app.utils import timezone as tz

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=("GET", "POST"))
def login():
    form = AdminLoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            error = None
            username = form.username.data
            password = form.password.data
            try:
                user = AdminUser.get_by_email(email=username)
            except AdminUser.DoesNotExist:
                error = "Incorrect username."
            else:
                if not check_password_hash(user.password_hash, password):
                    error = "Incorrect password."
        else:
            error = form.errors

        if error is None:
            session.clear()
            session["user_id"] = str(user.id)
            return redirect(url_for("podcast.main_page"))

        flash(error)
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("podcast.main_page"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("admin.login"))

        return view(**kwargs)

    return wrapped_view


@admin_bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = EpisodeUploadForm()
    if form.validate_on_submit():
        if form.cover_image.data:
            name = form.cover_image.data.filename
            image_uploader = LocalFileUploader(
                FileTypes.IMAGE.value,
                name=secure_filename(name),
                data=form.cover_image.data,
            )
            image_url = image_uploader.upload()
        if form.audio.data:
            name = form.audio.data.filename
            audio_uploader = LocalFileUploader(
                FileTypes.AUDIO.value, name=secure_filename(name), data=form.audio.data
            )
            audio_url = audio_uploader.upload()
        episode = Episode(
            title=form.title.data,
            themes=form.themes.data.split("."),
            text=form.text.data,
            mp3_url=audio_url,
            cover_url=image_url,
            date_created=datetime.now(tz),
        )
        episode.save()
        flash("Episode was uploaded.")
        return redirect(url_for("podcast.main_page"))

    return render_template("admin/create.html", form=form)
