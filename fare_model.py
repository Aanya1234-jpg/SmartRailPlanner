import pickle
import os
import numpy as np
import pandas as pd

def load_model(path='model/fare_model.pkl'):
    with open(path, 'rb') as f:
        model = pickle.load(f)
    return model

def predict_fare(model, distance, train_type=1, class_type=1):
    X = np.array([[distance, train_type, class_type]])
    fare = model.predict(X)[0]
    return float(round(fare,2))
