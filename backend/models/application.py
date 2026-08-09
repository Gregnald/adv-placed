from datetime import datetime

from db import db


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(40), unique=True, nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    resume_file_name = db.Column(db.String(255), default='', nullable=False)
    status = db.Column(db.String(40), default='Pending', nullable=False)
    interview_date = db.Column(db.String(80), default='', nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    drive = db.relationship('Drive', back_populates='applications')
    student = db.relationship('Student', back_populates='applications')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)