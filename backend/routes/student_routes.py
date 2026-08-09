from flask import Blueprint
from db import db
from dto import application_to_dict, drive_for_student, student_to_dict
from models import Application, Drive, Student
from routes.common import (
    auth_user,
    next_application_id,
    payload,
    response,
    student_for_user,
)

student_bp = Blueprint('student_bp', __name__)


@student_bp.route('/api/student/dashboard', methods=['GET'])
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


@student_bp.route('/api/student/profile', methods=['PATCH'])
def update_student_profile():
    _, user, error = auth_user(['student'])
    if error:
        return error

    student = student_for_user(user)
    if not student:
        return response({'message': 'Student profile not found.'}, 404)

    data = payload()
    if 'firstName' in data or 'first_name' in data:
        student.first_name = (data.get('firstName') or data.get('first_name') or '').strip().title()
    if 'surname' in data or 'last_name' in data:
        student.surname = (data.get('surname') or data.get('last_name') or '').strip().title()
    if 'username' in data:
        student.username = data['username'].strip()

    if 'enrollment' in data:
        new_enrollment = data['enrollment'].strip()
        if new_enrollment:
            existing = Student.query.filter(Student.enrollment == new_enrollment, Student.id != student.id).first()
            if existing:
                return response({'message': 'Enrollment number is already in use.'}, 400)
            student.enrollment = new_enrollment

    for key in ['email', 'course', 'year', 'status', 'resumeFileName']:
        if key in data:
            setattr(student, 'resume_file_name' if key == 'resumeFileName' else key, data[key])

    db.session.commit()
    return response({'profile': student_to_dict(student)})


@student_bp.route('/api/drives/<string:drive_code>/apply', methods=['POST'])
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

    if student.blacklisted or (student.status or '').lower() != 'active':
        return response({'message': 'Only active students can apply to placement drives.'}, 403)

    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        existing.resume_file_name = resume or student.resume_file_name
        existing.status = 'Applied'
        db.session.commit()
        return response({'application': application_to_dict(existing)})

    full_student_name = f"{student.first_name} {student.surname}".strip() or student.username
    application = Application(
        application_id=next_application_id(),
        drive_id=drive.id,
        student_id=student.id,
        student_name=full_student_name,
        resume_file_name=resume or student.resume_file_name,
        status='Applied'
    )

    drive.students_participating = (drive.students_participating or 0) + 1
    db.session.add(application)
    db.session.commit()
    return response({'application': application_to_dict(application)}, 201)
