from flask import Blueprint, request, session, g, redirect, url_for, \
     render_template
from benwaonline.models import BenwaPicture

gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static', static_url_path='/static/gallery')

BENWAS_PER_PAGE = 1

@gallery.route('/gallery')
def display_benwas():
    entries = BenwaPicture.query.all()
    return render_template('gallery.html', pics=entries)

@gallery.route('/rotating', methods=['GET', 'POST'])
@gallery.route('/rotating/<int:page>', methods=['GET', 'POST'])
def rotating(page=1):
    entries = BenwaPicture.query.paginate(page, BENWAS_PER_PAGE, False)
    return render_template('rotating.html', pics=entries)
