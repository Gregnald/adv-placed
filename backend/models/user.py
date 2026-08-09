from datetime import datetime

from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)