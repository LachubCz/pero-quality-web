import os

from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

def create_app():
    PEOPLE_FOLDER = os.path.join('static', 'images')
    print(PEOPLE_FOLDER)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
    app.config['SECRET_KEY'] = "random string"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
    Bootstrap(app)

    db = SQLAlchemy(app)

    class students(db.Model):
        id = db.Column('student_id', db.Integer, primary_key = True)
        name = db.Column(db.String(100))
        city = db.Column(db.String(50))
        addr = db.Column(db.String(200)) 
        pin = db.Column(db.String(10))

        def __init__(self, name, city, addr, pin):
            self.name = name
            self.city = city
            self.addr = addr
            self.pin = pin

    @app.route('/all')
    def show_all():
        return render_template('show_all.html', students = students.query.all() )

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/comparing_sets')
    def show_comparing_sets():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'RGBSCENE_2019-02-27_002.png')
        return render_template("comparing_sets.html", user_image = full_filename)
        return render_template('')

    @app.route('/ordering_sets')
    def show_ordering_sets():
        return render_template('ordering_sets.html')

    @app.route('/rating_sets')
    def show_rating_sets():
        return render_template('rating_sets.html')

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
