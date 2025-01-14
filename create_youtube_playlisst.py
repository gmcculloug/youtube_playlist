# Description: This script reads a list of songs from a file and adds them to a YouTube playlist.
# The script uses the YouTube API to search for songs in "master song list" playlists and
# adds them to the target playlist.
# The script also prints out any songs that were not found in the playlist.

import os
import sys
import argparse
from youtube import YouTube
from thefuzz import process

DEBUG_MODE = False
DEFAULT_PLAYLIST_NAME = 'TEST PLAYLIST'
SONG_LIST_INPUT_FILE = 'song_list.txt'
TOKEN_FILE = 'token.json'

def get_master_song_list(yt):
  master_playlists = find_master_playlists(yt)
  return collect_playlist_items(yt, master_playlists)

def find_master_playlists(yt):
  master_playlists = []

  for playlist in yt.my_playlists():
    if "master" in playlist["snippet"]["title"].lower():
      master_playlists.append(playlist)

  return master_playlists

def collect_playlist_items(yt, playlists):
  playlist_items = []

  for playlist in playlists:
    playlist_items.extend(yt.playlist_items(playlist["id"]))

  # Convert the playlist to a dictionary with the title as the key and item as the value
  playlist_items = {song_title_cleanup(item["snippet"]["title"]): item for item in playlist_items}

  return playlist_items

def song_title_cleanup(song_title):
  return song_title.translate(song_title.maketrans({
    '(': '',
    ')': '',
    '’': '',
    ',': '',
    '\'': ''}))

def read_song_list_from_file():
  with open(SONG_LIST_INPUT_FILE, 'r') as f:
    song_list = f.readlines()

  # Remove items that are empty or are just newlines
  song_list = [item.strip() for item in song_list if item.strip()]

  # Clean up song titles in one loop
  song_list = [song_title_cleanup(item.split(" - ")[0] if " - " in item else item) for item in song_list]

  print(f"Processing {len(song_list)} songs from file")

  return song_list

def find_matching_video(song_name, master_song_list):
  matches = process.extract(song_name, master_song_list.keys())
  if not matches:
    print(f"No matches found for {song_name}")
    return None

  for match in matches:
    video_title_match = str(match[0])

    # Print only if the song name is not part of the video title
    if song_name.lower() in song_title_cleanup(video_title_match).lower():
      return master_song_list[video_title_match]
    else:
      if DEBUG_MODE:
        print(f"Song name not in video title: {song_name}, {video_title_match}")

  print(f"No matches found for {song_name}")
  return None

def get_playlist(yt, args):
  if args.dry_run == True:
    print(f"(dry-run) Playlist: {args.playlist}")
    playlist = {"id": 1}
  else:
    playlist = yt.find_or_create_playlist(args.playlist, privacy_status='private')
  
  return playlist

def parse_args():
  # Parse command line options -d for dry_run collect remaining arguments as the playlist name
  parser = argparse.ArgumentParser(description='Create YouTube playlist from song list.')
  parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without making any changes')
  parser.add_argument("playlist", nargs="*", help="The value of the variable.")

  args = parser.parse_args()
  args.playlist = ' '.join(args.playlist)
  
  return args

def main():
  args = parse_args()
  song_list = read_song_list_from_file()

  yt = YouTube(TOKEN_FILE)
  yt.init_service()

  playlist = get_playlist(yt, args)
  master_song_list = get_master_song_list(yt)

  for song_name in song_list:
    video = find_matching_video(song_name, master_song_list)
    if not video:
      print(f"Could not find matching video for: {song_name}")
      continue
    else:
      video_id = video["snippet"]["resourceId"]["videoId"]
      if args.dry_run:
        print(f"(dry-run) Video found for: {song_name}")
      else:
        yt.add_video_to_playlist(playlist["id"], video_id)

if __name__ == "__main__":
  main()
