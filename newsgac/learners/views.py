from __future__ import absolute_import
from flask import Blueprint, render_template, request, session, flash, json, url_for

from pymodm.errors import ValidationError

from newsgac.learners.models.learner import Learner
from newsgac.learners import learners as learner_classes, factory
from newsgac.learners.factory import create_learner
from newsgac.users.view_decorators import requires_login
from newsgac.users.models import User
from newsgac.common.back import back

__author__ = 'abilgin'

learner_blueprint = Blueprint('learners', __name__)


@learner_blueprint.route('/')
@requires_login
@back.anchor
def user_learners():
    learners = list(Learner.objects.values())
    classes = {learner.tag: learner.name for learner in learner_classes}
    return render_template("learners/learners.html", learners=learners, learner_classes=classes)


@learner_blueprint.route('/new/<string:learner_tag>', methods=['GET', 'POST'])
@requires_login
@back.anchor
def new_learner(learner_tag=None):
    if request.method == 'POST':
        try:
            form_dict = request.form.to_dict()
            display_title = form_dict.pop('display_title')  # the rest are parameters...
            learner = create_learner(learner_tag,
                                     with_defaults=False,
                                     display_title=display_title,
                                     user=User(email=session['email']),
                                     parameters=form_dict
            )
            learner.save()
            flash('The configuration has been saved.', 'success')

        except (ValidationError, TypeError) as e:
                flash(str(e), 'error')

    else:
        learner = create_learner(learner_tag)

    return render_template(
        "learners/learner.html",
        learner=learner,
        parameters=learner.parameter_fields(),
        # save_url=url_for('learners.new_learner')
    )


@learner_blueprint.route('/<string:learner_id>')
@requires_login
def get_learner_page(learner_id):
    return render_template(
        "learners/learner.html",
    )
    pass

@learner_blueprint.route('/delete_all')
@requires_login
def delete_all():
    pass
