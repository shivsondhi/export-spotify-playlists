'''
Using Spotipy to make calls to the Spotify Web API. 

Control variables - [All are either global or in main()]
	* CLI_ID and CLI_KEY	(string)
'''

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import pandas as pd


CLI_ID 	= os.environ.get('CLI_ID') # CLIENT ID 
CLI_KEY = os.environ.get('CLI_KEY') # CLIENT SECRET 

# header row for tsv file 
tsv_headers = ["Name","Artist","Album","Label"]

def build_playlist(username, uri, cli_id=CLI_ID, cli_key=CLI_KEY, token=None):
	'''
	Query the spotify API and receive the playlist information. If mode is 'nan' you can view this information data structure in its raw form.
	Obtain the list of tracks from the playlist information data structure and write it to a txt or csv file.
	Select a random song from the list of tracks and print general information to the console. 
	'''
	global spotify, playlist_info
	playlist_df = pd.DataFrame(columns = tsv_headers)
	
	# step 1 - get authorized by the spotify API
	if token:
		webapp = True
		spotify = spotipy.Spotify(auth=token)
	else:
		webapp = False
		auth_manager = SpotifyClientCredentials(client_id=cli_id, client_secret=cli_key)
		spotify = spotipy.Spotify(auth_manager=auth_manager)
	
	try:
		playlist_info = spotify.user_playlist_tracks(username, uri)["items"]
	except:
		return "error"

	playlist_name = spotify.user_playlist(username, uri, fields="name")

	for track in playlist_info:
		album_id = track["track"]["album"]["uri"]

		# when a track cannot be found, skip to the next track
		if not album_id:
			continue

		length = len(album_id) # get length of string
		
		# create new string of last 22 characters
		album_id = album_id[length - 22:]
		album_label = spotify.album(album_id)["label"]
		
		# Create empty dict
		playlist_features = {}
		# Get metadata
		playlist_features["Name"] = track["track"]["name"]
		playlist_features["Artist"] = track["track"]["album"]["artists"][0]["name"]
		playlist_features["Album"] = track["track"]["album"]["name"]
		playlist_features["Label"] = album_label

		# Removes leading/trailing whitespace
		playlist_features = { x.translate({32:None}) : y 
        	for x, y in playlist_features.items()}
        
        # Concat the dfs
		track_df = pd.DataFrame(playlist_features, index = [0])
		playlist_df = pd.concat([playlist_df, track_df], ignore_index = True)

	# if tracks['total'] < 1:
	# 	if webapp:
	# 		# RETURN EMPTY PLAYLIST MESSAGE 
	# 		print("Playlist is empty!")
	# 	else:
	# 		print("Playlist is empty!")
	# 		return 

	filename = "{0}.tsv".format(playlist_name['name'])
	write_tsv_file(filename, playlist_df, webapp) 

	return filename


def write_tsv_file(filename, playlist_df, webapp):
	# Filename is in tsv format so will download as tsv
	return playlist_df.to_csv(filename, index=False, sep="\t")