from flask import Blueprint
from db import db
from dto import company_to_dict, drive_to_dict, student_to_dict
from models import Company, Drive, Student
from routes.common import auth_user, payload, response

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    _, _, error = auth_user(['admin'])
    if error:
        return error

    companies = Company.query.order_by(Company.id.asc()).all()
    students = Student.query.order_by(Student.id.asc()).all()
    drives = Drive.query.order_by(Drive.id.asc()).all()

    def is_placed(s):
        if (s.status or '').lower() == 'placed':
            return True
        return any((app.status or '').lower() in ['selected', 'placed'] for app in s.applications)

    placed_count = len([s for s in students if is_placed(s)])
    unplaced_count = len(students) - placed_count

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
            'approvedCompanies': len([company for company in companies if company.status == 'approved']),
            'rejectedDrives': len([drive for drive in drives if drive.status == 'Rejected']),
            'approvedDrives': len([drive for drive in drives if drive.status == 'Approved']),
            'pendingDrives': len([drive for drive in drives if drive.status == 'Pending']),
            'placedStudents': placed_count,
            'unplacedStudents': unplaced_count,
            'blacklistedCompanies': len([company for company in companies if company.blacklisted]),
            'blacklistedStudents': len([student for student in students if student.blacklisted]),
        }
    })


@admin_bp.route('/api/admin/companies/<string:company_name>', methods=['PATCH'])
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


@admin_bp.route('/api/admin/students/<string:enrollment>', methods=['PATCH'])
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


@admin_bp.route('/api/admin/drives/<string:drive_code>', methods=['PATCH'])
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
