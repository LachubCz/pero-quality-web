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

    parser.add_argument("-t", "--type", choices=["comparing", "ordering", "rating"],
                        required=True, help="type of set")
    parser.add_argument("-n", "--name", required=True, help="name of set")
    parser.add_argument("-d", "--description", default="", help="description of set")
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

    if args.type == "comparing":
        db_set = Set(0, args.name, not args.inactive, args.description)
    elif args.type == "ordering":
        db_set = Set(1, args.name, not args.inactive, args.description)
    elif args.type == "rating":
        db_set = Set(2, args.name, not args.inactive, args.description)

    db_session.add(db_set)
    db_session.commit()
    set_id = db_set.id
    print('Set id', set_id)

    crops_in_record = 1
    if args.type == "comparing":
        crops_in_record = 2
    elif args.type == "ordering":
        crops_in_record = 5

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

    with open(args.list_of_crops) as f:
        counter = 0
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

            record = Record(counter, set_id)
            db_session.add(record)
            db_session.commit()
            counter += 1

            record_crop_1 = RecordCrop(crop_1.id, record.id, 0)
            record_crop_2 = RecordCrop(crop_2.id, record.id, 1)
            db_session.add(record_crop_1)
            db_session.add(record_crop_2)
            db_session.commit()
