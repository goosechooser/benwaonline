from flask import Blueprint, render_template, redirect, url_for
from benwaonline.back import back
from benwaonline.front import front
from benwaonline.front.forms import SearchForm
# @bp.route('/')
# @back.anchor
# def under_construction():
#     return render_template('index.html')

@front.route('/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    print(form.tags.data)
    if form.validate_on_submit():
        tags = ['benwa']
        tags.extend(form.tags.data)
        joined = ' '.join(tags)
        return redirect(url_for('gallery.show_posts', tags=joined))

    return render_template('search.html', form=form)
