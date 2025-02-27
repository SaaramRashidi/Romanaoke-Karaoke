# Romanoake Project

## Description

The **Romanoake Project** is a Flask-based web application that integrates Spotify API, Genius API, Musixmatch, and Azure Cognitive Services to fetch and transliterate song lyrics in different scripts. The project includes a front-end interface for searching songs and displaying synchronized lyrics with real-time audio playback.

## Features

- Fetch song lyrics using Spotify and Genius API
- Transliterate lyrics into multiple scripts using Azure Cognitive Services
- Display real-time synchronized lyrics during playback
- Record audio snippets of lyrics in sync with playback
- Flask backend with API endpoints for lyric fetching, transliteration, and playback control
- Front-end interface built with HTML, JavaScript, and CSS

## Tech Stack

- **Backend**: Flask, Spotipy (Spotify API), LyricsGenius, Musixmatch API, Azure Cognitive Services
- **Frontend**: HTML, CSS, JavaScript
- **Other Libraries**:
  - `spotipy` (Spotify API)
  - `lyricsgenius` (Genius API)
  - `fuzzywuzzy` (Fuzzy string matching)
  - `numpy` (Data processing)
  - `requests` (HTTP requests)
  - `flask_cors` (CORS handling)
  - `dotenv` (Environment variable management)

## Installation

### Prerequisites

Ensure you have **Python 3.7+** and **pip** installed on your system.

### Setup Steps

1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd romanoake
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```sh
   CLIENT_ID=<your_spotify_client_id>
   CLIENT_SECRET=<your_spotify_client_secret>
   GENIUS_TOKEN=<your_genius_api_token>
   AZURE_KEY=<your_azure_key>
   MUSIXMATCH_KEY=<your_musixmatch_key>
   ```
4. Run the application:
   ```sh
   python app.py
   ```

## Usage

1. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```
2. Enter the song name and artist in the input field.
3. Click **Submit** to fetch lyrics.
4. If authorization is required, enter your Spotify authentication code.
5. Click **Play** to start synchronized lyric playback.

## API Endpoints

| Endpoint           | Method | Description                           |
| ------------------ | ------ | ------------------------------------- |
| `/`                | GET    | Serves the front-end page             |
| `/search_lyrics`   | POST   | Searches and retrieves song lyrics    |
| `/download_lyrics` | GET    | Downloads and processes lyrics        |
| `/playTrack`       | GET    | Starts playback of a track            |
| `/timestamp`       | GET    | Retrieves current playback timestamp  |
| `/send_auth`       | POST   | Sets the Spotify authentication token |
| `/audio_analysis`  | GET    | Analyzes audio features of a song     |

## Folder Structure

```
romanoake/
├── app.py             # Main Flask app
├── romanoaketest.py   # Backend logic for lyrics retrieval and API calls
├── flasktest.html     # Frontend interface
├── requirements.txt   # Dependencies
├── .env               # Environment variables (not included in repo)
```

## License

This project is open-source and available under the **MIT License**.

## Authors

Developed by **Saaram Rashidi** and **Adcharan Arivuchelvan**.

