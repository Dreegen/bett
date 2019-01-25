# %% Dependencies
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation
from keras.utils import to_categorical
from keras.optimizers import SGD


import pandas as pd

import numpy as np
from numpy import argmax

import sklearn
from sklearn.model_selection import train_test_split

# %% IMPORT DATA
loc = 'data/'
data = pd.read_csv('data/final_dataset.csv')

# %% PREPROCESS
# drop rows with empty cells
data = data.dropna(subset=['Odds_1', 'Odds_x', 'Odds_2', 'FTR'], how='any')

# Scale


# %% Split to X and Y and create training/testing
X_all = np.array(data.filter(['Odds_1', 'Odds_x', 'Odds_2']))
y_all = to_categorical(np.array(data.FTR.astype("category").cat.codes)).astype(int)
n_cols = X_all.shape[1]

# split the dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y_all, test_size=0.2, random_state=2)

# MOOEL 1 %% Sequence classification with LSTM:
model = Sequential()

model.add(Dense(25, activation='relu', input_shape=(n_cols,)))
model.add(Dense(25, activation='relu',))
model.add(Dense(3, activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=4)

test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Loss: {test_loss}, Acc: {test_acc}")


# %% Display prediction
y_names = ['Away', 'Draw', 'Home']
odds_order = ['Home', 'Draw', 'Away']

# 0.0.1 = HOME
# 0.1.0 = DRAW
# 1.0.0 = AWAY

rows_list2 = []
for i in range(X_test.shape[0]):
    odds = X_test[i]
    prob = model.predict(X_test)[i]
    dict = {'odds_1': odds[0], 'odds_x': odds[1], 'odds_2': odds[2], 'prob_1': prob[2], 'prob_x': prob[1], 'prob_2': prob[0],
            'predicted': y_names[np.argmax(prob)], 'winner': y_names[np.argmax(y_test[i])], 'favorite': odds_order[np.argmin(odds)]}
    rows_list2.append(dict)

columnsTitles = ['favorite', 'predicted', 'winner', 'odds_1',
                 'odds_x', 'odds_2', 'prob_1', 'prob_x', 'prob_2']
df = pd.DataFrame(rows_list2, columns=columnsTitles)
df.to_csv(loc + "predicted_dataset.csv")

# %% Save the model
model.save('working_model.h5')  # creates a HDF5 file 'my_model.h5'

#### DEV ####
# odds_1 = 1.3
# odds_x = 13
# odds_2 = 4.2
#
# # Make to np.array
# x = np.array([odds_1, odds_x, odds_2])
#
# # Add the input to a batch where it's the only member.
# x = (np.expand_dims(x, 0))
#
# model.predict(x)

# # IF NEED FOR JSON AND SEPERATE WEIGHTS
# # serialize model to JSON
# model_json = model.to_json()
# with open("model.json", "w") as json_file:
#     json_file.write(model_json)
# # serialize weights to HDF5
# model.save_weights("model.h5")
# print("Saved model to disk")
