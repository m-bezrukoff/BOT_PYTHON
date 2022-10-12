# -*- coding: utf-8 -*-

from ai._keras import keras_model, keras_train, keras_predict_playground
from ai._keras_plot import keras_plot
from numpy import loadtxt
from inc.inc_logger import get_logger
import shutil


log = get_logger('log.txt')


def keras_train_complex(limit, epochs=[10], batch_sizes=[4]):
    dataset = loadtxt('dataset_BTC_ETH.txt', delimiter=' ')
    # limit = 200000
    print('dataset:', dataset.shape)
    arr_dimension = dataset.shape[1] - 1

    x1 = dataset[:limit, 0:arr_dimension]  # данные для обучения
    print('x1', x1.shape)
    print(x1)
    y1 = dataset[:limit, arr_dimension]    # данные для обучения
    print(y1)

    x2 = dataset[limit:, 0:arr_dimension]  # данные для тестирования
    y2 = dataset[limit:, arr_dimension]    # данные для тестирования
    # print(y)

    # epochs = [5, 10, 15, 20, 50, 10, 150, 200, 250, 300, 400, 500, 700, 800, 900, 1000, 1500, 2000]
    # epochs = [10]
    # batch_sizes = [1, 2, 3, 4, 5, 8, 10, 15, 20, 25, 30, 40, 50]
    # batch_sizes = [4]

    min_errors = 99999999999999999
    max_signals = 0

    ai_model = keras_model(arr_dimension)

    for epoch in epochs:
        for batch_size in batch_sizes:
            for i in range(1):
                print('train epoch:', epoch, 'batch_size:', batch_size)
                history, tr_accuracy = keras_train(log, ai_model, x1, y1, epochs=epoch, batch_size=batch_size)
                # plot train history
                # keras_plot(history)
                print('predict')
                errors, signals = keras_predict_playground(log, ai_model, x2, y2)

                if errors < min_errors or signals > max_signals:

                    new_file_path = 'weights/' + \
                                    format(errors / signals if signals else 1, '.03f') + \
                                    '_sig_' + str(signals) + \
                                    '_err_' + str(errors) + \
                                    '_epo_' + str(epoch) + \
                                    '_bat_' + str(batch_size) + \
                                    '_dim_' + str(arr_dimension) + \
                                    '.hdf5'
                    shutil.copyfile('weights/temp.hdf5', new_file_path)

                    if errors < min_errors:
                        min_errors = errors

                    if signals > max_signals:
                        max_signals = signals

    return arr_dimension
