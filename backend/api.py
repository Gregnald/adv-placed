import json
from datetime import date
from uuid import uuid4

import bcrypt
from flask import jsonify, request

from dto import (
    application_to_dict,
    company_to_dict,
    drive_for_student,
    drive_to_dict,
    list_to_json,
    session_to_dict,
    student_to_dict,
    user_to_dict,
)
from db import db
from models import Application, Company, Drive, SessionAuth, Student, User


def response(data, status=200):
    return jsonify(data), status


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def payload():
    return request.get_json(silent=True) or {}


def next_drive_id():
    max_id = 200
    for drive in Drive.query.all():
        digits = ''.join(ch for ch in drive.drive_id if ch.isdigit())
        if digits:
            max_id = max(max_id, int(digits))
    return f'DRV{max_id + 1}'


def next_application_id():
    max_id = 300
    for application in Application.query.all():
        digits = ''.join(ch for ch in application.application_id if ch.isdigit())
        if digits:
            max_id = max(max_id, int(digits))
    return f'APP{max_id + 1}'


def next_enrollment():
    max_id = 1000
    for student in Student.query.all():
        digits = ''.join(ch for ch in student.enrollment if ch.isdigit())
        if digits:
            max_id = max(max_id, int(digits))
    return f'ENR{max_id + 1}'


def find_user(username, role=None):
    query = User.query.filter_by(username=username)
    if role:
        query = query.filter_by(role=role)
    return query.first()


def company_for_user(user):
    company = Company.query.filter_by(user_id=user.id).first()
    if company:
        return company
    return Company.query.filter_by(employer=user.username).first()


def student_for_user(user):
    return Student.query.filter_by(user_id=user.id).first()


def create_session(user):
    SessionAuth.query.filter_by(user_id=user.id).delete()
    session = SessionAuth(
        session_id=uuid4().hex,
        user_id=user.id,
        user_type=user.role,
    )
    db.session.add(session)
    db.session.flush()
    return session


def session_id_from_request():
    session_id = request.headers.get('X-Session-Id', '').strip()
    if session_id:
        return session_id

    session_id = request.args.get('sessionId', '').strip()
    if session_id:
        return session_id

    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        session_id = (payload().get('sessionId') or '').strip()
        if session_id:
            return session_id

    return ''


def auth_user(allowed_roles=None):
    session_id = session_id_from_request()
    if not session_id:
        return None, None, response({'message': 'Session ID is required.'}, 401)

    session = SessionAuth.query.filter_by(session_id=session_id).first()
    if not session:
        return None, None, response({'message': 'Invalid session. Please log in again.'}, 401)

    if allowed_roles and session.user_type not in allowed_roles:
        return None, None, response({'message': 'You are not authorized for this action.'}, 403)

    user = db.session.get(User, session.user_id)
    if not user:
        return None, None, response({'message': 'Session user not found.'}, 404)

    return session, user, None


def ensure_admin_account():
    admin = User.query.filter_by(username='admin', role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=hash_password('admin'),
            role='admin',
        )
        db.session.add(admin)
        db.session.commit()


def register_routes(app):
    @app.route('/api/health', methods=['GET'])
    def health():
        return response({'status': 'ok'})

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = payload()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        role = (data.get('role') or 'student').strip().lower()

        if not username or not password:
            return response({'message': 'Username and password are required.'}, 400)

        if role == 'admin':
            return response({'message': 'Admin account cannot be registered.'}, 400)

        user = find_user(username)
        if user:
            return response({'message': 'Username already exists.'}, 400)

        user = User(username=username, password=hash_password(password), role=role)
        db.session.add(user)
        db.session.flush()

        profile = None
        if role == 'company':
            company_name = (data.get('companyName') or username).strip()
            hr_mail = (data.get('companyHRMail') or '').strip()
            if not company_name or not hr_mail:
                return response({'message': 'Company name and HR mail are required.'}, 400)

            company = company_for_user(user) or Company.query.filter_by(employer=company_name).first()
            if not company:
                company = Company(
                    user_id=user.id,
                    employer=company_name,
                    website=(data.get('website') or '').strip(),
                    hr_mail=hr_mail,
                    status='requested',
                    blacklisted=False,
                )
                db.session.add(company)
            else:
                company.user_id = user.id
                company.hr_mail = hr_mail
                if data.get('website'):
                    company.website = data.get('website').strip()
            profile = company
        elif role == 'student':
            student = student_for_user(user)
            if not student:
                student = Student(
                    user_id=user.id,
                    enrollment=next_enrollment(),
                    name=(data.get('name') or username).strip().title(),
                    course='B.Tech Computer Science',
                    year='3rd Year',
                    status='Active',
                    blacklisted=False,
                    resume_file_name=''
                )
                db.session.add(student)
            profile = student

        session = create_session(user)
        db.session.commit()
        return response({
            'message': 'Registration successful.',
            'user': user_to_dict(user),
            'sessionId': session.session_id,
            'session': session_to_dict(session),
            'profile': company_to_dict(profile) if role == 'company' else student_to_dict(profile) if profile else None
        })

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = payload()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        role = (data.get('role') or 'student').strip().lower()

        if not username or not password:
            return response({'message': 'Username and password are required.'}, 400)

        user = find_user(username, role)
        if not user:
            return response({'message': 'Invalid username, password, or role.'}, 401)

        if not verify_password(password, user.password):
            return response({'message': 'Invalid username, password, or role.'}, 401)

        profile = None
        if role == 'company':
            company_name = (data.get('companyName') or username).strip()
            hr_mail = (data.get('companyHRMail') or '').strip()
            company = company_for_user(user) or Company.query.filter_by(employer=company_name).first()
            if not company:
                company = Company(
                    user_id=user.id,
                    employer=company_name,
                    website=(data.get('website') or '').strip(),
                    hr_mail=hr_mail,
                    status='requested',
                    blacklisted=False,
                )
                db.session.add(company)
            else:
                company.user_id = user.id
                if hr_mail:
                    company.hr_mail = hr_mail
                if data.get('website'):
                    company.website = data.get('website').strip()
            profile = company
        elif role == 'student':
            student = student_for_user(user)
            if not student:
                student = Student(
                    user_id=user.id,
                    enrollment=next_enrollment(),
                    name=username.title(),
                    course='B.Tech Computer Science',
                    year='3rd Year',
                    status='Active',
                    blacklisted=False,
                    resume_file_name=''
                )
                db.session.add(student)
            profile = student

        session = create_session(user)
        db.session.commit()
        return response({
            'message': 'Login successful.',
            'user': user_to_dict(user),
            'sessionId': session.session_id,
            'session': session_to_dict(session),
            'profile': company_to_dict(profile) if role == 'company' else student_to_dict(profile) if profile else None
        })

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        session, _, error = auth_user()
        if error:
            return error
        db.session.delete(session)
        db.session.commit()
        return response({'message': 'Logged out.'})

    @app.route('/api/admin/dashboard', methods=['GET'])
    def admin_dashboard():
        _, _, error = auth_user(['admin'])
        if error:
            return error

        companies = Company.query.order_by(Company.id.asc()).all()
        students = Student.query.order_by(Student.id.asc()).all()
        drives = Drive.query.order_by(Drive.id.asc()).all()

        return response({
            'user': {'name': 'Admin', 'userType': 'Admin'},
            'companies': [company_to_dict(company) for company in companies],
            'students': [student_to_dict(student) for student in students],
            'drives': [drive_to_dict(drive) for drive in drives],
            'reports': {
                'totalStudents': len(students),
                'totalCompanies': len(companies),
                'totalDrives': len(drives),
                'pendingCompanies': len([company for company in companies if company.status == 'requested']),
                'rejectedDrives': len([drive for drive in drives if drive.status == 'Rejected']),
                'approvedDrives': len([drive for drive in drives if drive.status == 'Approved']),
                'placedStudents': len([student for student in students if student.status.lower() == 'placed']),
                'blacklistedCompanies': len([company for company in companies if company.blacklisted]),
                'blacklistedStudents': len([student for student in students if student.blacklisted]),
            }
        })

    @app.route('/api/admin/companies/<string:company_name>', methods=['PATCH'])
    def update_company(company_name):
        _, _, error = auth_user(['admin'])
        if error:
            return error

        company = Company.query.filter_by(employer=company_name).first()
        if not company:
            return response({'message': 'Company not found.'}, 404)

        data = payload()
        if 'status' in data:
            company.status = data['status']
        if 'blacklisted' in data:
            company.blacklisted = bool(data['blacklisted'])
            if company.blacklisted:
                company.status = 'denied'
            

        db.session.commit()
        return response({'company': company_to_dict(company)})

    @app.route('/api/admin/students/<string:enrollment>', methods=['PATCH'])
    def update_student(enrollment):
        _, _, error = auth_user(['admin'])
        if error:
            return error

        student = Student.query.filter_by(enrollment=enrollment).first()
        if not student:
            return response({'message': 'Student not found.'}, 404)

        data = payload()
        for key in ['name', 'course', 'year', 'status', 'resumeFileName']:
            if key in data:
                setattr(student, 'resume_file_name' if key == 'resumeFileName' else key, data[key])
        if 'blacklisted' in data:
            student.blacklisted = bool(data['blacklisted'])
            if student.blacklisted:
                student.status = 'denied'

        db.session.commit()
        return response({'student': student_to_dict(student)})

    @app.route('/api/admin/drives/<string:drive_code>', methods=['PATCH'])
    def update_drive(drive_code):
        _, _, error = auth_user(['admin'])
        if error:
            return error

        drive = Drive.query.filter_by(drive_id=drive_code).first()
        if not drive:
            return response({'message': 'Drive not found.'}, 404)

        data = payload()
        if 'status' in data:
            drive.status = data['status']
        if 'studentsParticipating' in data:
            drive.students_participating = int(data['studentsParticipating'])

        db.session.commit()
        return response({'drive': drive_to_dict(drive)})

    @app.route('/api/company/dashboard', methods=['GET'])
    def company_dashboard():
        _, user, error = auth_user(['company'])
        if error:
            return error

        company = company_for_user(user)
        if not company:
            return response({'message': 'Company profile not found.'}, 404)

        drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.id.asc()).all()
        applications = []
        for drive in drives:
            applications.extend(drive.applications)

        return response({
            'company': company_to_dict(company),
            'drives': [drive_to_dict(drive) for drive in drives],
            'applications': [application_to_dict(application) for application in applications],
            'summary': {
                'totalDrives': len(drives),
                'approvedDrives': len([drive for drive in drives if drive.status == 'Approved']),
                'pendingDrives': len([drive for drive in drives if drive.status == 'Pending']),
                'totalApplications': len(applications),
            }
        })

    @app.route('/api/company/drives', methods=['POST'])
    def create_company_drive():
        _, user, error = auth_user(['company'])
        if error:
            return error

        company = company_for_user(user)
        if not company:
            return response({'message': 'Company profile not found.'}, 404)

        data = payload()
        drive = Drive(
            drive_id=next_drive_id(),
            company_id=company.id,
            company_name=company.employer,
            job_title=(data.get('jobTitle') or '').strip(),
            job_description=(data.get('jobDescription') or '').strip(),
            job_compensation=(data.get('jobCompensation') or '').strip(),
            start_date=(data.get('startDate') or '').strip(),
            end_date=(data.get('endDate') or '').strip(),
            application_deadline=(data.get('applicationDeadline') or '').strip(),
            min_cgpa=str(data.get('minCgpa') or '').strip(),
            eligible_branches=list_to_json(data.get('eligibleBranches') or []),
            eligible_years=list_to_json(data.get('eligibleYears') or []),
            company_website=(data.get('companyWebsite') or company.website).strip(),
            hr_mail=(data.get('hrMail') or company.hr_mail).strip(),
            status='Pending',
            students_participating=0,
        )
        db.session.add(drive)
        db.session.commit()
        return response({'drive': drive_to_dict(drive)}, 201)

    @app.route('/api/applications/<string:application_code>', methods=['PATCH'])
    def update_application(application_code):
        session, user, error = auth_user(['company', 'admin'])
        if error:
            return error

        application = Application.query.filter_by(application_id=application_code).first()
        if not application:
            return response({'message': 'Application not found.'}, 404)

        if session.user_type == 'company':
            company = company_for_user(user)
            if not company or not application.drive or application.drive.company_id != company.id:
                return response({'message': 'You can only update applications for your drives.'}, 403)

        data = payload()
        if 'status' in data:
            application.status = data['status']
        db.session.commit()
        return response({'application': application_to_dict(application)})

    @app.route('/api/student/dashboard', methods=['GET'])
    def student_dashboard():
        _, user, error = auth_user(['student'])
        if error:
            return error

        student = student_for_user(user)
        if not student:
            return response({'message': 'Student profile not found.'}, 404)

        drives = Drive.query.filter(Drive.status == 'Approved').order_by(Drive.id.asc()).all()
        applications = Application.query.filter_by(student_id=student.id).all()
        application_map = {application.drive_id: application for application in applications}

        active_drives = []
        applied_drives = []
        for drive in drives:
            application = application_map.get(drive.id)
            decorated = drive_for_student(drive, application)
            active_drives.append(decorated)
            if application:
                applied_drives.append(decorated)

        return response({
            'profile': student_to_dict(student),
            'activeDrives': active_drives,
            'appliedDrives': applied_drives
        })

    @app.route('/api/student/profile', methods=['PATCH'])
    def update_student_profile():
        _, user, error = auth_user(['student'])
        if error:
            return error

        student = student_for_user(user)
        if not student:
            return response({'message': 'Student profile not found.'}, 404)

        data = payload()
        for key in ['name', 'course', 'year', 'status', 'resumeFileName']:
            if key in data:
                setattr(student, 'resume_file_name' if key == 'resumeFileName' else key, data[key])

        db.session.commit()
        return response({'profile': student_to_dict(student)})

    @app.route('/api/drives/<string:drive_code>/apply', methods=['POST'])
    def apply_to_drive(drive_code):
        _, user, error = auth_user(['student'])
        if error:
            return error

        data = payload()
        resume = (data.get('resumeFileName') or '').strip()
        student = student_for_user(user)
        drive = Drive.query.filter_by(drive_id=drive_code).first()
        if not student or not drive:
            return response({'message': 'Student or drive not found.'}, 404)

        existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
        if existing:
            existing.resume_file_name = resume or student.resume_file_name
            existing.status = 'Applied'
            db.session.commit()
            return response({'application': application_to_dict(existing)})

        application = Application(
            application_id=next_application_id(),
            drive_id=drive.id,
            student_id=student.id,
            student_name=student.name,
            resume_file_name=resume or student.resume_file_name,
            status='Applied'
        )
        drive.students_participating = (drive.students_participating or 0) + 1
        db.session.add(application)
        db.session.commit()
        return response({'application': application_to_dict(application)}, 201)
