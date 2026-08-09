from db import db


class Drive(db.Model):
    __tablename__ = 'drives'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.String(40), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(160), nullable=False)
    job_description = db.Column(db.Text, default='', nullable=False)
    job_compensation = db.Column(db.Text, default='', nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    application_deadline = db.Column(db.String(20), default='', nullable=False)
    min_cgpa = db.Column(db.String(20), default='', nullable=False)
    eligible_branches = db.Column(db.Text, default='[]', nullable=False)
    eligible_years = db.Column(db.Text, default='[]', nullable=False)
    company_website = db.Column(db.String(255), default='', nullable=False)
    hr_mail = db.Column(db.String(255), default='', nullable=False)
    status = db.Column(db.String(40), default='Pending', nullable=False)
    students_participating = db.Column(db.Integer, default=0, nullable=False)

    company = db.relationship('Company', back_populates='drives')
    applications = db.relationship('Application', back_populates='drive', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)