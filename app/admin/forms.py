from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, validators


class AdminLoginForm(FlaskForm):
    username = StringField("username")
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
        ],
    )


class EpisodeUploadForm(FlaskForm):
    title = StringField("title", [validators.Length(min=8, max=120)])
    audio = FileField("audio", [FileRequired(), FileAllowed(["mp3"], "Audio only!")])
    cover_image = FileField(
        "cover_image", [FileRequired(), FileAllowed(["jpg", "png"], "Images only!")]
    )
    themes = StringField("themes", [validators.Length(min=8, max=1000)])
