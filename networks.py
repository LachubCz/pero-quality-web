from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D, AveragePooling2D, ZeroPadding2D
from keras.layers import GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.layers import Flatten
from keras.layers import Input
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import concatenate
from keras.layers import Subtract
from keras.layers import Activation
from keras.models import Model, Sequential
from keras.optimizers import Adadelta
from keras.regularizers import l1_l2, l2
from keras.activations import sigmoid, linear


def model(conv, size, summary=True):
    first_input = Input(shape=(size, size, 3))
    second_input = Input(shape=(size, size, 3))

    first = conv(first_input)
    second = conv(second_input)

    subtracted = Subtract()([first, second])
    output = Activation(sigmoid)(subtracted)

    model = Model(inputs=[first_input, second_input], outputs=output)
    model.compile(loss='binary_crossentropy', optimizer=Adadelta(lr=0.2), metrics=["binary_accuracy", "binary_crossentropy"])
    if summary:
        model.summary()

    return model


def comparing_model_128():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_128_drop():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Dropout(rate=0.2))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(Dropout(rate=0.2))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_128_all_avg_drop():
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


def comparing_model_128_all_max():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(GlobalMaxPooling2D())
    model.add(Dense(1))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_512():
    model = Sequential()

    model.add(Conv2D(32, (3, 3), input_shape = (512, 512, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(128, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(256, (3, 3), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1))

    imgInput = Input(shape=(512, 512, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_128_all_avg_drop_reg():
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
    model.add(Dense(1, activity_regularizer=l2(0.01)))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_128_reg():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1, activity_regularizer=l2(0.01)))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_128_reg12():
    model = Sequential()

    model.add(Conv2D(8, (3, 3), input_shape = (128, 128, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(16, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1, activity_regularizer=l1_l2(l1=0.01, l2=0.01)))

    imgInput = Input(shape=(128, 128, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_256_reg12():
    model = Sequential()

    model.add(Conv2D(16, (3, 3), input_shape = (256, 256, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (3, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(128, (3, 3), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1, activity_regularizer=l1_l2(l1=0.01, l2=0.01)))

    imgInput = Input(shape=(256, 256, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_256_5x5_reg12():
    model = Sequential()

    model.add(Conv2D(16, (5, 5), input_shape = (256, 256, 3), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(32, (5, 5), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(64, (5, 5), activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2, 2)))
    model.add(Conv2D(128, (5, 5), activation = 'relu'))
    model.add(GlobalAveragePooling2D())
    model.add(Dense(1, activity_regularizer=l1_l2(l1=0.01, l2=0.01)))

    imgInput = Input(shape=(256, 256, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def comparing_model_VGG_16(pop_count=6, summary=True):
    model = Sequential()

    model.add(ZeroPadding2D((1,1), input_shape=(224, 224, 3), data_format='channels_last'))
    model.add(Conv2D(64, kernel_size=(3, 3), strides=1, activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(64, kernel_size=(3, 3), strides=1, activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2), data_format='channels_last'))

    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2), data_format='channels_last'))

    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2), data_format='channels_last'))

    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2), data_format='channels_last'))

    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(ZeroPadding2D((1,1)))
    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D((2,2), strides=(2,2), data_format='channels_last'))

    model.add(Flatten())
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1000, activation='softmax'))

    model.load_weights('./models/vgg16_weights_tf_dim_ordering_tf_kernels.h5')

    for i in range(pop_count):
        model.pop()

    if summary:
        model.summary()

    model.add(GlobalAveragePooling2D())
    model.add(Dense(1, activity_regularizer=l1_l2(l1=0.01, l2=0.01)))

    imgInput = Input(shape=(224, 224, 3))
    imgOutput = model(imgInput)

    return Model(inputs=imgInput, outputs=imgOutput)


def get_network(model_name, summary=True):
    if model_name == "comparing_model_128":
        conv = comparing_model_128()
        size = 128
    elif model_name == "comparing_model_128_drop":
        conv = comparing_model_128_drop()
        size = 128
    elif model_name == "comparing_model_128_all_avg_drop":
        conv = comparing_model_128_all_avg_drop()
        size = 128
    elif model_name == "comparing_model_128_all_max":
        conv = comparing_model_128_all_max()
        size = 128
    elif model_name == "comparing_model_512":
        conv = comparing_model_512()
        size = 512
    elif model_name == "comparing_model_128_all_avg_drop_reg":
        conv = comparing_model_128_all_avg_drop_reg()
        size = 128
    elif model_name == "comparing_model_128_reg":
        conv = comparing_model_128_reg()
        size = 128
    elif model_name == "comparing_model_128_reg12":
        conv = comparing_model_128_reg12()
        size = 128
    elif model_name == "comparing_model_256_reg12":
        conv = comparing_model_256_reg12()
        size = 256
    elif model_name == "comparing_model_256_5x5_reg12":
        conv = comparing_model_256_5x5_reg12()
        size = 256
    elif model_name == "comparing_model_VGG_16":
        conv = comparing_model_VGG_16(summary=False)
        size = 224
    elif model_name == "comparing_model_VGG_16_small":
        conv = comparing_model_VGG_16(pop_count=20, summary=False)
        size = 224
    elif model_name == "comparing_model_VGG_16_smaller":
        conv = comparing_model_VGG_16(pop_count=27, summary=False)
        size = 224

    classifier = model(conv, size, summary)

    return classifier, conv, size


def get_convolution_part(conv, size, summary=True):
    net_input = Input(shape=(size, size, 3))
    net = conv(net_input)
    output = Activation(linear)(net)
    
    classifier = Model(inputs=[net_input], outputs=output)

    classifier.compile(loss='mse', optimizer='adam', metrics=["mean_absolute_error", "mean_absolute_percentage_error"])
    if summary:
        classifier.summary()

    return classifier

def get_end(model_name, model, size, summary=True):
    end = Sequential()

    end.add(Dense(units = 1, input_shape=(1,), activation = 'sigmoid'))
    end.load_weights('./models/end_of_{}.h5' .format(model_name))

    net_input = Input(shape=(size, size, 3))
    net = model(net_input)
    output = end(net)
    
    classifier = Model(inputs=[net_input], outputs=output)

    classifier.compile(loss='mse', optimizer='adam', metrics=["mean_absolute_error", "mean_absolute_percentage_error"])
    if summary:
        classifier.summary()

    return classifier
