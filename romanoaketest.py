import spotipy
import os
import requests
import string
# from unidecode import unidecode
from flask import Flask, request, jsonify, send_from_directory, abort, send_file, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import logging
import re
import langid
from aksharamukha import transliterate
import requests
from dotenv import load_dotenv
import os
import requests, uuid, json
import langid
import lyricsgenius
from fuzzywuzzy import fuzz
from unidecode import unidecode
import numpy as np

load_dotenv()

genius = lyricsgenius.Genius(os.getenv("GENIUS_TOKEN"))

romanoake_bp = Blueprint('romanoake', __name__)
CORS(romanoake_bp)  # Enable CORS for all routes

scope = "user-read-playback-state,user-modify-playback-state"

key = os.getenv("AZURE_KEY")
musixmatch = os.getenv("MUSIXMATCH_KEY")
track_uri = ""
data = {}
lyrics_data = []
authorization_bearer = ""
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("CLIENT_ID"),
                                               client_secret=os.getenv("CLIENT_SECRET"),
                                               redirect_uri="http://localhost:1234",
                                               scope=scope))

language_scripts = [
    {"code": "ar", "name": "Arabic", "scripts": ["Arab", "Latn"]},
    {"code": "as", "name": "Assamese", "scripts": ["Beng", "Latn"]},
    {"code": "be", "name": "Belarusian", "scripts": ["Cyrl", "Latn"]},
    {"code": "bg", "name": "Bulgarian", "scripts": ["Cyrl", "Latn"]},
    {"code": "bn", "name": "Bangla", "scripts": ["Beng", "Latn"]},
    {"code": "brx", "name": "Bodo", "scripts": ["Deva", "Latn"]},
    {"code": "el", "name": "Greek", "scripts": ["Grek", "Latn"]},
    {"code": "fa", "name": "Persian", "scripts": ["Arab", "Latn"]},
    {"code": "gom", "name": "Konkani", "scripts": ["Deva", "Latn"]},
    {"code": "gu", "name": "Gujarati", "scripts": ["Gujr", "Latn"]},
    {"code": "he", "name": "Hebrew", "scripts": ["Hebr", "Latn"]},
    {"code": "hi", "name": "Hindi", "scripts": ["Deva", "Latn"]},
    {"code": "ja", "name": "Japanese", "scripts": ["Jpan", "Latn"]},
    {"code": "kk", "name": "Kazakh", "scripts": ["Cyrl", "Latn"]},
    {"code": "kn", "name": "Kannada", "scripts": ["Knda", "Latn"]},
    {"code": "ko", "name": "Korean", "scripts": ["Kore", "Latn"]},
    {"code": "ks", "name": "Kashmiri", "scripts": ["Arab", "Latn"]},
    {"code": "ky", "name": "Kyrgyz", "scripts": ["Cyrl", "Latn"]},
    {"code": "mai", "name": "Maithili", "scripts": ["Deva", "Latn"]},
    {"code": "mk", "name": "Macedonian", "scripts": ["Cyrl", "Latn"]},
    {"code": "ml", "name": "Malayalam", "scripts": ["Mlym", "Latn"]},
    {"code": "mn-Cyrl", "name": "Mongolian (Cyrillic)", "scripts": ["Cyrl", "Latn"]},
    {"code": "mni", "name": "Manipuri", "scripts": ["Mtei", "Latn"]},
    {"code": "mr", "name": "Marathi", "scripts": ["Deva", "Latn"]},
    {"code": "ne", "name": "Nepali", "scripts": ["Deva", "Latn"]},
    {"code": "or", "name": "Odia", "scripts": ["Orya", "Latn"]},
    {"code": "pa", "name": "Punjabi", "scripts": ["Guru", "Latn"]},
    {"code": "ru", "name": "Russian", "scripts": ["Cyrl", "Latn"]},
    {"code": "sa", "name": "Sanskrit", "scripts": ["Deva", "Latn"]},
    {"code": "sd", "name": "Sindhi", "scripts": ["Arab", "Latn"]},
    {"code": "si", "name": "Sinhala", "scripts": ["Sinh", "Latn"]},
    {"code": "sr-Cyrl", "name": "Serbian (Cyrillic)", "scripts": ["Cyrl"]},
    {"code": "sr-Latn", "name": "Serbian (Latin)", "scripts": ["Latn"]},
    {"code": "ta", "name": "Tamil", "scripts": ["Taml", "Latn"]},
    {"code": "te", "name": "Telugu", "scripts": ["Telu", "Latn"]},
    {"code": "tg", "name": "Tajik", "scripts": ["Cyrl", "Latn"]},
    {"code": "th", "name": "Thai", "scripts": ["Thai", "Latn"]},
    {"code": "tt", "name": "Tatar", "scripts": ["Cyrl", "Latn"]},
    {"code": "uk", "name": "Ukrainian", "scripts": ["Cyrl", "Latn"]},
    {"code": "ur", "name": "Urdu", "scripts": ["Arab", "Latn"]},
    {"code": "zh-Hans", "name": "Chinese Simplified", "scripts": ["Hans", "Latn", "Hant"]},
    {"code": "zh-Hant", "name": "Chinese Traditional", "scripts": ["Hant", "Latn", "Hans"]}
]

path = '/transliterate'
endpoint = "https://api.cognitive.microsofttranslator.com"
constructed_url = endpoint + path

logging.basicConfig(level=logging.DEBUG)


def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c if c in valid_chars else '_' for c in filename)


def parselyrics(artist_name, track_num, album_name, release_year, track_name):
    global genius, key, language_scripts, constructed_url, lyrics_data
    track_file = f"{track_num}. {track_name}"
    album_folder = f"{album_name} ({release_year})"
    folder = os.getcwd()
    file_path_lrc = f"{folder}/Lyrics/{artist_name}/{album_folder}/{track_file}.lrc"
    # "C:\Users\mirun\Downloads\romanoake2\romanoake2\Lyrics"
    try:
        folder_path = f'{folder}/Lyrics/{artist_name}/{album_folder}/{track_file}'
        file_name = f'{track_file}transliterated.json'
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            lyrics_data = json.load(file)
        return lyrics_data
    except:
        try:
            with open(file_path_lrc, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            final_list = []
            for line in lines:
                real_lines = line.split("[")
                del real_lines[0]
                for real_line in real_lines:
                    final_list.append("[" + real_line)
            artist = genius.search_artist(artist_name, max_songs=0)
            song = artist.song(track_name)
            if (song):
                genius_lyrics = song.lyrics
                genius_lines = genius_lyrics.split('\n')
                current_artist = None
                tagged_lyrics = []
                artist_pattern = re.compile(r'\[.*: (.+)\]')

                # Process each line
                for line in genius_lines:
                    artist_match = artist_pattern.search(line)
                    if artist_match:
                        current_artist = artist_match.group(1)
                    else:
                        if current_artist:
                            tagged_lyrics.append({'artist': current_artist, 'lyrics': line})
                        else:
                            tagged_lyrics.append({'artist': "none", 'lyrics': line})
                print(tagged_lyrics)
            else:
                genius_lyrics = None
            headers = {
                'Ocp-Apim-Subscription-Key': key,
                'Ocp-Apim-Subscription-Region': 'eastus',
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }

            for line in final_list:
                match = re.match(r'\[(\d+):(\d+\.\d+)\](.*)', line)
                if match:
                    minutes = int(match.group(1))
                    seconds = float(match.group(2))
                    timestamp = minutes * 60 * 1000 + int(seconds * 1000)
                    lyrics = match.group(3).strip()

                    words = lyrics.split()
                    scripts = []
                    i = 0
                    limit = len(words)
                    isMultipleScripts = False
                    while (i < limit):
                        script = transliterate.auto_detect(words[i])
                        scripts.append(script)
                        j = 0
                        while (j <= i):
                            currentscript = scripts[j]
                            if (currentscript != script and script != "HK" and (
                                    currentscript != "Hiragana" and currentscript != "Katakana" and currentscript != "Hani") and (
                                    script != "Hiragana" and currentscript != "Katakana" and script != "Hani")):
                                isMultipleScripts = True
                            j += 1
                        i += 1
                    if (isMultipleScripts):
                        j = 0
                        transliterate_phrases = []
                        while (j < limit):
                            vocalist = None
                            lang, confidence = langid.classify(words[j])
                            for language in language_scripts:
                                code = language['code']
                                if (code == lang):
                                    script = language['scripts'][0]
                                    lang_param = language['name']
                                    break
                            if (lang != "en"):
                                params = {
                                    'api-version': '3.0',
                                    'language': lang,
                                    'fromScript': script,
                                    'toScript': 'Latn'
                                }
                                body = [{"text": words[j]}]
                                try:
                                    request = requests.post(constructed_url, params=params, headers=headers, json=body)
                                    response = request.json()
                                    params = {
                                        'api-version': '3.0',
                                        'language': lang,
                                        'fromScript': "Latn",
                                        'toScript': script
                                    }
                                    transliterate_phrases.append(response[0]["text"])
                                except:
                                    text = transliterate.process("autodetect", "HK", words[j])
                                    transliterate_phrases.append(text)
                            else:
                                transliterate_phrases.append(words[j])
                            j += 1
                        lyrics = ' '.join(transliterate_phrases)
                    else:
                        lang, confidence = langid.classify(lyrics)
                        for language in language_scripts:
                            code = language['code']
                            if (code == lang):
                                script = language['scripts'][0]
                                lang_param = language['name']
                                break
                        transliterated_lyrics = ""
                        if (lang != "en"):
                            params = {
                                'api-version': '3.0',
                                'language': lang,
                                'fromScript': script,
                                'toScript': 'Latn'
                            }
                            body = [{"text": lyrics}]
                            try:
                                request = requests.post(constructed_url, params=params, headers=headers, json=body)
                                response = request.json()
                                params = {
                                    'api-version': '3.0',
                                    'language': lang,
                                    'fromScript': "Latn",
                                    'toScript': script
                                }
                                lyrics = response[0]["text"]
                            except:
                                try:
                                    text = transliterate.process("autodetect", "HK", lyrics)
                                    lyrics = text
                                except:
                                    text = unidecode(lyrics)
                                    lyrics = text
                best_match = None
                highest_ratio = 0
                vocalist = artist_name
                if (genius_lyrics):
                    j = 0
                    index = 0
                    for lyrics2 in tagged_lyrics:
                        ratio = fuzz.ratio(lyrics2["lyrics"], lyrics)
                        if ratio > highest_ratio:
                            highest_ratio = ratio
                            if (lyrics2['artist'] != 'none'):
                                vocalist = lyrics2["artist"]

                lyrics_data.append({'timestamp': timestamp, 'lyrics': lyrics, 'artist': vocalist})
            folder = os.getcwd()
            folder_path = f'{folder}/Lyrics/{artist_name}/{album_folder}/{track_file}'
            file_name = f'{track_file}transliterated.json'
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, 'w') as file:
                json.dump(lyrics_data, file)
        except FileNotFoundError:
            logging.error(f"Lyrics file not found: {file_path}")

    return lyrics_data


@romanoake_bp.route('/')
def index():
    return send_from_directory('.', 'flasktest.html')


@romanoake_bp.route('/audio_analysis', methods=['GET'])
def audio_analysis():
    global lyrics_data, data
    track_analysis = []
    for i in range(len(lyrics_data)):  # Loop until the second last entry
        current_line = lyrics_data[i]
        if i == len(lyrics_data) - 1:
            next_line = None
            timestamp_end = data['duration_ms']
        else:
            next_line = lyrics_data[i + 1]
            timestamp_end = next_line['timestamp']
        timestamp_start = current_line['timestamp']

        # Add duration to the current line (if needed)
        tid = data['uri']
        analysis = sp.audio_analysis(tid)

        segments = analysis.get('segments')

        analysis_dict = {}

        print(segments)
        for j, segment in enumerate(segments):
            if (segment['start'] > (timestamp_start / 1000)) and (
                    (segment['duration'] + segment['start']) < (timestamp_end / 1000)) and (
                    segment['confidence'] > 0.5):
                # Add segment to the dictionary with a unique key
                analysis_dict[f"segment_{j}"] = segment
            print(type(segment))
        print(analysis_dict)
        temp_analysis = {}
        timbre_groupings = {}
        group_number = 1

        while (analysis_dict):
            temp_analysis = {}
            for segment_key, segment_value in analysis_dict.items():
                first_key = next(iter(analysis_dict))
                first_value = analysis_dict[first_key]
                # Retrieve the timbre arrays from the current segment and the first segment
                timbre1 = np.array(analysis_dict.get(segment_key, {}).get('timbre'))
                timbre2 = np.array(first_value['timbre'])
                # Check that both timbre arrays are not None before calculating cosine similarity
                if timbre1 is not None and timbre2 is not None:
                    # Calculate cosine similarity
                    cosine_similarity = np.dot(timbre1, timbre2) / (np.linalg.norm(timbre1) * np.linalg.norm(timbre2))
                    # Now you can compare the cosine similarity
                    if cosine_similarity > 0.5:
                        # Add the segment to temp_analysis using its key
                        temp_analysis[segment_key] = segment_value
                else:
                    print(f"Timbre data is missing for key {segment_key}")
            if len(temp_analysis) == 1:
                single_key = next(iter(temp_analysis))
                timbre_groupings[f'group_{group_number}'] = {single_key: temp_analysis[single_key]}
                group_number += 1
                del analysis_dict[single_key]
                continue

            while (temp_analysis):
                # Take the first entry in the temporary dictionary as the reference
                reference_key, reference_segment = next(iter(temp_analysis.items()))
                reference_timbre = np.array(reference_segment['timbre'])
                # Initialize the current group with the reference
                current_group = {reference_key: reference_segment}

                # List to hold keys of timbres that will be grouped together
                keys_to_remove = [reference_key]  # Include the reference key itself

                for key, segment in temp_analysis.items():
                    if key == reference_key:
                        continue  # Skip the reference segment

                    timbre_vector = np.array(segment['timbre'])
                    cosine_similarity = np.dot(reference_timbre, timbre_vector) / (
                                np.linalg.norm(reference_timbre) * np.linalg.norm(timbre_vector))

                    if cosine_similarity >= 0.75:
                        # Add this timbre to the current group
                        current_group[key] = segment
                        keys_to_remove.append(key)

                if (len(temp_analysis) >= (len(timbre_groupings) - 1)):
                    timbre_groupings[f'group_{group_number}'] = current_group

                # Remove grouped timbres from temp_analysis
                for key in keys_to_remove:
                    del temp_analysis[key]

                if len(current_group) == 1:
                    print(f"No similar timbres found for {reference_key}, keeping in analysis_dict")
                else:
                    # Store the current group in timbre_groupings
                    for key in keys_to_remove:
                        del analysis_dict[key]
                    timbre_groupings[f'group_{group_number}'] = current_group
                    group_number += 1
                prev_segment = segment

        limit = len(timbre_groupings)
        i = 1
        keys_to_remove = []
        while (i <= limit):
            group = timbre_groupings[f"group_{i}"]
            isSinger = True
            isSingerFaultCounter = 0
            for key, segment in group.items():
                pitches = segment['pitches']
                max_pitch = max(pitches)  # Highest pitch value
                sum_of_others = sum(pitches) - max_pitch  # Sum of all other pitch values\
                peak_ratio = max_pitch / sum_of_others
                pitches = np.array(segment['pitches'])
                std_dev = np.std(pitches)
                if (std_dev < 0.2):
                    isSingerFaultCounter += 1
                if (peak_ratio < 0.65):
                    isSingerFaultCounter += 1
            if (isSingerFaultCounter > 3):
                isSinger = False
            if (isSinger == False):
                keys_to_remove.append(f"group_{i}")
            i += 1

        for keys in keys_to_remove:
            del timbre_groupings[keys]
        print(timbre_groupings)
        track_analysis.append(
            {'timestamp': timestamp_start, 'lyrics': current_line['lyrics'], 'analysis': timbre_groupings,
             'artist': current_line['artist']})
    print(track_analysis)
    return track_analysis


@romanoake_bp.route('/search_lyrics', methods=['POST'])
def search_lyrics():
    global data, track_uri
    logging.debug("Received request: %s", request.json)
    response = request.json
    song = response.get('song')

    if not song:
        return jsonify({'error': 'No song provided'}), 400

    result = sp.search(song, limit=1)
    logging.debug("Spotify search result: %s", result)

    if not result['tracks']['items']:
        return jsonify({'error': 'No track found'}), 404

    track_info = result['tracks']['items'][0]
    data = track_info
    track_uri = track_info['uri']
    song_name = track_info['name']
    album_info = track_info['album']

    artist_info = result['tracks']['items'][0]['album']['artists'][0]['name']
    print(artist_info)
    album_name = sanitize_filename(album_info['name'])
    track_number = track_info['track_number']
    release_date = album_info['release_date'].replace('-', '/')
    release_year = release_date[:4]

    lyrics = parselyrics(artist_info, track_number, album_name, release_year, song_name)

    if not lyrics:
        return jsonify({'no_lyrics': True})

    logging.debug("Lyrics: %s", lyrics)
    return jsonify({'song_lyrics': lyrics})


@romanoake_bp.route('/timestamp', methods=['GET'])
def timestamp():
    global sp, data
    progress = sp.current_playback()
    if progress and 'progress_ms' in progress:
        progress_ms = progress['progress_ms']
        duration_ms = data['duration_ms']
        logging.debug(f"Current playback progress: {progress_ms}")
        return jsonify({'timestamp': progress_ms, 'duration': duration_ms})
    else:
        return jsonify({'error': 'No playback information available'}), 404


@romanoake_bp.route('/send_auth', methods=['POST'])
def set_auth():
    global data, authorization_bearer
    logging.debug("Received request: %s", request.json)
    response = request.json
    auth = response.get('auth')
    authorization_bearer = auth
    if not auth:
        return jsonify({'error': 'No authorization code provided'}), 400
    if authorization_bearer != "":
        print(authorization_bearer)
    return jsonify({'success': 'authorization bearer set'})


@romanoake_bp.route('/download_lyrics', methods=['GET'])
def download_lyrics():
    global data, sp, track_uri, authorization_bearer

    def process_lyrics(authorization):
        global authorization_bearer
        import os, re, sys, spotipy, itertools, json, requests, base64, linecache, bs4, time, pyperclip, pprint, \
            datetime, shutil, platform, subprocess
        import spotipy.util as util
        import requests
        import logging
        import string
        from spotipy import oauth2
        import spotipy
        from spotipy import client
        from os import path
        from spotipy.oauth2 import SpotifyOAuth
        from bs4 import BeautifulSoup
        from pathlib import Path  # using this module to solve difference path syntax between Mac OS and Windows
        from dotenv import load_dotenv

        load_dotenv()

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("CLIENT_ID"),
                                                       client_secret=os.getenv("CLIENT_SECRET"),
                                                       redirect_uri="http://localhost:1234"))
        # MAKE SURE THESE ARE CORRECT
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        REDIRECT_URI = 'http://localhost:1234'

        print(authorization)

        os.environ['SPOTIPY_CLIENT_ID'] = CLIENT_ID
        os.environ['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET
        os.environ['SPOTIPY_REDIRECT_URI'] = REDIRECT_URI
        scope = "user-read-currently-playing"
        # spotipy authentication to see currently playing song
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        current_track = sp.current_user_playing_track()

        def replace_line(database, line_num, text):
            lines = open(database, 'r').readlines()
            lines[line_num] = text
            out = open(database, 'w')
            out.writelines(lines)
            out.close()

        # for opening folder in various operating system explorers
        def open_file(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

        def sanitize_filename(filename):
            # Replace invalid characters with underscores
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
            return ''.join(c if c in valid_chars else '_' for c in filename)

        # see if song is playing
        if current_track == None:
            print("No song detected, make sure you're actively playing a song!")
            os._exit(0)
        '''
        song_uri_link = current_track.get("uri").replace('spotify:track:','')
        song_name = sanitize_filename(current_track.get("name"))
        cover_link = current_track.get("album").get("images")[0].get("url")
        release_date = current_track.get("album").get("release_date")
        album_name = sanitize_filename(current_track.get("album").get("name"))
        artist_name = sanitize_filename(current_track.get("album").get("artists")[0].get("name"))
        track_number = current_track.get("track_number")
        album_uri_link = current_track.get("album").get("uri")
        '''

        song_uri_link = current_track.get("item").get("uri").replace('spotify:track:', '')
        song_name = sanitize_filename(current_track.get("item").get("name"))
        cover_link = current_track.get("item").get("album").get("images")[0].get("url")
        release_date = current_track.get("item").get("album").get("release_date")
        album_name = current_track.get("item").get("album").get("name")
        artist_name = current_track.get("item").get("album").get("artists")[0].get("name")
        track_number = current_track.get("item").get("track_number")
        album_uri_link = current_track.get("item").get("album").get("uri")

        # generate lyrics link
        original_link = cover_link
        a = cover_link
        a = a.replace("/", "%2F")
        a = a.replace(":", "%3A")
        cover_link = a
        link_start = "https://spclient.wg.spotify.com/color-lyrics/v2/track/"
        lyrics_url = (
                    link_start + song_uri_link + "/image/" + cover_link + "?format=json&vocalRemoval=false&market=from_token")
        lyrics_url_no_access = (link_start + song_uri_link + "/image/" + cover_link)

        print("Success! Song detected! \n")
        print("Song: ", song_name)
        print("Album name:", album_name)
        print("Artist name:", artist_name)
        print("Track number: ", track_number)
        print("Release date: ", release_date)
        print("Album cover URL:", original_link)
        print("Track URI:", song_uri_link)
        print("Album URI:", album_uri_link)
        print("Lyric URL:", lyrics_url, "\n")

        # getting release year for album
        release_date = release_date.replace('-', '/')
        release_year = release_date[:4]

        # creates directory
        artist = artist_name
        album = (album_name + " (" + release_year + ")")
        song = song_name
        song = sanitize_filename(song)
        track_number = track_number
        lyrics = "Lyrics"
        host_dir = os.getcwd()
        # print("Host Directory: \n" + host_dir)

        album_info = sp.album_tracks(album_uri_link)

        # saves currently playing album info to txt file
        result = json.dumps(album_info)
        z = open("album_info.txt", "w")
        z.write(result)
        z.close()
        album_database = "album_info.txt"
        with open('album_info.txt', 'r') as handle:
            parsed = json.load(handle)
            parsed2 = (json.dumps(parsed, indent=1, sort_keys=True))
        with open('album_info.txt', 'w') as file:  # line breaks
            file.write(parsed2)
            file.close()

        # reading for short line removal
        with open('album_info.txt', 'r') as f:
            lines = f.readlines()
        # Removes region codes by removing all short lines
        filtered_lines = [line for line in lines if len(line) > 10]
        # writing out file w no 2-character country codes
        with open('filtered_album_info.txt', 'w') as f:
            for line in filtered_lines:
                f.write(line)
        os.remove("album_info.txt")
        os.rename('filtered_album_info.txt', "album_info.txt")
        # if needed, commewnt below line out for album_info saved to txt
        os.remove("album_info.txt")

        # creates lyrics folder
        lyrics = sanitize_filename(lyrics)
        if os.path.isdir(lyrics):
            os.chdir(lyrics)
            lyricdir = os.getcwd()
        else:
            os.mkdir(lyrics)
            os.chdir(lyrics)

        artist = sanitize_filename(artist)
        # creates artist folder
        if os.path.isdir(artist):
            os.chdir(artist)
            artistdir = os.getcwd()
        else:
            os.mkdir(artist)
            os.chdir(artist)
            artistdir = os.getcwd()

        album = sanitize_filename(album)
        # creates album folder
        if os.path.isdir(album):
            os.chdir(album)
            albumdir = os.getcwd()
        else:
            os.mkdir(album)
            os.chdir(album)
            albumdir = os.getcwd()

        os.chdir(host_dir)

        # set up variables for moving lyric and setting up cover.jpg location
        host_folder = host_dir
        lyrics = "Lyrics"
        artist_name = artist_name
        albumdir = albumdir
        song = song
        cover = lyrics_url
        originallyricsfile = (Path(host_folder) / "output.lrc")
        movedlyricsfile = (Path(albumdir) / (str(track_number) + ". " + str(song) + ".lrc"))
        movedcoverjpg = (Path(albumdir) / "cover.jpg")

        # checks if cover exists, if not it downloads
        os.chdir(albumdir)
        try:
            f = open(movedcoverjpg)
            print("Cover already downloaded, skipping download.")
            f.close()
        except IOError:
            print("No cover.jpg detected, downloading now")
            cover = requests.get(original_link).content
            f = open(movedcoverjpg, 'wb')
            f.write(cover)
            f.close()
            print("Cover downloaded!")

        os.chdir(host_dir)
        # checks if lyric exists, if not it downloads
        try:
            f = open(movedlyricsfile)
            print("Lyric already downloaded, skipping download. Enjoy!")
            f.close()
            open_file(albumdir)
            os.remove("currentsong.txt")
            quit()

        except IOError:
            print("No lyric detected, downloading now")

        headers = {
            'Host': 'spclient.wg.spotify.com',
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'accept-language': 'en',
            'sec-ch-ua-mobile': '?0',
            'app-platform': 'WebPlayer',
            'authorization': authorization,
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'accept': 'application/json',
            'spotify-app-version': '1.1.98.597.g7f2ab0d4',
            'sec-ch-ua-platform': '"macOS"',
            'origin': 'https://open.spotify.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://open.spotify.com/',
        }
        params = {
            'format': 'json',
            'vocalRemoval': 'false',
            'market': 'from_token',
        }
        response = requests.get(lyrics_url, params=params, headers=headers)
        response.encoding = 'utf-8'
        lyricdata = response.text
        # print(lyricdata)
        z = open("lyrics.txt", "w", encoding="utf-8")
        z.write(lyricdata)
        z.close()
        print("Successfully saved page text, will verify...")

        # coding:utf-8
        import os, re, sys, itertools, json, requests, base64, linecache, time, requests, bs4, time, pyperclip, pprint, \
            shutil, platform, subprocess
        import string
        from pathlib import Path  # using this module to solve difference path syntax between Mac OS and Windows

        host_folder = host_dir  # get work path
        os.chdir(host_folder)  # change path to work path
        lyrics_url = lyrics_url

        # Read in the jumbled Spotify lyric text
        with open('lyrics.txt', 'r', encoding='UTF-8') as file:
            filedata = file.read()
            fullstring = filedata
        substring_403 = "HTTP ERROR 403"
        substring_401 = '"status": 401,'
        substring_success = "lyrics"

        print("Searching for valid lyrics...")
        # exception for songs with no lyrics
        if substring_403 in fullstring:
            os.remove("lyrics.txt")
            print("Lyrics not available for this song, sorry!")
            if len(os.listdir(albumdir)) == 0:  # Check if the album folder is empty
                shutil.rmtree(albumdir)  # If so, delete it
                if len(os.listdir(artistdir)) == 0:  # Check if the artist folder is empty
                    shutil.rmtree(artistdir)  # If so, delete it
                    quit()
        # exception with no token, just redownloads it based on lyrics_url
        elif substring_401 in fullstring:
            print("Error, token has been expired, please open the browser to get a new one and restart the program")
            os._exit(0)

        # exception for successful lyric grab
        elif substring_success in fullstring:
            print("Lyric grab was success, converting now...")
            with open('lyrics.txt', 'r', encoding='utf-8') as file:
                filedata = file.read()
                fullstring = filedata

        # Remove some of the Spotify formatting
        filedata = filedata.replace('},', '} \n')
        filedata = filedata.replace('{"lyrics":{"syncType":"LINE_SYNCED","lines":[', '')
        filedata = filedata.replace('\\u0027', '\'')
        filedata = filedata.replace('{"startTimeMs":"', '[')
        filedata = filedata.replace(',"syllables":[]} ', '')
        filedata = filedata.replace('","words":', ']')
        filedata = filedata.replace('"', '')
        filedata = filedata.replace('hasVocalRemoval:false}', '')
        filedata = filedata.replace(']', '] ')
        filedata = filedata.replace('\\', '*')
        filedata = filedata.replace(',syllables:[] ,endTimeMs:0}', '')

        # Write the file out
        with open('lyricsfixed.lrc', 'w', encoding='utf-8') as file:
            file.write(filedata)

        # remove leftover shit from Spotify that doesnt apply to lrc files
        with open("lyricsfixed.lrc", "r", encoding='utf-8') as f:
            lines = f.readlines()
        with open("lyricsfixed.lrc", "w", encoding='utf-8') as new_f:
            for line in lines:
                if not line.startswith("colors:{background"):
                    new_f.write(line)

        # removes last line of gibberish
        import os, sys, re
        readFile = open("lyricsfixed.lrc", encoding='utf-8')
        lines = readFile.readlines()
        readFile.close()
        w = open("lyricsfixed.lrc", 'w', encoding='utf-8')
        w.writelines([item for item in lines[:-1]])
        w.close()

        with open('lyricsfixed.lrc', 'r', encoding='utf-8') as file:
            filedata = file.read()
        # I keep initializing it the same way and just reassigning the filedata string because i am idiot brain (stop doing this!)
        test_str = filedata

        # Extracts all regions in ms into a string
        # Using regex which i do not get at all
        res = re.findall(r"\[\s*\+?(-?\d+)\s*\]", test_str)
        # saving timings to timings.txt
        file = open("timings.txt", "w", encoding='utf-8')

        formatted_times = []  # timing conversion
        for time in res:
            millis = int((int(time) % 1000) / 10)
            secs = int(int(time) / 1000)
            mins = int(secs / 60)
            secs = secs % 60
            formatted_times.append(f"{mins}:{secs}.{millis}")

        text = '] \n'.join(formatted_times)  # line breaks
        file.write(text)
        file.close()

        # Read in the file
        with open('timings.txt', 'r', encoding='utf-8') as file:
            filedata = file.read()

        # Bad logic to add brackets and keep timing scheme consistent because im dumb
        filedata = filedata.replace('0:', '[00:')
        filedata = filedata.replace('1:', '[01:')
        filedata = filedata.replace('2:', '[02:')
        filedata = filedata.replace('3:', '[03:')
        filedata = filedata.replace('4:', '[04:')
        filedata = filedata.replace('5:', '[05:')
        filedata = filedata.replace('6:', '[06:')
        filedata = filedata.replace('7:', '[07:')
        filedata = filedata.replace('8:', '[08:')
        filedata = filedata.replace('9:', '[09:')
        filedata = filedata.replace(':0.', ':00.')
        filedata = filedata.replace(':1.', ':01.')
        filedata = filedata.replace(':2.', ':02.')
        filedata = filedata.replace(':3.', ':03.')
        filedata = filedata.replace(':4.', ':04.')
        filedata = filedata.replace(':5.', ':05.')
        filedata = filedata.replace(':6.', ':06.')
        filedata = filedata.replace(':7.', ':07.')
        filedata = filedata.replace(':8.', ':08.')
        filedata = filedata.replace(':9.', ':09.')
        filedata = filedata.replace('.9]', '.90]')
        filedata = filedata.replace('.8]', '.80]')
        filedata = filedata.replace('.7]', '.70]')
        filedata = filedata.replace('.6]', '.60]')
        filedata = filedata.replace('.5]', '.50]')
        filedata = filedata.replace('.4]', '.40]')
        filedata = filedata.replace('.3]', '.30]')
        filedata = filedata.replace('.2]', '.20]')
        filedata = filedata.replace('.1]', '.10]')
        filedata = filedata.replace('.0]', '.00]')
        with open('timingsfixed.txt', 'w', encoding='utf-8') as file:
            file.write(filedata)

        with open('timingsfixed.txt', 'r', encoding='utf-8') as file:
            filedata = file.read()
        filedata = filedata.replace('1 ', '1]')
        filedata = filedata.replace('2 ', '2]')
        filedata = filedata.replace('3 ', '3]')
        filedata = filedata.replace('4 ', '4]')
        filedata = filedata.replace('5 ', '5]')
        filedata = filedata.replace('6 ', '6]')
        filedata = filedata.replace('7 ', '7]')
        filedata = filedata.replace('8 ', '8')
        filedata = filedata.replace('9 ', '9]')

        # bad file editing to catch the last bracket not applying
        s1 = filedata
        s2 = "]"
        filedatawithlastbracket = (s1 + s2)

        with open('timingsfixed.txt', 'w', encoding='utf-8') as file:
            file.write(filedatawithlastbracket)

        os.remove("timings.txt")
        os.rename('timingsfixed.txt', 'timingsfixed.lrc')

        with open('lyricsfixed.lrc', 'r', encoding='utf-8') as file:
            filedata = file.read()
        # doing what i did earlier, very janky and very backwards, to extract whats *not* in the brackets to get the words to apply the new times to
        test_str = filedata
        a_string = test_str
        modified_string = re.sub(r"\[\s*\+?(-?\d+)\s*\]", "",
                                 a_string)  # just the words from the song, prints without timecodes
        # print(modified_string)

        with open('lyricstimingsremoved.txt', 'w', encoding='utf-8') as file:
            file.write(modified_string)

        from itertools import zip_longest
        with open('timingsfixed.lrc', 'r', encoding='utf-8') as file:
            filedata = file.read()
        with open('lyricstimingsremoved.txt', 'r', encoding='utf-8') as file1:
            test_str = file1.read()
        # combines new timing and lyric files, A/B/A/B style, no AA/BB
        with open('timingsfixed.lrc', 'r', encoding='utf-8') as src1, open('lyricstimingsremoved.txt', 'r',
                                                                           encoding='utf-8') as src2, open('output.lrc',
                                                                                                           'w',
                                                                                                           encoding='utf-8') as dst:
            for line_from_first, line_from_second in itertools.zip_longest(src1, src2):
                if line_from_first is not None:
                    dst.write(line_from_first)
                if line_from_second is not None:
                    dst.write(line_from_second)

        with open('output.lrc', 'r', encoding='utf-8') as file:
            filedata = file.read()
        filedata = filedata.replace('   ', '')
        with open('output.lrc', 'w', encoding='utf-8') as file:
            file.write(filedata)
        # combines into one line where line breaks can be added
        with open('output.lrc', encoding='utf-8') as f:
            all_lines = f.readlines()
            all_lines = [x.strip() for x in all_lines if x.strip()]
            two_lines = " ".join(x for x in all_lines[:2])
            lines_left = " ".join(x for x in all_lines[2:])

        oneline = (two_lines + lines_left)
        # everything put into one line, needed for line breaks

        # Breaks multiple lines colliding making LRC file unreadable
        oneline = oneline.replace(' [', '\n[')
        oneline = oneline.replace('\\', '')
        oneline = oneline.replace(')[', ')\n[')
        oneline = oneline.replace('.[', '.\n[')
        oneline = oneline.replace('![', '!\n[')
        oneline = oneline.replace('?[', '?\n[')
        oneline = oneline.replace('a[', 'a\n[')
        oneline = oneline.replace('b[', 'b\n[')
        oneline = oneline.replace('c[', 'c\n[')
        oneline = oneline.replace('d[', 'd\n[')
        oneline = oneline.replace('e[', 'e\n[')
        oneline = oneline.replace('f[', 'f\n[')
        oneline = oneline.replace('g[', 'g\n[')
        oneline = oneline.replace('h[', 'h\n[')
        oneline = oneline.replace('i[', 'i\n[')
        oneline = oneline.replace('j[', 'j\n[')
        oneline = oneline.replace('k[', 'k\n[')
        oneline = oneline.replace('l[', 'l\n[')
        oneline = oneline.replace('m[', 'm\n[')
        oneline = oneline.replace('n[', 'n\n[')
        oneline = oneline.replace('o[', 'o\n[')
        oneline = oneline.replace('p[', 'p\n[')
        oneline = oneline.replace('q[', 'q\n[')
        oneline = oneline.replace('r[', 'r\n[')
        oneline = oneline.replace('s[', 's\n[')
        oneline = oneline.replace('t[', 't\n[')
        oneline = oneline.replace('u[', 'u\n[')
        oneline = oneline.replace('v[', 'v\n[')
        oneline = oneline.replace('w[', 'w\n[')
        oneline = oneline.replace('x[', 'x\n[')
        oneline = oneline.replace('y[', 'y\n[')
        oneline = oneline.replace('z[', 'z\n[')
        oneline = oneline.replace('[00:00.00] {lyrics:{syncType:UNSYNCED,lines:[ ', '')
        oneline = oneline.replace('[00:00.00] ', '')
        oneline = oneline.replace('[00:00.0] ', '')
        oneline = oneline.replace('.9]', '.90]')
        oneline = oneline.replace('.8]', '.80]')
        oneline = oneline.replace('.7]', '.70]')
        oneline = oneline.replace('.6]', '.60]')
        oneline = oneline.replace('.5]', '.50]')
        oneline = oneline.replace('.4]', '.40]')
        oneline = oneline.replace('.3]', '.30]')
        oneline = oneline.replace('.2]', '.20]')
        oneline = oneline.replace('.1]', '.10]')
        oneline = oneline.replace('.0]', '.00]')

        # writing final lines
        with open('output.lrc', 'w', encoding='utf-8') as file:
            file.write(oneline)
            print("Conversion complete!")

        # remove leftover files
        os.remove("lyricsfixed.lrc")
        os.remove("lyricstimingsremoved.txt")
        os.remove("timingsfixed.lrc")
        os.remove("lyrics.txt")

        # set up variables for moving lyric and setting up cover.jpg location
        host_folder = host_dir
        lyrics = "Lyrics"
        artist_name = artist_name
        albumdir = albumdir
        song = song_name
        cover = lyrics_url
        originallyricsfile = (Path(host_folder) / "output.lrc")
        movedlyricsfile = (Path(albumdir) / (str(track_number) + ". " + str(song) + ".lrc"))
        movedcoverjpg = (Path(albumdir) / "cover.jpg")

        # prints folder where lyric went
        print("\n")
        print("Moved lyric to:")
        print(movedlyricsfile, "\n")
        newPath = shutil.move(originallyricsfile, movedlyricsfile)
        '''
        def open_file(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

        open_file(albumdir)
        '''

    res = sp.devices()
    devices = res['devices']
    sp.volume(0)
    logging.debug("Active devices: %s", devices)
    if devices:
        sp.start_playback(uris=[track_uri])
    else:
        return jsonify({'error': 'No active devices found'}), 404
    try:
        process_lyrics(authorization_bearer)
    except:
        return jsonify({'error': 'Lyrics not downloaded'}), 404
    return jsonify({'success': 'Lyrics Downloaded'})


@romanoake_bp.route('/playTrack', methods=['GET'])
def play():
    global track_uri, sp
    res = sp.devices()
    devices = res['devices']
    sp.volume(100)
    logging.debug("Active devices: %s", devices)
    if devices:
        sp.start_playback(uris=[track_uri])
        return jsonify({'success': 'Playback started'})
    else:
        return jsonify({'error': 'No active devices found'}), 404


