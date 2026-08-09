from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.common import ensure_admin_account
from routes.company_routes import company_bp
from routes.export_routes import export_bp
from routes.student_routes import student_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(export_bp)


__all__ = ['register_routes', 'ensure_admin_account']
