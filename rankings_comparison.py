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

    records_set_1 = Record.query.filter(Record.set_id == 1).all()
    records_set_3 = Record.query.filter(Record.set_id == 3).all()
    records_set_5 = Record.query.filter(Record.set_id == 5).all()
    
    records = records_set_1 + records_set_3 + records_set_5
    
    not_empty = []
    for i, item in enumerate(records):
        if len(item.annotations) > 0:
            not_empty.append(item)

    prep_data = []
    set_ = set()
    for i, item in enumerate(not_empty):
        record_crop = RecordCrop.query.filter(RecordCrop.record_id == item.id).order_by(RecordCrop.order).all()
        _01 = 0
        _10 = 0
        for e, elem in enumerate(item.annotations):
            if elem.annotation == "01":
                _01 += 1
            else:
                _10 += 1
        if _01 > _10:
            prep_data.append([record_crop[0].crop_id, record_crop[1].crop_id])
            set_.add(record_crop[0].crop_id)
            set_.add(record_crop[1].crop_id)
        elif _01 < _10:
            prep_data.append([record_crop[1].crop_id, record_crop[0].crop_id])
            set_.add(record_crop[0].crop_id)
            set_.add(record_crop[1].crop_id)
    
    n_items = len(set_)
    set_ = sorted(list(set_))
    mapping = dict()
    for i in range(len(set_)):
        mapping[i] = set_[0]
        for e, elem in enumerate(prep_data):
            if elem[0] == set_[0]:
                elem[0] = i
            if elem[1] == set_[0]:
                elem[1] = i
        set_ = set_[1:]
    
    data = []
    
    for i, item in enumerate(prep_data):
        data.append((item[0], item[1]))

    params = choix.ilsr_pairwise(n_items, data, 0.0001, max_iter=1000)

    min_, max_ = min(params), max(params)
    normalized = params.copy()
    for i, val in enumerate(params):
        normalized[i] = (val-min_) / (max_-min_)

    for i, item in enumerate(np.argsort(normalized)):
        print(mapping[item], normalized[item])
