from flask import Blueprint, render_template

from benwaonline.comments import comments
from benwaonline import gateways as rf
from benwaonline.entities import Comment, Preview

@comments.route('/comments/')
def show_comments():
    fields = {'users': ['username']}
    include = ['post.preview', 'user']
    r = rf.get(Comment(), include=include, fields=fields)
    comments = Comment.from_response(r, many=True)

    if comments:
        previews = Preview.from_included(r, many=True)
        # this sucks, refactor it
        pdict = {p.id: p for p in previews}
        for comment in comments:
            post = comment.post
            # KeyError can occur here if theres gaps
            # FIX IT
            post['preview'] = pdict[post['id']]
        # the suck ends here

    return render_template('comments.html', comments=comments)
