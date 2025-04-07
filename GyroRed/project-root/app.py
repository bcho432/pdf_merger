from flask import Flask, render_template, request
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import urllib.request
import urllib.parse
import json
import base64

app = Flask(__name__)
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request) as response:
        result = json.load(response)
        return result["access_token"]

def search_for_artist(artist_name):
    token = get_token()
    
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    request = urllib.request.Request(full_url, headers=headers)
    
    with urllib.request.urlopen(request) as response:
        result = json.load(response)
        artists = result.get("artists", {}).get("items", [])
        if artists:
            return artists[0]
        else:
            return None

def get_top_tracks(artist_id):
    token = get_token()
    
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"market": "US"}
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    request = urllib.request.Request(full_url, headers=headers)
    
    with urllib.request.urlopen(request) as response:
        result = json.load(response)
        return result.get("tracks", [])

def calculate_average_popularity(tracks, num_tracks=3):
    if not tracks:
        return 0
    limited_tracks = tracks[:num_tracks]
    total_popularity = sum(track.get("popularity", 0) for track in limited_tracks)
    return total_popularity / len(limited_tracks)

def get_popularity_message(average_popularity):
    if average_popularity >= 80:
        return "One of the most famous artists right now"
    elif average_popularity >= 60:
        return "Famous artist/group"
    elif average_popularity > 40:
        return "Average in popularity"
    elif average_popularity > 20:
        return "Below average in popularity"
    else:
        return "Underground artist"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["artist_name"]
        if user_input.lower() == "top 10 tracks":
            results = sp.playlist_tracks('37i9dQZEVXbMDoHDwVN2tF', limit=10)
            tracks = results['items']
            return render_template("top_tracks.html", tracks=tracks)
        else:
            artist = search_for_artist(user_input)
            if artist:
                artist_id = artist.get("id")
                artist_name = artist.get("name")
                artist_followers = artist.get("followers", {}).get("total", "N/A")
                top_tracks = get_top_tracks(artist_id)
                average_popularity = calculate_average_popularity(top_tracks, num_tracks=3)
                popularity_message = get_popularity_message(average_popularity)
                return render_template("artist.html", artist_name=artist_name, artist_followers=artist_followers, top_tracks=top_tracks, popularity_message=popularity_message)
            else:
                return render_template("index.html", error="Artist not found.")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5003)