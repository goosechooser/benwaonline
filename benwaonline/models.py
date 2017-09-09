# from flask import current_app
# from flask_sqlalchemy import SQLAlchemy
from benwaonline.database import db

class BenwaPicture(db.Model):
    __tablename__ = 'benwapictures'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True, unique=True)
    date_posted = db.Column(db.DateTime)
    viewed = db.Column(db.Integer)

    def __init__(self, filename=None, date_posted=None, viewed=None):
        self.filename = filename
        self.date_posted = date_posted
        self.viewed = viewed

    def __repr__(self):
        return '<Post %r>' % (self.filename)

class GuestbookEntry(db.Model):
    # __tablename__ = 'guestbook'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)

    def __init__(self, name=None, content=None, date_posted=None):
        self.name = name
        self.content = content
        self.date_posted = date_posted

    def __repr__(self):
        return'<GuestbookEntry %r>' % (self.name)
