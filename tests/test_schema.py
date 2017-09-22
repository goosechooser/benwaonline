from datetime import datetime
from benwaonline.models import Tag, Post

def test_tag(session):
    created = datetime.utcnow()
    name = 'benwa'
    tag = Tag(name=name, created=created)
    session.add(tag)
    q = Tag.query.first()

    assert q
    assert q.id == 1
    assert q.name == name
    assert q.created == created

def test_post(session):
    tag_name = 'benwa'
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