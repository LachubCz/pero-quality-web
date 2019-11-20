import os
import argparse

import cv2
import numpy as np

from networks import get_network, get_convolution_part

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model_name", action="store", type=str, required=True)
    parser.add_argument("-f", "--trn_file", action="store", type=str, required=True)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    with open(args.trn_file) as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    crops = []
    ranking = dict()
    x = []
    y = []
    xw = []
    yh = []

    for i, item in enumerate(content):
        crops.append(item.split(' ')[0])
        x.append(int(item.split(' ')[2]))
        y.append(int(item.split(' ')[3]))
        xw.append(int(item.split(' ')[4]))
        yh.append(int(item.split(' ')[5]))
        ranking[int(item.split(' ')[0])] = float(item.split(' ')[6])

    tst = int(len(crops)/100)*10

    trn_crops = crops[tst:]
    tst_crops = crops[:tst]

    classifier, conv, size = get_network(args.model_name)
    conv_model = get_convolution_part(conv, size)

    #path = './app/static/crops'
    episodes = 10000
    minibatch_size = 1024
    highest_val_acc = 0
    for i in range(episodes):
        indexes_trn = np.random.randint(low=0, high=len(trn_crops), size=minibatch_size)
        indexes_tst = np.random.randint(low=0, high=len(tst_crops), size=int(minibatch_size/10))

        image_batch_trn = []
        for _, item in enumerate(indexes_trn):
            image = cv2.imread(trn_crops[item])

            image = image[y[item]:yh[item], x[item]:xw[item]]
            image_batch_trn.append(image/255.0)

        image_batch_tst = []
        for _, item in enumerate(indexes_tst):
            image = cv2.imread(tst_crops[item])

            image = image[y[item]:yh[item], x[item]:xw[item]]
            image_batch_tst.append(image/255.0)

        labs_trn = []
        for e, elem in enumerate(indexes_trn):
            labs_trn.append(ranking[trn_crops[elem]])

        labs_tst = []
        for e, elem in enumerate(indexes_tst):
            labs_tst.append(ranking[tst_crops[elem]])

        hist = conv_model.fit([np.array(image_batch_trn)], np.array(labs_trn), 
            epochs=50, verbose=1, validation_data=([np.array(image_batch_tst)], np.array(labs_tst)))

        if hist.history["val_mean_absolute_error"][-1] > highest_val_acc:
            conv_model.save_weights("comparing_model_{}.h5" .format(i))
            highest_val_acc = hist.history["val_mean_absolute_error"][-1]
