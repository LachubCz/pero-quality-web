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

from app.main import bp

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
engine = create_engine('sqlite:///database.sqlite3',
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

def add_annotation(user_id, record_id, annotation, annotation_time):
    db_ann = Annotation(user_id, record_id, annotation, annotation_time)
    db_session.add(db_ann)
    db_session.commit()

@bp.route('/get_crop/<crop_id>')
def get_crop(crop_id):
    crop_id = int(crop_id)
    crop = Crop.query.get(crop_id)

    if crop.cropped:
        filename = str(crop.id)+'.jpg'
        image = cv2.imread(os.path.join('./app/static/crops', filename))
    else:
        page = Page.query.get(crop.page_id)
        image = cv2.imread(page.path)
        image = image[crop.y:crop.y+crop.height, crop.x:crop.x+crop.width]
        if not os.path.exists('./app/static/crops'):
            os.makedirs('./app/static/crops')
        cv2.imwrite(os.path.join('./app/static/crops', str(crop.id)+'.jpg'), image)
        crop.cropped = True
        db_session.commit()

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
    set_comp = Set.query.filter(Set.type==0, Set.active==True).first()
    record = Record.query.filter(Record.set_id==set_comp.id).first()
    record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
    crops.append(record_crop.crop_id)
    set_ratg = Set.query.filter(Set.type==2, Set.active==True).first()
    record = Record.query.filter(Record.set_id==set_ratg.id).first()
    record_crop = RecordCrop.query.filter(RecordCrop.record_id==record.id, RecordCrop.order==0).first()
    crops.append(record_crop.crop_id)
    return render_template('index.html', set_comp=set_comp, set_ratg=set_ratg, crops=crops)

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

    return render_template("datasets.html", set_1=enumerate(set_1), set_2=enumerate(set_2), set_3=enumerate(set_3), 
                           set_1_crops=set_1_crops, set_2_crops=set_2_crops, set_3_crops=set_3_crops)

@bp.route('/comparing_help/<set>')
def show_comparing_help(set):
    user = user_cookie()
    return render_template("comparing_help.html", set=set)

@bp.route('/ordering_help/<set>')
def show_ordering_help(set):
    user = user_cookie()
    return render_template("ordering_help.html", set=set)

@bp.route('/rating_help/<set>')
def show_rating_help(set):
    user = user_cookie()
    return render_template("rating_help.html", set=set)

@bp.route('/comparing_sets')
def show_comparing_sets():
    user = user_cookie()
    set_ = Set.query.filter(Set.type==0, Set.active==True).all()
    return render_template("comparing_sets.html", sets=set_)

@bp.route('/ordering_sets')
def show_ordering_sets():
    user = user_cookie()
    set_ = Set.query.filter(Set.type==1, Set.active==True).all()
    return render_template("ordering_sets.html", sets=set_)

@bp.route('/rating_sets')
def show_rating_sets():
    user = user_cookie()
    set_ = Set.query.filter(Set.type==2, Set.active==True).all()
    return render_template("rating_sets.html", sets=set_)

@bp.route('/comparing/<set_id>', methods=['GET', 'POST'])
def show_comparing(set_id):
    user = user_cookie()
    if request.method == 'POST':
        print(request.form)
        time_ = time(int(request.form['hour']), int(request.form['min']), int(request.form['sec']),
                     int(request.form['milisec'])*10000)
        if '0' in request.form:
            add_annotation(user.id, request.form['record'], '01', time_)
        elif '1' in request.form:
            add_annotation(user.id, request.form['record'], '10', time_)

    set_ = Set.query.get(set_id)
    if set_.type != 0 or set_.active == False:
        abort(404)

    rnd_record = db_session.query(Record).filter(Record.set_id==set_id).order_by(Record.position.desc()).first()
    rnd_record.position -= 10000
    db_session.commit()
    record_crops = db_session.query(RecordCrop).filter(RecordCrop.record_id==rnd_record.id).order_by(RecordCrop.order).all()

    return render_template("comparing.html", record_id=rnd_record.id, record_crops=enumerate(record_crops))

@bp.route('/ordering/<set_id>', methods = ['GET', 'POST'])
def show_ordering(set_id):
    user = user_cookie()
    if request.method == 'POST':
        print(request.form)
        time_ = time(int(request.form['hour']),int(request.form['min']),int(request.form['sec']),
                     int(request.form['milisec'])*10000)
        add_annotation(user.id, request.form['record'], request.form['order'], time_)

    set_ = Set.query.get(set_id)
    if set_.type != 1 or set_.active == False:
        abort(404)

    rnd_record = db_session.query(Record).filter(Record.set_id==set_id).order_by(Record.position.desc()).first()
    rnd_record.position -= 10000
    db_session.commit()
    record_crops = db_session.query(RecordCrop).filter(RecordCrop.record_id==rnd_record.id).order_by(RecordCrop.order).all()

    return render_template("ordering.html", record_id=rnd_record.id, record_crops=enumerate(record_crops))

@bp.route('/rating/<set_id>', methods = ['GET', 'POST'])
def show_rating(set_id):
    user = user_cookie()
    print(user)
    if request.method == 'POST':
        print(request.form)
        time_ = time(int(request.form['hour']),int(request.form['min']),int(request.form['sec']),
                     int(request.form['milisec'])*10000)

        if request.form['submit_button'] == '1':
            add_annotation(user.id, request.form['record'], '1', time_)
        elif request.form['submit_button'] == '2':
            add_annotation(user.id, request.form['record'], '2', time_)
        elif request.form['submit_button'] == '3':
            add_annotation(user.id, request.form['record'], '3', time_)
        elif request.form['submit_button'] == '4':
            add_annotation(user.id, request.form['record'], '4', time_)
        elif request.form['submit_button'] == '5':
            add_annotation(user.id, request.form['record'], '5', time_)
        elif request.form['submit_button'] == '6':
            add_annotation(user.id, request.form['record'], '6', time_)
        elif request.form['submit_button'] == '7':
            add_annotation(user.id, request.form['record'], '7', time_)
    
    set_ = Set.query.get(set_id)
    if set_.type != 2 or set_.active == False:
        abort(404)

    rnd_record = db_session.query(Record).filter(Record.set_id==set_id).order_by(Record.position.desc()).first()
    rnd_record.position -= 10000
    db_session.commit()
    record_crops = db_session.query(RecordCrop).filter(RecordCrop.record_id==rnd_record.id).order_by(RecordCrop.order).all()

    return render_template("rating.html", record_id=rnd_record.id, record_crop=record_crops[0])

@bp.route('/img/<filename>')
def send_file(filename):
    return send_from_directory("./static/crops/", filename)
