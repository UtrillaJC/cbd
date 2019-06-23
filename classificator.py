
from tensorflow import keras
from source_data import SourceData
import pickle

# Loading a neural network already trained and using it to evaluate and derive what is its ontological classification.
model = keras.models.load_model("model.h5")
print("Loaded model from disk")
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['acc'])

# Loading the word index
word_index = []
with open('word_index.pkl', 'rb') as f:
    word_index = pickle.load(f)

# The text to classify:
text = """
    Utrilla was born on Seville the year 1990. He is a student at the Universidad de Sevilla.
"""
text2 = """
"""
vectorized_text = SourceData.vectorize_text(word_index, text2)
data_to_evaluate = keras.preprocessing.sequence.pad_sequences([vectorized_text,],
                                                        value=word_index["<PAD>"],
                                                        padding='post',
                                                        maxlen=256)

classification = model.predict_classes(data_to_evaluate)
values_mapping = {0: "work", 1: "person", 2: "animal"}
print("The text:"+'"'+text2+'"'+", is about:")
print(values_mapping[classification[0]])
