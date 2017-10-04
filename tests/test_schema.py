from datetime import datetime
from benwaonline.models import Tag, Post, Preview, Image

def test_preview(session):
    created = datetime.utcnow()
    filepath = 'testpath'
    preview = Preview(filepath=filepath, created=created)
    session.add(preview)
    q = Preview.query.one()

    assert q
    assert q.filepath == filepath
    assert q.created == created

def test_image(session):
    created = datetime.utcnow()
    filepath = 'testpath'
    preview = Preview(filepath=filepath, created=created)
    session.add(preview)

    image = Image(filepath=filepath, created=created, preview=preview)
    session.add(image)
    q = Image.query.one()

    assert q
    assert q.filepath == filepath
    assert q.created == created
    assert q.preview == preview

    q = Preview.query.one()
    assert q.image == image

def test_post(session):
    tag_name = 'oldbenwa'
    title = 'Benwas the best'
    created = datetime.utcnow()

    tag = Tag(name=tag_name, created=created)
    session.add(tag)

    post = Post(title=title, created=created)
    post.tags.append(tag)
    session.add(post)
    q = Post.query.first()

    assert q
    assert q.id == 1
    assert q.title == title
    assert q.created == created
    assert len(q.tags) == 1
    assert Post.query.filter(Post.tags.any(name=tag_name))