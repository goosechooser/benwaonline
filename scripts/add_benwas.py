from os.path import split
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

def add_posts(img_paths, preview_paths, tags=None):
    tag = 'old_benwas'
    folder = os.path.join(current_app.static_folder, tag, 'imgs')
    benwas = [f for f in os.listdir(folder)]
    tag_model = Tag(name=tag, created=datetime.utcnow())
    db.session.add(tag_model)

    for benwa in benwas:
        filepath = '/'.join([tag, 'imgs', benwa])
        img = Image(filepath=filepath, created=datetime.utcnow())
        db.session.add(img)

        thumb = '/'.join([tag, 'thumbs', benwa])
        preview = Preview(filepath=thumb, created=datetime.utcnow())
        db.session.add(preview)

        post = Post(title=benwa, created=datetime.utcnow(), preview=preview, image=img)

        post.tags.append(tag_model)
        db.session.add(post)

    db.session.commit()