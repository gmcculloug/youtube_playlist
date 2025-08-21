# Test Suite for YouTube Playlist Creator

This directory contains comprehensive tests for the YouTube Playlist Creator application, covering both YouTube and Spotify integration paths.

## Test Coverage

The test suite validates:

### Core Functionality (`create_playlist.py`)
- ✅ Song title cleanup and normalization
- ✅ Reading song lists from files
- ✅ Command-line argument parsing
- ✅ Service initialization (YouTube vs Spotify)
- ✅ Master playlist discovery and collection
- ✅ Song matching using fuzzy search
- ✅ Playlist creation and management
- ✅ Dry-run mode functionality
- ✅ Playlist reset functionality
- ✅ Main application flow

### YouTube Service (`youtube.py`)
- ✅ Service initialization and authentication
- ✅ Playlist name extraction
- ✅ Song name extraction
- ✅ Song ID extraction

### Spotify Service (`spotify.py`)
- ✅ Service initialization and authentication
- ✅ Playlist name extraction
- ✅ Song name extraction
- ✅ Song ID extraction

## Running the Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Basic Test Execution

Run all tests:
```bash
python run_tests.py
```

Run tests with verbose output:
```bash
python run_tests.py -v
```

Run tests with coverage report:
```bash
python run_tests.py -c
```

Run a specific test:
```bash
python run_tests.py -t "test_song_title_cleanup"
```

### Alternative Test Runners

Using unittest directly:
```bash
python -m unittest test_create_playlist.py -v
```

Using pytest (if installed):
```bash
pytest test_create_playlist.py -v
```

Using pytest with coverage:
```bash
pytest test_create_playlist.py --cov=create_playlist --cov=youtube --cov=spotify --cov-report=html
```

## Test Structure

### TestCreatePlaylist
Tests for the main application logic:
- `test_song_title_cleanup()` - Validates song title normalization
- `test_read_song_list_from_file()` - Tests file reading functionality
- `test_parse_args()` - Validates command-line argument parsing
- `test_initialize_service_youtube()` - Tests YouTube service initialization
- `test_initialize_service_spotify()` - Tests Spotify service initialization
- `test_find_master_playlists()` - Tests master playlist discovery
- `test_collect_playlist_items()` - Tests playlist item collection
- `test_find_matching_song()` - Tests fuzzy song matching
- `test_get_playlist_dry_run()` - Tests dry-run playlist handling
- `test_playlist_name_dry_run()` - Tests dry-run naming
- `test_reset_playlist_*()` - Tests playlist reset scenarios
- `test_update_playlist_*()` - Tests playlist update scenarios
- `test_main_function()` - Tests the main application flow

### TestYouTubeService
Tests for YouTube API integration:
- `test_init_service()` - Tests YouTube service initialization
- `test_playlist_name()` - Tests playlist name extraction
- `test_song_name()` - Tests song name extraction
- `test_song_id()` - Tests song ID extraction

### TestSpotifyService
Tests for Spotify API integration:
- `test_init_service()` - Tests Spotify service initialization
- `test_playlist_name()` - Tests playlist name extraction
- `test_song_name()` - Tests song name extraction
- `test_song_id()` - Tests song ID extraction

## Mocking Strategy

The tests use comprehensive mocking to avoid external API calls:

1. **External Services**: YouTube and Spotify API calls are mocked
2. **File System**: File operations use temporary directories
3. **User Input**: Interactive prompts are mocked
4. **Environment**: Environment variables and credentials are mocked

## Test Data

The tests use realistic but fictional data:
- Sample song lists with various formats
- Mock playlists with different naming patterns
- Test cases for edge cases (empty files, special characters, etc.)

## Coverage Goals

The test suite aims for:
- **Function Coverage**: All public functions tested
- **Branch Coverage**: All code paths exercised
- **Edge Case Coverage**: Error conditions and boundary cases
- **Integration Coverage**: Service interactions validated

## Continuous Integration

To integrate with CI/CD:
```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    python run_tests.py -c
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **Missing Dependencies**: Install requirements with `pip install -r requirements-test.txt`
3. **Permission Errors**: Make sure `run_tests.py` is executable (`chmod +x run_tests.py`)

### Debug Mode

For debugging specific tests, you can run individual test methods:
```bash
python -m unittest test_create_playlist.TestCreatePlaylist.test_song_title_cleanup -v
```

### Coverage Analysis

After running with coverage, view the HTML report:
```bash
open htmlcov/index.html  # macOS
# or
firefox htmlcov/index.html  # Linux
``` 