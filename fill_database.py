import os
import cv2
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from app import create_app

if __name__ == "__main__":
    app = create_app()
    db = SQLAlchemy(app)

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
        #id  = db.Column(db.Integer, primary_key = True)
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

    db.create_all()

    #sets
    data = Set(0, "Czech news from 19. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 0)
        db.session.add(data)
    data = Set(0, "German news from 20. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 1)
        db.session.add(data)
    data = Set(0, "Slovak news from 20. century", False, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 2)
        db.session.add(data)
    
    data = Set(1, "English books from 17. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 3)
        db.session.add(data)
    data = Set(1, "Czech books from 18. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 4)
        db.session.add(data)
    data = Set(1, "Slovak books from 18. century", False, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 5)
        db.session.add(data)

    data = Set(2, "Czech books from 20. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 6)
        db.session.add(data)
    data = Set(2, "Japanese books from 20. century", True, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 7)
        db.session.add(data)
    data = Set(2, "Slovak books from 20. century", False, "description")
    db.session.add(data)
    for i in range((np.random.randint(100, size=1)[0]+5)):
        data = Record(np.random.rand(1)[0], 8)
        db.session.add(data)

    db.session.commit()

    list_of_images = os.listdir("./app/static/pages")

    width_  = 388
    height_ = 512
    for i, item in enumerate(list_of_images):
        data = Page(item[:-4], "./app/static/pages")
        db.session.add(data)

        img = cv2.imread(os.path.join("./app/static/pages", item))
        height = img.shape[0]
        weight = img.shape[1]
        right_ = weight - width_
        bottom_ = height - height_

        for _ in range(50):
            x = np.random.randint(right_, size=1)[0]
            y = np.random.randint(bottom_, size=1)[0]

            data = Crop(item[:-4], int(x), int(y), int(width_), int(height_), False)
            db.session.add(data)

    db.session.commit()

    crops_ = Crop.query.order_by(Crop.x).all()

    counter = 0
    for i in range(1,10):
        rec_ = Record.query.filter(Record.set_id==i).all()
        if i == 1 or i == 2 or i == 3:
            for e, elem in enumerate(rec_):
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=0)
                db.session.execute(statement)
                counter += 1
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=1)
                db.session.execute(statement)
                counter += 1
        if i == 4 or i == 5 or i == 6:
            for e, elem in enumerate(rec_):
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=0)
                db.session.execute(statement)
                counter += 1
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=1)
                db.session.execute(statement)
                counter += 1
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=2)
                db.session.execute(statement)
                counter += 1
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=3)
                db.session.execute(statement)
                counter += 1
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=4)
                db.session.execute(statement)
                counter += 1
        if i == 7 or i == 8 or i == 9:
            for e, elem in enumerate(rec_):
                statement = record_crop.insert().values(record_id=elem.id, crop_id=crops_[counter].id, order=1)
                db.session.execute(statement)
                counter += 1

    db.session.commit()