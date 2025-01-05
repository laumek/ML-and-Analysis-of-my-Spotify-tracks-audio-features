import os, sys
import numpy as np
import pandas as pd
import dill
import time
from src.exception import CustomException
from spotipy.exceptions import SpotifyException

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path, exist_ok= True)

        with open(file_path, 'wb') as file_obj:
            dill.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    

def load_object(file_path):
    try:
        with open(file_path, 'rb') as file_obj:
            return dill.load(file_obj)
        
    except Exception as e:
        raise CustomException(e, sys)
    
def exponential_backoff_retry(func, *args, max_retries=3, base_delay=1, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 429:
                print(f"Rate limited. Retrying in {base_delay * 2 ** attempt} seconds.")
                time.sleep(base_delay * 2 ** attempt)
            else:
                raise e
    print("Max retries exceeded. Unable to fetch track features.")
    return None
    


def get_track_ids(sp):
    # Get all track IDs from the user's saved tracks
    ids = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results['items']:
            track = item['track']
            ids.append(track['id'])

        if results['next']:
            results = sp.next(results)
        else:
            results = None

    # Save track IDs to a pickle file
    with open('spotify_tracks_ids.pkl', 'wb') as f:
        dill.dump(ids, f)
    return ids



def get_user_saved_track_features(sp, ids, start_track_id=0, batch_size=100):
    all_tracks = []
    # total_tracks = len(ids)
    

    end_track_id = start_track_id+200
    tracks_features = []
    tracks_meta = []
    
    # Iterate through each batch of track IDs
    batches = [ids[i:i+batch_size] for i in range(start_track_id, end_track_id, batch_size)]
    for batch in batches:
        for track_id in batch:
            meta = exponential_backoff_retry(sp.track, track_id)
            if meta is None:
                continue
            name = meta['name']
            album = meta['album']['name']
            artist = meta['album']['artists'][0]['name']
            release_date = meta['album']['release_date']
            length = meta['duration_ms']
            popularity = meta['popularity']
            tracks_meta.append([name, album, artist, release_date, length, popularity])
            print(f"Processed meta for track ID {track_id}")
        
        batch_features = exponential_backoff_retry(sp.audio_features, batch)

        if batch_features:
            for features in batch_features:
                print(features)
                if features is not None and any(value is not None for value in features.values()):
                    acousticness = features['acousticness']
                    danceability = features['danceability']
                    energy = features['energy']
                    instrumentalness = features['instrumentalness']
                    liveness = features['liveness']
                    loudness = features['loudness']
                    speechiness = features['speechiness']
                    tempo = features['tempo']
                    valence = features['valence']
                    time_signature = features['time_signature']
                    key = features['key']
                    mode = features['mode']
                    uri = features['uri']

                    tracks_features.append([acousticness, danceability, energy, instrumentalness,
                                    liveness, loudness, speechiness, tempo, valence,
                                    time_signature, key, mode, uri])
                    print(f"Processed track ID {track_id}, {features['uri']}")
                else:
                    print(f"Skipping track ID {track_id} because at least one feature value is None")

                time.sleep(1)  # Sleep for 1 second per song
        elif batch_features is None:
            print(f"Skipping batch due to error")

        time.sleep(1) # Sleep for 1 second per batch to avoid rate limiting
    
    batch_results = [meta_data + track_feature for meta_data, track_feature in zip(tracks_meta, tracks_features)]
    all_tracks.extend(batch_results)

    start_track_id = end_track_id  # Update start_track_id to the next batch

    return all_tracks

# def get_user_saved_track_features(sp, ids, start_track_id=0, batch_size=100):
#     all_tracks = []
#     total_tracks = len(ids)
    
#     while start_track_id < total_tracks:
#         end_track_id = min(start_track_id + 1000, total_tracks)
#         tracks_features = []
#         tracks_meta = []
        
#         # Iterate through each batch of track IDs
#         batches = [ids[i:i+batch_size] for i in range(start_track_id, end_track_id, batch_size)]
#         for batch in batches:
#             for track_id in batch:
#                 meta = exponential_backoff_retry(sp.track, track_id)
#                 if meta is None:
#                     continue
#                 name = meta['name']
#                 album = meta['album']['name']
#                 artist = meta['album']['artists'][0]['name']
#                 release_date = meta['album']['release_date']
#                 length = meta['duration_ms']
#                 popularity = meta['popularity']
#                 tracks_meta.append([name, album, artist, release_date, length, popularity])
#                 print(f"Processed meta for track ID {track_id}")
            
#             batch_features = exponential_backoff_retry(sp.audio_features, batch)

#             if batch_features:
#                 for features in batch_features:
#                     print(features)
#                     if features is not None and any(value is not None for value in features.values()):
#                         acousticness = features['acousticness']
#                         danceability = features['danceability']
#                         energy = features['energy']
#                         instrumentalness = features['instrumentalness']
#                         liveness = features['liveness']
#                         loudness = features['loudness']
#                         speechiness = features['speechiness']
#                         tempo = features['tempo']
#                         valence = features['valence']
#                         time_signature = features['time_signature']
#                         key = features['key']
#                         mode = features['mode']
#                         uri = features['uri']

#                         tracks_features.append([acousticness, danceability, energy, instrumentalness,
#                                        liveness, loudness, speechiness, tempo, valence,
#                                        time_signature, key, mode, uri])
#                         print(f"Processed track ID {track_id}, {features['uri']}")
#                     else:
#                         print(f"Skipping track ID {track_id} because at least one feature value is None")

#                     time.sleep(1)  # Sleep for 1 second per song
#             elif batch_features is None:
#                 print(f"Skipping batch due to error")

#             time.sleep(1) # Sleep for 1 second per batch to avoid rate limiting
        
#         batch_results = [meta_data + track_feature for meta_data, track_feature in zip(tracks_meta, tracks_features)]
#         all_tracks.extend(batch_results)

#         start_track_id = end_track_id  # Update start_track_id to the next batch

#     return all_tracks


def get_years(df):
    years = []
    for date in df['release_date'].values:
        if '-' in date:
            years.append(date.split('-')[0])
        else:
            years.append(date)
    df['release_year'] = years

    df.drop(columns= 'release_date', inplace=True)
    column_to_move = df.pop('release_year')
    df.insert(loc=4, column='release_year', value=column_to_move)
    df['release_year'] = pd.to_numeric(df['release_year'])
    return df


# # ALGORITHM: df.isnull().sum() , if any null value in any row, find a replacing strategy
# missing_values_found = False

# for idx,row in X.iterrows():
#     if row.isnull().any():
#         X.drop(index=idx, inplace = True)
#         missing_values_found = True

# if missing_values_found:
#     X= X.reset_index(drop = True)
# print('No missing values found.')

# print(f'Our data has a shape {X.shape}.')


def evaluate_models():
    pass
