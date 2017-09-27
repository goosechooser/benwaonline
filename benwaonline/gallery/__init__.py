from flask import Blueprint

gallery = Blueprint('gallery', __name__, template_folder='templates')

from benwaonline.gallery import views