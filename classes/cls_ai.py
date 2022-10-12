from inc.inc_system import to8, ro8
from config import *

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from keras.models import Sequential
from keras.layers import Dense

from keras.callbacks import ModelCheckpoint
from numpy import loadtxt
from time import time


class AiFindMininimumBeforeRise:
    def __init__(self, log):
        self.log = log
        self.model_a = self.keras_model()

    def keras_model(self):
        model = Sequential()
        # units - количество нейронов
        model.add(Dense(units=128, input_dim=7, activation='relu'))
        model.add(Dense(units=64, activation='relu'))
        model.add(Dense(units=32, activation='relu'))
        model.add(Dense(units=8, activation='relu'))
        model.add(Dense(units=1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        # model.compile(loss='mse', optimizer='sgd', metrics=['accuracy'])
        return model

    def keras_predict(self, model, x):
        model.load_weights('_weights50_2_errors21_signals77.hdf5')
        predictions = model.predict_classes(x)
        return predictions[-1]
