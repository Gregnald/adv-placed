from db import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    enrollment = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(120), default='B.Tech Computer Science', nullable=False)
    year = db.Column(db.String(40), default='3rd Year', nullable=False)
    status = db.Column(db.String(40), default='Active', nullable=False)
    blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    resume_file_name = db.Column(db.String(255), default='', nullable=False)

    user = db.relationship('User', back_populates='student_profile')
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')