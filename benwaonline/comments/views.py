from flask import Blueprint, render_template

from benwaonline.comments import comments
from benwaonline.entity_gateways import CommentGateway

@comments.route('/comments/')
def show_comments():
    fields = {'users': ['username']}
    include = ['post.preview', 'user']
    comments = CommentGateway().get(include=include, fields=fields)

    return render_template('comments.html', comments=comments)
