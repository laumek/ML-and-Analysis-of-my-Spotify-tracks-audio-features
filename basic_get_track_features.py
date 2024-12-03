

# # Iterate through each track ID
# for track_id in ids:
#     featuress = get_track_features(sp, track_id)
#     tracks.append(featuress)

# # Create DataFrame from the list of track features
# df = pd.DataFrame(tracks, columns=['name', 'album', 'artist', 'release_date',
#                                    'length', 'popularity', 'acousticness', 'danceability',
#                                    'energy', 'instrumentalness', 'liveness', 'loudness',
#                                    'speechiness', 'tempo', 'valence', 'time_signature',
#                                    'key', 'mode', 'uri'])

# return df


# def get_user_saved_track_features(sp, ids, start_track_id=None):
#     tracks = []

#     # Iterate through each track ID
#     for i,track_id in enumerate(ids):
#         if i < start_track_id:
#             continue
#         else:
#             featuress = get_track_features(sp, track_id)
#             tracks.append(featuress)
            
#     # Create DataFrame from the list of track features
#     df = pd.DataFrame(tracks, columns=['name', 'album', 'artist', 'release_date',
#                                        'length', 'popularity', 'acousticness', 'danceability',
#                                        'energy', 'instrumentalness', 'liveness', 'loudness',
#                                        'speechiness', 'tempo', 'valence', 'time_signature',
#                                        'key', 'mode', 'uri'])

#     return df

import time

def get_user_saved_track_features(sp, ids, start_track_id=None, batch_size=100):
    tracks = []

    # Iterate through each batch of track IDs
    for i in range(start_track_id, start_track_id+1000, batch_size):
        batch = ids[i:i+batch_size]
        batch_features = get_batch_track_features(sp, batch)
        tracks.extend(batch_features)

        time.sleep(30)  # Sleep for 30 seconds to avoid rate limiting
            
    # Create DataFrame from the list of track features
    df = pd.DataFrame(tracks, columns=['name', 'album', 'artist', 'release_date',
                                       'length', 'popularity', 'acousticness', 'danceability',
                                       'energy', 'instrumentalness', 'liveness', 'loudness',
                                       'speechiness', 'tempo', 'valence', 'time_signature',
                                       'key', 'mode', 'uri'])

    return df


def get_batch_track_features(sp, batch):
    batch_features = []

    # Iterate through each track ID in the batch
    for track_id in batch:
        features = get_track_features(sp, track_id)
        if features is not None:
            batch_features.append(features)
        time.sleep(1)  # Sleep for 1 second to avoid rate limiting

    return batch_features


def get_track_features(sp, track_id):
    meta = sp.track(track_id)
    features = sp.audio_features(track_id)

    if features is None or not features:
        print(f"No features found for track ID {track_id}")
        return None
    
    
    # Extract relevant track metadata
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    release_date = meta['album']['release_date']
    length = meta['duration_ms']
    popularity = meta['popularity']

    # Extract audio features if available
    if features[0] is None:
        print(f"Skipping track ID {id} due to missing audio features")
        return None

    if any(value is None for value in features[0].values()):
        print(f"Skipping track ID {id} because at least one feature value is None")
        return None
    
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    tempo = features[0]['tempo']
    valence = features[0]['valence']
    time_signature = features[0]['time_signature']
    key = features[0]['key']
    mode = features[0]['mode']
    uri = features[0]['uri']

    return [name, album, artist, release_date,
            length, popularity, acousticness,
            danceability, energy, instrumentalness,
            liveness, loudness, speechiness, tempo,
            valence, time_signature, key, mode, uri]

  
