from flask import Blueprint, request, session, url_for, render_template, flash
from markupsafe import Markup
from werkzeug.utils import redirect
import src.models.users.errors as UserErrors
import src.models.users.decorators as user_decorators
from src.common.back import back
from src.models.users.user import User

__author__ = 'abilgin'

user_blueprint = Blueprint("users", __name__)

@user_blueprint.route('/login', methods=['GET', 'POST'])
@user_decorators.requires_no_login
def login_user():
    error = None
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        if (identifier == "") or (password == ""):
            error = "All fields are required."
            flash(error, 'error')
        else:
            try:
                if User.is_login_valid(identifier, password):
                    user = User.get_by_identifier(identifier)
                    session['email'] = user.email
                    flash('You were successfully logged in.', 'success')
                    return redirect(url_for("experiments.user_experiments"))
            except UserErrors.UserError as e:
                error = e.message
                flash(error, 'error')
                return render_template("users/login.html", error=error, request=request.form)

    return render_template("users/login.html", error=error)


@user_blueprint.route('/register', methods=['GET', 'POST'])
@user_decorators.requires_no_login
def register_user():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        if (username == "") or (name == "") or (surname == "") or (email == "") or (password == ""):
            error = "All fields are required."
            flash(error, 'error')
        else :
            try:
                if User.register_user(username, name, surname, email, password):
                    session['email'] = email
                    flash('You were successfully registered.', 'success')
                    return redirect(url_for("experiments.user_experiments"))
            except UserErrors.UserError as e:
                error = e.message
                flash(error, 'error')
        
        return render_template("users/register.html", error=error, request=request.form)
    else:
        flash(Markup('You need to have an account to create your experiments.'+
                         ' Already have an account? <a href="/users/login" class="alert-link">Log in here.</a><br/>'+
                        'If you would like to find out more, why not <a href="/experiments/public" class="alert-link">browse public experiments?</a>'), 'info')

    return render_template("users/register.html", error=error)


@user_blueprint.route('/logout')
@user_decorators.requires_login
def logout_user():
    session['email'] = None
    flash('You were successfully logged out.', 'success')
    return redirect(url_for('home'))


