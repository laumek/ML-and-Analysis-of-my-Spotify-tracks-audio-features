import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dill
import time
from src.exception import CustomException
from spotipy.exceptions import SpotifyException
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from kneed import KneeLocator

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

def get_user_saved_track_features(sp, ids, start_track_id=0, batch_size=10):
    all_tracks = []
    # total_tracks = len(ids)
    

    end_track_id = 200
    tracks_features = []
    tracks_meta = []
    batch_size =10
    
    # Iterate through each batch of track IDs
    batches = [ids[i:i+batch_size] for i in range(start_track_id, end_track_id, batch_size)]
    numbered_ids_dict = {i + 1: id for i, id in enumerate(ids)}


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
            track_number = next((num for num, track in numbered_ids_dict.items() if track == track_id), None)
            print(f"Processed meta {track_number} for track ID {track_id}")
        
        print(len(tracks_meta))
        
        batch_features = exponential_backoff_retry(sp.audio_features, batch)
        print('donio')

        if batch_features:
            print('done')
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

def get_user_saved_track_features(sp, ids, start_track_id=0, batch_size=100):
    all_tracks = []
    total_tracks = len(ids)
    
    while start_track_id < total_tracks:
        end_track_id = min(start_track_id + 1000, total_tracks)
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


def evaluate_models():
    pass

def find_elbow_point(X):

    sse = []
    k_values = range(1, 11)
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X)
        sse.append(kmeans.inertia_)

    knee_locator = KneeLocator(k_values, sse, curve="convex", direction="decreasing")
    elbow_point = knee_locator.knee

    return elbow_point

    print(f"The optimal number of clusters is: {elbow_point}")

def fit_model(X, elbow_point):

    kmeans = KMeans(n_clusters=elbow_point, random_state=42)  # You can change n_clusters based on the elbow method
    X['Cluster'] = kmeans.fit_predict(X)

    # Visualise clusters using PCA (reduces dimensions to 2D for visualization)
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(X)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=pca_features[:, 0], y=pca_features[:, 1], hue=X['Cluster'], palette='viridis')
    plt.title('Clusters Visualized in 2D using PCA')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend(title='Cluster')


