import imp
import os, sys
import shutil
import obspy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tensorflow import keras
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
from os import listdir
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from os.path import isfile, join
from itertools import cycle
import itertools

# to_categorical function
def to_categorical(y, num_classes=None, dtype='float32'):
    """Converts a class vector (int
    egers) to binary class matrix.
    E.g. for use with categorical_crossentropy.
    Arguments
        y: class vector to be converted into a matrix

    (integers from 0 to num_classes).
        num_classes: total number of classes.
        dtype: The data type expected by the input. Default: 'float32'.
    Returns
        A binary matrix representation of the input. The classes axis is placed
        last.
    """
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=dtype)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical

# import the keras libraries
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPooling1D, BatchNormalization, Activation, GlobalAveragePooling1D


def make_model(input_shape):
    input_layer = keras.layers.Input(input_shape)

    conv1 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(input_layer)
    conv1 = keras.layers.BatchNormalization()(conv1)
    conv1 = keras.layers.ReLU()(conv1)

    conv2 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(conv1)
    conv2 = keras.layers.BatchNormalization()(conv2)
    conv2 = keras.layers.ReLU()(conv2)

    conv3 = keras.layers.Conv1D(filters=64, kernel_size=3, padding="same")(conv2)
    conv3 = keras.layers.BatchNormalization()(conv3)
    conv3 = keras.layers.ReLU()(conv3)

    gap = keras.layers.GlobalAveragePooling1D()(conv3)

    num_classes = 3

    output_layer = keras.layers.Dense(num_classes, activation="softmax")(gap)

    return keras.models.Model(inputs=input_layer, outputs=output_layer)


plt.style.use('ggplot')
plt.rcParams['font.family'] = 'sans-serif' 
plt.rcParams['font.serif'] = 'Ubuntu' 
plt.rcParams['font.monospace'] = 'Ubuntu Mono' 
plt.rcParams['font.size'] = 14 
plt.rcParams['axes.labelsize'] = 12 
plt.rcParams['axes.labelweight'] = 'bold' 
plt.rcParams['axes.titlesize'] = 12 
plt.rcParams['xtick.labelsize'] = 12 
plt.rcParams['ytick.labelsize'] = 12 
plt.rcParams['legend.fontsize'] = 12 
plt.rcParams['figure.titlesize'] = 12 
plt.rcParams['image.cmap'] = 'jet' 
plt.rcParams['image.interpolation'] = 'none' 
plt.rcParams['figure.figsize'] = (12, 10) 
plt.rcParams['axes.grid']=True
plt.rcParams['lines.linewidth'] = 2 
plt.rcParams['lines.markersize'] = 8
colors = ['xkcd:pale orange', 'xkcd:sea blue', 'xkcd:pale red', 'xkcd:sage green', 'xkcd:terra cotta', 'xkcd:dull purple', 'xkcd:teal', 'xkcd: goldenrod', 'xkcd:cadet blue',
'xkcd:scarlet']

target_freq = 10


source_path = r'/Volumes/UNTITLE/10_cft_snr/'
file = 'main_stalta_labelled.txt'

# read the file
df = pd.read_csv(os.path.join(source_path, file), sep=' ', header=None)

event_data = df.iloc[:,0]
snr = df.iloc[:,1]
mag = df.iloc[:,2]
ray_param = df.iloc[:,3]
incidence = df.iloc[:,4]
distance = df.iloc[:,5]
label = df.iloc[:,6]

# convert the label to numerical values
le = LabelEncoder()
le.fit(label)
label = le.transform(label)
print(le.classes_)

# create a new df with the numerical values
df_new = pd.DataFrame({'event_data': event_data, 'snr': snr, 'mag': mag, 'ray_param': ray_param, 'incidence': incidence, 'distance': distance, 'label': label})


# create a new df with the numerical values
df_new = pd.DataFrame({'event_data': event_data, 'snr': snr, 'mag': mag, 'ray_param': ray_param, 'incidence': incidence, 'distance': distance, 'label': label})

print(df_new.head())


# read the data with obspy and resample to target frequency by using decimation factor
def read_data(file):
    st = obspy.read(file)
    st.decimate(int(st[0].stats.sampling_rate/target_freq))
    data_input = st[0].data
    # clear the memory
    st.clear()
    return data_input

# read the data and create a new df with the data
data = []
for i in range(len(df_new)):

    file = df_new.iloc[i,0]

    # if read_data returns an error, then skip the file and drop the row
    try:
        data_input = read_data(file)
        print('reading file: ', file)
    except:
        print('error reading file: ', file)
        df_new.drop(i, inplace=True)
        continue

    data.append(data_input)

# create a new df with the data
df_new['data'] = data
# append label to the data
df_new['label'] = label

# drop the rows with NaN values
df_new.dropna(inplace=True)

# reset the index
df_new.reset_index(drop=True, inplace=True)


label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(df_new['label'])
print(encoded_labels)

# actual labels
print(label_encoder.classes_)







# # train test split
# from sklearn.model_selection import train_test_split
# X_train, X_test, y_train, y_test = train_test_split(df_new['data'], df_new['label'], test_size=0.2, random_state=42)

# # convert the data to numpy array
# X_train = np.array(X_train.tolist())
# X_test = np.array(X_test.tolist())

# # convert the labels to categorical
# y_train = to_categorical(y_train)
# y_test = to_categorical(y_test)

# # reshape the data
# X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
# X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# print(X_train.shape)
# print(X_test.shape)

# model = make_model(input_shape=(X_train.shape[1], 1))
# print(model.summary())

# model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
# print(model.summary())

# # define the callbacks
# early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, verbose=1, mode='auto')
# model_checkpoint = keras.callbacks.ModelCheckpoint('model.h5', monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
# reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, verbose=1, mode='auto', min_delta=0.0001, cooldown=0, min_lr=0)
# print('callbacks defined')

# # reshape the data to make it for fitting
# X_train = X_train.reshape(X_train.shape[0], X_train.shape[1])
# X_test = X_test.reshape(X_test.shape[0], X_test.shape[1])

# # fit the model
# history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stopping, model_checkpoint, reduce_lr])


# 

# model = make_model(input_shape=(X_train.shape[1], 1))

# model.summary()

# # compile the model
# model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# # save the model
# model_json = model.to_json()

# # lets train the model
# history = model.fit(X_train, y_train, batch_size=32, epochs=100, validation_data=(X_test, y_test))

# # save the model
# model_json = model.to_json()

# with open("model.json", "w") as json_file:
#     json_file.write(model_json)

# model.save_weights("model.h5")

# # plot the loss and accuracy
# plt.figure(figsize=(12, 10))
# plt.plot(history.history['loss'], label='train')
# plt.plot(history.history['val_loss'], label='test')
# plt.legend()
# plt.title('Loss')
# plt.xlabel('Epochs')
# plt.ylabel('Loss')
# plt.show()

# plt.figure(figsize=(12, 10))
# plt.plot(history.history['accuracy'], label='train')
# plt.plot(history.history['val_accuracy'], label='test')
# plt.legend()
# plt.title('Accuracy')
# plt.xlabel('Epochs')
# plt.ylabel('Accuracy')
# plt.show()

# # evaluate the model
# score = model.evaluate(X_test, y_test, verbose=0)
# print('Test loss:', score[0])
# print('Test accuracy:', score[1])

# # predict the model
# y_pred = model.predict(X_test)

# # convert the predictions to categorical
# y_pred = np.argmax(y_pred, axis=1)

# # convert the test labels to categorical
# y_test = np.argmax(y_test, axis=1)

# # plot the confusion matrix
# cm = confusion_matrix(y_test, y_pred)

# plt.figure(figsize=(12, 10))
# sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=le.classes_, yticklabels=le.classes_)
# plt.title('Confusion Matrix')
# plt.xlabel('Predicted')
# plt.ylabel('True')
# plt.show()









