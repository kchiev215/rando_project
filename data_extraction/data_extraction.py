# Python project with data visualization
import spotipy
import mysql.connector
from credentials import *
from datetime import datetime, timedelta

# STEPS TO GET DONE

# Get authentication of spotify
sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                                      redirect_uri=SPOTIPY_REDIRECT_URI,
                                      scope=scope))

rp = sp.current_user_recently_played(limit=50)

# Connect to mysql database
cnn = mysql.connector.connect(user=user, password=password, host=host, database=database)

# Create table to store date
create_db_query = """CREATE TABLE IF NOT EXISTS rando_project(
                    track_name VARCHAR(255) NOT NULL, 
                    artist_name VARCHAR(255) NOT NULL,
                    track_popularity INT NOT NULL,
                    album VARCHAR(255) NOT NULL,
                    artist_genre VARCHAR(255) NOT NULL,
                    release_date DATE NOT NULL,
                    timestamp_formatted TIMESTAMP NOT NULL PRIMARY KEY,
                    timestamp_est_formatted TIMESTAMP NOT NULL,
                    danceability INT NOT NULL,
                    energy INT NOT NULL,
                    key_of_song INT NOT NULL,
                    loudness INT NOT NULL,
                    mode INT NOT NULL,
                    speechiness INT NOT NULL,
                    acousticness INT NOT NULL,
                    instrumentalness INT NOT NULL,
                    liveness INT NOT NULL,
                    valence INT NOT NULL,
                    tempo INT NOT NULL,
                    duration_ms INT NOT NULL)"""

# Create a cursor for sql query
cursor = cnn.cursor()

# Open up the database
cursor.execute(create_db_query)


# Pull from spotify API
for item in rp['items']:
    track = item['track']
    track_name = track['name']
    artist_name = track['artists'][0]['name']
    track_popularity = track['popularity']
    album = track['album']['name']
    artist_genres = sp.artist(track['artists'][0]['uri'])['genres']
    artist_genre = artist_genres[0] if artist_genres else "N/A"
    release_date = track['album']['release_date']
    timestamp_str = item['played_at']
    danceability = sp.audio_features(track['uri'])[0]['danceability']
    energy = sp.audio_features(track['uri'])[0]['energy']
    key_of_song = sp.audio_features(track['uri'])[0]['key']
    loudness = sp.audio_features(track['uri'])[0]['loudness']
    mode = sp.audio_features(track['uri'])[0]['mode']
    speechiness = sp.audio_features(track['uri'])[0]['speechiness']
    acousticness = sp.audio_features(track['uri'])[0]['acousticness']
    instrumentalness = sp.audio_features(track['uri'])[0]['instrumentalness']
    liveness = sp.audio_features(track['uri'])[0]['liveness']
    valence = sp.audio_features(track['uri'])[0]['valence']
    tempo = sp.audio_features(track['uri'])[0]['tempo']
    duration_ms = sp.audio_features(track['uri'])[0]['duration_ms']

    # Convert timestamp to datetime object in UTC
    timestamp = datetime.fromisoformat(timestamp_str[:-1])

    # Convert timestamp from UTC to EST
    est_offset = -5  # Eastern Standard Time (EST) offset is -5 hours
    timestamp_est = timestamp - timedelta(hours=est_offset)

    # Format datetime objects as strings without "Z" character
    timestamp_formatted = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_est_formatted = timestamp_est.strftime('%Y-%m-%d %H:%M:%S')

    # Push into mysql database
    insert_query = """
        INSERT INTO rando_project(
            track_name, artist_name, track_popularity, album, artist_genre, release_date, timestamp_formatted, 
            timestamp_est_formatted, danceability, energy, key_of_song, loudness, mode, speechiness, acousticness, 
            instrumentalness,liveness, valence, tempo, duration_ms) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE
            artist_name=VALUES(artist_name),
            track_popularity=VALUES(track_popularity),
            album=VALUES(album),
            artist_genre=VALUES(artist_genre),
            release_date=VALUES(release_date),
            timestamp_est_formatted=VALUES(timestamp_est_formatted),
            danceability=VALUES(danceability),
            energy=VALUES(energy),
            key_of_song=VALUES(key_of_song),
            loudness=VALUES(loudness),
            mode=VALUES(mode),
            speechiness=VALUES(speechiness),
            acousticness=VALUES(acousticness),
            instrumentalness=VALUES(instrumentalness),
            liveness=VALUES(liveness),
            valence=VALUES(valence),
            tempo=VALUES(tempo),
            duration_ms=VALUES(duration_ms)
        """

    # ON DUPLICATE KEY UPDATE = equivalent to UPSERT(Insert or update into [name of table])

    values = (
        track_name, artist_name, track_popularity, album, artist_genre, release_date, timestamp_formatted,
        timestamp_est_formatted, danceability, energy, key_of_song, loudness, mode, speechiness, acousticness,
        instrumentalness, liveness, valence, tempo, duration_ms
    )

    # Execute the query with the values
    cursor.execute(insert_query, values)

    # Commit the transaction
    cnn.commit()
