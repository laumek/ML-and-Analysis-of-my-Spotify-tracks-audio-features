import os, sys

from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, load_object, evaluate_models, find_elbow_point, fit_model
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA

#@dataclass

class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig

    def initiate_model_trainer(self, train_array):

        try:
            elbow_point = find_elbow_point(train_array)
            fit_model(train_array, elbow_point)

        except Exception as e:
            raise CustomException(e,sys)
