import os
import datetime
from datetime import time 
import cv2

from flask import Flask, request, url_for, redirect, render_template, send_from_directory, abort, session, make_response
from flask_bootstrap import Bootstrap

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

from jinja2 import Environment, FileSystemLoader

from uuid import uuid4


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/data/pero_quality_web_data/database.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['CROPS_PATH'] = '/mnt/data/pero_quality_web_data/crops'
    bootstrap = Bootstrap(app)

    print(app.config['SQLALCHEMY_DATABASE_URI'])
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    file_loader = FileSystemLoader(
            [os.path.join(os.path.dirname(__file__), "templates"),
             os.path.join(os.path.dirname(__file__), "posts"),
             os.path.join(os.path.dirname(__file__), "")])
    env = Environment(loader=file_loader)

    init_db(engine)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

def init_db(engine):
    from app.db import Base
    Base.metadata.create_all(bind=engine)
