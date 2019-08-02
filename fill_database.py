import os
import re
import argparse

import cv2
import numpy as np

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from app import create_app

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--type", action="store", dest="type", type=str, choices=["comparing", "ordering", "rating"],
                        required=True, help="type of set")
    parser.add_argument("-n", "--name", action="store", dest="name", type=str, required=True,
                        help="name of set")
    parser.add_argument("-d", "--description", action="store", dest="description", type=str, default="",
                        help="description of set")
    parser.add_argument("-a", "--active", action="store_true", dest="active", default=True,
                        help="is set active?")

    parser.add_argument("-l", "--list_of_crops", action="store", dest="list_of_crops", type=str,
                        required=True, help="file with list of images in form \"path/image_name x y\"")
    parser.add_argument("-w", "--width", action="store", dest="width", type=int,
                        default=512, help="width of images in set")
    parser.add_argument("--height", action="store", dest="height", type=int,
                        default=512, help="height of images in set")

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = get_args()

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

    if args.type == "comparing":
        data = Set(0, args.name, args.active, args.description)
    elif args.type == "ordering":
        data = Set(1, args.name, args.active, args.description)
    elif args.type == "rating":
        data = Set(2, args.name, args.active, args.description)

    db.session.add(data)
    set_id = Set.query.all()[-1].id

    num_crops = sum(1 for line in open(args.list_of_crops))

    crops_in_record = 1
    if args.type == "comparing":
        crops_in_record = 2
    elif args.type == "ordering":
        crops_in_record = 5
    
    num_of_records = num_crops//crops_in_record

    for i in range(num_of_records):
        data = Record(np.random.rand(1)[0], set_id)
        db.session.add(data)

    records = Record.query.all()[-num_of_records:]

    db.session.commit()
    
    with open(args.list_of_crops) as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    for i, item in enumerate(content):
        content[i] = item.split(' ')

    content = content[:num_of_records*crops_in_record]

    page_names = Page.query.all()
    page_names = (p.name for p in page_names)

    counter_records = -1
    crops_ = Crop.query.all()
    if crops_ == []:
        crop_id = 1
    else:
        crop_id = crops_[-1].id + 1

    for i, item in enumerate(content):
        if i % crops_in_record == 0:
            counter_records += 1

        name = re.sub(r'.*/', '', item[0])
        path = item[0][:-len(name)]
        name = name[:-4]
        if name not in page_names:
            data = Page(name, path)
            db.session.add(data)

        data = Crop(name, int(item[1]), int(item[2]), int(args.width), int(args.height), False)
        db.session.add(data)
        db.session.commit()

        statement = record_crop.insert().values(record_id=records[counter_records].id, crop_id=crop_id, order=(i % crops_in_record))
        db.session.execute(statement)
        crop_id += 1

    db.session.commit()
