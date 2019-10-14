import sys
import argparse

import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt

from networks import get_network, get_convolution_part

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model_name", action="store", type=str, required=True)
    parser.add_argument("-i", "--image_name", action="store", type=str, required=True)
    parser.add_argument("-w", "--model_weights", action="store", type=str, required=True)
    parser.add_argument("--normalization", action="store_true")
    parser.add_argument("--distribution", action="store_true")


    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()

    classifier, conv, size = get_network(args.model_name)
    classifier.load_weights(args.model_weights)
    print("Weights loaded.")

    conv_model = get_convolution_part(conv, size)

    image = cv2.imread("{}" .format(args.image_name))

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

    if args.distribution:
        x = preds
        plt.hist(x, normed=True, bins=30)
        plt.ylabel('Probability');
        plt.show()

    average = np.average(preds)
    std = np.std(preds)
    median = np.median(preds)
    mean = np.mean(preds)
    max_ = np.max(preds)
    min_ = np.min(preds)

    print("Minimum: ",            min_)
    print("Maximum: ",            max_)
    print("Median: ",             median)
    print("Mean value: ",         mean)
    print("Average value: ",      average)
    print("Standart deviation: ", std)

    if args.normalization:
        for i, val in enumerate(preds):
            if val > median + std*(median/average):
                if (median - std*(median/average)) > max_:
                    preds[i] = max_
                else:
                    preds[i] = median + std*(median/average)
                
            elif val < median - std*(median/average):
                if (median - std*(median/average)) < min_:
                    preds[i] = min_
                else:
                    preds[i] = median - std*(median/average)
        print("Values normalized.")

    min_, max_ = min(preds), max(preds)
    normalized = preds.copy()
    for i, val in enumerate(preds):
        normalized[i] = (val-min_) / (max_-min_)

    matrix = np.zeros((shape[-1][0]+1, shape[-1][1]+1))
    for i, item in enumerate(shape):
        matrix[item[0]][item[1]] = normalized[i]

    overlay = image.copy()
    for y in range(np.shape(matrix)[0]):
        for x in range(np.shape(matrix)[1]):
            #R = (255 * int(matrix[y][x]*100)) / 100
            #G = (255 * (100 - int(matrix[y][x]*100))) / 100 
            G = (255 * int(matrix[y][x]*100)) / 100
            R = (255 * (100 - int(matrix[y][x]*100))) / 100 
            B = 0

            cv2.rectangle(overlay, (x*size, y*size), ( x*size+size, y*size+size), (B, G, R), -1)

    alpha = 0.3
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    cv2.imshow(args.image_name, image)
    cv2.waitKey(0)