# Description: This script reads a list of songs from a file and adds them to a YouTube playlist.
# The script uses the YouTube API to search for songs in "master song list" playlists and
# adds them to the target playlist.
# The script also prints out any songs that were not found in the playlist.

import os
import sys
import argparse
from youtube import YouTube
from spotify import Spotify
from thefuzz import process

DEBUG_MODE = False
DEFAULT_PLAYLIST_NAME = 'TEST PLAYLIST'
SONG_LIST_INPUT_FILE = 'song_list.txt'
TOKEN_FILE = 'token.json'

def get_master_song_list(m_svc):
  master_playlists = find_master_playlists(m_svc)
  return collect_playlist_items(m_svc, master_playlists)

def find_master_playlists(m_svc):
  master_playlists = []

  for playlist in m_svc.my_playlists():
    if "master" in m_svc.playlist_name(playlist).lower():
      master_playlists.append(playlist)

  return master_playlists

def collect_playlist_items(m_svc, playlists):
  playlist_items = []

  for playlist in playlists:
    playlist_items.extend(m_svc.playlist_items(playlist["id"]))

  # Convert the playlist to a dictionary with the title as the key and item as the value
  playlist_items = {song_title_cleanup(m_svc.song_name(item)): item for item in playlist_items}

  return playlist_items

def song_title_cleanup(song_title):
  return song_title.translate(song_title.maketrans({
    '(': '',
    ')': '',
    '’': '',
    ',': '',
    '➔': '',
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

def find_matching_song(song_name, master_song_list):
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

def get_playlist(m_svc, args):
  if args.dry_run == True:
    print(f"(dry-run) Playlist: {args.playlist}")
    playlist = {"id": 1}
  else:
    playlist = m_svc.find_or_create_playlist(args.playlist)
  
  return playlist

def parse_args():
  # Parse command line options -d for dry_run collect remaining arguments as the playlist name
  parser = argparse.ArgumentParser(description='Create YouTube playlist from song list.')
  parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without making any changes')
  parser.add_argument('-s', '--spotify', action='store_true', help='Use Spotify')
  parser.add_argument("playlist", nargs="*", help="The value of the variable.")

  args = parser.parse_args()
  args.playlist = ' '.join(args.playlist)
  
  return args

def initialize_service(args):
  m_svc = None
  if args.spotify:
    m_svc = Spotify()
    m_svc.init_service()
  else:
    m_svc = YouTube(TOKEN_FILE)
    m_svc.init_service()

  return m_svc

def main():
  args = parse_args()
  song_list = read_song_list_from_file()

  m_svc = initialize_service(args)

  playlist = get_playlist(m_svc, args)
  master_song_list = get_master_song_list(m_svc)

  song_ids = []
  for song_name in song_list:
    song = find_matching_song(song_name, master_song_list)
    if not song:
      print(f"Could not find matching song for: {song_name}")
      continue
    else:
      song_id = m_svc.song_id(song)
      if args.dry_run:
        print(f"(dry-run) song found for: {song_name}")
      else:
        song_ids.append(song_id)
  
  if song_ids:
    m_svc.add_songs_to_playlist(playlist["id"], song_ids)

if __name__ == "__main__":
  main()
