import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

def model():
    classifier = Sequential()

    classifier.add(Dense(units = 1, input_shape=(1,), activation = 'sigmoid'))

    classifier.compile(optimizer = 'sgd', loss = 'binary_crossentropy', metrics = ['accuracy'])
    classifier.summary()

    return classifier

if __name__ == "__main__":
    array = [line for line in open('./correlation.txt')]

    crop = []
    x = []
    y = []

    for i, item in enumerate(array):
        crop.append(int(item.split(" ")[0]))
        x.append(float(item.split(" ")[1]))
        y.append(float(item.split(" ")[2]))

    end = model()

    end.fit(x, y, epochs = 10000)
    end.save_weights("end_of_network")

    pred = end.predict(x)

    ready = []
    for i, item in enumerate(pred):
        ready.append(item[0])
    print(ready)
    #correlation
    print(np.corrcoef(ready, y))

    #scatter plot
    plt.scatter(ready, y)
    plt.show()


    """
    train_datagen = ImageDataGenerator(rescale = 1./255, shear_range = 0.2, zoom_range = 0.2, horizontal_flip = True)
    test_datagen = ImageDataGenerator(rescale = 1./255)
    training_set = train_datagen.flow_from_directory('dataset/training_set', target_size = (64, 64), batch_size = 32, class_mode = 'binary')
    test_set = test_datagen.flow_from_directory('dataset/test_set', target_size = (64, 64), batch_size = 32, class_mode = 'binary')

    classifier.fit_generator(training_set, steps_per_epoch = 5, epochs = 500, validation_data = test_set, validation_steps = 1)
    classifier.save_weights("annotation_model.h5")
    """