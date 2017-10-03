from flask import Blueprint
from flask_uploads import UploadSet, IMAGES

gallery = Blueprint('gallery', __name__, template_folder='templates')
images = UploadSet('images', IMAGES)

from benwaonline.gallery import views