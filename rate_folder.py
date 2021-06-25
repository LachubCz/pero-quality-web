import os
import sys
import argparse

import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt

from networks import get_network, get_convolution_part, get_end

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model_name", action="store", type=str, required=True)
    parser.add_argument("-w", "--model_weights", action="store", type=str, required=True)
    parser.add_argument("-f", "--folder", action="store", type=str, required=True)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    classifier, conv, size = get_network(args.model_name, summary=False)
    conv.load_weights(args.model_weights)
    conv_model = conv
    #conv_model = get_end(args.model_name, conv, size)
    #conv_model = get_convolution_part(conv, size, summary=False)

    files = os.listdir(args.folder)

    for i, item in enumerate(files):
        image = cv2.imread(os.path.join(args.folder, item))
        batch = []
        shape = []
        row = True
        column = True
        row_end = size
        column_end = size

        while row:
            column = True
            column_end = size
            while column:
                crop = image[column_end - size:column_end, row_end - size:row_end]

                if np.shape(crop)[0] != size:
                    column = False
                elif np.shape(crop)[1] != size:
                    row = False
                    column = False
                else:
                    batch.append(crop)
                    shape.append((int((column_end-size)/size), int((row_end-size)/size)))
                column_end += size
            row_end += size

        preds = conv_model.predict(np.array(batch))

        average = np.average(preds)
        std = np.std(preds)
        median = np.median(preds)
        mean = np.mean(preds)
        max_ = np.max(preds)
        min_ = np.min(preds)

        print("{} {}" .format(item.split(".")[0], round(average, 2)))
