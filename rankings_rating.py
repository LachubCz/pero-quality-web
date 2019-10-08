import choix
import networkx as nx
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

if __name__ == "__main__":
    engine = create_engine('sqlite:///database.sqlite3',
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    records_set_2 = Record.query.filter(Record.set_id == 2).all()
    records_set_4 = Record.query.filter(Record.set_id == 4).all()
    
    records = records_set_2 + records_set_4
    
    not_empty = []
    for i, item in enumerate(records):
        if len(item.annotations) > 0:
            not_empty.append(item)

    data = []
    labels = []
    for i, item in enumerate(not_empty):
        record_crop = RecordCrop.query.filter(RecordCrop.record_id == item.id).order_by(RecordCrop.order).all()
        average = 0
        for e, elem in enumerate(item.annotations):
            average += int(elem.annotation)
        average = average / len(item.annotations)
        labels.append(average)
        data.append(record_crop[0].crop_id)

    min_, max_ = min(labels), max(labels)
    normalized = labels.copy()
    for i, val in enumerate(labels):
        normalized[i] = (val-min_) / (max_-min_)

    for i, item in enumerate(data):
        print(item, normalized[i])