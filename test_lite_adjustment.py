import os
import tempfile

fd, db_path = tempfile.mkstemp(suffix='.db')
os.close(fd)
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

from app import create_app, db
from app.models import AccessLog

app = create_app()
app.config['TESTING'] = True
with app.app_context():
    db.create_all()
    db.session.add(AccessLog(
        vehicle_plate='BB-22-33', vehicle_type='pesado',
        driver_name='Condutor anterior', driver_doc='111',
        company='Empresa anterior'
    ))
    db.session.commit()

client = app.test_client()
response = client.post('/access/new', data={
    'vehicle_plate': 'bb-22-33',
    'company': 'Empresa nova',
    'driver_name': 'Condutor novo',
    'driver_doc': '222',
}, follow_redirects=True)
assert response.status_code == 200
with app.app_context():
    logs = AccessLog.query.order_by(AccessLog.id).all()
    assert logs[-1].vehicle_type == 'pesado'
    assert logs[-1].trailer_plate is None
    assert logs[-1].company == 'Empresa nova'

client.post('/access/new', data={
    'vehicle_plate': 'CC-33-44',
    'company': 'Empresa nova',
    'driver_name': 'Outro condutor',
    'driver_doc': '333',
})
with app.app_context():
    assert AccessLog.query.filter_by(vehicle_plate='CC-33-44').one().vehicle_type == 'pesado'

pdf = client.get('/report/pdf')
assert pdf.status_code == 200 and pdf.data.startswith(b'%PDF')
with app.app_context():
    db.drop_all()
os.unlink(db_path)
print('lite_adjustment: OK')
