import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from client import cid, secret

os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback'

auth_manager = SpotifyClientCredentials(client_id=cid,
                                        client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

username = ""
scope = 'user-top-read playlist-modify-public'
token = util.prompt_for_user_token(username, scope)

time_range = sys.argv[1]


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

    danceability = track_analysis[0]['danceability']
    energy = track_analysis[0]['energy']
    valence = track_analysis[0]['valence']

    artist_id = sp.track(track)['artists'][0]['id']
    artists = [artist_id]
    tracks = [track]
    genre = sp.artist(artist_id)['genres']

    recommended = sp.recommendations(seed_artists=artists, seed_genres=genre, seed_tracks=tracks, limit=20,
                                     target_danceability=danceability, target_energy=energy,
                                     target_valence=valence)
    rec_tracks = []

    for i in range(20):
        rec_tracks.append(recommended['tracks'][i]['id'])

    while track in rec_tracks:
        rec_tracks.remove(track)
        recommended = sp.recommendations(seed_artists=artists, seed_genres=genre, seed_tracks=tracks, limit=1,
                                         target_danceability=danceability, target_energy=energy,
                                         target_valence=valence)
        rec_tracks.append(recommended['tracks'][0]['id'])

    return rec_tracks


def rec_playlist(recs):
    playlist = sp.user_playlist_create(sp.current_user()['id'], 'moodi recs')
    playlist_id = playlist['id']
    sp.user_playlist_add_tracks(sp.current_user(), playlist_id, recs)


if token:
    sp = spotipy.Spotify(auth=token)
    top_tracks = get_top_tracks()
    tracks_analysis = get_mood(top_tracks)
    average_mood = average_mood()
    if len(sys.argv) > 2:
        track_id = sys.argv[2]
        mood = get_mood([track_id])
    recommendations = recommendation(top_tracks[0])
    rec_analysis = get_mood(recommendations)
    rec_playlist(recommendations)

else:
    print("Can't get token for " + username)
