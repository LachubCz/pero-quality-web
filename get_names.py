import pickle
import cv2

from shutil import copyfile

"""
with open("dataset_large.pkl", "rb") as input:
    dataset = pickle.load(input)

set_ = set()
for i, item in enumerate(dataset[0]):
    set_.add(item[0][0])
    set_.add(item[1][0])
    

#print(len(set_))
for i, item in enumerate(set_):
    print(item)
"""

with open("items_in_dataset.txt") as f:
    content = f.readlines()

content = [x.strip() for x in content] 

for i, item in enumerate(content):
    print(item.split("/")[1].split(".")[0])
    #copyfile("./" + item, "./images2/" + item.split("/")[1])