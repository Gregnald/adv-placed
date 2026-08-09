from uuid import uuid4
from flask import Blueprint
import tasks
from db import db
from dto import application_to_dict, company_to_dict, drive_to_dict, list_to_json
from models import Application, Company, Drive
from routes.common import IN_MEMORY_TASK_RESULTS, auth_user, company_for_user, next_drive_id, payload, response

company_bp = Blueprint('company_bp', __name__)


@company_bp.route('/api/company/dashboard', methods=['GET'])
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


@company_bp.route('/api/company/profile', methods=['PATCH'])
def update_company_profile():
    _, user, error = auth_user(['company'])
    if error:
        return error

    company = company_for_user(user)
    if not company:
        return response({'message': 'Company profile not found.'}, 404)

    if company.blacklisted:
        return response({'message': 'Blacklisted companies cannot toggle status.'}, 403)

    data = payload()
    if 'status' in data:
        new_status = data['status'].strip().lower()
        if new_status in ['active', 'inactive']:
            company.status = new_status
        else:
            return response({'message': 'Invalid status choice.'}, 400)

    if 'hr_mail' in data or 'hrMail' in data:
        company.hr_mail = (data.get('hr_mail') or data.get('hrMail') or '').strip()
    if 'website' in data:
        company.website = data['website'].strip()

    db.session.commit()
    return response({'company': company_to_dict(company)})


@company_bp.route('/api/company/drives', methods=['POST'])
def create_company_drive():
    _, user, error = auth_user(['company'])
    if error:
        return error

    company = company_for_user(user)
    if not company:
        return response({'message': 'Company profile not found.'}, 404)

    if company.blacklisted or (company.status or '').lower() != 'active':
        return response({'message': 'Only active companies can create placement drives.'}, 403)

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


@company_bp.route('/api/applications/<string:application_code>', methods=['PATCH'])
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
        if application.student:
            if (data['status'] or '').lower() in ['selected', 'placed']:
                application.student.status = 'Placed'
            else:
                has_other_selected = any(
                    (a.status or '').lower() in ['selected', 'placed']
                    for a in application.student.applications
                    if a.id != application.id
                )
                if not has_other_selected and (application.student.status or '').lower() == 'placed':
                    application.student.status = 'Active'

    if 'interviewDate' in data or 'interview_date' in data:
        application.interview_date = (data.get('interviewDate') or data.get('interview_date') or '').strip()
    db.session.commit()
    return response({'application': application_to_dict(application)})


@company_bp.route('/api/company/report/generate', methods=['POST'])
def generate_company_monthly_report():
    session, user, error = auth_user(['company', 'admin'])
    if error:
        return error

    data = payload()
    req_company_id = data.get('company_id')

    if user.role == 'company':
        target_user_id = user.id
        target_company_id = None
    else:
        target_user_id = None
        target_company_id = req_company_id
        if not target_company_id:
            return response({'message': 'Company ID is required for admin report generation.'}, 400)

    task_id = str(uuid4())
    try:
        html_content = tasks.generate_monthly_company_report_task(user_id=target_user_id, company_id=target_company_id)
        IN_MEMORY_TASK_RESULTS[task_id] = html_content
    except Exception as e:
        return response({'message': f'Failed to generate report: {str(e)}'}, 500)

    return response({'message': 'Company monthly report generated.', 'taskId': task_id}, 202)


@company_bp.route('/api/company/report/download/<string:task_id>', methods=['GET'])
def download_company_monthly_report(task_id):
    _, _, error = auth_user(['company', 'admin'])
    if error:
        return error

    html_content = IN_MEMORY_TASK_RESULTS.get(task_id)
    if html_content is None:
        try:
            async_result = tasks.generate_monthly_company_report_task.AsyncResult(task_id)
            if async_result.ready():
                html_content = async_result.result
            else:
                html_content = async_result.get(timeout=2)
        except Exception:
            pass

    if html_content is None:
        return response({'message': 'Report file not ready or task failed.'}, 404)

    from flask import Response
    return Response(
        html_content,
        mimetype='text/html',
        headers={
            'Content-Disposition': f'attachment; filename=monthly_report_{task_id[:8]}.html',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )
