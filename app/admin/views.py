import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import AdminUser


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        try:
            user = AdminUser.objects(email=username).get()
        except AdminUser.DoesNotExist:
            error = 'Incorrect username.'
        else:
            if not check_password_hash(user.password, password):
                error = 'Incorrect password.'

        if error is None:
            session.clear()
            print(user._id)
            session['user_id'] = str(user._id)
            return redirect(url_for('podcast.main_page'))

        flash(error)
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('admin.login'))

        return view(**kwargs)

    return wrapped_view
