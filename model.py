import os

import cv2
import numpy as np

from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Input
from keras.layers import Dense
from keras.layers import concatenate
from keras.layers import Subtract
from keras.models import Model
from keras.optimizers import Adadelta
from keras.layers import GlobalAveragePooling2D


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from app.db import Base, User, Annotation, Crop, Page, Record, Set, RecordCrop

def model():
    first_input = Input(shape=(128, 128, 3))
    second_second = Input(shape=(128, 128, 3))

    first = Conv2D(32, (3, 3), input_shape = (128, 128, 3), activation = 'relu')(first_input)
    first = MaxPooling2D(pool_size = (2, 2))(first)
    first = Conv2D(32, (3, 3), activation = 'relu')(first)
    first = MaxPooling2D(pool_size = (2, 2))(first)
    first = GlobalAveragePooling2D()(first)
    first = Dense(1, activation='relu')(first)

    second = Conv2D(32, (3, 3), input_shape = (128, 128, 3), activation = 'relu')(second_second)
    second = MaxPooling2D(pool_size = (2, 2))(second)
    second = Conv2D(32, (3, 3), activation = 'relu')(second)
    second = MaxPooling2D(pool_size = (2, 2))(second)
    second = GlobalAveragePooling2D()(second)
    second = Dense(1, activation='relu')(second)

    subtracted = Subtract()([first, second])
    
    output = Dense(1, activation='sigmoid')(subtracted)
    #binary cross entropy
    model = Model(inputs=[first_input, second_second], outputs=output)


    model.compile(loss='binary_crossentropy', optimizer=Adadelta(lr=0.02), metrics=["binary_accuracy", "binary_crossentropy"])
    model.summary()

    return model

    
if __name__ == "__main__":
    engine = create_engine('sqlite:///database.sqlite3',
                           convert_unicode=True,
                           connect_args={'check_same_thread': False})
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)

    records_set_1 = Record.query.filter(Record.set_id == 1).all()
    records_set_4 = Record.query.filter(Record.set_id == 4).all()

    merged_records = records_set_1 + records_set_4
    not_empty_records = []
    labels = []
    for i, item in enumerate(merged_records):
        if len(item.annotations) > 0:
            _01 = 0
            _10 = 0
            for e, elem in enumerate(item.annotations):
                if elem.annotation == "01":
                    _01 += 1
                elif elem.annotation == "10":
                    _10 += 1
            labels.append([_01 / (_01 + _10), _10 / (_01 + _10)])
            
            not_empty_records.append(item.id)

    #print(labels)

    crops = []
    for i, item in enumerate(not_empty_records):
        record = RecordCrop.query.filter(RecordCrop.record_id == item).order_by(RecordCrop.order).all()
        crops.append([record[0].crop_id, record[1].crop_id])

    print(len(crops), len(labels))
    
    #print(crops)
    classifier = model()

    path = './app/static/crops'
    episodes = 1000
    minibatch_size = 256
    for i in range(episodes):
        indexes = np.random.randint(low=0, high=len(crops), size=minibatch_size)
        image_batch_1 = []
        image_batch_2 = []
        for i, item in enumerate(indexes):
            image = cv2.imread(os.path.join(path, str(crops[item][0])+'.jpg'))
            max_width = image.shape[1] - 128
            max_height = image.shape[0] - 128

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+128, width[0]:width[0]+128]

            image_batch_1.append(image)

            image = cv2.imread(os.path.join(path, str(crops[item][1])+'.jpg'))
            max_width = image.shape[1] - 128
            max_height = image.shape[0] - 128

            width = np.random.randint(max_width, size=1)
            height = np.random.randint(max_height, size=1)

            image = image[height[0]:height[0]+128, width[0]:width[0]+128]

            image_batch_2.append(image)
            #image_batch_2.append(cv2.resize(cv2.imread(os.path.join(path, str(crops[item][1])+'.jpg')), (128, 128)))

        labs = [labels[x] for x in indexes]
        for i, item in enumerate(labs):
            labs[i] = [round(item[0]), round(item[1])]

        classifier.fit([np.array(image_batch_1), np.array(image_batch_2)], np.array(labs), epochs=1, verbose=1)

    classifier.save_weights("annotator.h5")
    #classifier.fit()
    