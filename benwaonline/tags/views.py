from flask import Blueprint, render_template, redirect, url_for

from benwaonline.tags import tags
from benwaonline.front.forms import SearchForm
from benwaonline.gateways import RequestFactory
from benwaonline.entities import Tag

rf = RequestFactory()

@tags.route('/tags/', methods=['GET', 'POST'])
def show_tags():
    # Need to consider paginating
    r = rf.get(Tag(), page_opts={'size': 0})
    tags = Tag.from_response(r, many=True)

    form = SearchForm()
    if form.validate_on_submit():
        if form.tags.data:
            joined = ' '.join(form.tags.data)
        else:
            joined = None
        return redirect(url_for('gallery.show_posts', tags=joined))

    return render_template('tags.html', form=form, tags=tags)
