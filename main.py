import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
#from client import cid, secret

"""
os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:5000/callback'

auth_manager = SpotifyClientCredentials(client_id=cid,
                                        client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

username = ""
scope = 'user-top-read playlist-modify-public'
token = util.prompt_for_user_token(username, scope)
"""
# Returns list of user's top ten track id's
def get_top_tracks(time_range):
    results = sp.current_user_top_tracks(limit=10, offset=0, time_range=time_range)
    tracks = []
    for song in range(10):
        tracks.append(results["items"][song]["id"])
    return tracks


# Returns list of moods for inputted track
def get_mood(track):
    track_analysis = sp.audio_features(track)
    tracks_mood = [
        {
            'name': 'Danceability',
            'score': round(100 * track_analysis[0]['danceability'])
        },

        {
            'name': 'Valence',
            'score': round(100 * track_analysis[0]['valence'])
        },

        {
            'name': 'Energy',
            'score': round(100 * track_analysis[0]['energy'])
        }
    ]
    return tracks_mood


# Returns list of recommended tracks based on inputted track
def recommendation(track):
    track_analysis = sp.audio_features(track)

    artist_id = sp.track(track)['artists'][0]['id']
    artists = [artist_id]
    tracks = [track]
    genre = sp.artist(artist_id)['genres']
    if len(genre) > 3:
        genre = genre[0:3]
    elif len(genre) < 3:
        artists.append(sp.artist_related_artists(artist_id)['artists'][0]['id'])

    danceability = track_analysis[0]['danceability']
    energy = track_analysis[0]['energy']
    valence = track_analysis[0]['valence']
    popularity = (sp.track(track)['popularity'] + sp.artist(artist_id)['popularity']) / 2
    popularity = round(popularity)

    recommended = sp.recommendations(seed_artists=artists, seed_genres=genre, seed_tracks=tracks, limit=20,
                                     min_danceability=max(danceability - .15, .01),
                                     max_danceability=min(danceability + .15, .99),
                                     min_energy=max(energy - .15, .01), max_energy=min(energy + .15, .99),
                                     min_valence=max(valence - .15, .01), max_valence=min(valence + .15, .99),
                                     min_popularity=max(popularity - 15, 1), max_popularity=min(popularity + 15, 99))

    rec_tracks = []
    for i in range(len(recommended['tracks'])):
        rec_tracks.append(recommended['tracks'][i]['id'])
    rec_tracks = list(set(rec_tracks))

    if track in rec_tracks:
        rec_tracks.remove(track)

    count = 0.05
    while len(rec_tracks) != 20:
        recommended = sp.recommendations(seed_artists=artists, seed_genres=genre, seed_tracks=tracks,
                                         limit=20 - len(rec_tracks),
                                         min_danceability=max(danceability - .15 - count, 0.01),
                                         max_danceability=min(danceability + .15 + count, 0.99),
                                         min_energy=max(energy - .15 - count, 0.01), max_energy=min(energy + .15 - count, 0.99),
                                         min_valence=max(valence - .15 - count, 0.01),
                                         max_valence=min(valence + .15 + count, 0.99),
                                         min_popularity=max(popularity - 15 - int(count * 100), 1),
                                         max_popularity=min(popularity + 15 + int(count * 100), 99))
        for i in range(len(recommended['tracks'])):
            rec_tracks.append(recommended['tracks'][i]['id'])
        rec_tracks = list(set(rec_tracks))
        if track in rec_tracks:
            rec_tracks.remove(track)
        count = count + 0.05
    return rec_tracks


def save_recs(rec, track):
    playlist = sp.user_playlist_create(sp.current_user()['id'], sp.track(track)['name'] + ' Recs')
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, rec)


def save_top_tracks(tracks, time_range):
    playlist = sp.user_playlist_create(sp.current_user()['id'], "Your Top Tracks " + time_range)
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, tracks)


def search_track(query):
    results = sp.search(query, limit=20, type="track")['tracks']['items']
    search_results = []
   
    for result in results:
        id = result['id']
        search_results.append(id)
    return search_results

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for " + username)