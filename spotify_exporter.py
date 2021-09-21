'''
Using Spotipy to make calls to the Spotify Web API. 

Control variables - [All are either global or in main()]
	* CLI_ID and CLI_KEY	(string)
	* overwrite 			(boolean)
	* mode 					(string)
	* playlist 				(list of strings)
'''

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
from pprint import pprint
import csv
import os


# client ID and secret key to authorize querying of spotify data through the API
CLI_ID 	= 'CLIENT ID' # YOUR CLIENT ID
CLI_KEY = 'CLIENT KEY' # YOUR CLIENT SECRET


# header row for csv file 
csv_headers = ["url", "name", "artist", "explicit", "popularity", "duration_ms"]
# whether you want to overwrite existing files or not
OVERWRITE = True


def main():
	# Choose whether you want to export playlist to a txt file, csv file or if you just want to view the playlist data structure or get a random song. 
	modes = ["txt", "csv", "show_ds", "nan"]
	mode = modes[0]
	
	# dictionary of playlists with their IDs and owner IDs
	playlists_info = {
		"rock" 					: ["37i9dQZF1DWXRqgorJj26U", "spotify"],
		"hiphop"				: ["37i9dQZF1DX0XUsuxWHRQd", "spotify"],
		"classical"				: ["37i9dQZF1DWWEJlAGA9gs0", "spotify"], 
		"focus"					: ["37i9dQZF1DWZeKCadgRdKQ", "spotify"],
		"edm"					: ["37i9dQZF1DX5Q27plkaOQ3", "spotify"],
		"reggaton"				: ["3MQzcmwPwvpy2tdVbqy775", "pcnaimad"]}
	playlist = playlists_info['hiphop']

	# write playlist contents to file and other playlist-operations
	write_playlist(playlist[1], playlist[0], mode, cli_id=CLI_ID, cli_key=CLI_KEY)


def write_playlist(username, uri, mode, cli_id=None, cli_key=None, token=None):
	'''
	Query the spotify API and receive the playlist information. If mode is 'nan' you can view this information data structure in its raw form.
	Obtain the list of tracks from the playlist information data structure and write it to a txt or csv file.
	Select a random song from the list of tracks and print general information to the console. 
	'''
	global spotify

	# step 1 - get authorized by the spotify API
	if token:
		webapp = True
		spotify = spotipy.Spotify(auth=token)
	else:
		webapp = False
		auth_manager = SpotifyClientCredentials(client_id=cli_id, client_secret=cli_key)
		spotify = spotipy.Spotify(auth_manager=auth_manager)
	
	playlist_info = spotify.user_playlist(username, uri) 						#, fields='tracks,next,name'
	tracks = playlist_info['tracks']
	if tracks['total'] < 1:
		if token:
			# RETURN EMPTY PLAYLIST MESSAGE 
			print("Playlist is empty!")
		else:
			print("Playlist is empty!")
			return 
	if mode == 'txt':
		filename = "{0}.txt".format(playlist_info['name'])
		old_total = write_txt(username, filename, tracks, webapp)
	elif mode == 'csv':
		filename = "{0}.csv".format(playlist_info['name'])
		old_total = write_csv(filename, tracks, webapp)
	elif mode == 'show_ds':
		pprint(playlist_info)
	elif mode == 'nan':
		pass
	# randomly select song 
	song = random.choice(tracks['items'])
	if token:
		# RETURN NUM OF TRACKS AND RANDOM SONG TO FRONTEND 
		# RETURN FILE OBJECT OR WHATEVER 
		pass
	else:
		print("Number of tracks = {} --> {} ".format(
			old_total, tracks['total'])
		)
		print("Randomly selected song for you - {0} by {1}\n".format(
			song['track']['name'], song['track']['artists'][0]['name'])
		)


def write_txt(username, filename, tracks, webapp):
	'''
	ADD TO TXT FILE
	View the playlist information data structure if this is confusing! 
	Specify the destination file path and check if the file exists already. If the file exists and you selected to not overwrite, the program will end here.
	Open the file and read the contents of the file to get the number of songs that are already recorded. 
	Seek the file pointer back to the beginning and overwrite the file contents with the track information as required. 
	Finally, truncate any extra bytes of the file, if the overwritten portion is less than the original portion. 
	Return the original number of songs to the calling function. 
	Exceptions handle the cases where the characters in the track info cannot be understood by the system and where the key is invalid (usually due to local files in the playlist).
	'''
	if webapp:
		parent_path = "Saved Data\\Text\\"
		if not os.path.exists(parent_path):
			os.makedirs(parent_path)
		filepath = parent_path + filename
	else:
		filepath = "C:\\path\\to\\the\\directory\\{0}".format(filename)
	if os.path.isfile(filepath):
		print("File already exists!")
		ex = True
		filemode = 'r+'
		if not OVERWRITE:
			return
		else:
			print("Rewriting...")
	else:
		ex = False
		filemode = 'w'
	with open(filepath, filemode) as file:
		# reading number of songs from the file if it exists
		if ex:
			content = file.readlines()
			curr_tot = content[-2][14:]
			curr_tot = curr_tot.strip() 						# to remove the trailing newline character
			file.seek(0)
		else:
			curr_tot = None
		# write new songs to the file
		while True:
			for item in tracks['items']:
				if ('track' in item) and (item['track']):
					track = item['track']
				else:
					track = item
				try:
					track_url = track['external_urls']['spotify']
					file.write("{0:<60} - {1:<90} - {2} \n".format(track_url, track['name'], track['artists'][0]['name']))
				except KeyError:
					print("Skipping track (LOCAL FILE) - {0} by {1}".format(track['name'], track['artists'][0]['name']))
				except UnicodeEncodeError:
					print("Skipping track (UNDEFINED CHARACTERS) - {0} by {1}".format(track['name'], track['artists'][0]['name']))
			# 1 page = 50 results
			# check if there are more pages
			if tracks['next']:
				tracks = spotify.next(tracks)
			else:
				break
		file.write("\n\nTotal Songs - {0}\nUser - {1}".format(tracks['total'], username))
		file.truncate()
	print("Playlist written to file.", end="\n\n")
	print("-----\t\t\t-----\t\t\t-----\n")
	return curr_tot


def write_csv(filename, tracks, webapp):
	'''
	ADD TO CSV FILE
	View the playlist information data structure if this is confusing! 
	Specify the destination file path and check if the file exists already. If the file exists and you selected to not overwrite, the program will end here.
	Traverse the tracks data structure and add whatever information you want to store to a python list. These are the rows for your csv file
	Append all of these lists to a main python list which will store all the rows for your csv file.
	Write the data to the csv file!
	Exceptions handle the cases where the characters in the track info cannot be understood by the system and where the key is invalid (usually due to local files in the playlist).
	'''
	if webapp:
		parent_path = "Saved Data\\CSV\\"
		if not os.path.exists(parent_path):
			os.makedirs(parent_path)
		filepath = parent_path + filename
	else:
		filepath = "C:\\path\\to\\the\\directory\\{0}".format(filename)
	tracklist = []
	tracklist.append(csv_headers)
	if os.path.isfile(filepath):
		print("File already exists!")
		if not OVERWRITE:
			return
		else:
			print("Rewriting...")
	while True:
		for item in tracks['items']:
			if ('track' in item) and (item['track']):
				track = item['track']
			else:
				track = item
			try:
				track_url = track['external_urls']['spotify']
				# add to list of lists
				track_info = [track_url, track['name'], track['artists'][0]['name'], track['explicit'], track['popularity'], track['duration_ms']]
				tracklist.append(track_info)
			except KeyError:
				print("Skipping track (LOCAL ONLY) - {0} by {1}".format(track['name'], track['artists'][0]['name']))
			except TypeError:
				print("NoneType object detected.")
		if tracks['next']:
			tracks = spotify.next(tracks)
		else:
			break
	with open(filepath, 'w', newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerows(tracklist)
	print("Playlist written to file.", end="\n\n")
	print("-----\t\t\t-----\t\t\t-----\n")
	return


if __name__ == "__main__":
	main()