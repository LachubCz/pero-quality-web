import os

import numpy as np
from shutil import copyfile

if __name__ == "__main__":
    #file with outputs from quality network
    array = [line for line in open('crops_rating.txt')]

    average = []

    for i, item in enumerate(array):
        crop.append(item.split(" ")[0])
        average.append(float(item.split(" ")[1]))

    min_, max_ = np.min(average), np.max(average)
    normalized = average.copy()
    for i, val in enumerate(average):
        normalized[i] = (val-min_) / (max_-min_)

    closest_to = []
    counter = 0
    for i in range(51):
        closest_to.append(counter)
        counter += 0.02

    print(closest_to)

    for i, item in enumerate(closest_to):
        value = min(normalized, key=lambda x:abs(x-item))
        index = normalized.index(value)

        copyfile(os.path.join("/mnt/c/Users/LachubCz_NTB/Documents/GitHub/pero-web-data/crops", crop[index]+".jpg"), os.path.join("./crops/", crop[index]+".jpg"))
