import os
import argparse

import cv2
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
    parser.add_argument("-w", "--model_weights", action="store", type=str, required=True)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    with open("rankings_rating.txt") as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    crops = []
    ranking = dict()
    for i, item in enumerate(content):
        crops.append(int(item.split(' ')[0]))
        ranking[int(item.split(' ')[0])] = float(item.split(' ')[1])

    tst = int(len(crops)/100)*10

    trn_crops = crops[tst:]
    tst_crops = crops[:tst]

    args = get_args()

    classifier, conv, size = get_network(args.model_name)
    classifier.load_weights(args.model_weights)
    print("Weights loaded.")

    conv_model = get_convolution_part(conv, size)

    path = './app/static/crops'
    episodes = 1000
    minibatch_size = 1024
    for i in range(episodes):
        indexes_trn = np.random.randint(low=0, high=len(trn_crops), size=minibatch_size)
        indexes_tst = np.random.randint(low=0, high=len(tst_crops), size=int(minibatch_size/10))

        image_batch_trn = []
        for _, item in enumerate(indexes_trn):
            image = cv2.imread(os.path.join(path, str(trn_crops[item])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_trn.append(image/255.0)

        image_batch_tst = []
        for _, item in enumerate(indexes_tst):
            image = cv2.imread(os.path.join(path, str(tst_crops[item])+".jpg"))

            max_width = image.shape[1] - size
            max_height = image.shape[0] - size

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+size, width[0]:width[0]+size]
            image_batch_tst.append(image/255.0)

        labs_trn = []
        for e, elem in enumerate(indexes_trn):
            labs_trn.append(ranking[trn_crops[elem]])

        labs_tst = []
        for e, elem in enumerate(indexes_tst):
            labs_tst.append(ranking[tst_crops[elem]])

        conv_model.fit([np.array(image_batch_trn)], np.array(labs_trn), 
            epochs=50, verbose=1, validation_data=([np.array(image_batch_tst)], np.array(labs_tst)))

        conv_model.save_weights("comparing_model_{}.h5" .format(i))
