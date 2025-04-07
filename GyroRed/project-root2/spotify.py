from flask import Flask, render_template, request, redirect, session, url_for
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

app = Flask(__name__, template_folder='webpages')
app.secret_key = os.urandom(24)  # Set a secret key for session management
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri, 
    scope="user-library-read user-top-read"
)
def get_token():
    token_info = session.get("token_info", None)
    if not token_info:
        return None
    # Check if the token has expired
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    return token_info

def get_popularity_message(popularity):
    if popularity >= 90:
        return "One of the most popular songs right now"
    elif popularity >= 80:
        return "Popular song right now"
    elif popularity >= 65:
        return "Popular"
    elif popularity >= 50:
        return "Average"
    elif popularity >= 30:
        return "Not famous, but probably still a good song :)"
    else:
        return "Underground song :P"

@app.route("/")
def index():
    if not session.get("token_info"):
        return redirect(url_for("login"))
    
    token_info = session.get("token_info")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args.get("code"))
    session["token_info"] = token_info
    return redirect(url_for("user_top_tracks"))

def time_adjust(time_range):
    if time_range == "medium_term":
        return "Last 6 Months"
    elif time_range == "short_term":
        return "Last Month"
    else:
        return "All Time"
    


@app.route("/top_tracks")
def user_top_tracks():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("login"))

    time_range = request.args.get('time_range', 'medium_term')  # Default to 'medium_term'
    display_time_range = time_adjust(time_range)  # Use this for display purposes
    sp = spotipy.Spotify(auth=token_info["access_token"])
    top_tracks_data = sp.current_user_top_tracks(limit=10, time_range=time_range)
    top_tracks = top_tracks_data['items']

    # Add popularity messages to each track
    tracks_with_messages = []
    for track in top_tracks:
        popularity_message = get_popularity_message(track['popularity'])
        tracks_with_messages.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],  # Get the name of the first artist
            'popularity': track['popularity'],
            'popularity_message': popularity_message
        })

    # Pass the adjusted display time range to the template
    return render_template("top_tracks.html", tracks=tracks_with_messages, time_range=display_time_range)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0' port=5001)
