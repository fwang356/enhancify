import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

cid = '91c9906120ee44bdb039a305efe5bbd1'
secret = 'b1d12fe0c2264a0c9ce7ca3af96818e5'

os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback'

auth_manager = SpotifyClientCredentials(client_id=cid,
                                        client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

username = ""
scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope)

time_range = sys.argv[1]


def get_top_tracks(spotify, limit):
    results = spotify.current_user_top_tracks(limit=limit, offset=0, time_range=time_range)
    tracks = []
    for song in range(limit):
        tracks.append(results["items"][song]["id"])
    return tracks


def average_mood(spotify):
    tracks = get_top_tracks(spotify, 50)
    tracks_mood = sp.audio_features(tracks)
    danceability = 0
    energy = 0
    valence = 0
    tempo = 0

    for track in tracks_mood:
        danceability = danceability + track['danceability']
        energy = energy + track['energy']
        valence = valence + track['valence']
        tempo = tempo + track['tempo']

    danceability = round(danceability / 50, 5)
    energy = round(energy / 50, 5)
    valence = round(valence / 50, 5)
    tempo = round(tempo / 50, 5)

    average = {'danceability': danceability, 'energy': energy, 'valence': valence, 'tempo': tempo}
    return average


if token:
    sp = spotipy.Spotify(auth=token)
    top_tracks = get_top_tracks(sp, 10)  # List of user's top ten tracks
    tracks_moods = sp.audio_features(top_tracks)  # List of moods for user's top tracks
    average_mood = average_mood(sp)  # User's average mood from top fifty tracks
    if len(sys.argv) > 2:
        track_id = sys.argv[2]
        mood = sp.audio_features(track_id)  # Mood for inputted track
else:
    print("Can't get token for " + username)

