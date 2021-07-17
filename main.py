import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from client import cid, secret

os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:5000/callback'

auth_manager = SpotifyClientCredentials(client_id=cid,
                                        client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

username = ""
scope = 'user-top-read playlist-modify-public'
token = util.prompt_for_user_token(username, scope)

time_range = "short_term"


# Returns list of user's top ten track id's
def get_top_tracks():
    results = sp.current_user_top_tracks(limit=10, offset=0, time_range=time_range)
    tracks = []
    for song in range(10):
        tracks.append(results["items"][song]["id"])
    return tracks


# Returns list of moods for inputted tracks
def get_mood(tracks):
    track_analysis = sp.audio_features(tracks)
    moods = {}
    for i in range(len(tracks)):
        tracks_mood = {tracks[i]: {'danceability': track_analysis[i]['danceability'],
                                   'energy': track_analysis[i]['energy'], 'valence': track_analysis[i]['valence']}}
        moods.update(tracks_mood)
    return moods


# Returns average mood for user's top tracks
def average_mood():
    tracks = get_top_tracks()
    track_analysis = sp.audio_features(tracks)
    danceability = 0
    energy = 0
    valence = 0

    for track in track_analysis:
        danceability = danceability + track['danceability']
        energy = energy + track['energy']
        valence = valence + track['valence']

    danceability = round(danceability / 10, 5)
    energy = round(energy / 10, 5)
    valence = round(valence / 10, 5)

    average = {'danceability': danceability, 'energy': energy, 'valence': valence}
    return average


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
                                     min_popularity=max(popularity - 15, 1), max_popularity=min(popularity + 15, 99),)

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


def save_top_tracks(tracks):
    playlist = sp.user_playlist_create(sp.current_user()['id'], "Your Top Tracks")
    playlist_id = playlist['id']
    sp.playlist_add_items(playlist_id, tracks)

"""
def get_track_name(track):
    return sp.track(track)['name']


def get_artist_name(track):
    return sp.track(track)['artists'][0]['name']


def get_album_cover(track):
    return sp.track(track)['album']['images'][0]['url']
"""


def get_user_pfp():
    return sp.current_user()['images'][0]['url']


if token:
    sp = spotipy.Spotify(auth=token)
    top_tracks = get_top_tracks()
    tracks_analysis = get_mood(top_tracks)
    average_mood = average_mood()
    if len(sys.argv) > 2:
        track_id = sys.argv[2]
        mood = get_mood([track_id])

    print(get_user_pfp())
    #recs = recommendation('5XXJnC5TvcL2QsAZ3Nxgku')
    #rec_analysis = get_mood(recs)
    #save_top_tracks(top_tracks)
else:
    print("Can't get token for " + username)