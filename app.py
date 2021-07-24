from flask import Flask, render_template, url_for, request, redirect, jsonify, session
import json
import sys
import os
import time
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from main import get_top_tracks, recommendation, get_mood, save_top_tracks, save_recs, search_track

app = Flask(__name__)

app.secret_key = 'SOMETHING-RANDOM'
cid = os.getenv('cid')
secret = os.getenv('secret')
cid = '91c9906120ee44bdb039a305efe5bbd1'
secret = 'b1d12fe0c2264a0c9ce7ca3af96818e5'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=cid,
            client_secret=secret,
            redirect_uri=url_for('authorize', _external=True),
            scope='user-top-read playlist-modify-public')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form['login'] == 'login':
            sp_oauth = create_spotify_oauth()
            auth_url = sp_oauth.get_authorize_url()
            return redirect(auth_url)
    else:
        return render_template("home.html")
    

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()

    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info

    if os.path.exists(".cache"):
        print('nice!')
        os.remove(".cache")

    return redirect('/top-tracks/short-term')
    

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


@app.route('/top-tracks/short-term', methods=['GET', 'POST'])
def show_short_top_tracks():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    short_top_tracks = get_top_tracks("short_term", sp)
    return render_template('top1.html', sp=sp, top_tracks=short_top_tracks)


@app.route('/top-tracks/medium-term', methods=['GET', 'POST'])
def show_medium_top_tracks():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    medium_top_tracks = get_top_tracks("medium_term", sp)
    return render_template('top2.html', sp=sp, top_tracks=medium_top_tracks)


@app.route('/top-tracks/long-term', methods=['GET', 'POST'])
def show_long_top_tracks():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    long_top_tracks = get_top_tracks("long_term", sp)
    return render_template('top3.html', sp=sp, top_tracks=long_top_tracks)


@app.route('/recs/', methods=['GET', 'POST'])
def recs():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        track = request.form['recs']
        mood = get_mood(track, sp)
        mood_string = json.dumps(mood)
        recs = recommendation(track, sp)
        return render_template('recs.html', sp=sp, recs=recs, track=track, mood=mood, data=mood_string)


@app.route('/save-top-tracks/', methods=['GET','POST'])
def save():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    short_top_tracks = get_top_tracks("short_term", sp)
    medium_top_tracks = get_top_tracks("medium_term", sp)
    long_top_tracks = get_top_tracks("long_term", sp)
    if request.method == 'POST':
        if request.form['save'] == 'save_short_top_tracks':
            save_top_tracks(short_top_tracks, "for the Last Month", sp)
        elif request.form['save'] == 'save_medium_top_tracks':
            save_top_tracks(medium_top_tracks, "for the Last Six Months",sp)
        elif request.form['save'] == 'save_long_top_tracks':
            save_top_tracks(long_top_tracks, "of All Time", sp)
    return ('', 204)


@app.route('/save-recs/', methods=['GET', 'POST'])
def save_recommendations():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        recs = []
        for i in range(20):
            recs.append(request.form['save'][(i*22):((i+1)*22)])
        track = request.form['save'][440:]
        save_recs(recs, track, sp)
    return ('', 204)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    token_info = get_token()
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    if request.method == 'POST':
        query = request.form['search']
        results = search_track(query, sp)
    return render_template('search.html', sp=sp, results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
