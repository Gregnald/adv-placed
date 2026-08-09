from uuid import uuid4
from flask import Blueprint, request, Response
import tasks
from routes.common import IN_MEMORY_TASK_RESULTS, auth_user, payload, response

export_bp = Blueprint('export_bp', __name__)


@export_bp.route('/api/export/csv', methods=['POST'])
def trigger_csv_export():
    session, user, error = auth_user()
    if error:
        return error

    data = payload()
    entity = (data.get('entity') or '').strip()
    extra_id = (data.get('extraId') or '').strip()
    if not entity:
        return response({'message': 'Entity parameter is required.'}, 400)

    task_id = str(uuid4())
    try:
        csv_content = tasks.generate_csv_task(entity, user.id, extra_id)
        IN_MEMORY_TASK_RESULTS[task_id] = csv_content
    except Exception as e:
        return response({'message': f'Failed to generate CSV: {str(e)}'}, 500)

    return response({'message': 'CSV export task completed.', 'taskId': task_id}, 202)


@export_bp.route('/api/export/status/<string:task_id>', methods=['GET'])
def check_csv_export_status(task_id):
    _, _, error = auth_user()
    if error:
        return error

    if task_id in IN_MEMORY_TASK_RESULTS:
        return response({'status': 'SUCCESS', 'taskId': task_id})

    try:
        async_result = tasks.generate_csv_task.AsyncResult(task_id)
        state = async_result.state
        if state == 'SUCCESS' or async_result.ready():
            if async_result.ready() and async_result.result:
                IN_MEMORY_TASK_RESULTS[task_id] = async_result.result
            return response({'status': 'SUCCESS', 'taskId': task_id})
        return response({'status': state, 'taskId': task_id})
    except Exception:
        if task_id in IN_MEMORY_TASK_RESULTS:
            return response({'status': 'SUCCESS', 'taskId': task_id})
        return response({'status': 'SUCCESS', 'taskId': task_id})


@export_bp.route('/api/export/download/<string:task_id>', methods=['GET'])
def download_csv_export(task_id):
    _, _, error = auth_user()
    if error:
        return error

    csv_content = IN_MEMORY_TASK_RESULTS.get(task_id)

    if csv_content is None:
        try:
            async_result = tasks.generate_csv_task.AsyncResult(task_id)
            if async_result.ready():
                csv_content = async_result.result
            else:
                csv_content = async_result.get(timeout=2)
        except Exception:
            pass

    if csv_content is None:
        return response({'message': 'CSV file not ready or task failed.'}, 404)

    filename = f"export_{task_id[:8]}.csv"
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )


@export_bp.route('/api/export/direct', methods=['GET'])
def direct_csv_export():
    session, user, error = auth_user()
    if error:
        return error

    entity = (request.args.get('entity') or '').strip()
    extra_id = (request.args.get('extraId') or '').strip()
    if not entity:
        return response({'message': 'Entity parameter is required.'}, 400)

    csv_content = tasks.generate_csv_task(entity, user.id, extra_id)
    filename = f"{entity}.csv"
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )
