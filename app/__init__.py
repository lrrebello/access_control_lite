from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy import inspect, text


db = SQLAlchemy()
load_dotenv()


def ensure_lite_schema():
    inspector = inspect(db.engine)
    if 'access_log' not in inspector.get_table_names():
        return

    columns = {column['name'] for column in inspector.get_columns('access_log')}
    additions = {
        'product': "VARCHAR(150) NOT NULL DEFAULT ''",
        'destination': "VARCHAR(150) NOT NULL DEFAULT ''",
        'movement': "VARCHAR(40) NOT NULL DEFAULT ''",
    }
    with db.engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f'ALTER TABLE access_log ADD COLUMN {name} {definition}'))
        connection.execute(text(
            "UPDATE access_log SET product = COALESCE(NULLIF(product, ''), company) "
            "WHERE product IS NULL OR product = ''"
        ))


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'access-control-lite')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///lite.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_lite_schema()

    from app.main import main
    from app.reports import reports
    app.register_blueprint(main)
    app.register_blueprint(reports)

    return app
