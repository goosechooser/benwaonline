from flask import Blueprint

comments = Blueprint('comments', __name__, template_folder='templates')

from benwaonline.comments import views
