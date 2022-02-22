'''
Spotify playlist exporter. 

CONTROL FLOW:
/ > /login > /callback > /connected > /data
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
from spotify_exporter import build_playlist
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
app.secret_key = 'selectARandomsecret_Key-forTheAPP'


@app.route("/")
def home():
	return render_template("home.html") 


@app.route("/data", methods={"GET", "POST"})
def data():
	print("Request method", request.method)

	if request.method == "GET":
		return """The URL http://localhost:5000/data cannot be accessed directly. 
		Try submitting the form at http://localhost:5000/connected first."""
	if request.method == "POST":
		form_data = request.form.to_dict(flat=False) 
		# get playlist data 
		uri_len = 22
		playlist_url = form_data['url'][0]
		start = playlist_url.find("playlist")
		mid = len("playlist/")
		end = start + mid
		playlist_uri = playlist_url[end:end+uri_len] 
		user = form_data['name'][0]
		filename = build_playlist(user, playlist_uri, token=session.get('tokens').get('access_token')) 
		return render_template("data.html", filename=filename)


@app.route('/download/<filename>', methods=['POST', 'GET'])
def download(filename): 
	print("Download file", filename)
	return send_file(filename, as_attachment=True)


@app.route("/login")
def login():
	state = ''.join(
		secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
	)
	scope = "playlist-read-private"
	payload = {
		'client_id': CLI_ID,
		'response_type': 'code',
		'redirect_uri': REDIRECT_URI,
		'state': state,
		'scope': scope
	}
	res = make_response(redirect(f'{AUTH_URL}/?{urlencode(payload)}'))
	res.set_cookie('spotify_auth_state', state, samesite="Strict")
	return res


@app.route("/callback")
def callback():
	error = request.args.get('error')
	code = request.args.get('code')
	state = request.args.get('state')
	stored_state = request.cookies.get('spotify_auth_state')

	# check state 
	# if state is None or state != stored_state:
	# 	app.logger.error('Error message: {}'.format(repr(error)))
	# 	app.logger.error('State mismatch: {} != {}'.format(stored_state, state))
	# 	abort(400)
	
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
	# TO DO: session tokens is not returning anything
	payload = {
		'grant_type': 'refresh_token',
		'refresh_token': session.get('tokens').get('refresh_token'),
	}
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}

	res = requests.post(
		TOKEN_URL, auth=(CLI_ID, CLI_KEY), data=payload, headers=headers
	)
	res_data = res.json()
	# load new tokens into session
	session['tokens']['access_token'] = res_data.get('access_token')
	# return json.dumps(session['tokens'])

	return redirect(url_for('connected'))


@app.route('/connected')
def connected():
	token = session.get('tokens').get('access_token')
	if token:
		return render_template("home_connected.html") 
	else:
		return render_template("home.html")


if __name__ == "__main__":
	app.run(debug=True)
