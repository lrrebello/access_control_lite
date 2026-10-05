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

client = app.test_client()
assert client.get('/').status_code == 200

response = client.post('/access/new', data={
    'vehicle_plate': 'aa-12-34',
    'vehicle_type': 'ligeiro',
    'company': 'Empresa Teste',
    'driver_name': 'João Silva',
    'driver_doc': '123456789',
    'companion_name[]': ['Maria'],
    'companion_doc[]': ['987654321'],
    'observations': 'Entrada teste',
}, follow_redirects=True)
assert response.status_code == 200

with app.app_context():
    log = AccessLog.query.one()
    assert log.vehicle_plate == 'AA-12-34'
    assert log.total_people == 2
    log_id = log.id

lookup = client.get('/access/lookup?plate=aa-12-34')
assert lookup.json['found'] is True
assert lookup.json['driver_name'] == 'João Silva'
assert lookup.json['driver_doc'] == '123456789'

pdf = client.get('/report/pdf')
assert pdf.status_code == 200
assert pdf.mimetype == 'application/pdf'
assert pdf.data.startswith(b'%PDF')

exit_response = client.post(f'/access/exit/{log_id}', follow_redirects=True)
assert exit_response.status_code == 200
with app.app_context():
    assert AccessLog.query.one().exit_time is not None

with app.app_context():
    db.drop_all()
os.unlink(db_path)
print('lite_flow: OK')
