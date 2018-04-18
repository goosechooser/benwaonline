from flask import Blueprint, render_template, redirect, url_for

from benwaonline.tags import tags
from benwaonline.front.forms import SearchForm
from benwaonline.entity_gateways import TagGateway

@tags.route('/tags/', methods=['GET', 'POST'])
def show_tags():
    tags = TagGateway().get(page_size=20)

    form = SearchForm()
    if form.validate_on_submit():
        if form.tags.data != ['']:
            joined = ' '.join(form.tags.data)
        else:
            joined = None

        return redirect(url_for('gallery.show_posts', tags=joined))

    return render_template('tags.html', form=form, tags=tags)
