from sqlalchemy import desc
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from benwaonline.database import db

class Preview(db.Model):
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    poster_name = db.Column(db.String(255))
    content = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    preview = db.relationship('Preview', uselist=False, backref='post')
    image = db.relationship('Image', uselist=False, backref='post')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = association_proxy('post_tags', 'tag', creator=lambda tag: PostTag(tag=tag))

class PostTag(db.Model):
    __tablename__ = 'post_tag'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

    post = db.relationship('Post', backref=backref('post_tags', cascade="all, delete-orphan"))
    tag = db.relationship('Tag')

    def __init__(self, post=None, tag=None):
        self.post = post
        self.tag = tag

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    posts = association_proxy('post_tag', 'post', creator=lambda post: PostTag(post=post))
