from flask import Blueprint

authbp = Blueprint('authbp', __name__, template_folder='templates')

from benwaonline.auth import views

