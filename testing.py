'''
Author: Richard Guinto
Project: DeepHomography
Dependencies: keras
Usage: python <this file>
'''


# From baudm
# Efficient loading in Keras using a Python generator

import os.path
import glob

import numpy as np
from keras.models import load_model
#from keras.layers import Activation, Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization, InputLayer
from keras import backend as K
from keras import optimizers

def data_loader(path, batch_size=64):
    """Generator to be used with model.fit_generator()"""
    while True:
        for npz in glob.glob(os.path.join(path, '*.npz')):
            # Load pack into memory
            archive = np.load(npz)
            images = archive['images']
            offsets = archive['offsets']
            # Yield minibatch
            for i in range(0, len(offsets), batch_size):
                end_i = i + batch_size
                try:
                    batch_images = images[i:end_i]
                    batch_offsets = offsets[i:end_i]
                except IndexError:
                    continue
                # Normalize
                batch_images = (batch_images - 127.5) / 127.5
                batch_offsets = batch_offsets / 32.
                yield batch_images, batch_offsets
#end of baudm code

def euclidean_l2(y_true, y_pred):
    return K.sqrt(K.sum(K.square(y_pred - y_true), axis=-1, keepdims=True))
#    return K.sqrt(K.maximum(K.sum(K.square(y_pred - y_true), axis=-1, keepdims=True), K.epsilon()))

# Dataset-specific
train_data_path = '/home/samsung/richard/dataset/training'
test_data_path = '/home/samsung/richard/dataset/test'
num_samples = 3 * 9216 # 43 archives x 9,216 samples per archive, but use just 40 and save the 3 for testing

# From the paper
batch_size = 64
total_iterations = 90000

steps_per_epoch = num_samples / batch_size # As stated in Keras docs
epochs = int(total_iterations / steps_per_epoch)


# load model
model = load_model("/data/richard/model.hdf5")

#ues optimizer Stochastic Gradient Methond with a Learning Rate of 0.005 and momentus of 0.9
sgd = optimizers.SGD(lr=0.005, momentum=0.9, decay=0.001355)

#compile model
model.compile(loss=euclidean_l2,\
        optimizer=sgd, metrics=['mean_squared_error'])


# Test
score = model.evaluate_generator(data_loader(test_data_path, batch_size),
                         steps=steps_per_epoch)

print('Test score:', score)

