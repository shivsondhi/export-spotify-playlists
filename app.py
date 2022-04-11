'''
Spotify playlist exporter. 

CONTROL FLOW:
/ > /login > /callback > /connected
'''

from flask import (
	Flask, 
	render_template,   
	request, 
	url_for, 
	flash, 
	redirect,
	make_response,
	session,
	abort, 
	send_file, 
)
from flask_cors import CORS
from spotify_exporter import build_playlist, get_user_playlists
import string 
import secrets
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()                    #for python-dotenv method
import os


CLI_ID 	= os.environ.get('CLI_ID') # CLIENT ID 
CLI_KEY = os.environ.get('CLI_KEY') # CLIENT SECRET 
REDIRECT_URI = "http://127.0.0.1:5000/callback"
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origin": "http://localhost:3000", "credentials": True }})
app.secret_key = 'selectARandomsecret_Key-forTheAPP'

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route("/")
def home():
	return render_template("home.html") 


@app.route("/export", methods={"POST"})
def export():
	# get form inputs
	form_data = request.form.to_dict(flat=False)
	uri = list(form_data.keys())

	# create tsv file
	filename = build_playlist(uri[0], token=session.get('tokens').get('access_token'))

	if filename == "error":
		return render_template("home.html", value="reauthorize")

	# prepare file export
	file_export = send_file(filename, as_attachment=True)
	# remove file from path as its no longer needed
	os.remove(f"./{filename}")
	# download file export
	return file_export



@app.route("/login")
def login():
	state = ''.join(
		secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
	)
	# scope = "playlist-read-private"
	payload = {
		'client_id': CLI_ID,
		'response_type': 'code',
		'redirect_uri': REDIRECT_URI,
		'state': state
	}
	res = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
	res.set_cookie('spotify_auth_state', state, samesite="Strict")
	return res


@app.route("/callback")
def callback():
	code = request.args.get('code')
	state = request.args.get('state') or None

	# check state 
	if state is None:
		return render_template("home.html", value="error")
	
	# request token's payload 
	payload = {
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': REDIRECT_URI,
	}
	res = requests.post(TOKEN_URL, auth=(CLI_ID, CLI_KEY), data=payload)
	res_data = res.json()

	if res_data.get('error') or res.status_code != 200:
		app.logger.error(
			'Failed to get tokens {}'.format(
				res_data.get('error', 'No error information received.'),
			)
		)
		abort(res.status_code)
	
	session['tokens'] = {
		'access_token': res_data.get('access_token'),
		'refresh_token': res_data.get('refresh_token'),
	}
	session.modified = True 

	return redirect(url_for('connected'))


@app.route('/refresh')
def refresh():
	tokens = session.get('tokens') or None

	if tokens is None:
		return render_template("home.html", value="reauthorize")

	payload = {
		'grant_type': 'refresh_token',
		'refresh_token': tokens.get('refresh_token'),
	}
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}

	res = requests.post(
		TOKEN_URL, auth=(CLI_ID, CLI_KEY), data=payload, headers=headers
	)
	res_data = res.json()
	# load new tokens into session
	session['tokens']['access_token'] = res_data.get('access_token')
	return redirect(url_for('connected'))


@app.route('/connected', methods = ['GET'])
def connected():
	token = session.get('tokens').get('access_token')
	if token:
		data = get_user_playlists(token=session.get('tokens').get('access_token'))
		return render_template("home_connected.html", user=data['user'], playlists=data['playlists'], token=token) 
	else:
		return render_template("home.html")


if __name__ == "__main__":
	app.run(debug=True)
