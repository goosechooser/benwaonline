from flask import Blueprint, render_template
from benwaonline.back import back

bp = Blueprint('benwaonline', __name__)

@bp.route('/')
@back.anchor
def under_construction():
    return render_template('index.html')
