from datetime import datetime
from app import db


class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_plate = db.Column(db.String(20), nullable=False)
    trailer_plate = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(20), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_doc = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    exit_time = db.Column(db.DateTime)
    observations = db.Column(db.Text)

    companions = db.relationship(
        'Companion', back_populates='access_log',
        cascade='all, delete-orphan', order_by='Companion.id'
    )

    @property
    def total_people(self):
        return 1 + len(self.companions)

    @property
    def duration(self):
        end = self.exit_time or datetime.now()
        diff = end - self.entry_time
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes = remainder // 60
        return f'{days}d {hours}h {minutes}m' if days else f'{hours}h {minutes}m'


class Companion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_log_id = db.Column(db.Integer, db.ForeignKey('access_log.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.String(50), nullable=False)
    access_log = db.relationship('AccessLog', back_populates='companions')
