import os
import cv2
import pickle

if __name__ == "__main__":
    with open("dataset_large.pkl", "rb") as input:
        dataset = pickle.load(input)

    crops = dataset[0]

    path = './'
    counter = 0
    for i, item in enumerate(crops):
        image = cv2.imread(os.path.join(path, str(item[0][0])))
        image = image[item[0][2]:item[0][2]+item[0][4], item[0][1]:item[0][1]+item[0][3]]
        cv2.imwrite("./images/{}.jpg" .format(counter), image)

        dataset[0][i][0] = "./images/" + str(counter) + ".jpg"
        counter += 1
        ########################################

        image = cv2.imread(os.path.join(path, str(item[1][0])))
        image = image[item[1][2]:item[1][2]+item[1][4], item[1][1]:item[1][1]+item[1][3]]
        cv2.imwrite("./images/{}.jpg" .format(counter), image)

        dataset[0][i][1] = "./images/" + str(counter) + ".jpg"
        counter += 1

    with open("dataset_large_converted.pkl", "wb") as output:
        pickle.dump(dataset, output, pickle.HIGHEST_PROTOCOL)
