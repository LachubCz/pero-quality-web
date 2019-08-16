import os
import re
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
    parser.add_argument("-w", "--width",  type=int,
                        default=512, help="width of images in set")
    parser.add_argument("--height", type=int,
                        default=512, help="height of images in set")
    parser.add_argument("-c", "--count", type=int,
                        default=1000, help="Number of records to generate.")
    parser.add_argument("--crop_it", action="store_true", help="save cropped crops?")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    engine = create_engine('sqlite:///database.sqlite3',
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
        for line in [line.split() for line in f]:
            if line[0] in pages.keys():
                page_id = pages[line[0]]
            else:
                page = Page(line[0])
                db_session.add(page)
                db_session.commit()
                page_id = page.id
                pages[page.path] = page.id

            for position in line[1:]:
                x, y = position.split(':')
                is_in = False

                try:
                    for c, crop in enumerate(crops[str(page_id)]):
                        if crop == (int(x), int(y), int(args.width), int(args.height)):
                            is_in = True
                            break
                except:
                    pass

                if not is_in:
                    crop = Crop(page_id, int(x), int(y), int(args.width), int(args.height), False)
                    db_session.add(crop)
                    db_session.commit()
                else:
                    crop = Crop.query.filter(Crop.page_id==page_id, Crop.x==int(x), Crop.y==int(y), Crop.width==int(args.width), Crop.height==int(args.height)).first()

                if args.crop_it:
                    page = Page.query.get(crop.page_id)
                    image = cv2.imread(page.path)
                    image = image[crop.y:crop.y+crop.height, crop.x:crop.x+crop.width]
                    cv2.imwrite(os.path.join('./app/static/crops', str(crop.id)+'.jpg'), image)
                    crop.cropped = True
                    db_session.commit()

                all_crops.append(crop)
            db_session.commit()

    print("Writing records")

    if args.type == "rating":
        for i, crop in enumerate(all_crops):
            record = Record(i, set_id)
            db_session.add(record)
            db_session.commit()

            record_crop = RecordCrop(crop.id, record.id, 0)
            db_session.add(record_crop)
            db_session.commit()
    else:
        for i in range(args.count):
            record = Record(i, set_id)
            db_session.add(record)
            db_session.commit()

            selected_crops = np.random.choice(len(all_crops), crops_in_record, replace=False)
            selected_crops = [all_crops[x] for x in selected_crops]
            for order, crop in enumerate(selected_crops):
                record_crop = RecordCrop(crop.id, record.id, order)
                db_session.add(record_crop)
            db_session.commit()
