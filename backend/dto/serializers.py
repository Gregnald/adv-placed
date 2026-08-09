import json
from datetime import date, datetime


def _json_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(',') if item.strip()]
    return []


def list_to_json(value):
    return json.dumps(value if isinstance(value, list) else [])


def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'role': user.role
    }


def session_to_dict(session):
    return {
        'sessionId': session.session_id,
        'userId': session.user_id,
        'userType': session.user_type
    }


def student_to_dict(student):
    fn = getattr(student, 'first_name', '') or ''
    sn = getattr(student, 'surname', '') or ''
    uname = getattr(student, 'username', '') or (student.user.username if getattr(student, 'user', None) else '')
    full_name = f"{fn} {sn}".strip() if (fn or sn) else uname

    st_status = student.status
    if getattr(student, 'applications', None):
        if any((app.status or '').lower() in ['selected', 'placed'] for app in student.applications):
            st_status = 'Placed'

    return {
        'id': student.id,
        'userId': student.user_id,
        'enrollment': student.enrollment,
        'username': uname,
        'name': full_name,
        'firstName': fn,
        'surname': sn,
        'email': getattr(student, 'email', '') or '',
        'course': student.course,
        'year': student.year,
        'status': st_status,
        'blacklisted': student.blacklisted,
        'resumeFileName': student.resume_file_name
    }






def company_to_dict(company):
    return {
        'id': company.id,
        'userId': company.user_id,
        'employer': company.employer,
        'website': company.website,
        'hr_mail': company.hr_mail,
        'status': company.status,
        'blacklisted': company.blacklisted
    }


def drive_to_dict(drive, include_applications=False):
    payload = {
        'id': drive.id,
        'driveId': drive.drive_id,
        'companyId': drive.company_id,
        'companyName': drive.company_name,
        'jobTitle': drive.job_title,
        'jobDescription': drive.job_description,
        'jobCompensation': drive.job_compensation,
        'startDate': drive.start_date,
        'endDate': drive.end_date,
        'applicationDeadline': drive.application_deadline,
        'minCgpa': drive.min_cgpa,
        'eligibleBranches': _json_list(drive.eligible_branches),
        'eligibleYears': _json_list(drive.eligible_years),
        'companyWebsite': drive.company_website,
        'hrMail': drive.hr_mail,
        'status': drive.status,
        'studentsParticipating': drive.students_participating,
        'jdInfo': {
            'jobTitle': drive.job_title,
            'jobDescription': drive.job_description,
            'jobCompensation': drive.job_compensation,
            'companyWebsite': drive.company_website,
            'hrMail': drive.hr_mail
        }
    }
    if include_applications:
        payload['applications'] = [application_to_dict(application) for application in drive.applications]
    return payload


def application_to_dict(application):
    return {
        'id': application.id,
        'applicationId': application.application_id,
        'driveId': application.drive.drive_id if application.drive else None,
        'studentId': application.student_id,
        'studentName': application.student_name,
        'resume': application.resume_file_name,
        'status': application.status,
        'interviewDate': getattr(application, 'interview_date', '') or '',
        'appliedAt': application.applied_at.isoformat()
    }


def drive_for_student(drive, application=None):
    today = date.today()
    start = datetime.fromisoformat(f'{drive.start_date}T00:00:00').date()
    end = datetime.fromisoformat(f'{drive.end_date}T00:00:00').date()
    
    # Compare just the date parts, treating start and end dates as inclusive
    if end < today:
        visibility = 'Past'
    elif start <= today <= end:
        visibility = 'Active'
    else:
        visibility = 'Upcoming'

    payload = drive_to_dict(drive)
    payload['visibility'] = visibility
    if application:
        payload['applied'] = True
        payload['applicationStatus'] = application.status
        payload['interviewDate'] = getattr(application, 'interview_date', '') or ''
        payload['appliedResume'] = application.resume_file_name
        payload['accepted'] = application.status == 'Selected'
    else:
        payload['applied'] = False
        payload['accepted'] = False
        payload['interviewDate'] = ''
    return payload