import json
from flask import Blueprint, render_template, redirect, url_for
from benwaonline.back import back
from benwaonline.front import front
from benwaonline.front.forms import SearchForm
# @bp.route('/')
# @back.anchor
# def under_construction():
#     return render_template('index.html')

@front.route('/faq')
def faq():
    with front.open_resource('templates/faq_entries.json', mode='r') as f:
        faq_entries = json.loads(f.read())
    return render_template('faq.html', entries=faq_entries['entries'])

@front.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        if any(form.tags.data):
            joined = ' '.join(form.tags.data)
        else:
            joined = None
        return redirect(url_for('gallery.show_posts', tags=joined))

    return render_template('search.html', form=form)
