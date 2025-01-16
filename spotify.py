import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

class Spotify:
  SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
  SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
  SPOTIFY_REDIRECT_URI = "https://example.com"  # Can be any valid URI

  # Define the scope for accessing user's playlists
  SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"

  def __init__(self):
    self.service = None
      
  def init_service(self):
    # Authenticate and initialize Spotify client
    self.service = spotipy.Spotify(auth_manager=SpotifyOAuth(
      client_id=self.SPOTIFY_CLIENT_ID,
      client_secret=self.SPOTIFY_CLIENT_SECRET,
      redirect_uri=self.SPOTIFY_REDIRECT_URI,
      scope=self.SCOPE
    ))

  def list_songs_in_playlist(playlist_id):
      # Fetch playlist tracks
      results = sp.playlist_tracks(playlist_id)
      tracks = results['items']
      
      # Handle pagination (if there are more than 100 tracks)
      while results['next']:
          results = sp.next(results)
          tracks.extend(results['items'])

      # Print track details
      print(f"Songs in Playlist (ID: {playlist_id}):")
      for idx, item in enumerate(tracks, start=1):
          track = item['track']
          print(f"{idx}. {track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")

  def my_playlists(self):
    # Fetch current user's playlists
    playlists = self.service.current_user_playlists()
    return playlists['items']

  def create_playlist(self, title, description=None, privacy_status='public'):
    user_id = self.service.current_user()['id']

    public = True
    if privacy_status != 'public':
      public = False

    return self.service.user_playlist_create(
      user=user_id,
      name=title,
      public=public,
      description=description
    )

  def find_or_create_playlist(self, title, description=None, privacy_status='public'):
    playlists = self.my_playlists()
    for playlist in playlists:
      if playlist['name'] == title:
        return playlist
    return self.create_playlist(title, description, privacy_status)

  # def update_playlist(self, playlist_id, title, description=None, privacy_status=None):

  def playlist_items(self, playlist_id):
    results = self.service.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Handle pagination (if there are more than 100 tracks)
    while results['next']:
        results = self.service.next(results)
        tracks.extend(results['items'])

    return tracks

  def add_song_to_playlist(self, playlist_id, song_id):
    return self.service.playlist_add_items(playlist_id, [video_id])

  def add_songs_to_playlist(self, playlist_id, song_ids):
    return self.service.playlist_add_items(playlist_id, song_ids)

  # def delete_video_to_playlist(self, playlist_id, video_id):

  # def delete_playlist(self, playlist_id):

  def playlist_name(self, playlist):
    return playlist["name"]

  def song_name(self, item):
    return item['track']['name']

  def song_id(self, item):
    return item["track"]["uri"]

if __name__ == "__main__":
  yt = Spotify()
  yt.init_service()
  yt.my_playlists()
  playlists = yt.my_playlists()
  for playlist in playlists:
    print(yt.playlist_name(playlist))
