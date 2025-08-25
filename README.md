# Playlist Creator

A Python tool that creates YouTube or Spotify playlists from a song list file. The tool searches for songs in your "master" playlists and adds matching tracks to a target playlist.

## Description

This project allows you to:
- Create YouTube or Spotify playlists from a text file of song names
- Search for songs in existing "master" playlists to find matches
- Use fuzzy string matching to handle variations in song titles
- Support both dry-run mode for testing and actual playlist creation

## Setup

### Prerequisites

- Python 3.x
- YouTube Data API v3 credentials (for YouTube functionality)
- Spotify API credentials (for Spotify functionality)

### Installation

#### Setting up Python Virtual Environment on Mac

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd playlist_creator
   ```

2. Create a Python virtual environment:
   ```bash
   # Using venv (recommended for Python 3.3+)
   python3 -m venv venv
   
   # Alternatively, using virtualenv if you have it installed
   virtualenv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
   
   Note: You'll need to activate this environment each time you work on the project. To deactivate, simply run `deactivate`.

4. Install the required dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

5. Verify the installation:
   ```bash
   python --version
   pip list
   ```

### Authentication Setup

#### YouTube Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (OAuth 2.0 client ID)
5. Download the credentials JSON file and save it as `credentials.json` in the project directory

#### Spotify Setup

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create app"
4. Fill in the app details:
   - App name: Choose any name (e.g., "YouTube Playlist Creator")
   - App description: Brief description of your app
   - Website: You can use `http://localhost` for personal use
   - Redirect URI: Add `http://localhost:8080/callback`
   - Check the boxes to agree to the terms
5. Click "Save"
6. On your app's page, click "Settings"
7. Copy your Client ID and Client Secret

Set the following environment variables in your terminal:
```bash
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

To make these environment variables persistent, add them to your shell profile file:
```bash
# For bash users
echo 'export SPOTIFY_CLIENT_ID="your_spotify_client_id"' >> ~/.bash_profile
echo 'export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"' >> ~/.bash_profile

# For zsh users (default on newer Macs)
echo 'export SPOTIFY_CLIENT_ID="your_spotify_client_id"' >> ~/.zshrc
echo 'export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"' >> ~/.zshrc
```

Then restart your terminal or run `source ~/.bash_profile` (or `source ~/.zshrc` for zsh).

### Song List File

Create a `song_list.txt` file with one song per line. Example:
```
Tainted Love
You Oughta Know
Authority Song
American Girl
```

## Usage

```bash
python create_playlist.py [options] <playlist_name>
```

### Available Flags and Parameters

#### Options
- `-d, --dry-run`: Perform a dry run without making any changes to playlists
- `-s, --spotify`: Use Spotify instead of YouTube (default is YouTube)
not empty

#### Parameters
- `playlist_name`: The name of the playlist to create or update (can contain spaces)

### Examples

```bash
# Create a YouTube playlist called "My Playlist"
python create_playlist.py My Playlist

# Dry run to test without making changes
python create_playlist.py -d Test Playlist

# Create a Spotify playlist
python create_playlist.py -s My Spotify Playlist

# Combine options
python create_playlist.py -s -d My Test Playlist
```

## How It Works

1. The script reads songs from `song_list.txt`
2. It searches your existing playlists for any with "master" in the name
3. Collects all songs from these master playlists
4. Uses fuzzy string matching to find the best matches for each song in your list
5. Creates or updates the target playlist with the matched songs
6. Reports any songs that couldn't be found

## File Structure

- `create_playlist.py` - Main script
- `youtube.py` - YouTube API wrapper class
- `spotify.py` - Spotify API wrapper class
- `song_list.txt` - Input file with song names
- `credentials.json` - YouTube API credentials (not included)
- `token.json` - Generated YouTube OAuth token (created automatically)

## Notes

- The tool requires existing "master" playlists containing your song library
- Song matching uses fuzzy string matching to handle title variations
- YouTube requires OAuth authentication on first run
- Spotify credentials must be set as environment variables
