import argparse

import numpy as np

from keras.models import Sequential
from keras.layers import Dense

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')


def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--model_name", action="store", type=str, required=True)
    parser.add_argument("-c", "--correlation_file", action="store", type=str, required=True)

    args = parser.parse_args()

    return args


def model():
    classifier = Sequential()

    classifier.add(Dense(units = 1, input_shape=(1,), activation = 'sigmoid'))
    classifier.compile(optimizer = 'RMSprop', loss = 'binary_crossentropy')
    classifier.summary()

    return classifier

if __name__ == "__main__":
    args = get_args()

    array = [line for line in open(args.correlation_file)]

    crop = []
    x = []
    y = []

    for i, item in enumerate(array):
        crop.append(int(item.split(" ")[0]))
        x.append(float(item.split(" ")[1]))
        y.append(float(item.split(" ")[2]))

    end = model()

    end.fit(x, y, epochs = 5000)
    end.save_weights("./models/end_of_{}.h5" .format(args.model_name))

    pred = end.predict(x)

    ready = []
    for i, item in enumerate(pred):
        ready.append(item[0])

    #correlation
    print(np.corrcoef(ready, y))

    #scatter plot
    #plt.scatter(ready, y)
    #plt.show()
