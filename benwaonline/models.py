from sqlalchemy import desc
from benwaonline.database import db

class Benwa(db.Model):
    __tables__ = 'benwas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    picture = db.relationship('BenwaPicture', backref='owner', lazy='dynamic')
    comments = db.relationship('GuestbookEntry', backref='owner', lazy='dynamic')
    tag = db.Column(db.String(64))
    pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'))

    def __repr__(self):
        return '<Benwa %r>' % (self.name)

    def pic(self):
        return self.picture.first()

    def guestbook(self):
        return self.comments.order_by(desc(GuestbookEntry.id)).all()

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
    filename = db.Column(db.String(64))
    thumbnail = db.Column(db.String(64))
    date_posted = db.Column(db.DateTime)
    views = db.Column(db.Integer)
    benwa_id = db.Column(db.Integer, db.ForeignKey('benwa.id'))

    def __repr__(self):
        return '<Benwa Picture %r>' % (self.filename)

class Pool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date_created = db.Column(db.DateTime)
    benwas = db.relationship('Benwa', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<Pool %r>' % (self.name)

    def members(self):
        return self.benwas.all()
