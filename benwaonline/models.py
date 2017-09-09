# from flask import current_app
# from flask_sqlalchemy import SQLAlchemy
from benwaonline.database import db

class Benwa(db.Model):
    __tables__ = 'benwas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    picture = db.relationship('BenwaPicture', backref='owner', lazy='dynamic')
    comments = db.relationship('GuestbookEntry', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<Benwa %r>' % (self.name)

class GuestbookEntry(db.Model):
    __tablename__ = 'guestbook'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)
    benwa_id = db.Column(db.Integer, db.ForeignKey('benwa.id'))

    def __repr__(self):
        return'<GuestbookEntry %r>' % (self.name)

class BenwaPicture(db.Model):
    __tablename__ = 'benwapictures'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True, unique=True)
    date_posted = db.Column(db.DateTime)
    views = db.Column(db.Integer)
    benwa_id = db.Column(db.Integer, db.ForeignKey('benwa.id'))

    def __repr__(self):
        return '<Benwa Picture %r>' % (self.filename)
