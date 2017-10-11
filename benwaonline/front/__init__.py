from flask import Blueprint

front = Blueprint('front', __name__, template_folder='templates')

from benwaonline.front import views
