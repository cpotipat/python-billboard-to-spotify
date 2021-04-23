import requests
import spotipy
import os
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

APP_CLIENT_ID = os.environ.get("APP_CLIENT_ID")
APP_CLIENT_SECRET = os.environ.get("APP_CLIENT_SECRET")
APP_REDIRECT_URI = os.environ.get("APP_REDIRECT_URI")

# Scraping Billboard top 100 songs
user_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
url = f"https://www.billboard.com/charts/hot-100/{user_date}"

response = requests.get(url)
response.raise_for_status()
song_list = response.text

soup = BeautifulSoup(song_list, "html.parser")
hundred_songs = [song.getText() for song in soup.find_all(name="span", class_="chart-element__information__song")]


# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=APP_CLIENT_ID,
                                               client_secret=APP_CLIENT_SECRET,
                                               redirect_uri=APP_REDIRECT_URI,
                                               scope="playlist-modify-private"))

user_id = sp.current_user()["id"]


# Searching Spotify for songs by title
song_uris = []
year = user_date.split("-")[0]

for song in hundred_songs:
    results = sp.search(q=f"track: {song} year: {year}", type="track")

    try:
        uri = results["tracks"]["items"][0]["uri"]
        song_uris.append(uri)

    except IndexError:
        print(f"Not found '{song}' in Spotify. Skipped.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{user_date} Billboard 100", public=False)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)


