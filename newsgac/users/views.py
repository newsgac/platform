from flask import Blueprint, request, session, url_for, render_template, flash
from werkzeug.utils import redirect
from pymodm.errors import ValidationError
from pymongo.errors import DuplicateKeyError
from markupsafe import Markup

from .errors import UserError
from . import view_decorators as user_decorators
from .models import User

__author__ = 'abilgin'

user_blueprint = Blueprint("users", __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
@user_decorators.requires_no_login
def login_user():
    if request.method == 'POST':
        try:
            identifier = request.form['identifier']
            password = request.form['password']
            user = User.from_login(identifier, password)
            session['email'] = user.email
            flash('You were successfully logged in.', 'success')
            return redirect(url_for("experiments.user_experiments"))
        except UserError:
            flash('User not found or password incorrect', 'error')

    return render_template("users/login.html", request=request.form)


@user_blueprint.route('/register', methods=['GET', 'POST'])
@user_decorators.requires_no_login
def register_user():
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        try:
            user = User(**form_dict)
            user.save(force_insert=True)  # force_insert throws when primary key exists (email)
            session['email'] = user.email
            flash('You were successfully registered.', 'success')
            return redirect(url_for("experiments.user_experiments"))
        except ValidationError as e:
            error_dict = e.message
            if 'password' in error_dict.keys():
                # hide entered password from error msg
                error_dict['password'] = [
                    msg.replace(form_dict.get('password', ''), 'password') for msg in error_dict['password']
                ]

            flash(Markup('<br>'.join([
                '%s: %s' % (key, ' '.join(value)) for (key, value) in error_dict.iteritems()
            ])), 'error')
        except DuplicateKeyError:
            flash('E-mail address is already in use', 'error')

    else:
        flash(Markup("""
You need to have an account to create your experiments.
Already have an account? 
<a href="/users/login" class="alert-link">
    Log in here.
</a><br/>
If you would like to find out more, why not
 <a href="/experiments/public" class="alert-link">
    browse public experiments?
 </a>
"""), 'info')

    return render_template("users/register.html")


@user_blueprint.route('/logout')
@user_decorators.requires_login
def logout_user():
    session['email'] = None
    flash('You were successfully logged out.', 'success')
    return render_template('home.html')


