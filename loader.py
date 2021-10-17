# This uses the Caltech bird database: http://www.vision.caltech.edu/visipedia
import os
import matplotlib.pyplot as plt
import tensorflow as tf
import pandas as pd
import numpy as np

print("TensorFlow version: {}".format(tf.__version__))
print("Eager execution: {}".format(tf.executing_eagerly()))

data_location="/media/ssd/strube1/CUB_200_2011"
train_dataset_fp = "%s/images.txt" % data_location


print("Local copy of the dataset file: {}".format(train_dataset_fp))

batch_size=128

images=pd.read_csv("%s/images.txt" % data_location, sep=' ', header=None)
images.index=images.index+1  # It begins with 1
classes=pd.read_csv("%s/classes.txt" % data_location, sep=' ', header=None)
classes.index=classes.index+1  # It begins with 1
labels=pd.read_csv("%s/image_class_labels.txt" % data_location, sep=' ', header=None)
labels.index=labels.index+1
bounding_boxes=pd.read_csv("%s/bounding_boxes.txt" % data_location, sep=' ', header=None)
bounding_boxes.index=bounding_boxes.index+1

classes[1][labels[1][images[0][555]]]


train_dataset = tf.data.experimental.make_csv_dataset(
    train_dataset_fp,
    batch_size,
    column_names=column_names,
    label_name=label_name,
    num_epochs=1)