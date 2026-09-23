from datetime import datetime

from flask import jsonify, redirect, render_template, request, url_for, flash

from app import db
from app.main import main
from app.models import AccessLog, Companion


@main.app_template_filter('nl2br')
def nl2br_filter(value):
    return (value or '').replace('\n', '<br>\n')


@main.route('/')
@main.route('/dashboard')
def dashboard():
    filter_type = request.args.get('filter', 'active')
    search_query = request.args.get('search', '').strip()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59)

    query = AccessLog.query
    if search_query:
        query = query.filter(
            (AccessLog.vehicle_plate.ilike(f'%{search_query}%')) |
            (AccessLog.driver_name.ilike(f'%{search_query}%')) |
            (AccessLog.company.ilike(f'%{search_query}%'))
        )

    if filter_type == 'active':
        query = query.filter(AccessLog.exit_time.is_(None))
    elif filter_type == 'today_entries':
        query = query.filter(AccessLog.entry_time.between(today_start, today_end))
    elif filter_type == 'today_exits':
        query = query.filter(
            AccessLog.exit_time.is_not(None),
            AccessLog.exit_time.between(today_start, today_end)
        )
    elif filter_type == 'finished':
        query = query.filter(AccessLog.exit_time.is_not(None))

    logs = query.order_by(AccessLog.entry_time.desc()).all()
    active_logs = AccessLog.query.filter(AccessLog.exit_time.is_(None)).all()
    today_entries = AccessLog.query.filter(AccessLog.entry_time.between(today_start, today_end)).count()
    today_exits = AccessLog.query.filter(
        AccessLog.exit_time.is_not(None),
        AccessLog.exit_time.between(today_start, today_end)
    ).count()

    return render_template(
        'main/dashboard.html', logs=logs, filter_type=filter_type,
        search_query=search_query, total_active=len(active_logs),
        people_inside=sum(log.total_people for log in active_logs),
        today_entries=today_entries, today_exits=today_exits,
    )


@main.route('/access/lookup')
def lookup_access_data():
    plate = request.args.get('plate', '').strip().upper()
    if not plate or plate == 'PEDESTRE':
        return jsonify({'found': False})

    last_access = AccessLog.query.filter_by(vehicle_plate=plate).order_by(
        AccessLog.entry_time.desc()
    ).first()
    if not last_access:
        return jsonify({'found': False})

    return jsonify({
        'found': True,
        'vehicle_type': last_access.vehicle_type,
        'company': last_access.company or '',
        'driver_name': last_access.driver_name,
        'driver_doc': last_access.driver_doc,
    })


@main.route('/access/new', methods=['POST'])
def new_access():
    vehicle_plate = request.form.get('vehicle_plate', '').strip().upper()
    last_access = AccessLog.query.filter_by(vehicle_plate=vehicle_plate).order_by(
        AccessLog.entry_time.desc()
    ).first() if vehicle_plate else None
    vehicle_type = request.form.get('vehicle_type') or (
        last_access.vehicle_type if last_access else 'pesado'
    )
    if vehicle_type == 'pedestre':
        vehicle_plate = 'PEDESTRE'
    trailer_plate = None
    driver_name = request.form.get('driver_name', '').strip()
    driver_doc = request.form.get('driver_doc', '').strip()
    company = request.form.get('company', '').strip() or 'Não informada'

    if vehicle_type != 'pedestre' and not vehicle_plate:
        flash('A matrícula é obrigatória para veículos.', 'danger')
        return redirect(url_for('main.dashboard'))
    if not driver_name or not driver_doc:
        flash('Nome e documento são obrigatórios.', 'danger')
        return redirect(url_for('main.dashboard'))

    log = AccessLog(
        vehicle_plate=vehicle_plate, trailer_plate=trailer_plate,
        vehicle_type=vehicle_type, driver_name=driver_name,
        driver_doc=driver_doc, company=company,
        observations=request.form.get('observations', '').strip() or None,
    )
    db.session.add(log)
    db.session.flush()

    names = request.form.getlist('companion_name[]')
    docs = request.form.getlist('companion_doc[]')
    for name, document in zip(names, docs):
        if name.strip() and document.strip():
            db.session.add(Companion(
                access_log_id=log.id,
                name=name.strip(), document=document.strip()
            ))

    db.session.commit()
    flash('Entrada registrada com sucesso.', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/access/exit/<int:log_id>', methods=['POST'])
def exit_access(log_id):
    log = AccessLog.query.get_or_404(log_id)
    if not log.exit_time:
        log.exit_time = datetime.now()
        db.session.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/access/remove_exit/<int:log_id>', methods=['POST'])
def remove_exit(log_id):
    log = AccessLog.query.get_or_404(log_id)
    log.exit_time = None
    db.session.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/access/edit/<int:log_id>', methods=['GET', 'POST'])
def edit_access(log_id):
    log = AccessLog.query.get_or_404(log_id)
    if request.method == 'POST':
        log.vehicle_plate = request.form.get('vehicle_plate', '').strip().upper()
        log.trailer_plate = request.form.get('trailer_plate', '').strip().upper() or None
        log.vehicle_type = request.form.get('vehicle_type', 'ligeiro')
        log.driver_name = request.form.get('driver_name', '').strip()
        log.driver_doc = request.form.get('driver_doc', '').strip()
        log.company = request.form.get('company', '').strip() or 'Não informada'
        log.observations = request.form.get('observations', '').strip() or None
        entry_time = request.form.get('entry_time')
        exit_time = request.form.get('exit_time')
        if entry_time:
            log.entry_time = datetime.strptime(entry_time, '%Y-%m-%dT%H:%M')
        log.exit_time = datetime.strptime(exit_time, '%Y-%m-%dT%H:%M') if exit_time else None

        Companion.query.filter_by(access_log_id=log.id).delete()
        for name, document in zip(
            request.form.getlist('companion_name[]'),
            request.form.getlist('companion_doc[]')
        ):
            if name.strip() and document.strip():
                db.session.add(Companion(
                    access_log_id=log.id,
                    name=name.strip(), document=document.strip()
                ))
        db.session.commit()
        flash('Registro atualizado com sucesso.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('main/edit_access.html', log=log)
