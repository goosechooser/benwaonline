from pathlib import Path
from random import choice

from flask import Blueprint, render_template, redirect, url_for, current_app, json
from benwaonline.gateways import PostGateway
from benwaonline.back import back
from benwaonline.front import front
from benwaonline.front.forms import SearchForm

def load_backgrounds(folder):
    front = Path(current_app.static_folder)
    front = front / folder
    try:
        frontwas = [folder + '/' + f.name for f in front.iterdir()]
    except FileNotFoundError:
        frontwas = ['']
    return frontwas

@front.route('/faq')
def faq():
    with front.open_resource('templates/faq_entries.json', mode='r') as f:
        faq_entries = json.loads(f.read())
    return render_template('faq.html', entries=faq_entries['entries'])

@front.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        if form.tags.data != ['']:
            joined = ' '.join(form.tags.data)
        else:
            joined = None

        return redirect(url_for('gallery.show_posts', tags=joined))

    # cache this
    posts = PostGateway().get(fields={'posts':['title']}, page_size=0)
    post_count = len(posts)
    return render_template('front.html', form=form, post_count=post_count)

@front.route('/tos')
def tos():
    return render_template('tos.html')

@front.route('/contact')
def contact():
    return render_template('contact.html')

@front.route('/takedown')
def takedown():
    return render_template('takedown.html')