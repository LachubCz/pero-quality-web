import os

import cv2
import json
import pickle
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

"""
if __name__ == "__main__":
    engine = create_engine('sqlite:///database_old.sqlite3',
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    sets = Set.query.all()
    with open("./old_database/sets.pkl", "wb") as output:
        pickle.dump(sets, output, pickle.HIGHEST_PROTOCOL)

    users = User.query.all()
    with open("./old_database/users.pkl", "wb") as output:
        pickle.dump(users, output, pickle.HIGHEST_PROTOCOL)

    records = Record.query.all()
    with open("./old_database/records.pkl", "wb") as output:
        pickle.dump(records, output, pickle.HIGHEST_PROTOCOL)

    recordcrops = RecordCrop.query.all()
    with open("./old_database/recordcrops.pkl", "wb") as output:
        pickle.dump(recordcrops, output, pickle.HIGHEST_PROTOCOL)

    annotations = Annotation.query.all()
    with open("./old_database/annotations.pkl", "wb") as output:
        pickle.dump(annotations, output, pickle.HIGHEST_PROTOCOL)

"""
if __name__ == "__main__":
    engine = create_engine('sqlite:///database.sqlite3',
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    with open("./old_database/sets.pkl", "rb") as input:
        sets = pickle.load(input)

    sets_dict = dict()
    for i, item in enumerate(sets):
        db_item = Set(item.type, item.name, item.active, item.description)
        db_session.add(db_item)
        db_session.commit()
        last = Set.query.order_by(Set.id).all()[-1].id
        sets_dict[item.id] = last

    print(sets_dict)

    with open("./old_database/users.pkl", "rb") as input:
        sets = pickle.load(input)

    users_dict = dict()
    for i, item in enumerate(sets):
        db_item = User(item.cookie_id)
        db_session.add(db_item)
        db_session.commit()
        last = User.query.order_by(User.id).all()[-1].id
        users_dict[item.id] = last

    print(users_dict)

    with open("./old_database/records.pkl", "rb") as input:
        records = pickle.load(input)

    records_dict = dict()
    for i, item in enumerate(records):
        db_item = Record(item.position, sets_dict[item.set_id])
        db_session.add(db_item)
        db_session.commit()
        last = Record.query.order_by(Record.id).all()[-1].id
        records_dict[item.id] = last

    print(records_dict)

    with open("./old_database/recordcrops.pkl", "rb") as input:
        recordcrops = pickle.load(input)

    for i, item in enumerate(recordcrops):
        db_item = RecordCrop(item.crop_id, records_dict[item.record_id], item.order)
        db_session.add(db_item)
        db_session.commit()

    with open("./old_database/annotations.pkl", "rb") as input:
        annotations = pickle.load(input)

    for i, item in enumerate(annotations):
        db_item = Annotation(users_dict[item.user_id], records_dict[item.record_id], item.annotation, item.annotation_time, item.user_info)
        db_session.add(db_item)
        db_session.commit()
        last = Annotation.query.order_by(Annotation.id).all()[-1]
        last.timestamp = item.timestamp
        db_session.commit()
