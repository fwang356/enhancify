from flask import Flask, render_template, url_for, request, redirect
import sys
import os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from client import cid, secret
from main import get_top_tracks, recommendation, get_mood, save_top_tracks, save_recs

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


if token:
    sp = spotipy.Spotify(auth=token)
    short_top_tracks = get_top_tracks("short_term")
    medium_top_tracks = get_top_tracks("medium_term")
    long_top_tracks = get_top_tracks("long_term")
else:
    print("Can't get token for " + username)


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("home.html")

@app.route('/top-tracks/short-term', methods=['GET', 'POST'])
def show_short_top_tracks():
    """
    if request.method == 'POST':
        if request.form['save'] == 'save_top_tracks':
            save_top_tracks(top_tracks)
    """
    return render_template('top1.html', sp=sp, top_tracks=short_top_tracks)


@app.route('/top-tracks/medium-term', methods=['GET', 'POST'])
def show_medium_top_tracks():
    return render_template('top2.html', sp=sp, top_tracks=medium_top_tracks)

@app.route('/top-tracks/long-term', methods=['GET', 'POST'])
def show_long_top_tracks():
    return render_template('top3.html', sp=sp, top_tracks=long_top_tracks)


@app.route('/recs/', methods=['GET', 'POST'])
def recs():
    if request.method == 'POST':
        track = request.form['recs']
        mood = get_mood(track)
        recs = recommendation(track)
        return render_template('recs.html', sp=sp, recs=recs, track=track, mood=mood)
"""
@app.route('/saved-recs/', methods=['GET', 'POST'])
def saved_recs():
    if request.method == 'POST':
        track = request.form['save']
        mood = get_mood(track)
"""   

@app.route('/save-top-tracks/', methods=['GET','POST'])
def save():
    if request.method == 'POST':
        if request.form['save'] == 'save_short_top_tracks':
            save_top_tracks(short_top_tracks, "for the Last Month.")
        elif request.form['save'] == 'save_medium_top_tracks':
            save_top_tracks(medium_top_tracks, "for the Last Six Months.")
        elif request.form['save'] == 'save_long_top_tracks':
            save_top_tracks(long_top_tracks, "of All Time.")
    return ('', 204)

@app.route('/save-recs/', methods=['GET', 'POST'])
def save_recommendations():
    if request.method == 'POST':
        recs = []
        for i in range(20):
            recs.append(request.form['save'][(i*22):((i+1)*22)])
        track = request.form['save'][440:]
        save_recs(recs, track)
    return ('', 204)


if __name__ == "__main__":
    app.run(debug=True)