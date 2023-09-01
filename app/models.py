from mongoengine import queryset_manager

from app.database import db


class AdminUser(db.Document):
    email = db.EmailField(required=True)
    password_hash = db.StringField(required=True)

    @queryset_manager
    def get_by_email(doc_cls, queryset, email: str):
        return queryset(email=email).get()

    @queryset_manager
    def get_by_id(doc_cls, queryset, admin_id: str):
        return queryset(id=admin_id).get()


class Episode(db.Document):
    title = db.StringField()
    number = db.SequenceField()
    cover_url = db.URLField()
    mp3_url = db.URLField()
    description = db.StringField()
    themes = db.ListField()
    text = db.StringField()
    date_created = db.DateTimeField()

    @queryset_manager
    def get(doc_cls, queryset, number):
        return queryset(number=number).get()
