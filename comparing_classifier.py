import os
import argparse

import cv2
import pickle
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

from networks import get_network, get_convolution_part

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model_name", action="store", type=str, required=True)

    args = parser.parse_args()

    return args

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

    merged_records = records_set_1 + records_set_3 + records_set_5 + records_set_6 + records_set_10
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
        crops.append([record[0].crop_id, record[1].crop_id])

    print(len(crops), len(labels))

    tst = int(len(crops)/100)*10

    trn_crops = crops[tst:]
    trn_labels = labels[tst:]

    tst_crops = crops[:tst]
    tst_labels = labels[:tst]

    print(len(trn_crops), len(tst_crops))

    args = get_args()

    classifier, conv, size = get_network(args.model_name)

    path = './app/static/crops'
    episodes = 1000
    minibatch_size = 1024
    for i in range(episodes):
        indexes_trn = np.random.randint(low=0, high=len(trn_crops), size=minibatch_size)
        indexes_tst = np.random.randint(low=0, high=len(tst_crops), size=int(minibatch_size/10))

        image_batch_1_trn = []
        image_batch_2_trn = []
        for _, item in enumerate(indexes_trn):
            image = cv2.imread(os.path.join(path, str(trn_crops[item][0])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_1_trn.append(image/255.0)

            ########################################

            image = cv2.imread(os.path.join(path, str(trn_crops[item][1])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_2_trn.append(image/255.0)

        image_batch_1_tst = []
        image_batch_2_tst = []
        for _, item in enumerate(indexes_tst):
            image = cv2.imread(os.path.join(path, str(tst_crops[item][0])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_1_tst.append(image/255.0)

            ########################################

            image = cv2.imread(os.path.join(path, str(tst_crops[item][1])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_2_tst.append(image/255.0)

        labs_tst = [tst_labels[x] for x in indexes_tst]

        for e, elem in enumerate(labs_tst):
            labs_tst[e] = [round(elem[0])]

        labs_trn = [trn_labels[x] for x in indexes_trn]

        for e, elem in enumerate(labs_trn):
            labs_trn[e] = [round(elem[0])]

        classifier.fit([np.array(image_batch_1_trn), np.array(image_batch_2_trn)], np.array(labs_trn), 
            epochs=50, verbose=1, validation_data=([np.array(image_batch_1_tst), np.array(image_batch_2_tst)], np.array(labs_tst)))

        classifier.save_weights("comparing_model_{}.h5" .format(i))
