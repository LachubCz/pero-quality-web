import os
import sys
import argparse

from timeit import default_timer as timer

import cv2
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt

import tensorflow as tf

from networks import get_network, get_convolution_part, get_end

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--image_name", action="store", type=str, required=True)

    args = parser.parse_args()

    return args


def confidence_to_rgb(confidence):
    if confidence <= 0.5:
        color_amount = int(confidence * 2 * 255)
        return 0, color_amount, 255
    else:
        color_amount = int((confidence - 0.5) * 2 * 255)
        return 0, 255, 255 - color_amount


if __name__ == "__main__":
    args = get_args()

    _, conv_model, size = get_network("regression_model_linear")
    conv_model.load_weights("./models/comparing_model_duo_7.h5")
    conv_model = get_end("regression_model_linear", conv_model, size)

    image = cv2.imread("{}" .format(args.image_name))

    batch = []
    shape = []
    skip = []
    row = True
    column = True
    row_end = size
    column_end = size

    model_path = './models/model_textseg'

    resized = cv2.resize(image, (0,0), fx=1/4, fy=1/4)

    saver = tf.train.import_meta_graph(model_path + '.meta')
    
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    segmentation_session = tf.Session(config=tf_config)
    saver.restore(segmentation_session, model_path)
    
    new_shape_x = resized.shape[0]
    new_shape_y = resized.shape[1]
    while not new_shape_x % 8 == 0:
        new_shape_x += 1
    while not new_shape_y % 8 == 0:
        new_shape_y += 1
    test_img_canvas = np.zeros((1, new_shape_x, new_shape_y, 3))
    test_img_canvas[0, :resized.shape[0], :resized.shape[1], :] = resized/256.

    out_map = segmentation_session.run('inderence:0', feed_dict={'inference_input:0': test_img_canvas})
    out_map = cv2.resize(cv2.cvtColor(out_map[0], cv2.COLOR_BGR2GRAY), (np.shape(image)[1], np.shape(image)[0]))

    while row:
        column = True
        column_end = size
        while column:
            crop = image[column_end - size:column_end, row_end - size:row_end]
            crop_ = out_map[column_end - size:column_end, row_end - size:row_end]

            if np.shape(crop)[0] != size:
                column = False
            elif np.shape(crop)[1] != size:
                row = False
                column = False
            else:
                brightness = np.mean(crop_)
                print(brightness)
                if brightness < 0.33:
                    skip.append(True)
                else:
                    skip.append(False)
                batch.append(crop)
                shape.append((int((column_end-size)/size), int((row_end-size)/size)))
            column_end += size
        row_end += size

    preds = conv_model.predict(np.array(batch))

    print(np.average(np.delete(preds, np.where(np.array(skip) == 1.0))))

    matrix = np.zeros((shape[-1][0]+1, shape[-1][1]+1))
    skip_matrix = np.zeros((shape[-1][0]+1, shape[-1][1]+1))
    for i, item in enumerate(shape):
        matrix[item[0]][item[1]] = preds[i]
        skip_matrix[item[0]][item[1]] = skip[i]

    overlay = image.copy()
    for y in range(np.shape(matrix)[0]):
        for x in range(np.shape(matrix)[1]):
            if not skip_matrix[y][x]:
                B, G, R = confidence_to_rgb(matrix[y][x])
                cv2.rectangle(overlay, (x*size, y*size), ( x*size+size, y*size+size), (B, G, R), -1)

    alpha = 0.5
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    if not os.path.exists("./heatmaps/{}" .format("regression_model")):
        os.makedirs("./heatmaps/{}" .format("regression_model"))
    cv2.imwrite("./heatmaps/{}/output_" .format("regression_model") + args.image_name.split("/")[-1], image)
