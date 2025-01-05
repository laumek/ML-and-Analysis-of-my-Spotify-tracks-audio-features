import pandas as pd
import os, sys
import spotipy
from src.exception import CustomException
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from src.components.data_transformation import DataTransformation, DataTransformationConfig, DropMissingValuesTransformer
from src.logger import logging
from src.utils import save_object, load_object, get_track_ids, exponential_backoff_retry, get_user_saved_track_features
from dataclasses import dataclass


class DataIngestionConfig:
    # train_data_path: str=os.path.join('artifacts', 'train.csv')
    # test_data_path: str=os.path.join('artifacts', 'test.csv')
    raw_data_path: str = os.path.join('artifacts', 'spotify_data.pkl')

class DataIngestion:
    def __init__(self):
        self.dataingestion_config = DataIngestionConfig()
        logging.info('Logging credentials')
        self.sp = self.authenticate_spotify()
    
    def authenticate_spotify(self):
        # Assuming you've stored client info in a CSV file
        spotify_client_info = pd.read_csv('spotify_client_info.csv')
        client_id = spotify_client_info.iloc[0, 0]
        client_secret = spotify_client_info.iloc[0, 1]

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri='http://localhost:8888/callback',
            scope="user-library-read"
        ))
        return sp
    
    def initiate_data_ingestion(self):
        logging.info('Entering the data ingestion method or component')

        try:
            # Get track IDs
            ids = get_track_ids(self.sp)
            logging.info(f"Fetched {len(ids)} track IDs")

            # Fetch track features from Spotify
            all_tracks_features = get_user_saved_track_features(self.sp, ids, start_track_id=0, batch_size=100)

            while None in all_tracks_features:
                all_tracks_features.remove(None)
            
            df = pd.DataFrame(all_tracks_features, columns=['name', 'album', 'artist', 'release_date',
                                       'length', 'popularity', 'acousticness', 'danceability',
                                       'energy', 'instrumentalness', 'liveness', 'loudness',
                                       'speechiness', 'tempo', 'valence', 'time_signature',
                                       'key', 'mode', 'uri'
                                       ])
            
            save_object(self.dataingestion_config.raw_data_path,df)

            logging.info('Data ingestion completed')

            return self.dataingestion_config.raw_data_path

        except Exception as e:
            raise CustomException(e,sys)
        


if __name__ == '__main__':
    obj= DataIngestion()
    raw = obj.initiate_data_ingestion()

    data_transformation = DataTransformation()
    train_arr, _ = data_transformation.initiate_data_transformation(raw)

