from __future__ import absolute_import, division, print_function, unicode_literals
from source_data import SourceData
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import pickle

print(tf.__version__)
# Preparing data
source = SourceData()
examples =source.data_examples()
n_examples = len(examples[0])
print(n_examples)
train_data = examples[0][:n_examples//2]
train_labels = examples[1][:n_examples//2]
test_data = examples[0][n_examples//2:]
test_labels = examples[1][n_examples//2:]

# A dictionary mapping words to an integer index
word_index = source.get_word_index()

# The first indices are reserved
word_index = {k: (v + 3) for k, v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2  # unknown
word_index["<UNUSED>"] = 3

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])


# This vectorize every word.
def create_embedding_matrix(filepath, word_index, embedding_dim):
    vocab_size = len(word_index) + 1
    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    with open(filepath) as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word]
                embedding_matrix[idx] = np.array(
                    vector, dtype=np.float32)[:embedding_dim]

    return embedding_matrix


# We need every text has the same lenght, that is "maxlen"
train_data = keras.preprocessing.sequence.pad_sequences(train_data,
                                                        value=word_index["<PAD>"],
                                                        padding='post',
                                                        maxlen=256)

test_data = keras.preprocessing.sequence.pad_sequences(test_data,
                                                       value=word_index["<PAD>"],
                                                       padding='post',
                                                       maxlen=256)

vocab_size = len(word_index)+1

# Here, we are declaring neural network structure.
model = keras.Sequential(
    [
        keras.layers.Embedding(input_dim=vocab_size, output_dim=50, weights=[create_embedding_matrix('glove.6B.50d.txt', word_index, 50)], input_length=256, trainable=True),
        keras.layers.Conv1D(50, 6, activation='relu'),
        keras.layers.GlobalAveragePooling1D(),
        keras.layers.Dense(6),
        keras.layers.Activation('relu'),
        #keras.layers.Dense(1), keras.layers.Activation('sigmoid')
        keras.layers.Dense(3, activation=tf.nn.softmax)

    ]
)
"""

model.add(keras.layers.Embedding(vocab_size, 16))
model.add(keras.layers.Flatten(input_shape=(256, 1)))
#model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

"""
model.summary()

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['acc'])


x_val = train_data[:len(train_data)//2]
partial_x_train = train_data[len(train_data)//2:]

y_val = train_labels[:len(train_labels)//2]

partial_y_train = train_labels[len(train_labels)//2:]
# Training our model with the data:
history = model.fit(partial_x_train,
                    partial_y_train,
                    epochs=125,
                    batch_size=200,
                    validation_data=(x_val, y_val),
                    verbose=1)

results = model.evaluate(test_data, test_labels)

print(results)


history_dict = history.history


# Preparing data for graphic representation
acc = history_dict['acc']
val_acc = history_dict['val_acc']
loss = history_dict['loss']
val_loss = history_dict['val_loss']

epochs = range(1, len(acc) + 1)

# Printing loss graphic
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.show()

# Printing accuracity graphic
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

# Saving the model
model.save("model.h5")
# Saving the word index
with open('word_index.pkl', 'wb') as f:
    pickle.dump(word_index, f, pickle.HIGHEST_PROTOCOL)
print("Saved model to disk")
