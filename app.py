from flask import Flask, render_template, url_for, request, redirect
import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from client import cid, secret
# from main import get_album_cover, get_artist_name, get_mood, get_track_name, get_top_tracks

app = Flask(__name__)


os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback'

auth_manager = SpotifyClientCredentials(client_id=cid,
                                        client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=auth_manager)

username = ""
scope = 'user-top-read playlist-modify-public'
token = util.prompt_for_user_token(username, scope)

time_range = "short_term"

"""
if token:
    sp = spotipy.Spotify(auth=token)
    top_tracks = get_top_tracks()
    tracks = get_names(top_tracks)
    artists = get_artist_names(top_tracks)
    album_covers = get_album_covers(top_tracks)
else:
    print("Can't get token for " + username)
"""

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("home.html")

@app.route('/top-tracks/')
def show_top_tracks():
    return render_template('top.html')

@app.route('/recs/')
def recs():
    return render_template('recs.html')

if __name__ == "__main__":
    app.run(debug=True)