from sqlalchemy import desc
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
from flask_security import SQLAlchemyUserDatastore, Security, UserMixin, RoleMixin
from benwaonline.database import db

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64))
    oauth_token_hash = db.Column(db.String(64))
    oauth_secret_hash = db.Column(db.String(64))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref='users', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='user', lazy='dynamic')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

class Preview(db.Model):
    __tablename__ = 'preview'
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    image = db.relationship('Image', uselist=False, back_populates='preview')

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    preview = db.relationship('Preview', uselist=False, back_populates='image')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    created = db.Column(db.DateTime)
    image = db.relationship('Image', uselist=False, backref='post')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = association_proxy('post_tags', 'tag', creator=lambda tag: PostTag(tag=tag))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class PostTag(db.Model):
    __tablename__ = 'post_tag'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

    post = db.relationship('Post', backref=backref('post_tags', cascade="all, delete-orphan"))
    tag = db.relationship('Tag', backref=backref('post_tags', cascade="all, delete-orphan"))

    def __init__(self, post=None, tag=None):
        self.post = post
        self.tag = tag

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    created = db.Column(db.DateTime)
    posts = association_proxy('post_tags', 'post', creator=lambda post: PostTag(post=post))
