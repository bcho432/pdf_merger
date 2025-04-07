from flask import Flask, render_template, request, redirect, session, url_for
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import re
import ssl

app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

# Spotify API credentials from .env file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Set up Spotify OAuth
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
)

def get_token():
    token_info = sp_oauth.get_access_token(request.args.get("code"))
    if not token_info:
        return None
    # Check if the token has expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    return token_info

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/play", methods=["POST"])
def play():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("login"))

    combined_input = request.form.get("combined_input")
    
    # Use regex to split input into artist and song
    match = re.match(r"(.+) by (.+)", combined_input, re.IGNORECASE)
    if match:
        song_name, artist_name = match.groups()
    else:
        return "Invalid input format. Use 'Song Title by Artist Name'."

    sp = spotipy.Spotify(auth=token_info["access_token"])

    # Get list of active devices
    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
    else:
        return "No active device found. Please open Spotify on a device and try again."

    # Search for the track with a flexible query
    query = f"artist:{artist_name} track:{song_name}"
    results = sp.search(q=query, type="track", limit=10)
    tracks = results['tracks']['items']

    if tracks:
        # Sort tracks by popularity to ensure we get the most relevant track
        tracks_sorted = sorted(tracks, key=lambda x: x['popularity'], reverse=True)
        top_track = tracks_sorted[0]  # Get the top track based on popularity
        track_uri = top_track['uri']
        track_name = top_track['name']
        track_artist = top_track['artists'][0]['name']
        
        # Optional: Inform the user about the track that will be played
        print(f"Playing: {track_name} by {track_artist}")
        
        sp.start_playback(device_id=device_id, uris=[track_uri])  # Specify device_id
        
        # Redirect back to the home page after playing the song
        return redirect(url_for("index"))
    else:
        return "No tracks found. Please try a different search."

@app.route("/seek", methods=["POST"])
def seek():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("login"))

    seek_time = request.form.get("seek_time")
    if not seek_time:
        return "Seek time is required."

    # Parse the MM:SS or MM.SS format
    try:
        # Split the time into minutes and seconds using regex that matches either ":" or "."
        match = re.match(r'(\d+)[.:](\d+)', seek_time)
        if not match:
            raise ValueError("Invalid format")

        minutes, seconds = map(int, match.groups())
        # Convert total time to milliseconds
        seek_position = (minutes * 60 + seconds) * 1000
    except ValueError:
        return "Invalid time format. Use MM:SS or MM.SS."

    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    # Get list of active devices
    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
    else:
        return "No active device found. Please open Spotify on a device and try again."

    # Check current playback status
    playback = sp.current_playback()
    if playback is None or not playback.get('is_playing'):
        return "No track is currently playing."

    # Seek to the specified time
    try:
        sp.seek_track(position_ms=seek_position, device_id=device_id)
    except Exception as e:
        print(f"Error seeking track: {e}")
        return "Failed to seek track."

    # Redirect back to the home page after seeking
    return redirect(url_for("index"))

if __name__ == "__main__":
    context = ('192.168.12.90.pem', '192.168.12.90-key.pem')  # Paths to your certificate and key files
    app.run(debug=True, host='0.0.0.0', port=5002)