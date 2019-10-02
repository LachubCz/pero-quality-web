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
from keras.optimizers import Adadelta
from keras.layers import GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.activations import sigmoid
from keras.layers import Activation

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
    conv = convolutional_part()
    classifier = model(conv)

    classifier.load_weights("comparing_model_all_avg_drop.h5")
    print("Weights loaded.")

    image = cv2.imread("636.jpg")

    batch = []
    shape = []
    size = 128
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

    preds = conv.predict(np.array(batch))

    min_, max_ = min(preds), max(preds)
    normalized = preds.copy()
    for i, val in enumerate(preds):
        normalized[i] = (val-min_) / (max_-min_)

    matrix = np.zeros((shape[-1][0]+1, shape[-1][1]+1))
    for i, item in enumerate(shape):
        matrix[item[0]][item[1]] = normalized[i]

    for y in range(np.shape(matrix)[0]):
        for x in range(np.shape(matrix)[1]):
            overlay = image.copy()
            alpha = 0.3

            R = (255 * int(matrix[y][x]*100)) / 100
            G = (255 * (100 - int(matrix[y][x]*100))) / 100 
            B = 0

            cv2.rectangle(overlay, (x*size, y*size), ( x*size+size, y*size+size), (B, G, R), -1)
            cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    cv2.imshow("image", image)
    cv2.waitKey(0)
