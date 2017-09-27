from flask import Blueprint

auth = Blueprint('auth', __name__)

from benwaonline.auth import views