from flask import Blueprint, render_template

from benwaonline.comments import comments
from benwaonline.gateways import CommentGateway

@comments.route('/comments/')
def show_comments():
    fields = {'users': ['username']}
    include = ['post.preview', 'user']
    comments = CommentGateway().get(include=include, fields=fields, page_size=0)

    return render_template('comments.html', comments=comments)
