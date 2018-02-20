from flask import Blueprint, render_template

from benwaonline.comments import comments
from benwaonline.gateways import RequestFactory
from benwaonline.entities import Comment, Preview

rf = RequestFactory()

@comments.route('/comments/')
def show_comments():
    fields = [{'users': ['username']}]
    include = ['post.preview', 'user']
    r = rf.get(Comment(), include=include, fields=fields)
    comments = Comment.from_response(r, many=True)

    # this sucks, refactor it
    json_ = {}
    json_['data'] = [entry for entry in r.json()['included'] if entry['type'] == 'previews']
    previews = Preview.from_json(json_, many=True)
    pdict = {p.id: p for p in previews}
    for comment in comments:
        post = comment.post
        post['preview'] = pdict[post['id']]
    # the suck ends here

    return render_template('comments.html', comments=comments)
