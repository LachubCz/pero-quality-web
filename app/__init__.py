import os
import cv2

from flask import Flask, request, flash, url_for, redirect, render_template, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from  sqlalchemy.sql.expression import func
#from app.db.model import initialize_database

from jinja2 import Environment, FileSystemLoader



def create_app():
    PEOPLE_FOLDER = os.path.join('static', 'images')
    print(PEOPLE_FOLDER)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    bootstrap = Bootstrap(app)

    db = SQLAlchemy(app)

    file_loader = FileSystemLoader(
            [os.path.join(os.path.dirname(__file__), "templates"),
             os.path.join(os.path.dirname(__file__), "posts"),
             os.path.join(os.path.dirname(__file__), "")])
    env = Environment(loader=file_loader)

    class User(db.Model):
        id        = db.Column(db.Integer, primary_key = True)
        cookie_id = db.Column(db.String(200))

        def __init__(self, cookie_id):
            self.cookie_id = cookie_id


    class Set(db.Model):
        id          = db.Column(db.Integer, primary_key = True)
        type        = db.Column(db.Integer)
        name        = db.Column(db.String(200))
        active      = db.Column(db.Boolean)
        description = db.Column(db.String(200))

        def __init__(self, type, name, active, description):
            self.type        = type
            self.name        = name
            self.active      = active
            self.description = description


    class Page(db.Model):
        #id  = db.Column(db.Integer, primary_key = True)
        name = db.Column(db.String(200), primary_key = True)

        def __init__(self, name):
            self.name = name


    class Annotation(db.Model):
        id              = db.Column(db.Integer, primary_key = True)
        set_id          = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=False)
        user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        record_id       = db.Column(db.Integer, db.ForeignKey('record.id'), nullable=False)
        annotation      = db.Column(db.String(50))
        annotation_time = db.Column(db.Integer)

        def __init__(self, name, city, addr, pin):
            self.set_id          = set_id
            self.user_id         = user_id
            self.record_id       = record_id
            self.annotation      = annotation
            self.annotation_time = annotation_time


    class Record(db.Model):
        id        = db.Column(db.Integer, primary_key = True)
        position  = db.Column(db.Integer)
        set_id    = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=False)

        def __init__(self, position, set_id):
            self.position  = position
            self.set_id    = set_id


    class Crop(db.Model):
        id      = db.Column(db.Integer, primary_key = True)
        page_id = db.Column(db.String(200), db.ForeignKey('page.name'), nullable=False)
        x       = db.Column(db.Integer)
        y       = db.Column(db.Integer)
        cropped = db.Column(db.Boolean)

        def __init__(self, page_id, x, y, cropped):
            self.page_id = page_id
            self.x  = x
            self.y  = y
            self.cropped = cropped


    record_crop = db.Table('record_crop',
        db.Column('record_id', db.Integer, db.ForeignKey('record.id'), primary_key=True),
        db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'), primary_key=True)
    )

    @app.route('/all')
    def show_all():
        return render_template('show_all.html', students = students.query.all())

    @app.route('/navbar')
    def navbar():
        return render_template('navbar.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/comparing_sets')
    def show_comparing_sets():
        set_ = Set.query.filter(Set.type==1, Set.active==True).all()
        return render_template("comparing_sets.html", sets=set_)

    @app.route('/ordering_sets')
    def show_ordering_sets():
        set_ = Set.query.filter(Set.type==2, Set.active==True).all()
        return render_template("ordering_sets.html", sets=set_)

    @app.route('/rating_sets')
    def show_rating_sets():
        set_ = Set.query.filter(Set.type==3, Set.active==True).all()
        return render_template("rating_sets.html", sets=set_)

    def show_page(page, *args, **kwargs):
        template = env.get_template(page)
        print(args, kwargs)
        return template

    @app.route('/comparing/<set>')
    def show_comparing(set):
        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 1:
            abort(404)

        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crops_ = []
        for i, item in enumerate(record_crop_):
            crops_.append(Crop.query.filter(Crop.id==record_crop_[i][1]).all())

        full_filenames = []
        for i, crop_ in enumerate(crops_):
            if crop_[0].cropped:
                full_filenames.append(str(crop_[0].id)+'.jpg')
            else:
                page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
                img = cv2.imread(os.path.join('./app/static/pages', crop_[0].page_id+'.jpg'))
                crop_img = img[crop_[0].y:crop_[0].y+512, crop_[0].x:crop_[0].x+512]
                cv2.imwrite("./app/static/crops/"+str(crop_[0].id)+'.jpg', crop_img)
                full_filenames.append(str(crop_[0].id)+'.jpg')
                crop_[0].cropped = True
                db.session.commit()

        #return show_page("static/comparing.html", images_for_annotation = full_filenames)
        #template= show_page("static/comparing.html")
        return render_template("comparing.html", images_for_annotation = full_filenames)

    @app.route('/ordering/<set>')
    def show_ordering(set):
        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 2:
            abort(404)

        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crops_ = []
        for i, item in enumerate(record_crop_):
            crops_.append(Crop.query.filter(Crop.id==record_crop_[i][1]).all())

        full_filenames = []
        for i, crop_ in enumerate(crops_):
            if crop_[0].cropped:
                full_filenames.append(str(crop_[0].id)+'.jpg')
            else:
                page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
                img = cv2.imread(os.path.join('./app/static/pages', crop_[0].page_id+'.jpg'))
                crop_img = img[crop_[0].y:crop_[0].y+512, crop_[0].x:crop_[0].x+512]
                cv2.imwrite("./app/static/crops/"+str(crop_[0].id)+'.jpg', crop_img)
                full_filenames.append(str(crop_[0].id)+'.jpg')
                crop_[0].cropped = True
                db.session.commit()

        #return show_page("static/comparing.html", images_for_annotation = full_filenames)
        #template= show_page("static/comparing.html")
        return render_template("ordering.html", images_for_annotation = full_filenames)


    @app.route('/rating/<set>')
    def show_rating(set):
        set_ = Set.query.filter_by(id=set).first()
        if set_.type != 3:
            abort(404)
        #print(set_.type)
        rnd_record_id = Record.query.filter_by(set_id=set).order_by(func.random()).first().id
        statement = db.session.query(record_crop).filter_by(record_id=rnd_record_id)
        record_crop_ = db.session.execute(statement).fetchall()
        crop_ = Crop.query.filter(Crop.id==record_crop_[0][1]).all()
        if crop_[0].cropped:
            full_filename = str(crop_[0].id)+'.jpg'
        else:
            page_ = Page.query.filter(Page.name==crop_[0].page_id).all()
            img = cv2.imread(os.path.join('./app/static/pages', crop_[0].page_id+'.jpg'))
            crop_img = img[crop_[0].y:crop_[0].y+512, crop_[0].x:crop_[0].x+512]
            cv2.imwrite("./app/static/crops/"+str(crop_[0].id)+'.jpg', crop_img)
            full_filename = str(crop_[0].id)+'.jpg'
            crop_[0].cropped = True
            db.session.commit()

        return render_template("rating.html", image_for_annotation = full_filename)

    @app.route('/img/<filename>')
    def send_file(filename):
        return send_from_directory("./static/crops/", filename)

    @app.route('/new', methods = ['GET', 'POST'])
    def new():
        if request.method == 'POST':
            if not request.form['name'] or not request.form['city'] or not request.form['addr']:
                flash('Please enter all the fields', 'error')
            else:
                student = students(request.form['name'], request.form['city'],
                                   request.form['addr'], request.form['pin'])
             
                db.session.add(student)
                db.session.commit()
                flash('Record was successfully added')
                return redirect(url_for('show_all'))
        return render_template('new.html')

    db.create_all()
    
    return app
