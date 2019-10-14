import os

import cv2
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
    records_set_6 = Record.query.filter(Record.set_id == 6).all()
    records_set_10 = Record.query.filter(Record.set_id == 10).all()
    
    records = records_set_1 + records_set_3 + records_set_5 + records_set_6 + records_set_10
    
    crops = []
    for i, item in enumerate(records):
        if len(item.annotations) > 0:
            record_crop = RecordCrop.query.filter(RecordCrop.record_id == item.id).order_by(RecordCrop.order).all()
            crops.append(Crop.query.get(record_crop[0].crop_id))

    for _, crop in enumerate(crops):
        if not os.path.isfile('./app/static/crops/{}.jpg' .format(crop.id)):
            page = Page.query.get(crop.page_id)
            image = cv2.imread(page.path)
            image = image[crop.y:crop.y+crop.height, crop.x:crop.x+crop.width]
            if not os.path.exists('./app/static/crops'):
                os.makedirs('./app/static/crops')
            cv2.imwrite(os.path.join('./app/static/crops', str(crop.id)+'.jpg'), image)
            print("Added crop num. {}." .format(crop.id))
        else:
            print("Crop num. {} already exists." .format(crop.id))