from app.database import db


class AdminUser(db.Document):
    email = db.EmailField(required=True)
    password = db.StringField(required=True)


class Episode(db.Document):
    title = db.StringField()
    cover_url = db.URLField()
    mp3_url = db.URLField()
    description = db.StringField()
    date_created = db.DateTimeField()
