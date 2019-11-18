import os
import json
import datetime
from datetime import time

import cv2
import numpy as np

from flask import Flask, request, url_for, redirect, render_template, send_from_directory, abort, session, make_response, jsonify
from flask import request
from flask_bootstrap import Bootstrap

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop
from app import create_app

from jinja2 import Environment, FileSystemLoader

from uuid import uuid4

from app.main import bp

from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = create_app()

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                       convert_unicode=True,
                       connect_args={'check_same_thread': False})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

def user_cookie():
    user = None
    if 'uid' in session:
        user = User.query.filter(User.cookie_id==str(session['uid'])).first()
    if user is None:
        session['uid'] = uuid4()
        data = User(str(session['uid']))
        db_session.add(data)
        db_session.commit()
        user = User.query.filter(User.cookie_id==str(session['uid'])).first()

    return user

def add_annotation(user_id, record_id, annotation, annotation_time, user_info):
    db_ann = Annotation(user_id, record_id, annotation, annotation_time, user_info)
    db_session.add(db_ann)
    db_session.commit()


@bp.route('/language/<lang>')
def get_language(lang):    
    path = urlparse(request.headers['Referer']).path
    request.cookies.get("language")

    resp = make_response(redirect(path))
    resp.set_cookie('language', lang, expires=(datetime.datetime.now()+datetime.timedelta(days=365)))

    return resp


@bp.route('/get_crop/<crop_id>')
def get_crop(crop_id):
    crop_id = int(crop_id)
    crop = Crop.query.get(crop_id)
    page = Page.query.get(crop.page_id)

    image = cv2.imread(page.path)

    image = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tobytes()

    response = make_response(image, 200, {'Content-type': 'image/jpeg'})
    return response

@bp.route('/navbar')
def navbar():
    user = user_cookie()
    return render_template('navbar.html')

@bp.route('/')
def index():
    user = user_cookie()
    crops = []
    set_comp = Set.query.filter(Set.id==2, Set.active==True).first()
    if set_comp is not None:
        record = Record.query.filter(Record.set_id==set_comp.id).first()
        record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
        crops.append(record_crop.crop_id)
    set_ratg = Set.query.filter(Set.id==1, Set.active==True).first()
    if set_ratg is not None:
        record = Record.query.filter(Record.set_id==set_ratg.id).first()
        record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
        crops.append(record_crop.crop_id)

    if request.cookies.get("language") == "en":
        resp = make_response(render_template('index.html', set_comp=set_comp, set_ratg=set_ratg, crops=crops))
    elif request.cookies.get("language") == "cz":
        resp = make_response(render_template('index_cz.html', set_comp=set_comp, set_ratg=set_ratg, crops=crops))
    else:
        resp = make_response(render_template('index_cz.html', set_comp=set_comp, set_ratg=set_ratg, crops=crops))
        resp.set_cookie('language', 'cz', expires=(datetime.datetime.now()+datetime.timedelta(days=365)))
    
    if request.cookies.get("annotated") == None:
        resp.set_cookie('annotated', '0', expires=(datetime.datetime.now()+datetime.timedelta(hours=1)))

    return resp 

@bp.route('/datasets')
def show_datasets():
    user = user_cookie()
    set_1 = Set.query.filter(Set.type==0, Set.active==True).all()
    set_1_crops = []
    for i, set_ in enumerate(set_1):
        record = Record.query.filter(Record.set_id==set_.id).first()
        record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
        set_1_crops.append(record_crop.crop_id)

    set_2 = Set.query.filter(Set.type==1, Set.active==True).all()
    set_2_crops = []
    for i, set_ in enumerate(set_2):
        record = Record.query.filter(Record.set_id==set_.id).first()
        record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
        set_2_crops.append(record_crop.crop_id)

    set_3 = Set.query.filter(Set.type==2, Set.active==True).all()
    set_3_crops = []
    for i, set_ in enumerate(set_3):
        record = Record.query.filter(Record.set_id==set_.id).first()
        record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
        set_3_crops.append(record_crop.crop_id)

    if request.cookies.get("language") == "en":
        resp = make_response(render_template("datasets.html", set_1=enumerate(set_1), set_2=enumerate(set_2), set_3=enumerate(set_3), 
                                              set_1_crops=set_1_crops, set_2_crops=set_2_crops, set_3_crops=set_3_crops))
    elif request.cookies.get("language") == "cz":
        resp = make_response(render_template("datasets_cz.html", set_1=enumerate(set_1), set_2=enumerate(set_2), set_3=enumerate(set_3), 
                                              set_1_crops=set_1_crops, set_2_crops=set_2_crops, set_3_crops=set_3_crops))
    else:
        resp = make_response(render_template("datasets_cz.html", set_1=enumerate(set_1), set_2=enumerate(set_2), set_3=enumerate(set_3), 
                                              set_1_crops=set_1_crops, set_2_crops=set_2_crops, set_3_crops=set_3_crops))
        resp.set_cookie('language', 'cz', expires=(datetime.datetime.now()+datetime.timedelta(days=365)))

    if request.cookies.get("annotated") == None:
        resp.set_cookie('annotated', '0', expires=(datetime.datetime.now()+datetime.timedelta(hours=1)))
    return resp


@bp.route('/comparing_help/<set>')
def show_comparing_help(set):
    user = user_cookie()
    set_obj = Set.query.filter(Set.id==set).first()
    if request.cookies.get("language") == "en":
        resp = make_response(render_template("comparing_help.html", set_obj=set_obj, set=set))
    elif request.cookies.get("language") == "cz":
        resp = make_response(render_template("comparing_help_cz.html", set_obj=set_obj, set=set))
    else:
        resp = make_response(render_template("comparing_help_cz.html", set_obj=set_obj, set=set))
        resp.set_cookie('language', 'cz', expires=(datetime.datetime.now()+datetime.timedelta(days=365)))

    if request.cookies.get("annotated") == None:
        resp.set_cookie('annotated', '0', expires=(datetime.datetime.now()+datetime.timedelta(hours=1)))
    return resp


@bp.route('/comparing/<set_id>', methods=['GET', 'POST'])
def show_comparing(set_id):
    user = user_cookie()
    if request.method == 'POST':
        if request.form['annotated'] == 'true':
            annotated = 0
        else:
            print(request.form)
            time_ = time(int(request.form['hour']), int(request.form['min']), int(request.form['sec']),
                         int(request.form['milisec'])*10000)

            if request.form['mobile'] == "true":
                user_info = json.dumps({"os": str(request.form['os']), "b": str(request.form['browser']), 
                                        "m": True, "ss": str(request.form['screen_size']),
                                        "bs": str(request.form['browser_size']), 
                                        "is": str(request.form['image_size'])})
            else:
                user_info = json.dumps({"os": str(request.form['os']), "b": str(request.form['browser']),
                                        "m": False, "ss": str(request.form['screen_size']),
                                        "bs": str(request.form['browser_size']), 
                                        "is": str(request.form['image_size'])})

            if '0' in request.form:
                add_annotation(user.id, request.form['record'], '01', time_, user_info)
            elif '1' in request.form:
                add_annotation(user.id, request.form['record'], '10', time_, user_info)

        if request.cookies.get("annotated") != None:
            annotated = int(request.cookies.get("annotated")) + 1
        else:
            annotated = 0

        if request.form['annotated'] == 'true':
            annotated = 0
    else:
        if request.cookies.get("annotated") != None:
            annotated = int(request.cookies.get("annotated"))
        else:
            annotated = 0

    set_ = Set.query.get(set_id)
    if set_.type != 0 or set_.active == False:
        abort(404)

    rnd_record = db_session.query(Record).filter(Record.set_id==set_id).order_by(Record.position.desc()).first()
    rnd_record.position -= 10000 + int(np.random.normal(0, 10, 1)[0])
    db_session.commit()
    record_crops = db_session.query(RecordCrop).filter(RecordCrop.record_id==rnd_record.id).order_by(RecordCrop.order).all()
    
    if annotated >= 50:
        if request.cookies.get("language") == "en":
            resp = make_response(render_template("done.html"))
        elif request.cookies.get("language") == "cz":
            resp = make_response(render_template("done_cz.html"))
        else:
            resp = make_response(render_template("done_cz.html"))
            resp.set_cookie('language', 'cz', expires=(datetime.datetime.now()+datetime.timedelta(days=365)))
        resp.set_cookie('annotated', '0', expires=(datetime.datetime.now()+datetime.timedelta(hours=1)))
    else:
        if request.cookies.get("language") == "en":
            resp = make_response(render_template("comparing.html", record_id=rnd_record.id, record_crops=enumerate(record_crops), set_=set_, annotated=annotated))
        elif request.cookies.get("language") == "cz":
            resp = make_response(render_template("comparing_cz.html", record_id=rnd_record.id, record_crops=enumerate(record_crops), set_=set_, annotated=annotated))
        else:
            resp = make_response(render_template("comparing_cz.html", record_id=rnd_record.id, record_crops=enumerate(record_crops), set_=set_, annotated=annotated))
            resp.set_cookie('language', 'cz', expires=(datetime.datetime.now()+datetime.timedelta(days=365)))
        resp.set_cookie('annotated', str(annotated), expires=(datetime.datetime.now()+datetime.timedelta(hours=1)))

    return resp


@bp.route('/img/<filename>')
def send_file(filename):
    return send_from_directory(app.config['CROPS_PATH'], filename)
