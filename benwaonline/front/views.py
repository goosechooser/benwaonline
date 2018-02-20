from pathlib import Path
from random import choice
import json
from flask import Blueprint, render_template, redirect, url_for, current_app
from benwaonline.back import back
from benwaonline.front import front
from benwaonline.front.forms import SearchForm

def load_backgrounds(folder):
    front = Path(current_app.static_folder)
    front = front / folder
    frontwas = [folder + '/' + f.name for f in front.iterdir()]
    return frontwas

@front.route('/faq')
def faq():
    with front.open_resource('templates/faq_entries.json', mode='r') as f:
        faq_entries = json.loads(f.read())
    return render_template('faq.html', entries=faq_entries['entries'])

@front.route('/', methods=['GET', 'POST'])
def search():
    bg_img = choice(load_backgrounds('imgs'))

    form = SearchForm()
    if form.validate_on_submit():
        if form.tags.data:
            joined = ' '.join(form.tags.data)
        else:
            joined = None
        return redirect(url_for('gallery.show_posts', tags=joined))

    return render_template('front.html', form=form, bg_img=bg_img)
