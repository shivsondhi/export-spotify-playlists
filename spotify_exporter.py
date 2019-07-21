'''
Using Spotipy to make calls to the Spotify Web API. 

Control variables - [All are either global or in main()]
	* CLI_ID and CLI_KEY	(string)
	* overwrite 			(boolean)
	* mode 					(string)
	* playlist 				(string)
'''

import spotipy
import spotipy.oauth2 as oauth2
import random
from pprint import pprint
import csv
import os


# client ID and secret key to authorize querying of spotify data through the API
CLI_ID 	= # YOUR CLIENT ID
CLI_KEY = # YOUR CLIENT SECRET


# header row for csv file 
csv_headers = ["url", "name", "artist", "explicit", "popularity", "duration_ms"]
# whether you want to overwrite existing files or not
OVERWRITE = True


def main():
	global spotify

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
		"just"					: ["1MlVgfN4qPrG7cWQLhC4O9", "shivsondhi"],
		"reggaton"				: ["3MQzcmwPwvpy2tdVbqy775", "pcnaimad"]}
	playlist = playlists_info['hiphop']

	# step 1 - get the token to get authorized by the spotify API
	token = get_token()
	spotify = spotipy.Spotify(auth=token)
	
	# write playlist contents to file and other playlist-operations
	write_playlist(playlist[1], playlist[0], mode)


def get_token():
	'''
	Your client ID and client secret key are used to get a token. 
	If both your credentials were legitimate, you will get and return a valid token. 
	'''
	credentials = oauth2.SpotifyClientCredentials(
		client_id = CLI_ID, 
		client_secret = CLI_KEY)
	token = credentials.get_access_token()
	return token 


def write_playlist(username, uri, mode):
	'''
	Query the spotify API and receive the playlist information. If mode is 'nan' you can view this information data structure in its raw form.
	Obtain the list of tracks from the playlist information data structure and write it to a txt or csv file.
	Select a random song from the list of tracks and print general information to the console. 
	'''
	playlist_info = spotify.user_playlist(username, uri) 						#, fields='tracks,next,name'
	tracks = playlist_info['tracks']
	if mode == 'txt':
		filename = "{0}.txt".format(playlist_info['name'])
		old_total = write_txt(username, filename, tracks)
	elif mode == 'csv':
		filename = "{0}.csv".format(playlist_info['name'])
		old_total = write_csv(filename, tracks)
	elif mode == 'show_ds':
		pprint(playlist_info)
	elif mode == 'nan':
		pass
	# print randomly selected song! 
	song = random.choice(tracks['items'])
	print("Number of tracks = {} --> {} ".format(old_total, tracks['total']))
	print("Randomly selected song for you - {0} by {1}\n".format(song['track']['name'], song['track']['artists'][0]['name']))


def write_txt(username, filename, tracks):
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
				if 'track' in item:
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


def write_csv(filename, tracks):
	'''
	ADD TO CSV FILE
	View the playlist information data structure if this is confusing! 
	Specify the destination file path and check if the file exists already. If the file exists and you selected to not overwrite, the program will end here.
	Traverse the tracks data structure and add whatever information you want to store to a python list. These are the rows for your csv file
	Append all of these lists to a main python list which will store all the rows for your csv file.
	Write the data to the csv file!
	Exceptions handle the cases where the characters in the track info cannot be understood by the system and where the key is invalid (usually due to local files in the playlist).
	'''
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
			if 'track' in item:
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
		if tracks['next']:
			tracks = spotify.next(tracks)
		else:
			break
	with open(filepath, 'w', newline='') as file:
		try:
			writer = csv.writer(file)
			writer.writerows(tracklist)
		except UnicodeEncodeError:
			print("Skipping track (UNDEFINED CHARACTERS) - {0} by {1}".format(track['name'], track['artists'][0]['name']))
	print("Playlist written to file.", end="\n\n")
	print("-----\t\t\t-----\t\t\t-----\n")
	return


if __name__ == "__main__":
	main()