from flask import Blueprint, request, redirect, url_for, render_template

from benwaonline.user import user
from benwaonline.database import db
from benwaonline.models import User

USERS_PER_PAGE = 20

@user.route('/user')
@user.route('/user?page=<int:page>')
def show_users(page=1):
    users = User.query.order_by(User.id.desc()).paginate(page, USERS_PER_PAGE, False).items
    return render_template('users.html', users=users)

