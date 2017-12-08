from flask import Blueprint

userinfo = Blueprint('userinfo', __name__, template_folder='templates')

from benwaonline.userinfo import views