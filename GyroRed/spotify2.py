import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set up Spotify client credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="078218dff1e4439582ec0b8d6858be26",
                                                           client_secret="ba0bde2c3a1d4d1dad7cf7714d33d0ec"))

# Function to get top tracks
def get_top_tracks():
    # Get the current top tracks (chart data may vary, using 'global' playlist)
    results = sp.playlist_tracks('37i9dQZEVXbMDoHDwVN2tF', limit=10)
    tracks = results['items']
    
    # Display top 10 tracks
    print("Top 10 Tracks Right Now:")
    for idx, item in enumerate(tracks):
        track = item['track']
        print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")

if __name__ == '__main__':
    get_top_tracks()