# models.py
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Text

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    profile_img = db.Column(db.LargeBinary, nullable=True)  # Adjust the length as needed
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref='followed', lazy='dynamic')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref='follower', lazy='dynamic')
    saves = db.relationship('Saves', backref='user', passive_deletes=True)

    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        if self.is_following(user):
            follow = self.following.filter_by(followed_id=user.id).first()
            db.session.delete(follow)
            db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    titletext = db.Column(db.Text, nullable=False)
    totaltext = db.Column(db.Text, nullable=False)
    img = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # New column for category
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    likes = db.relationship('Like', backref='post', passive_deletes=True)
    saves = db.relationship('Saves', backref='post', passive_deletes=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Saves(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"))
    date_saved = db.Column(db.DateTime(timezone=True), default=func.now())