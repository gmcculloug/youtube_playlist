# Description: This module provides a class to interact with the YouTube API.
# The class provides methods to create, update, and delete playlists, as well as
# add videos to a playlist.

import os
from functools import lru_cache
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTube:
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    API_MAX_RESULTS = 100
    SCOPES = ['https://www.googleapis.com/auth/youtube',
                'https://www.googleapis.com/auth/youtube.force-ssl']

    def __init__(self, client_file):
        self.service = None
        self.client_file = client_file
        
    def init_service(self):        
        # self.service = create_service(self.client_file, self.API_NAME, self.API_VERSION, self.SCOPES)
        creds = self.credentials()
        self.service = build("youtube", "v3", credentials=creds)

    def credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    @lru_cache(maxsize=None)  # Cache all calls
    def my_playlists(self):
        playlists = []
        response = self.service.playlists().list(
            part='id,contentDetails,player,snippet,status',
            mine=True,
            maxResults=self.API_MAX_RESULTS
        ).execute()

        playlists.extend(response.get('items'))
        next_page_token = response.get('nextPageToken')

        while next_page_token:
            response = self.service.playlists().list(
                part='id,contentDetails,player,snippet,status',
                mine=True,
                maxResults=self.API_MAX_RESULTS,
                pageToken=next_page_token
            ).execute()            
            playlists.extend(response.get('items'))
            next_page_token = response.get('nextPageToken')
        return playlists 

    def create_playlist(self, title, description=None, privacy_status='public'):
        """
        visit https://developers.google.com/youtube/v3/docs/playlists#resource for
        request json representation and parameters
        """
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        response = self.service.playlists().insert(
            part='snippet,status',
            body=request_body
        ).execute()
        return response

    def find_or_create_playlist(self, title, description=None, privacy_status='public'):
        playlists = self.my_playlists()
        for playlist in playlists:
            if playlist['snippet']['title'] == title:
                return playlist
        return self.create_playlist(title, description, privacy_status)
        
    def update_playlist(self, playlist_id, title, description=None, privacy_status=None):
        request_body = {
            'id': playlist_id,
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        print(request_body)
        response = self.service.playlists().update(
            part='snippet,status',
            body=request_body
        ).execute()
        return response

    def playlist_items(self, playlist_id):
        playlist_items = []
        response = self.service.playlistItems().list(
            part='id,contentDetails,snippet',
            playlistId=playlist_id,
            maxResults=self.API_MAX_RESULTS
        ).execute()
        playlist_items.extend(response.get('items'))
        next_page_token = response.get('nextPageToken')

        while next_page_token:
            response = self.service.playlistItems().list(
                part='id,contentDetails,snippet',
                playlistId=playlist_id,
                maxResults=self.API_MAX_RESULTS,
                pageToken=next_page_token
            ).execute()
            playlist_items.extend(response.get('items'))
            next_page_token = response.get('nextPageToken')
        return playlist_items

    def add_video_to_playlist(self, playlist_id, video_id):
        request_body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        response = self.service.playlistItems().insert(
            part='snippet',
            body=request_body
        ).execute()
        return response

    def delete_playlist(self, playlist_id):
        self.service.playlists().delete(id=playlist_id).execute()
