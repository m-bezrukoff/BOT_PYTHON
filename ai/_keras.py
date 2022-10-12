# -*- coding: utf-8 -*-
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from keras.models import Sequential
from keras.layers import Dense

from keras.callbacks import ModelCheckpoint
from numpy import loadtxt
from time import time


def keras_model(dim, weights_file_name=''):
    model = Sequential()
    # units - количество нейронов
    # model.add(Dense(units=64, input_dim=dim, activation='relu'))
    # model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=128, input_dim=dim, activation='relu'))
    model.add(Dense(units=64, activation='relu'))
    model.add(Dense(units=32, activation='relu'))
    model.add(Dense(units=8, activation='relu'))
    model.add(Dense(units=1, activation='sigmoid'))

    # model.compile(loss='mse', optimizer='sgd', metrics=['accuracy'])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print('Keras model created')
    if weights_file_name:
        model.load_weights(weights_file_name)
        print(weights_file_name, 'weights loaded')
    return model


def keras_predict_class(model, data):
    return model.predict_classes(data)[-1]


def keras_predict_playground(log, model, x, y):
    filepath = 'weights/temp.hdf5'
    model.load_weights(filepath)
    # predictions = model.predict(x)
    predictions = model.predict_classes(x)

    signals = 0
    errors = 0
    iterations = 0

    for i in range(len(x)):
        iterations += 1
        # print('%s => %d (expected %d)' % (x[i].tolist(), predictions[i], y[i]))
        if predictions[i] == 1:
            signals += 1
        if predictions[i] != y[i]:
            errors += 1

    log.debug('{} errors / {} iterations => {}% errors '.format(errors, iterations, round(errors / (iterations / 100)), 2))
    log.debug('total signals: {}'.format(signals))

    return errors, signals


def keras_train(log, model, x, y, epochs=10, batch_size=10):
    t1 = time()
    filepath = 'weights/temp.hdf5'
    checkpoint = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=0, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    history = model.fit(x,
                        y,
                        validation_split=0.1,
                        epochs=epochs,
                        batch_size=batch_size,
                        callbacks=callbacks_list,
                        verbose=1)
    # print(history)
    # history = model.fit(x, y, epochs=100, batch_size=10, verbose=0)

    _, accuracy = model.evaluate(x, y)

    log.debug('----------------------------------------------------------')
    log.debug('New keras model with epochs: {} & batch_size: {}'.format(epochs, batch_size))
    log.debug('Accuracy: %.2f' % (accuracy*100))
    log.debug('Time spent: {} sec'.format(int(time()-t1)))

    return history, accuracy
