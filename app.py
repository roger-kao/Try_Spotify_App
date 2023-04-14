from flask import Flask, render_template, request, redirect, session, url_for
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates")

app.secret_key = os.getenv("FLASK_SECRET_KEY")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

@app.route("/")
def index():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return render_template("index.html", auth_url=auth_url)

@app.route("/callback")
def callback():
    sp_oauth = create_spotify_oauth()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("search", _external=True))

@app.route("/search", methods=["GET", "POST"])
def search():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        playlist_name = request.form.get("playlist_name")
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read playlist-read-private",
            cache_path=".spotifycache",
            show_dialog=True,
        ))
        playlists = sp.current_user_playlists()
        playlist_found = False
        for playlist in playlists["items"]:
            if playlist["name"].lower() == playlist_name.lower():
                playlist_id = playlist["id"]
                playlist_found = True
                break
        if playlist_found:
            playlist = sp.playlist(playlist_id)
            tracks = [track["track"]["name"] for track in playlist["tracks"]["items"]]
            return render_template("playlist.html", tracks=tracks)
        else:
            return "Playlist not found."
    else:
        return render_template("search.html")

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-library-read playlist-read-private",
        cache_path=".spotifycache",
        show_dialog=True,
    )

if __name__ == "__main__":
    app.run(port=8000, debug=True)
