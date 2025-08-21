import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os
import tempfile
import shutil
from io import StringIO

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from create_playlist import (
    get_master_song_list, find_master_playlists, collect_playlist_items,
    song_title_cleanup, read_song_list_from_file, find_matching_song,
    get_playlist, parse_args, initialize_service, reset_playlist,
    update_playlist, playlist_name, main
)
from youtube import YouTube
from spotify import Spotify


class TestCreatePlaylist(unittest.TestCase):
    """Test cases for the create_playlist module"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create a mock song list file
        self.song_list_content = """Song 1 - Artist 1
Song 2 - Artist 2
Song 3 - Artist 3
Song 4 - Artist 4
Song 5 - Artist 5"""
        
        with open('song_list.txt', 'w') as f:
            f.write(self.song_list_content)

    def tearDown(self):
        """Clean up after each test method"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_song_title_cleanup(self):
        """Test song title cleanup function"""
        test_cases = [
            ("Song (Remix)", "Song Remix"),
            ("Artist's Song", "Artists Song"),
            ("Song, The", "Song The"),
            ("Song ➔ Remix", "Song  Remix"),
            ("Song 'Live'", "Song Live"),
            ("Normal Song", "Normal Song"),
            ("", ""),
        ]
        
        for input_title, expected in test_cases:
            with self.subTest(input_title=input_title):
                result = song_title_cleanup(input_title)
                self.assertEqual(result, expected)

    def test_read_song_list_from_file(self):
        """Test reading song list from file"""
        songs = read_song_list_from_file()
        
        expected_songs = [
            "Song 1",
            "Song 2", 
            "Song 3",
            "Song 4",
            "Song 5"
        ]
        
        self.assertEqual(songs, expected_songs)
        self.assertEqual(len(songs), 5)

    def test_read_song_list_from_file_with_empty_lines(self):
        """Test reading song list with empty lines and whitespace"""
        content = """Song 1 - Artist 1

Song 2 - Artist 2
   Song 3 - Artist 3   
Song 4 - Artist 4

"""
        with open('song_list.txt', 'w') as f:
            f.write(content)
            
        songs = read_song_list_from_file()
        expected_songs = ["Song 1", "Song 2", "Song 3", "Song 4"]
        self.assertEqual(songs, expected_songs)

    def test_read_song_list_from_file_missing_file(self):
        """Test reading song list when file doesn't exist"""
        # Remove the test file
        os.remove('song_list.txt')
        
        with self.assertRaises(FileNotFoundError):
            read_song_list_from_file()

    def test_parse_args(self):
        """Test argument parsing"""
        # Test with playlist name
        with patch('sys.argv', ['create_playlist.py', 'My Playlist']):
            args = parse_args()
            self.assertEqual(args.playlist, 'My Playlist')
            self.assertFalse(args.dry_run)
            self.assertFalse(args.spotify)
            # Reset argument is commented out, so don't test it
            # self.assertFalse(args.reset)

        # Test with dry run
        with patch('sys.argv', ['create_playlist.py', '-d', 'Test Playlist']):
            args = parse_args()
            self.assertEqual(args.playlist, 'Test Playlist')
            self.assertTrue(args.dry_run)

        # Test with spotify flag
        with patch('sys.argv', ['create_playlist.py', '-s', 'Spotify Playlist']):
            args = parse_args()
            self.assertEqual(args.playlist, 'Spotify Playlist')
            self.assertTrue(args.spotify)

        # Test with reset flag - disabled since reset is commented out
        # with patch('sys.argv', ['create_playlist.py', '-r', 'Reset Playlist']):
        #     args = parse_args()
        #     self.assertEqual(args.playlist, 'Reset Playlist')
        #     self.assertTrue(args.reset)

        # Test with multiple flags - excluding reset since it's commented out
        with patch('sys.argv', ['create_playlist.py', '-d', '-s', 'Complex Playlist']):
            args = parse_args()
            self.assertEqual(args.playlist, 'Complex Playlist')
            self.assertTrue(args.dry_run)
            self.assertTrue(args.spotify)
            # Reset argument is commented out, so don't test it
            # self.assertTrue(args.reset)

    @patch('create_playlist.YouTube')
    def test_initialize_service_youtube(self, mock_youtube_class):
        """Test YouTube service initialization"""
        mock_youtube = Mock()
        mock_youtube_class.return_value = mock_youtube
        
        args = Mock()
        args.spotify = False
        
        service = initialize_service(args)
        
        mock_youtube_class.assert_called_once()
        mock_youtube.init_service.assert_called_once()
        self.assertEqual(service, mock_youtube)

    @patch('create_playlist.Spotify')
    def test_initialize_service_spotify(self, mock_spotify_class):
        """Test Spotify service initialization"""
        mock_spotify = Mock()
        mock_spotify_class.return_value = mock_spotify
        
        args = Mock()
        args.spotify = True
        
        service = initialize_service(args)
        
        mock_spotify_class.assert_called_once()
        mock_spotify.init_service.assert_called_once()
        self.assertEqual(service, mock_spotify)

    def test_find_master_playlists(self):
        """Test finding master playlists"""
        mock_service = Mock()
        
        # Mock playlists with different names
        mock_playlists = [
            {'id': '1', 'snippet': {'title': 'Master Rock Songs'}},
            {'id': '2', 'snippet': {'title': 'Pop Hits'}},
            {'id': '3', 'snippet': {'title': 'Master Jazz Collection'}},
            {'id': '4', 'snippet': {'title': 'Country Music'}},
        ]
        
        mock_service.my_playlists.return_value = mock_playlists
        mock_service.playlist_name.side_effect = lambda p: p['snippet']['title']
        
        master_playlists = find_master_playlists(mock_service)
        
        expected_master_playlists = [
            {'id': '1', 'snippet': {'title': 'Master Rock Songs'}},
            {'id': '3', 'snippet': {'title': 'Master Jazz Collection'}},
        ]
        
        self.assertEqual(master_playlists, expected_master_playlists)

    def test_collect_playlist_items(self):
        """Test collecting playlist items"""
        mock_service = Mock()
        
        mock_playlists = [
            {'id': 'playlist1'},
            {'id': 'playlist2'},
        ]
        
        mock_items1 = [
            {'snippet': {'title': 'Song 1 (Remix)'}},
            {'snippet': {'title': 'Song 2'}},
        ]
        
        mock_items2 = [
            {'snippet': {'title': 'Song 3'}},
            {'snippet': {'title': 'Song 4 (Live)'}},
        ]
        
        mock_service.playlist_items.side_effect = [mock_items1, mock_items2]
        mock_service.song_name.side_effect = lambda item: item['snippet']['title']
        
        result = collect_playlist_items(mock_service, mock_playlists)
        
        expected_keys = ['Song 1 Remix', 'Song 2', 'Song 3', 'Song 4 Live']
        self.assertEqual(set(result.keys()), set(expected_keys))
        
        # Verify the items are stored correctly
        self.assertEqual(result['Song 1 Remix'], mock_items1[0])
        self.assertEqual(result['Song 2'], mock_items1[1])
        self.assertEqual(result['Song 3'], mock_items2[0])
        self.assertEqual(result['Song 4 Live'], mock_items2[1])

    def test_get_master_song_list(self):
        """Test getting master song list"""
        mock_service = Mock()
        
        # Mock master playlists
        mock_master_playlists = [
            {'id': 'master1', 'snippet': {'title': 'Master Rock Songs'}},
            {'id': 'master2', 'snippet': {'title': 'Master Jazz Collection'}},
        ]
        
        # Mock collected items
        mock_collected_items = {
            'Song 1': {'id': 'item1'},
            'Song 2': {'id': 'item2'},
        }
        
        with patch('create_playlist.find_master_playlists', return_value=mock_master_playlists) as mock_find:
            with patch('create_playlist.collect_playlist_items', return_value=mock_collected_items) as mock_collect:
                result = get_master_song_list(mock_service)
                
                mock_find.assert_called_once_with(mock_service)
                mock_collect.assert_called_once_with(mock_service, mock_master_playlists)
                self.assertEqual(result, mock_collected_items)

    def test_find_matching_song(self):
        """Test finding matching songs"""
        master_song_list = {
            'Song 1': {'id': 'song1'},
            'Song 2 Remix': {'id': 'song2'},
            'Artist Song 3': {'id': 'song3'},
            'Song 4 Live': {'id': 'song4'},
        }
        
        # Test exact match
        result = find_matching_song('Song 1', master_song_list)
        self.assertEqual(result, {'id': 'song1'})
        
        # Test partial match
        result = find_matching_song('Song 2', master_song_list)
        self.assertEqual(result, {'id': 'song2'})
        
        # Test no match
        result = find_matching_song('Nonexistent Song', master_song_list)
        self.assertIsNone(result)

    def test_find_matching_song_empty_list(self):
        """Test finding matching song with empty master list"""
        master_song_list = {}
        
        result = find_matching_song('Any Song', master_song_list)
        self.assertIsNone(result)

    def test_find_matching_song_debug_mode(self):
        """Test finding matching song with debug mode enabled"""
        import create_playlist
        
        # Save original debug mode state
        original_debug = create_playlist.DEBUG_MODE
        
        try:
            # Enable debug mode
            create_playlist.DEBUG_MODE = True
            
            master_song_list = {
                'Different Song': {'id': 'different'},
            }
            
            # This should trigger the debug print statement
            with patch('builtins.print') as mock_print:
                result = find_matching_song('Test Song', master_song_list)
                self.assertIsNone(result)
                # Verify debug message was printed
                mock_print.assert_any_call("Song name not in video title: Test Song, Different Song")
        finally:
            # Restore original debug mode
            create_playlist.DEBUG_MODE = original_debug

    def test_get_playlist_dry_run(self):
        """Test getting playlist in dry run mode"""
        mock_service = Mock()
        args = Mock()
        args.dry_run = True
        args.playlist = 'Test Playlist'
        
        playlist = get_playlist(mock_service, args)
        
        self.assertEqual(playlist, {'id': 1})
        mock_service.find_or_create_playlist.assert_not_called()

    def test_get_playlist_normal(self):
        """Test getting playlist in normal mode"""
        mock_service = Mock()
        mock_playlist = {'id': 'playlist123', 'name': 'Test Playlist'}
        mock_service.find_or_create_playlist.return_value = mock_playlist
        
        args = Mock()
        args.dry_run = False
        args.playlist = 'Test Playlist'
        
        playlist = get_playlist(mock_service, args)
        
        mock_service.find_or_create_playlist.assert_called_once_with('Test Playlist')
        self.assertEqual(playlist, mock_playlist)

    def test_playlist_name_dry_run(self):
        """Test playlist name in dry run mode"""
        mock_service = Mock()
        args = Mock()
        args.dry_run = True
        playlist = {'id': 1}
        
        name = playlist_name(mock_service, args, playlist)
        self.assertEqual(name, '(dry-run) [No Playlist]')

    def test_playlist_name_normal(self):
        """Test playlist name in normal mode"""
        mock_service = Mock()
        mock_service.playlist_name.return_value = 'My Playlist'
        
        args = Mock()
        args.dry_run = False
        playlist = {'id': 'playlist123'}
        
        name = playlist_name(mock_service, args, playlist)
        self.assertEqual(name, 'My Playlist')
        mock_service.playlist_name.assert_called_once_with(playlist)

    @patch('builtins.input', return_value='n')
    def test_reset_playlist_no_reset(self, mock_input):
        """Test playlist reset when user declines"""
        mock_service = Mock()
        mock_service.playlist_items.return_value = [{'id': 'item1'}, {'id': 'item2'}]
        mock_service.playlist_name.return_value = 'Test Playlist'
        
        args = Mock()
        args.dry_run = False
        args.reset = False  # Need to add this since reset_playlist function checks it
        playlist = {'id': 'playlist123'}
        
        reset_playlist(args, mock_service, playlist)
        
        mock_input.assert_called_once()
        mock_service.delete_songs_from_playlist.assert_not_called()

    @patch('builtins.input', return_value='y')
    def test_reset_playlist_user_approves(self, mock_input):
        """Test playlist reset when user approves"""
        mock_service = Mock()
        mock_items = [{'id': 'item1'}, {'id': 'item2'}]
        mock_service.playlist_items.return_value = mock_items
        mock_service.playlist_name.return_value = 'Test Playlist'
        
        args = Mock()
        args.dry_run = False
        args.reset = False  # Need to add this since reset_playlist function checks it
        playlist = {'id': 'playlist123'}
        
        reset_playlist(args, mock_service, playlist)
        
        mock_input.assert_called_once()
        mock_service.delete_songs_from_playlist.assert_called_once_with(playlist, mock_items)

    def test_reset_playlist_with_reset_flag(self):
        """Test playlist reset with reset flag"""
        mock_service = Mock()
        mock_items = [{'id': 'item1'}, {'id': 'item2'}]
        mock_service.playlist_items.return_value = mock_items
        
        args = Mock()
        args.dry_run = False
        args.reset = True  # Need to add this since reset_playlist function checks it
        playlist = {'id': 'playlist123'}
        
        reset_playlist(args, mock_service, playlist)
        
        mock_service.delete_songs_from_playlist.assert_called_once_with(playlist, mock_items)

    def test_reset_playlist_empty_playlist(self):
        """Test playlist reset with empty playlist"""
        mock_service = Mock()
        mock_service.playlist_items.return_value = []
        
        args = Mock()
        args.dry_run = False
        args.reset = False  # Need to add this since reset_playlist function checks it
        playlist = {'id': 'playlist123'}
        
        reset_playlist(args, mock_service, playlist)
        
        mock_service.delete_songs_from_playlist.assert_not_called()

    def test_reset_playlist_dry_run(self):
        """Test playlist reset in dry run mode"""
        mock_service = Mock()
        
        args = Mock()
        args.dry_run = True
        playlist = {'id': 'playlist123'}
        
        reset_playlist(args, mock_service, playlist)
        
        mock_service.playlist_items.assert_not_called()
        mock_service.delete_songs_from_playlist.assert_not_called()

    def test_update_playlist_dry_run(self):
        """Test playlist update in dry run mode"""
        mock_service = Mock()
        mock_service.song_id.return_value = 'video123'
        
        args = Mock()
        args.dry_run = True
        
        playlist = {'id': 'playlist123'}
        song_list = ['Song 1', 'Song 2']
        
        # Mock master song list
        master_song_list = {
            'Song 1': {'snippet': {'title': 'Song 1', 'resourceId': {'videoId': 'video1'}}},
            'Song 2': {'snippet': {'title': 'Song 2', 'resourceId': {'videoId': 'video2'}}},
        }
        
        with patch('create_playlist.get_master_song_list', return_value=master_song_list):
            with patch('create_playlist.find_matching_song') as mock_find:
                mock_find.side_effect = [
                    master_song_list['Song 1'],
                    master_song_list['Song 2']
                ]
                
                update_playlist(mock_service, args, playlist, song_list)
                
                # Should not add songs in dry run mode
                mock_service.add_songs_to_playlist.assert_not_called()

    def test_update_playlist_normal(self):
        """Test playlist update in normal mode"""
        mock_service = Mock()
        mock_service.song_id.return_value = 'video123'
        
        args = Mock()
        args.dry_run = False
        
        playlist = {'id': 'playlist123'}
        song_list = ['Song 1', 'Song 2']
        
        # Mock master song list
        master_song_list = {
            'Song 1': {'snippet': {'title': 'Song 1', 'resourceId': {'videoId': 'video1'}}},
            'Song 2': {'snippet': {'title': 'Song 2', 'resourceId': {'videoId': 'video2'}}},
        }
        
        with patch('create_playlist.get_master_song_list', return_value=master_song_list):
            with patch('create_playlist.find_matching_song') as mock_find:
                mock_find.side_effect = [
                    master_song_list['Song 1'],
                    master_song_list['Song 2']
                ]
                
                update_playlist(mock_service, args, playlist, song_list)
                
                # Should add songs in normal mode
                mock_service.add_songs_to_playlist.assert_called_once_with('playlist123', ['video123', 'video123'])

    def test_update_playlist_with_missing_songs(self):
        """Test playlist update with songs that can't be found"""
        mock_service = Mock()
        mock_service.song_id.side_effect = ['video1', 'video2']  # Return different IDs for each call
        
        args = Mock()
        args.dry_run = False
        
        playlist = {'id': 'playlist123'}
        song_list = ['Song 1', 'Missing Song', 'Song 2']
        
        # Mock master song list
        master_song_list = {
            'Song 1': {'snippet': {'title': 'Song 1', 'resourceId': {'videoId': 'video1'}}},
            'Song 2': {'snippet': {'title': 'Song 2', 'resourceId': {'videoId': 'video2'}}},
        }
        
        with patch('create_playlist.get_master_song_list', return_value=master_song_list):
            with patch('create_playlist.find_matching_song') as mock_find:
                mock_find.side_effect = [
                    master_song_list['Song 1'],
                    None,  # Missing song
                    master_song_list['Song 2']
                ]
                
                update_playlist(mock_service, args, playlist, song_list)
                
                # Should only add found songs
                mock_service.add_songs_to_playlist.assert_called_once_with('playlist123', ['video1', 'video2'])

    @patch('create_playlist.read_song_list_from_file')
    @patch('create_playlist.initialize_service')
    @patch('create_playlist.get_playlist')
    @patch('create_playlist.playlist_name')
    @patch('create_playlist.update_playlist')
    def test_main_function(self, mock_update, mock_playlist_name, mock_get_playlist, 
                          mock_init_service, mock_read_songs):
        """Test the main function"""
        # Mock return values
        mock_read_songs.return_value = ['Song 1', 'Song 2']
        mock_service = Mock()
        mock_init_service.return_value = mock_service
        mock_playlist = {'id': 'playlist123'}
        mock_get_playlist.return_value = mock_playlist
        mock_playlist_name.return_value = 'Test Playlist'
        
        # Mock args
        args = Mock()
        args.playlist = 'Test Playlist'
        args.dry_run = False
        args.spotify = False
        args.reset = False  # Need to add this since reset_playlist function checks it
        
        with patch('create_playlist.parse_args', return_value=args):
            main()
            
            # Verify all functions were called
            mock_read_songs.assert_called_once()
            mock_init_service.assert_called_once_with(args)
            mock_get_playlist.assert_called_once_with(mock_service, args)
            mock_playlist_name.assert_called_once_with(mock_service, args, mock_playlist)
            mock_update.assert_called_once_with(mock_service, args, mock_playlist, ['Song 1', 'Song 2'])


class TestYouTubeService(unittest.TestCase):
    """Test cases for the YouTube service class"""

    @patch('youtube.build')
    @patch('youtube.Credentials')
    def test_init_service(self, mock_credentials, mock_build):
        """Test YouTube service initialization"""
        mock_creds = Mock()
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        mock_creds.valid = True
        
        youtube = YouTube()
        youtube.init_service()
        
        mock_build.assert_called_once_with("youtube", "v3", credentials=mock_creds)

    def test_playlist_name(self):
        """Test getting playlist name"""
        youtube = YouTube()
        playlist = {'snippet': {'title': 'Test Playlist'}}
        
        name = youtube.playlist_name(playlist)
        self.assertEqual(name, 'Test Playlist')

    def test_song_name(self):
        """Test getting song name"""
        youtube = YouTube()
        item = {'snippet': {'title': 'Test Song'}}
        
        name = youtube.song_name(item)
        self.assertEqual(name, 'Test Song')

    def test_song_id(self):
        """Test getting song ID"""
        youtube = YouTube()
        item = {'snippet': {'resourceId': {'videoId': 'video123'}}}
        
        song_id = youtube.song_id(item)
        self.assertEqual(song_id, 'video123')

    @patch('youtube.build')
    @patch('youtube.Credentials')
    def test_credentials_valid(self, mock_credentials, mock_build):
        """Test credentials when they are valid"""
        mock_creds = Mock()
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        mock_creds.valid = True
        
        with patch('os.path.exists', return_value=True):
            youtube = YouTube()
            creds = youtube.credentials()
            
            self.assertEqual(creds, mock_creds)
            mock_credentials.from_authorized_user_file.assert_called_once()

    @patch('youtube.build')
    @patch('youtube.InstalledAppFlow')
    @patch('youtube.Credentials')
    def test_credentials_need_refresh(self, mock_credentials, mock_flow, mock_build):
        """Test credentials when they need refresh"""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                youtube = YouTube()
                creds = youtube.credentials()
                
                mock_creds.refresh.assert_called_once()

    @patch('youtube.build')
    @patch('youtube.InstalledAppFlow')
    @patch('youtube.Credentials')
    def test_credentials_refresh_error(self, mock_credentials, mock_flow, mock_build):
        """Test credentials refresh error handling"""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock refresh to raise an exception
        mock_creds.refresh.side_effect = Exception("Refresh failed")
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.print') as mock_print:
                youtube = YouTube()
                
                with self.assertRaises(Exception):
                    youtube.credentials()
                
                mock_print.assert_any_call("Error refreshing credentials: Refresh failed")
                mock_print.assert_any_call("Please delete the 'token.json' file and try again.\n")

    @patch('youtube.build')
    def test_create_playlist(self, mock_build):
        """Test creating a playlist"""
        mock_service = Mock()
        mock_response = {'id': 'new_playlist_id'}
        mock_service.playlists().insert().execute.return_value = mock_response
        
        youtube = YouTube()
        youtube.service = mock_service
        
        result = youtube.create_playlist('Test Playlist', 'Test Description')
        
        self.assertEqual(result, mock_response)
        # Check that insert was called with the correct parameters
        mock_service.playlists().insert.assert_called_with(
            part='snippet,status',
            body={
                'snippet': {
                    'title': 'Test Playlist',
                    'description': 'Test Description'
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
        )

    @patch('youtube.build')
    def test_find_or_create_playlist_existing(self, mock_build):
        """Test finding existing playlist"""
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        existing_playlist = {'id': 'existing_id', 'snippet': {'title': 'Test Playlist'}}
        mock_playlists = [existing_playlist]
        
        youtube = YouTube()
        youtube.service = mock_service
        
        with patch.object(youtube, 'my_playlists', return_value=mock_playlists):
            result = youtube.find_or_create_playlist('Test Playlist')
            
            self.assertEqual(result, existing_playlist)

    @patch('youtube.build')
    def test_find_or_create_playlist_new(self, mock_build):
        """Test creating new playlist when not found"""
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        new_playlist = {'id': 'new_id', 'snippet': {'title': 'New Playlist'}}
        mock_playlists = []
        
        youtube = YouTube()
        youtube.service = mock_service
        
        with patch.object(youtube, 'my_playlists', return_value=mock_playlists):
            with patch.object(youtube, 'create_playlist', return_value=new_playlist) as mock_create:
                result = youtube.find_or_create_playlist('New Playlist')
                
                mock_create.assert_called_once_with('New Playlist', None, 'public')
                self.assertEqual(result, new_playlist)

    @patch('youtube.build')
    def test_add_songs_to_playlist(self, mock_build):
        """Test adding multiple songs to playlist"""
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        youtube = YouTube()
        youtube.service = mock_service
        
        with patch.object(youtube, 'add_song_to_playlist') as mock_add_song:
            youtube.add_songs_to_playlist('playlist123', ['video1', 'video2'])
            
            mock_add_song.assert_any_call('playlist123', 'video1')
            mock_add_song.assert_any_call('playlist123', 'video2')
            self.assertEqual(mock_add_song.call_count, 2)

    @patch('youtube.build')
    def test_delete_songs_from_playlist(self, mock_build):
        """Test deleting songs from playlist"""
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        youtube = YouTube()
        youtube.service = mock_service
        
        playlist = {'id': 'playlist123'}
        songs = [{'id': 'item1'}, {'id': 'item2'}]
        
        with patch.object(youtube, 'delete_song_from_playlist') as mock_delete:
            youtube.delete_songs_from_playlist(playlist, songs)
            
            mock_delete.assert_any_call('playlist123', {'id': 'item1'})
            mock_delete.assert_any_call('playlist123', {'id': 'item2'})
            self.assertEqual(mock_delete.call_count, 2)


class TestSpotifyService(unittest.TestCase):
    """Test cases for the Spotify service class"""

    @patch('spotify.SpotifyOAuth')
    @patch('spotify.spotipy.Spotify')
    def test_init_service(self, mock_spotify, mock_oauth):
        """Test Spotify service initialization"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        spotify = Spotify()
        spotify.init_service()
        
        mock_oauth.assert_called_once()
        mock_spotify.assert_called_once_with(auth_manager=mock_oauth_instance)

    def test_playlist_name(self):
        """Test getting playlist name"""
        spotify = Spotify()
        playlist = {'name': 'Test Playlist'}
        
        name = spotify.playlist_name(playlist)
        self.assertEqual(name, 'Test Playlist')

    def test_song_name(self):
        """Test getting song name"""
        spotify = Spotify()
        item = {'track': {'name': 'Test Song'}}
        
        name = spotify.song_name(item)
        self.assertEqual(name, 'Test Song')

    def test_song_id(self):
        """Test getting song ID"""
        spotify = Spotify()
        item = {'track': {'uri': 'spotify:track:123'}}
        
        song_id = spotify.song_id(item)
        self.assertEqual(song_id, 'spotify:track:123')

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_my_playlists(self, mock_oauth, mock_spotify):
        """Test getting user playlists"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        mock_playlists = {'items': [{'id': 'playlist1', 'name': 'Test Playlist'}]}
        mock_spotify_instance.current_user_playlists.return_value = mock_playlists
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.my_playlists()
        
        self.assertEqual(result, mock_playlists['items'])
        mock_spotify_instance.current_user_playlists.assert_called_once()

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_create_playlist_public(self, mock_oauth, mock_spotify):
        """Test creating a public playlist"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        mock_user = {'id': 'user123'}
        mock_spotify_instance.current_user.return_value = mock_user
        mock_playlist = {'id': 'new_playlist_id'}
        mock_spotify_instance.user_playlist_create.return_value = mock_playlist
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.create_playlist('Test Playlist', 'Test Description', 'public')
        
        mock_spotify_instance.user_playlist_create.assert_called_once_with(
            user='user123',
            name='Test Playlist',
            public=True,
            description='Test Description'
        )
        self.assertEqual(result, mock_playlist)

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_create_playlist_private(self, mock_oauth, mock_spotify):
        """Test creating a private playlist"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        mock_user = {'id': 'user123'}
        mock_spotify_instance.current_user.return_value = mock_user
        mock_playlist = {'id': 'new_playlist_id'}
        mock_spotify_instance.user_playlist_create.return_value = mock_playlist
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.create_playlist('Test Playlist', 'Test Description', 'private')
        
        mock_spotify_instance.user_playlist_create.assert_called_once_with(
            user='user123',
            name='Test Playlist',
            public=False,
            description='Test Description'
        )
        self.assertEqual(result, mock_playlist)

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_find_or_create_playlist_existing(self, mock_oauth, mock_spotify):
        """Test finding existing Spotify playlist"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        existing_playlist = {'id': 'existing_id', 'name': 'Test Playlist'}
        mock_playlists = [existing_playlist]
        mock_spotify_instance.current_user_playlists.return_value = {'items': mock_playlists}
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.find_or_create_playlist('Test Playlist')
        
        self.assertEqual(result, existing_playlist)

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_find_or_create_playlist_new(self, mock_oauth, mock_spotify):
        """Test creating new Spotify playlist when not found"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        # Mock empty playlists list
        mock_spotify_instance.current_user_playlists.return_value = {'items': []}
        
        # Mock user and new playlist creation
        mock_user = {'id': 'user123'}
        mock_spotify_instance.current_user.return_value = mock_user
        new_playlist = {'id': 'new_id', 'name': 'New Playlist'}
        mock_spotify_instance.user_playlist_create.return_value = new_playlist
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.find_or_create_playlist('New Playlist')
        
        mock_spotify_instance.user_playlist_create.assert_called_once_with(
            user='user123',
            name='New Playlist',
            public=True,
            description=None
        )
        self.assertEqual(result, new_playlist)

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_playlist_items(self, mock_oauth, mock_spotify):
        """Test getting playlist items from Spotify"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        # Mock playlist tracks response
        mock_tracks = {
            'items': [{'track': {'name': 'Song 1'}}, {'track': {'name': 'Song 2'}}],
            'next': None
        }
        mock_spotify_instance.playlist_tracks.return_value = mock_tracks
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.playlist_items('playlist123')
        
        self.assertEqual(result, mock_tracks['items'])
        mock_spotify_instance.playlist_tracks.assert_called_once_with('playlist123')

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_playlist_items_with_pagination(self, mock_oauth, mock_spotify):
        """Test getting playlist items with pagination"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        # Mock paginated response
        first_page = {
            'items': [{'track': {'name': 'Song 1'}}],
            'next': 'next_url'
        }
        second_page = {
            'items': [{'track': {'name': 'Song 2'}}],
            'next': None
        }
        
        mock_spotify_instance.playlist_tracks.return_value = first_page
        mock_spotify_instance.next.return_value = second_page
        
        spotify = Spotify()
        spotify.init_service()
        result = spotify.playlist_items('playlist123')
        
        # Expected result should be first page items + second page items
        expected_items = [{'track': {'name': 'Song 1'}}, {'track': {'name': 'Song 2'}}]
        self.assertEqual(result, expected_items)
        mock_spotify_instance.next.assert_called_once_with(first_page)

    @patch('spotify.spotipy.Spotify')
    @patch('spotify.SpotifyOAuth')
    def test_add_songs_to_playlist(self, mock_oauth, mock_spotify):
        """Test adding songs to Spotify playlist"""
        mock_oauth_instance = Mock()
        mock_oauth.return_value = mock_oauth_instance
        mock_spotify_instance = Mock()
        mock_spotify.return_value = mock_spotify_instance
        
        spotify = Spotify()
        spotify.init_service()
        
        song_ids = ['spotify:track:1', 'spotify:track:2']
        spotify.add_songs_to_playlist('playlist123', song_ids)
        
        mock_spotify_instance.playlist_add_items.assert_called_once_with('playlist123', song_ids)


if __name__ == '__main__':
    unittest.main() 