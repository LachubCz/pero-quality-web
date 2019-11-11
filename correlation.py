import os
import argparse

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

from shutil import copyfile

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--quality_network_file", action="store", type=str, required=True)
    parser.add_argument("-a", "--annotation_model_file", action="store", type=str, required=True)
    parser.add_argument("-m", "--mode", choices=["compare", "result", "display"], action="store", type=str, required=True)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    #quality network file
    array = [line for line in open(args.quality_network_file)]

    crop_1 = []
    average_1 = []

    for i, item in enumerate(array):
        crop_1.append(int(item.split(" ")[0].split(".")[0]))
        average_1.append(float(item.split(" ")[1]))
    normalized = average_1
    """
    min_, max_ = np.min(average_1), np.max(average_1)
    normalized = average_1.copy()
    for i, val in enumerate(average_1):
        normalized[i] = (val-min_) / (max_-min_)
    """

    #annotation model file
    array = [line for line in open(args.annotation_model_file)]

    crop_2 = []
    y = []

    for i, item in enumerate(array):
        crop_2.append(int(item.split(" ")[0]))
        y.append(float(item.split(" ")[1]))

    x = y.copy()
    for i, item in enumerate(crop_2):
        index = crop_1.index(item)
        x[i] = normalized[index]

    #correlation
    corr = np.corrcoef(x, y)

    if corr[0][1] < 0:
        y = []
        for i, item in enumerate(array):
            y.append(1-float(item.split(" ")[1]))

    if args.mode == "result":
        corr = np.corrcoef(x, y)
        print(args.quality_network_file, corr[0][1])
    elif args.mode == "compare":
        for i, item in enumerate(crop_2):
            print(crop_2[i], x[i], y[i])
    elif args.mode == "display":
        #scatter plot
        corr = np.corrcoef(x, y)
        print(args.quality_network_file, corr[0][1])
        
        plt.scatter(x, y)
        plt.show()
