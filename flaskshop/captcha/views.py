from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from .forms import CaptchaForm
from pluggy import HookimplMarker

impl = HookimplMarker("flaskshop")

@login_required
def captcha():
    """captcha form"""
    form = CaptchaForm(request.form)
    if form.validate_on_submit():
        current_user.update(bot = False)
        return redirect(request.args.get("next") or "/")
    
    form.generate()
    return render_template("captcha/captcha.html", form=form)

def captcha_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user and current_user.bot:
            return redirect(url_for('captcha.captcha', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("captcha", __name__)
    bp.add_url_rule("/", view_func=captcha, methods=["GET", "POST"])
    app.register_blueprint(bp, url_prefix="/captcha")
