import os
import cv2
import argparse
import numpy as np
from classifier import model

def get_args():
    """
    method for parsing of arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--count", type=int,
                        default=10, help="Number of records to generate.")
    parser.add_argument("-d", "--directory", action="store", type=str, required=True,
                        help="name of directory with images")
    parser.add_argument("-o", "--output_file", action="store", type=str, required=True,
                        help="name of output file with crops")
    parser.add_argument("-w", "--width", action="store", type=int,
                        default=512, help="width of images in set")
    parser.add_argument("--height", action="store", type=int,
                        default=512, help="height of images in set")
    parser.add_argument("--classifier", action="store_true", help="use classifier?")

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = get_args()
    print(args)

    classifier = model()
    classifier.load_weights("model.h5")

    f = open(args.output_file, "w")
    for i, item in enumerate(os.listdir(args.directory)):
        img = cv2.imread(os.path.join(args.directory, item))
        max_width = img.shape[1] - args.width
        max_height = img.shape[0] - args.height
        coords = []
        flag = True
        while flag:
            widths = np.random.randint(max_width, size=2*args.count)
            heights = np.random.randint(max_height, size=2*args.count)
            batch = []
            for e in range(args.count*2):
                image = img[heights[e]:heights[e]+args.height, widths[e]:widths[e]+args.width]
                image = cv2.resize(image, (64, 64))
                batch.append(image)

            predictions = classifier.predict(np.array(batch))
            for p, pred in enumerate(predictions):
                if pred == 1:
                    coords.append(str(widths[p])+':'+str(heights[p]))
                if len(coords) == args.count:
                    flag = False
                    break

        f.write("{} " .format(os.path.join(args.directory, item)))
        for c, coord in enumerate(coords):
            f.write("{} " .format(coord))
            if (c+1) == len(coords):
                f.write("\n")
    f.close()
