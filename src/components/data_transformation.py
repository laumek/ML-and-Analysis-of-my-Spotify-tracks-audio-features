import pandas as pd
import numpy as np
import os, sys
import seaborn as sns
import matplotlib
from math import pi
from src.utils import save_object, load_object, get_years
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin

class DropMissingValuesTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self  # No fitting required, this transformer does not need to learn anything

    def transform(self, X, y=None):
        missing_values_found = X.isnull().sum().any()
        
        if missing_values_found:
            X = X.dropna(axis=0)
            X = X.reset_index(drop=True)

            print(f'Missing values were found and rows with missing values were dropped.')
            print(f'Updated data shape: {X.shape}')
        else:
            print('No missing values found.')
            print(f'Data shape: {X.shape}')

        return X

class DataTransformationConfig:
    preprocessor_ob_file_path= os.path.join('artifacts', 'preprocessor.pkl')


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):

        '''
        This function is responsible for data transformation
        '''

        try:
            pipeline = Pipeline(
                steps = [
                    ('drop_missing', DropMissingValuesTransformer())
                    ('scaler', MinMaxScaler())
                ]  
            )    

            preprocessor = pipeline
            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)


    def initiate_data_transformation(self, data_path):
        try:
            data_df = pd.read_csv(data_path)
            data_df = data_df.sort_values(by='artist', )

            logging.info('Read train data completed')

            get_years(data_df)
            
            features = ['acousticness','danceability', 'energy', 'instrumentalness', 'liveness', 'loudness',
            'speechiness', 'tempo', 'valence', 'time_signature', 'key', 'mode']

            columns = ['album', 'length', 'release_year', 'popularity', 'acousticness','danceability', 'energy',
            'instrumentalness', 'liveness', 'loudness','speechiness', 'tempo', 'valence', 'time_signature',
            'key', 'mode','uri']


            logging.info(f'Columns: {columns}') 
            logging.info(f'Features: {features}') 

            X = data_df.copy()

            #Create index with song name + artist, create X based off only features
            X.loc[:, 'song'] = X['name'] + ' - ' + X['artist']
            X = X.drop(columns=['name', 'artist'])
            X = X.set_index('song')
            X_cluster = X[features]

            logging.info('Data ready to be preprocessed.')

            logging.info('Obtaining preprocessing object')

            preprocessing_obj = self.get_data_transformer_object()

            input_feature_data_df = X_cluster

            logging.info('Applying preprocessing object on training dataframe')

            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_data_df)

            save_object(

                file_path = self.data_transformation_config.preprocessor_ob_file_path,
                obj = preprocessing_obj
            )

            logging.info('Saved preprocessing object.')

            return (
                input_feature_train_arr,
                self.data_transformation_config.preprocessor_ob_file_path
            )

        except Exception as e:
            raise CustomException(e, sys)