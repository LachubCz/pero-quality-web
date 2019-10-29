import os
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

from shutil import copyfile

if __name__ == "__main__":
    #quality network file
    array = [line for line in open('./rankings/crops_48_quality_network.txt')]

    crop_1 = []
    average_1 = []

    for i, item in enumerate(array):
        crop_1.append(int(item.split(" ")[0].split(".")[0]))
        average_1.append(float(item.split(" ")[1]))

    min_, max_ = np.min(average_1), np.max(average_1)
    normalized = average_1.copy()
    for i, val in enumerate(average_1):
        normalized[i] = (val-min_) / (max_-min_)

    #annotation model file
    array = [line for line in open('./rankings/crops_48_annotation_model.txt')]

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
    print(np.corrcoef(x, y))

    #scatter plot
    plt.scatter(x, y)
    plt.show()
