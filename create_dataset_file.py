import os

import cv2
import pickle
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
    records_set_4 = Record.query.filter(Record.set_id == 4).all()

    merged_records = records_set_1 + records_set_4
    not_empty_records = []
    labels = []
    for i, item in enumerate(merged_records):
        if len(item.annotations) > 0:
            _01 = 0
            _10 = 0
            for e, elem in enumerate(item.annotations):
                if elem.annotation == "01":
                    _01 += 1
                elif elem.annotation == "10":
                    _10 += 1
            labels.append([_01 / (_01 + _10), _10 / (_01 + _10)])
            
            not_empty_records.append(item.id)

    crops = []
    for i, item in enumerate(not_empty_records):
        record = RecordCrop.query.filter(RecordCrop.record_id == item).order_by(RecordCrop.order).all()
        crop_1 = Crop.query.filter(Crop.id == record[0].crop_id).first()
        page_1 = Page.query.filter(Page.id == crop_1.page_id).first()
        crop_2 = Crop.query.filter(Crop.id == record[1].crop_id).first()
        page_2 = Page.query.filter(Page.id == crop_2.page_id).first()
        crops.append([[page_1.path, crop_1.x, crop_1.y, crop_1.width, crop_1.height], [page_2.path, crop_2.x, crop_2.y, crop_2.width, crop_2.height]])

    with open("dataset.pkl", "rb") as input:
        old_dataset = pickle.load(input)

    for i, item in enumerate(crops):
        old_dataset[0].append(crops[i])
        old_dataset[1].append(labels[i])

    with open("dataset_large.pkl", "wb") as output:
        pickle.dump(old_dataset, output, pickle.HIGHEST_PROTOCOL)
