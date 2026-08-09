from datetime import datetime

from db import db


class SessionAuth(db.Model):
    __tablename__ = 'session_auths'

    session_id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)