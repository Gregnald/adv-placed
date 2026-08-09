import csv
import io
from celery_app import celery_app
from models import User, Student, Company, Drive, Application


@celery_app.task(name='tasks.generate_csv_task')
def generate_csv_task(entity_type, user_id=None, extra_id=None):
    output = io.StringIO()
    writer = csv.writer(output)

    if entity_type == 'admin_companies':
        headers = ["ID", "Employer Name", "Website", "HR Mail", "Status", "Blacklisted"]
        writer.writerow(headers)
        companies = Company.query.order_by(Company.id.asc()).all()
        for c in companies:
            writer.writerow([c.id, c.employer, c.website, c.hr_mail, c.status, c.blacklisted])

    elif entity_type == 'admin_drives':
        headers = ["ID", "Drive Code", "Company Name", "Job Title", "Start Date", "End Date", "Application Deadline", "Min CGPA", "Status", "Students Participating"]
        writer.writerow(headers)
        drives = Drive.query.order_by(Drive.id.asc()).all()
        for d in drives:
            writer.writerow([d.id, d.drive_id, d.company_name, d.job_title, d.start_date, d.end_date, d.application_deadline, d.min_cgpa, d.status, d.students_participating])

    elif entity_type == 'admin_students':
        headers = ["ID", "Enrollment", "Name", "Course", "Year", "Status", "Blacklisted", "Resume File"]
        writer.writerow(headers)
        students = Student.query.order_by(Student.id.asc()).all()
        for s in students:
            writer.writerow([s.id, s.enrollment, s.name, s.course, s.year, s.status, s.blacklisted, s.resume_file_name])

    elif entity_type == 'admin_reports':
        headers = ["Metric", "Value"]
        writer.writerow(headers)
        companies = Company.query.all()
        students = Student.query.all()
        drives = Drive.query.all()
        writer.writerow(["Total Students", len(students)])
        writer.writerow(["Total Companies", len(companies)])
        writer.writerow(["Total Drives", len(drives)])
        writer.writerow(["Pending Companies", len([c for c in companies if c.status == 'requested'])])
        writer.writerow(["Rejected Drives", len([d for d in drives if d.status == 'Rejected'])])
        writer.writerow(["Approved Drives", len([d for d in drives if d.status == 'Approved'])])
        writer.writerow(["Placed Students", len([s for s in students if s.status.lower() == 'placed'])])
        writer.writerow(["Blacklisted Companies", len([c for c in companies if c.blacklisted])])
        writer.writerow(["Blacklisted Students", len([s for s in students if s.blacklisted])])

    elif entity_type == 'company_drives':
        headers = ["Drive ID", "Job Title", "Status", "Start Date", "End Date", "Application Deadline", "Min CGPA", "Students Participating"]
        writer.writerow(headers)
        user = User.query.get(user_id) if user_id else None
        company = Company.query.filter_by(user_id=user.id).first() if user else None
        if company:
            drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.id.asc()).all()
            for d in drives:
                writer.writerow([d.drive_id, d.job_title, d.status, d.start_date, d.end_date, d.application_deadline, d.min_cgpa, d.students_participating])

    elif entity_type == 'company_applications':
        headers = ["Application ID", "Drive ID", "Student Name", "Status", "Resume File", "Applied At"]
        writer.writerow(headers)
        user = User.query.get(user_id) if user_id else None
        company = Company.query.filter_by(user_id=user.id).first() if user else None
        if company:
            drives = Drive.query.filter_by(company_id=company.id).all()
            drive_ids = [d.id for d in drives]
            query = Application.query.filter(Application.drive_id.in_(drive_ids)) if drive_ids else None
            if query is not None:
                if extra_id:
                    target_drive = Drive.query.filter_by(drive_id=extra_id).first()
                    if target_drive:
                        query = query.filter_by(drive_id=target_drive.id)
                applications = query.all()
                for a in applications:
                    drive_code = a.drive.drive_id if a.drive else ''
                    applied_str = a.applied_at.strftime('%Y-%m-%d %H:%M:%S') if a.applied_at else ''
                    writer.writerow([a.application_id, drive_code, a.student_name, a.status, a.resume_file_name, applied_str])

    elif entity_type == 'student_active_drives':
        headers = ["Drive ID", "Company Name", "Job Title", "Start Date", "End Date", "Deadline", "Status"]
        writer.writerow(headers)
        drives = Drive.query.filter(Drive.status == 'Approved').order_by(Drive.id.asc()).all()
        for d in drives:
            writer.writerow([d.drive_id, d.company_name, d.job_title, d.start_date, d.end_date, d.application_deadline, d.status])

    elif entity_type == 'student_applied_drives':
        headers = ["Application ID", "Drive ID", "Company Name", "Job Title", "Application Status", "Resume File", "Applied At"]
        writer.writerow(headers)
        user = User.query.get(user_id) if user_id else None
        student = Student.query.filter_by(user_id=user.id).first() if user else None
        if student:
            applications = Application.query.filter_by(student_id=student.id).all()
            for a in applications:
                drive_code = a.drive.drive_id if a.drive else ''
                company_name = a.drive.company_name if a.drive else ''
                job_title = a.drive.job_title if a.drive else ''
                applied_str = a.applied_at.strftime('%Y-%m-%d %H:%M:%S') if a.applied_at else ''
                writer.writerow([a.application_id, drive_code, company_name, job_title, a.status, a.resume_file_name, applied_str])

    else:
        writer.writerow(["Error", "Unknown entity type"])

    return output.getvalue()


@celery_app.task(name='tasks.generate_monthly_company_report_task')
def generate_monthly_company_report_task(user_id=None, company_id=None):
    if company_id:
        company = Company.query.get(company_id)
    elif user_id:
        user = User.query.get(user_id) if user_id else None
        company = Company.query.filter_by(user_id=user.id).first() if user else None
    else:
        company = None

    if not company:
        return "<html><body><h1>Error</h1><p>Company profile not found.</p></body></html>"


    drives = Drive.query.filter_by(company_id=company.id).all()
    drive_ids = [d.id for d in drives]
    applications = Application.query.filter(Application.drive_id.in_(drive_ids)).all() if drive_ids else []

    total_apps = len(applications)
    shortlisted = len([a for a in applications if a.status == 'Shortlisted'])
    selected = len([a for a in applications if a.status == 'Selected'])
    rejected = len([a for a in applications if a.status == 'Rejected'])

    selection_rate = f"{(selected / total_apps * 100):.1f}%" if total_apps > 0 else "0.0%"

    rows_html = ""
    for d in drives:
        d_apps = [a for a in applications if a.drive_id == d.id]
        d_selected = len([a for a in d_apps if a.status == 'Selected'])
        rows_html += f"""
        <tr>
            <td>{d.drive_id}</td>
            <td>{d.job_title}</td>
            <td>{d.status}</td>
            <td>{len(d_apps)}</td>
            <td>{d_selected}</td>
        </tr>
        """
    if not drives:
        rows_html = "<tr><td colspan='5' style='text-align:center;'>No placement drives found for this month.</td></tr>"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Monthly Placement Report - {company.employer}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; line-height: 1.6; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; color: #111; }}
        .header p {{ margin: 5px 0 0; color: #666; font-size: 14px; }}
        .summary-grid {{ display: flex; gap: 15px; margin-bottom: 30px; }}
        .card {{ flex: 1; border: 1px solid #ddd; border-radius: 6px; padding: 15px; background: #f9f9f9; text-align: center; }}
        .card h3 {{ margin: 0 0 5px; font-size: 12px; color: #555; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 22px; font-weight: bold; color: #222; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Monthly Placement Performance Report</h1>
        <p><strong>Company:</strong> {company.employer} | <strong>HR Contact:</strong> {company.hr_mail} | <strong>Website:</strong> {company.website or 'N/A'}</p>
    </div>

    <h2>Recruitment Overview</h2>
    <div class="summary-grid">
        <div class="card">
            <h3>Total Drives</h3>
            <p>{len(drives)}</p>
        </div>
        <div class="card">
            <h3>Total Applications</h3>
            <p>{total_apps}</p>
        </div>
        <div class="card">
            <h3>Shortlisted</h3>
            <p>{shortlisted}</p>
        </div>
        <div class="card">
            <h3>Candidates Hired</h3>
            <p>{selected}</p>
        </div>
        <div class="card">
            <h3>Selection Rate</h3>
            <p>{selection_rate}</p>
        </div>
    </div>

    <h2>Drive Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Drive Code</th>
                <th>Job Title</th>
                <th>Drive Status</th>
                <th>Applications Received</th>
                <th>Students Selected</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div class="footer">
        <p>Report generated automatically by Placement Portal Application (PPA V2). Confidential document for official use only.</p>
    </div>
</body>
</html>
"""
    return html_content

