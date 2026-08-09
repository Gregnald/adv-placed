import json
from datetime import date
from uuid import uuid4

import bcrypt
from flask import jsonify, request, Response

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
from redis_client import delete_session_redis, get_session_redis, save_session_redis

IN_MEMORY_TASK_RESULTS = {}


class RedisSessionWrapper:
    def __init__(self, session_id, user_id, user_type):
        self.session_id = session_id
        self.user_id = user_id
        self.user_type = user_type


def response(data, status=200):
    return jsonify(data), status


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def payload():
    return request.get_json(silent=True) or {}


def next_drive_id():
    max_id = 0
    for drive in Drive.query.all():
        digits = ''.join(ch for ch in drive.drive_id if ch.isdigit())
        if digits:
            max_id = max(max_id, int(digits))
    return f'DRV{max_id + 1:03d}'


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
    return f'2026CS{max_id + 1}'


def find_user(username, role=None):
    query = User.query.filter_by(username=username)
    if role:
        query = query.filter_by(role=role)
    return query.first()


def company_for_user(user):
    return Company.query.filter_by(user_id=user.id).first()


def student_for_user(user):
    return Student.query.filter_by(user_id=user.id).first()


def create_session(user):
    SessionAuth.query.filter_by(user_id=user.id).delete()
    session_token = uuid4().hex
    session = SessionAuth(
        session_id=session_token,
        user_id=user.id,
        user_type=user.role,
    )
    db.session.add(session)
    db.session.flush()

    save_session_redis(session_token, user.id, user.role)
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

    redis_sess = get_session_redis(session_id)
    if redis_sess:
        user_id = redis_sess.get('user_id')
        user_type = redis_sess.get('user_type')
        if allowed_roles and user_type not in allowed_roles:
            return None, None, response({'message': 'You are not authorized for this action.'}, 403)

        user = db.session.get(User, user_id)
        if not user:
            return None, None, response({'message': 'Session user not found.'}, 404)

        return RedisSessionWrapper(session_id, user_id, user_type), user, None

    session = SessionAuth.query.filter_by(session_id=session_id).first()
    if not session:
        return None, None, response({'message': 'Invalid session. Please log in again.'}, 401)

    if allowed_roles and session.user_type not in allowed_roles:
        return None, None, response({'message': 'You are not authorized for this action.'}, 403)

    user = db.session.get(User, session.user_id)
    if not user:
        return None, None, response({'message': 'Session user not found.'}, 404)

    save_session_redis(session_id, user.id, user.role)
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
