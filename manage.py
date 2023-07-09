import click

from flask.cli import FlaskGroup
from app import create_app
from app.models import AdminUser
import werkzeug


flask_app = create_app()


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass


@cli.command("add_admin")
@click.argument("email")
@click.argument("password")
def add_admin(email, password):
    try:
        admin = AdminUser.objects(email=email).get()
    except AdminUser.DoesNotExist:
        password_hash = werkzeug.security.generate_password_hash(password)
        admin = AdminUser(email=email, password=password_hash)
        admin.save()
        click.echo("Admin was successfuly created.")
    else:
        click.echo("Admin with such email already exists.")


if __name__ == "__main__":
    cli()

