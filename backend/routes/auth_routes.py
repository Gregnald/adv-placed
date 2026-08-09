from flask import Blueprint
from db import db
from dto import company_to_dict, session_to_dict, student_to_dict, user_to_dict
from models import Company, Student, User
from redis_client import delete_session_redis
from routes.common import (
    auth_user,
    company_for_user,
    create_session,
    find_user,
    hash_password,
    next_enrollment,
    payload,
    response,
    session_id_from_request,
    student_for_user,
    verify_password,
)

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/api/health', methods=['GET'])
def health():
    return response({'status': 'ok'})


@auth_bp.route('/api/auth/register', methods=['POST'])
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
        student_email = (data.get('email') or '').strip()
        first_name = (data.get('firstName') or data.get('first_name') or '').strip().title()
        surname = (data.get('surname') or data.get('last_name') or '').strip().title()

        if not student_email:
            return response({'message': 'Email is required for student registration.'}, 400)
        if not first_name or not surname:
            return response({'message': 'First name and surname are required for student registration.'}, 400)

        student = student_for_user(user)
        if not student:
            student = Student(
                user_id=user.id,
                enrollment=next_enrollment(),
                username=username,
                first_name=first_name,
                surname=surname,
                email=student_email,
                course='B.Tech Computer Science',
                year='3rd Year',
                status='Active',
                blacklisted=False,
                resume_file_name=''
            )
            db.session.add(student)
        else:
            student.username = username
            student.email = student_email
            student.first_name = first_name
            student.surname = surname
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


@auth_bp.route('/api/auth/login', methods=['POST'])
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
                username=username,
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


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session, _, error = auth_user()
    if error:
        return error
    session_id = session_id_from_request()
    delete_session_redis(session_id)
    from models import SessionAuth
    SessionAuth.query.filter_by(session_id=session_id).delete()
    db.session.commit()
    return response({'message': 'Logged out.'})
