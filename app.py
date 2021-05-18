import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import uuid
import threading
import difflib
import json
from datetime import datetime
import psql

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
	os.makedirs(caches_folder)

def session_cache_path():
	return caches_folder + session.get('uuid')

@app.route('/')
def index():
	if not session.get('uuid'):
		session['uuid'] = str(uuid.uuid4())

	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-private user-read-currently-playing playlist-read-private', cache_handler=cache_handler, show_dialog=True)

	if request.args.get('code'):
		auth_manager.get_access_token(request.args.get("code"), as_dict=False)
		return redirect('/')

	if not auth_manager.validate_token(cache_handler.get_cached_token()):
		auth_url = auth_manager.get_authorize_url()
		return render_template('sign-in.html', auth_url=auth_url)

	spotify = spotipy.Spotify(auth_manager=auth_manager)
	display_name = spotify.me()['display_name']
	return render_template('index.html', display_name=display_name)          

@app.route('/sign_out')
def sign_out():
	try:
		os.remove(session_cache_path())
		session.clear()
	except OSError as e:
		print("Error: %s - %s." % (e.filename, e.strerror))
	return redirect('/')

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
	spotify = spotipy.Spotify(auth_manager=auth_manager)
	playlists_response = spotify.current_user_playlists()
	playlists = []
	for playlist in playlists_response['items']:
		p = { 'id': playlist['id'], 'name': playlist['name'] }
		playlists.append(p)
	return json.dumps(playlists)

@app.route('/api/save-snapshot', methods=['POST'])
def save_snapshot():
	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
	spotify = spotipy.Spotify(auth_manager=auth_manager)

	playlist_id = request.form['playlist_id']
	playlist = spotify.playlist(playlist_id, fields='snapshot_id,tracks.items.track.id')
	snapshot_id = playlist['snapshot_id']
	user_id = spotify.me()['id']

	if psql.get_snapshot(snapshot_id, user_id) is not None:
		return "duplicate"

	track_ids = [item['track']['id'] for item in playlist['tracks']['items']]
	dt = datetime.today()
	name = dt.replace(microsecond=0).isoformat()

	snapshot = (snapshot_id, dt, name, playlist_id, user_id, track_ids)
	psql.insert_snapshot(snapshot)

	return "success"

@app.route('/api/snapshots', methods=['GET'])
def get_snapshots():
	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
	spotify = spotipy.Spotify(auth_manager=auth_manager)

	playlist_id = request.args.get('playlist_id')
	user_id = spotify.me()['id']
	snapshots_full = psql.get_snapshots(playlist_id, user_id)

	snapshots_partial = [{ 'id': snapshot[0], 'name': snapshot[2] } for snapshot in snapshots_full]
	return json.dumps(snapshots_partial)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
