import os
from os.path import split, abspath, relpath, normcase
import sys
from datetime import datetime
from benwaonline import models
from benwaonline.database import db
from run import app

def get_or_create_tag(session, tagname):
    instance = models.Tag.query.filter_by(name=tagname).first()
    if instance:
        return instance, False
    else:
        created = datetime.utcnow()
        instance = models.Tag(name=tagname, created=created)
        session.add(instance)

    return instance, True

def format_path(path_, static_folder):
    path_ = normcase(relpath(path_, static_folder))
    correct_slashes = '/'.join(path_.split('\\'))
    return correct_slashes

def add_post(img_path, preview_path, tags=['benwa']):
    created = datetime.utcnow()
    with app.app_context():
        rel_preview = format_path(preview_path, app.static_folder)
        preview = models.Preview(filepath=rel_preview, created=created)
        db.session.add(preview)

        rel_img = format_path(img_path, app.static_folder)
        img = models.Image(filepath=rel_img, created=created, preview=preview)
        db.session.add(img)

        tag_models = [get_or_create_tag(db.session, tag)[0] for tag in tags]

        _, title = split(img_path)
        post = models.Post(title=title, created=datetime.utcnow(), image=img, tags=tag_models)
        db.session.add(post)

        db.session.commit()

def add_posts(img_path, preview_path, tags=['benwa']):
    files_ = [f for f in os.listdir(img_path)]
    for f in files_:
        img = '/'.join([img_path, f])
        preview = '/'.join([preview_path, f])
        add_post(img, preview, tags)

if __name__ == '__main__':
    img_path = abspath(sys.argv[1])
    preview_path = abspath(sys.argv[2])

    add_posts(img_path, preview_path)
