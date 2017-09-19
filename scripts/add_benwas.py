from os import listdir
from os.path import split, isfile, join
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from benwaonline import models
from benwaonline.database import db

def add_post(img_path, preview_path, tags=['benwa']):
    created = datetime.utcnow()

    img = models.Image(filepath=img_path, created=created)
    db.session.add(img)

    preview = models.Preview(filepath=preview_path, created=created)
    db.session.add(preview)

    tag_models = []
    for tag in tags:
        t = models.Tag(name=tag, created=created)
        try:
            db.session.add(t)
        except IntegrityError as e:
            t = models.Tag.query.filter(models.Tag.any(name=tag))
        finally:
            tag_models.append(t)

    _, title = split(img_path)
    post = models.Post(title=title, created=datetime.utcnow(), preview=preview, image=img)
    post.tags = tag_models
    db.session.add(post)

    db.session.commit()

def add_posts(img_path, preview_path, tags=['benwa']):
    files_ = [f for f in os.listdir(img_path)]
    for f in files_:
        img = '/'.join([img_path, f])
        preview = join(preview_path, f)
        add_post(img, preview, tags)
    