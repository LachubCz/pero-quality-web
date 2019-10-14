import os

import cv2
import numpy as np

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D, AveragePooling2D
from keras.layers import Flatten
from keras.layers import Input
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import concatenate
from keras.layers import Subtract
from keras.models import Model, Sequential
from keras.optimizers import Adadelta, SGD
from keras.layers import GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.activations import sigmoid, linear
from keras.layers import Activation

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

def model(conv):
    first_input = Input(shape=(128, 128, 3))
    second_input = Input(shape=(128, 128, 3))

    first = conv(first_input)
    second = conv(second_input)

    subtracted = Subtract()([first, second])
    output = Activation(sigmoid)(subtracted)

    model = Model(inputs=[first_input, second_input], outputs=output)
    model.compile(loss='binary_crossentropy', optimizer=Adadelta(lr=0.2), metrics=["binary_accuracy", "binary_crossentropy"])
    model.summary()

    return model

def convolutional_part():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(AveragePooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(AveragePooling2D(pool_size = (2, 2)))
    model.add(Dropout(rate=0.2))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(AveragePooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(Dropout(rate=0.2))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


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

    conv = convolutional_part()
    classifier = model(conv)

    classifier.load_weights("comparing_model_all_avg_drop.h5")
    print("Weights loaded.")

    net_input = Input(shape=(128, 128, 3))

    net = conv(net_input)
    output = Activation(linear)(net)

    conv = Model(inputs=[net_input], outputs=output)

    conv.compile(loss='mse', optimizer='adam', metrics=["mean_absolute_error", "mean_absolute_percentage_error"])
    conv.summary()

    path = './app/static/crops'
    episodes = 1000
    minibatch_size = 1024
    for i in range(episodes):
        indexes_trn = np.random.randint(low=0, high=len(trn_crops), size=minibatch_size)
        indexes_tst = np.random.randint(low=0, high=len(tst_crops), size=int(minibatch_size/10))

        image_batch_trn = []
        for _, item in enumerate(indexes_trn):
            image = cv2.imread(os.path.join(path, str(trn_crops[item])+".jpg"))

            max_width = image.shape[1] - 128
            max_height = image.shape[0] - 128

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+128, width[0]:width[0]+128]
            image_batch_trn.append(image/255.0)

        image_batch_tst = []
        for _, item in enumerate(indexes_tst):
            image = cv2.imread(os.path.join(path, str(tst_crops[item])+".jpg"))

            max_width = image.shape[1] - 128
            max_height = image.shape[0] - 128

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+128, width[0]:width[0]+128]
            image_batch_tst.append(image/255.0)

        labs_trn = []
        for e, elem in enumerate(indexes_trn):
            labs_trn.append(ranking[trn_crops[elem]])

        labs_tst = []
        for e, elem in enumerate(indexes_tst):
            labs_tst.append(ranking[tst_crops[elem]])

        conv.fit([np.array(image_batch_trn)], np.array(labs_trn), 
            epochs=50, verbose=1, validation_data=([np.array(image_batch_tst)], np.array(labs_tst)))

        conv.save_weights("comparing_model_{}.h5" .format(i))
