import os
import datetime
from datetime import time 
import cv2

from flask import Flask, request, flash, url_for, redirect, render_template, send_from_directory, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.sql.expression import func

from jinja2 import Environment, FileSystemLoader

from uuid import uuid4

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['CROPS_PATH'] = './app/static/crops/'
    bootstrap = Bootstrap(app)

    db = SQLAlchemy(app)

    file_loader = FileSystemLoader(
            [os.path.join(os.path.dirname(__file__), "templates"),
             os.path.join(os.path.dirname(__file__), "posts"),
             os.path.join(os.path.dirname(__file__), "")])
    env = Environment(loader=file_loader)

    class User(db.Model):
        id        = db.Column(db.Integer, primary_key = True)
        cookie_id = db.Column(db.String)

        def __init__(self, cookie_id):
            self.cookie_id = cookie_id


    class Set(db.Model):
        id          = db.Column(db.Integer, primary_key = True)
        type        = db.Column(db.Integer)
        name        = db.Column(db.String)
        active      = db.Column(db.Boolean)
        description = db.Column(db.String)

        def __init__(self, type, name, active, description):
            self.type        = type
            self.name        = name
            self.active      = active
            self.description = description


    class Page(db.Model):
        name = db.Column(db.String, primary_key = True)
        path = db.Column(db.String)

        def __init__(self, name, path):
            self.name = name
            self.path = path


    class Annotation(db.Model):
        id              = db.Column(db.Integer, primary_key = True)
        set_id          = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=False)
        user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        record_id       = db.Column(db.Integer, db.ForeignKey('record.id'), nullable=False)
        annotation      = db.Column(db.String)
        annotation_time = db.Column(db.Time())
        timestamp       = db.Column(db.DateTime())

        def __init__(self, set_id, user_id, record_id, annotation, annotation_time, timestamp):
            self.set_id          = set_id
            self.user_id         = user_id
            self.record_id       = record_id
            self.annotation      = annotation
            self.annotation_time = annotation_time
            self.timestamp       = timestamp


    class Record(db.Model):
        id        = db.Column(db.Integer, primary_key = True)
        position  = db.Column(db.Integer)
        set_id    = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=False)

        def __init__(self, position, set_id):
            self.position  = position
            self.set_id    = set_id


    class Crop(db.Model):
        id      = db.Column(db.Integer, primary_key = True)
        page_id = db.Column(db.String, db.ForeignKey('page.name'), nullable=False)
        x       = db.Column(db.Integer)
        y       = db.Column(db.Integer)
        width   = db.Column(db.Integer)
        height  = db.Column(db.Integer)
        cropped = db.Column(db.Boolean)

        def __init__(self, page_id, x, y, width, height, cropped):
            self.page_id = page_id
            self.x       = x
            self.y       = y
            self.width   = width
            self.height  = height
            self.cropped = cropped


    record_crop = db.Table('record_crop',
        db.Column('record_id', db.Integer, db.ForeignKey('record.id'), primary_key=True),
        db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'), primary_key=True), 
        db.Column('order', db.Integer)
    )

    def user_cookie():
        if 'uid' in session:
            user = User.query.filter(User.cookie_id==str(session['uid'])).first()
        else:
            session['uid'] = uuid4()
            data = User(str(session['uid']))
            db.session.add(data)
            db.session.commit()
            user = User.query.filter(User.cookie_id==str(session['uid'])).first()

        return user

    def add_annotation(db, set_id, user_id, record_id, annotation, annotation_time):
        data = Annotation(set_id, user_id, record_id, annotation, annotation_time, datetime.datetime.now())
        db.session.add(data)
        db.session.commit()

    @app.route('/navbar')
    def navbar():
        user = user_cookie()
        return render_template('navbar.html')

    @app.route('/')
    def index():
        user = user_cookie()
        return render_template('index.html')

    @app.route('/datasets')
    def show_datasets():
        user = user_cookie()
        set_1 = Set.query.filter(Set.type==0, Set.active==True).all()
        set_2 = Set.query.filter(Set.type==1, Set.active==True).all()
        set_3 = Set.query.filter(Set.type==2, Set.active==True).all()
        return render_template("datasets.html", set_1=set_1, set_2=set_2, set_3=set_3)

    @app.route('/comparing_help/<set>')
    def show_comparing_help(set):
        user = user_cookie()
        return render_template("comparing_help.html", set=set)

    @app.route('/ordering_help/<set>')
    def show_ordering_help(set):
        user = user_cookie()
        return render_template("ordering_help.html", set=set)

    @app.route('/rating_help/<set>')
    def show_rating_help(set):
        user = user_cookie()
        return render_template("rating_help.html", set=set)

    @app.route('/comparing_sets')
    def show_comparing_sets():
        user = user_cookie()
        set_ = Set.query.filter(Set.type==0, Set.active==True).all()
        return render_template("comparing_sets.html", sets=set_)

    @app.route('/ordering_sets')
    def show_ordering_sets():
        user = user_cookie()
        set_ = Set.query.filter(Set.type==1, Set.active==True).all()
        return render_template("ordering_sets.html", sets=set_)

    @app.route('/rating_sets')
    def show_rating_sets():
        user = user_cookie()
        set_ = Set.query.filter(Set.type==2, Set.active==True).all()
        return render_template("rating_sets.html", sets=set_)

    @app.route('/comparing/<set>', methods = ['GET', 'POST'])
    def show_comparing(set):
        user = user_cookie()
        if request.method == 'POST':
            print(request.form)
            time_ = time(int(request.form['hour']),int(request.form['min']),int(request.form['sec']),
                         int(request.form['milisec'])*10000)
            if '0' in request.form:
                add_annotation(db, set, user.id, request.form['record'], '01', time_)
            elif '1' in request.form:
                add_annotation(db, set, user.id, request.form['record'], '10', time_)

        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 0 or set_.active == False:
            abort(404)

        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crops_ = []

        record_crop_.sort(key=lambda tup: tup[2])
        for i, item in enumerate(record_crop_):
            crops_.append(Crop.query.filter(Crop.id==record_crop_[i][1]).all())

        full_filenames = []
        for i, crop_ in enumerate(crops_):
            if crop_[0].cropped:
                full_filenames.append((i, str(crop_[0].id)+'.jpg'))
            else:
                page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
                img = cv2.imread(os.path.join(page_[0].path, crop_[0].page_id+'.jpg'))
                crop_img = img[crop_[0].y:crop_[0].y+crop_[0].height, crop_[0].x:crop_[0].x+crop_[0].width]
                cv2.imwrite(os.path.join(app.config['CROPS_PATH'], str(crop_[0].id)+'.jpg'), crop_img)
                full_filenames.append((i, str(crop_[0].id)+'.jpg'))
                crop_[0].cropped = True
                db.session.commit()

        return render_template("comparing.html", record_id = rnd_record_id, images_for_annotation = full_filenames)

    @app.route('/ordering/<set>', methods = ['GET', 'POST'])
    def show_ordering(set):
        user = user_cookie()
        if request.method == 'POST':
            print(request.form)
            time_ = time(int(request.form['hour']),int(request.form['min']),int(request.form['sec']),
                         int(request.form['milisec'])*10000)
            add_annotation(db, set, user.id, request.form['record'], request.form['order'], time_)

        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 1 or set_.active == False:
            abort(404)

        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crops_ = []

        record_crop_.sort(key=lambda tup: tup[2])
        for i, item in enumerate(record_crop_):
            crops_.append(Crop.query.filter(Crop.id==record_crop_[i][1]).all())

        full_filenames = []
        for i, crop_ in enumerate(crops_):
            if crop_[0].cropped:
                full_filenames.append((i, str(crop_[0].id)+'.jpg'))
            else:
                page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
                img = cv2.imread(os.path.join(page_[0].path, crop_[0].page_id+'.jpg'))
                crop_img = img[crop_[0].y:crop_[0].y+crop_[0].height, crop_[0].x:crop_[0].x+crop_[0].width]
                cv2.imwrite(os.path.join(app.config['CROPS_PATH'], str(crop_[0].id)+'.jpg'), crop_img)
                full_filenames.append((i, str(crop_[0].id)+'.jpg'))
                crop_[0].cropped = True
                db.session.commit()

        return render_template("ordering.html", record_id = rnd_record_id, images_for_annotation = full_filenames)

    @app.route('/rating/<set>', methods = ['GET', 'POST'])
    def show_rating(set):
        user = user_cookie()
        print(user)
        if request.method == 'POST':
            print(request.form)
            time_ = time(int(request.form['hour']),int(request.form['min']),int(request.form['sec']),
                         int(request.form['milisec'])*10000)

            if request.form['submit_button'] == '1':
                add_annotation(db, set, user.id, request.form['record'], '1', time_)
            elif request.form['submit_button'] == '2':
                add_annotation(db, set, user.id, request.form['record'], '2', time_)
            elif request.form['submit_button'] == '3':
                add_annotation(db, set, user.id, request.form['record'], '3', time_)
            elif request.form['submit_button'] == '4':
                add_annotation(db, set, user.id, request.form['record'], '4', time_)
            elif request.form['submit_button'] == '5':
                add_annotation(db, set, user.id, request.form['record'], '5', time_)
            elif request.form['submit_button'] == '6':
                add_annotation(db, set, user.id, request.form['record'], '6', time_)
            elif request.form['submit_button'] == '7':
                add_annotation(db, set, user.id, request.form['record'], '7', time_)
        
        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 2 or set_.active == False:
            abort(404)

        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crop_ = Crop.query.filter(Crop.id==record_crop_[0][1]).all()
        if crop_[0].cropped:
            full_filename = str(crop_[0].id)+'.jpg'
        else:
            page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
            img = cv2.imread(os.path.join(page_[0].path, crop_[0].page_id+'.jpg'))
            crop_img = img[crop_[0].y:crop_[0].y+crop_[0].height, crop_[0].x:crop_[0].x+crop_[0].width]
            cv2.imwrite(os.path.join(app.config['CROPS_PATH'], str(crop_[0].id)+'.jpg'), crop_img)
            full_filename = str(crop_[0].id)+'.jpg'
            crop_[0].cropped = True
            db.session.commit()

        return render_template("rating.html", record_id = rnd_record_id, image_for_annotation = full_filename)

    @app.route('/img/<filename>')
    def send_file(filename):
        return send_from_directory("./static/crops/", filename)

    db.create_all()
    
    return app
