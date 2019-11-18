import os
import re
import random
import argparse

import cv2
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop


def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--description", default="", help="description of set")
    parser.add_argument("--question_cz", required=True, help="question in czech language")
    parser.add_argument("--question_en", required=True, help="question in czech language")
    parser.add_argument("--inactive", action="store_true", help="is set active?")

    parser.add_argument("-l", "--list-of-crops", type=str,
                        required=True, help="file with list of images in form \"path/image_name x y\"")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    engine = create_engine('sqlite:////mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/database.sqlite3',
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    db_set = Set(0, not args.inactive, args.description, args.question_cz, args.question_en)

    db_session.add(db_set)
    db_session.commit()
    set_id = db_set.id
    print('Set id', set_id)

    all_crops = []
    pages = {}
    for p, page in enumerate(Page.query.all()):
        pages[page.path] = page.id

    crops = {}
    for c, crop in enumerate(Crop.query.all()):
        if crop.page_id in crops.keys():
            crops[crop.page_id].append((crop.x, crop.y, crop.width, crop.height))
        else:
            crops[crop.page_id] = []
            crops[crop.page_id].append((crop.x, crop.y, crop.width, crop.height))

    pairs = []
    with open(args.list_of_crops) as f:
        for line in [line.split() for line in f]:
            if line[0] in pages.keys():
                page_id_1 = pages[line[0]]
            else:
                page = Page("/mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/lines/images/"+line[0])
                db_session.add(page)
                db_session.commit()
                page_id_1 = page.id
                pages[page.path] = page.id
                img = cv2.imread("/mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/lines/images/"+line[0])
                crop_1 = Crop(page_id_1, 0, 0, np.shape(img)[1], np.shape(img)[0], True)
                db_session.add(crop_1)
                db_session.commit()

            if line[1] in pages.keys():
                page_id_2 = pages[line[1]]
            else:
                page = Page("/mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/lines/images/"+line[1])
                db_session.add(page)
                db_session.commit()
                page_id_2 = page.id
                pages[page.path] = page.id
                img = cv2.imread("/mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/lines/images/"+line[0])
                crop_2 = Crop(page_id_2, 0, 0, np.shape(img)[1], np.shape(img)[0], True)
                db_session.add(crop_2)
                db_session.commit()
            pairs.append([crop_1.id, crop_2.id])

    random.shuffle(pairs)
    for i, item in enumerate(pairs):
        record = Record(i, set_id)
        db_session.add(record)
        db_session.commit()

        if np.random.randint(2, size=1)[0] == 0:
            record_crop_1 = RecordCrop(item[0], record.id, 0)
            record_crop_2 = RecordCrop(item[1], record.id, 1)
        else:
            record_crop_1 = RecordCrop(item[0], record.id, 1)
            record_crop_2 = RecordCrop(item[1], record.id, 0)
        db_session.add(record_crop_1)
        db_session.add(record_crop_2)
        db_session.commit()
