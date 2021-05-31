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
from enum import Enum

class SnapshotSaveResult(Enum):
	SUCCESS = 0
	DUPLICATE = 1

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
	auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-private playlist-read-private user-modify-playback-state playlist-modify-private', cache_handler=cache_handler, show_dialog=True)

	if request.args.get('code'):
		auth_manager.get_access_token(request.args.get("code"), as_dict=False)
		return redirect('/')

	if not auth_manager.validate_token(cache_handler.get_cached_token()):
		auth_url = auth_manager.get_authorize_url()
		return render_template('sign-in.html', auth_url=auth_url)

	spotify = spotipy.Spotify(auth_manager=auth_manager)
	display_name = spotify.me()['display_name']
	return render_template('index.html', display_name=display_name)          

@app.route('/sign-out')
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
	playlist = spotify.playlist(playlist_id, fields='snapshot_id,tracks(items.track.id, next)')
	snapshot_id = playlist['snapshot_id']
	user_id = spotify.me()['id']

	if psql.get_snapshot(snapshot_id, user_id) is not None:
		return str(SnapshotSaveResult.DUPLICATE.value)

	playlist_tracks = playlist['tracks']
	track_ids = []
	while True:
		track_ids += [item['track']['id'] for item in playlist_tracks['items'] if item['track']['id']]
		if not playlist_tracks['next']:
			break
		playlist_tracks = spotify.next(playlist_tracks)

	dt = datetime.today()
	name = dt.replace(microsecond=0).isoformat()

	snapshot = (snapshot_id, dt, name, playlist_id, user_id, track_ids)
	psql.insert_snapshot(snapshot)

	return str(SnapshotSaveResult.SUCCESS.value)

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

@app.route('/api/tracks', methods=['GET'])
def get_tracks():
	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
	spotify = spotipy.Spotify(auth_manager=auth_manager)

	tracks = []

	if snapshot_id := request.args.get('snapshot_id'):
		user_id = spotify.me()['id']
		track_ids = psql.get_snapshot_tracks(snapshot_id, user_id)

		if track_ids is None:
			return '[]'

		for i in range(0, len(track_ids), 50):
			result = spotify.tracks(track_ids[i:i+50])
			tracks += [{ 'id': track['id'], 'title': track['name'], 'artist': track['artists'][0]['name'] } for track in result['tracks']]

	elif playlist_id := request.args.get('playlist_id'):
		result = spotify.playlist_items(playlist_id, fields='items.track(artists.name, id, name),next')
		while True:
			tracks += [{ 'id': item['track']['id'], 'title': item['track']['name'], 'artist': item['track']['artists'][0]['name'] } for item in result['items']]
			if not result['next']:
				break
			result = spotify.next(result)

	return json.dumps(tracks)

@app.route('/api/play-tracks', methods=['POST'])
def play_tracks():
	cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
	spotify = spotipy.Spotify(auth_manager=auth_manager)

	track_ids_str = request.form['track_ids']
	track_ids = json.loads(track_ids_str)
	track_uris = [f'spotify:track:{id}' for id in track_ids]
	#spotify.start_playback(uris=track_uris)

	return '0'

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)
