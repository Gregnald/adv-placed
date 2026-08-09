from db import db


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    employer = db.Column(db.String(120), unique=True, nullable=False)
    website = db.Column(db.String(255), default='', nullable=False)
    hr_mail = db.Column(db.String(255), default='', nullable=False)
    status = db.Column(db.String(40), default='requested', nullable=False)
    blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', back_populates='company_profile')
    drives = db.relationship('Drive', back_populates='company', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)