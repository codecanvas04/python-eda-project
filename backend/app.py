from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "https://your-frontend-site.netlify.app"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "cleaned_spotify.csv")

df = pd.read_csv(DATA_PATH)

recommendation_features = [
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "valence"
]

for column in recommendation_features:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
df["track_name"] = df["track_name"].fillna("")
df["artists"] = df["artists"].fillna("")
df["track_genre"] = df["track_genre"].fillna("Unknown")

df = df.dropna(subset=recommendation_features).copy()


def get_song(song_name):
    if not song_name:
        return None

    results = df[
        df["track_name"].str.lower().str.strip() == song_name.lower().strip()
    ]

    if results.empty:
        results = df[
            df["track_name"].str.lower().str.contains(
                song_name.lower().strip(),
                na=False
            )
        ]

    if results.empty:
        return None

    return results.sort_values("popularity", ascending=False).iloc[0]


def calculate_similarity(target, values):
    target = np.asarray(target, dtype=float)
    values = np.asarray(values, dtype=float)

    distance = np.linalg.norm(values - target, axis=1)
    max_distance = np.sqrt(len(recommendation_features))

    similarity = (1 - distance / max_distance) * 100

    return np.clip(similarity, 0, 100)


def recommend_songs(song_name, n=8):
    song = get_song(song_name)

    if song is None:
        return []

    target = song[recommendation_features].astype(float).values

    candidates = df[
        (df["track_genre"] == song["track_genre"]) &
        (df["popularity"] >= 45)
    ].copy()

    candidates = candidates[
        candidates["track_name"].str.lower() != song["track_name"].lower()
    ]

    if len(candidates) < n:
        candidates = df[
            df["track_name"].str.lower() != song["track_name"].lower()
        ].copy()

    values = candidates[recommendation_features].astype(float).values

    candidates["similarity"] = calculate_similarity(target, values)

    target_artist = str(song["artists"]).lower()

    candidates["artist_bonus"] = candidates["artists"].str.lower().apply(
        lambda x: 12 if target_artist in x else 0
    )

    candidates["score"] = (
        candidates["similarity"] * 0.65 +
        candidates["popularity"] * 0.23 +
        candidates["artist_bonus"]
    )

    candidates = candidates.sort_values(
        ["score", "similarity"],
        ascending=False
    ).head(n)

    candidates["similarity"] = candidates["similarity"].round(1)

    return candidates[
        [
            "track_name",
            "artists",
            "track_genre",
            "popularity",
            "similarity"
        ]
    ].to_dict("records")


def get_music_dna(song_name):
    song = get_song(song_name)

    if song is None:
        return None

    return {
        "energy": round(float(song["energy"]) * 100, 1),
        "danceability": round(float(song["danceability"]) * 100, 1),
        "valence": round(float(song["valence"]) * 100, 1),
        "acousticness": round(float(song["acousticness"]) * 100, 1),
        "instrumentalness": round(float(song["instrumentalness"]) * 100, 1),
        "speechiness": round(float(song["speechiness"]) * 100, 1),
        "popularity": round(float(song["popularity"]), 1),
        "tempo": round(float(song["tempo"]), 1)
    }


def classify_mood(row):
    energy = row["energy"]
    valence = row["valence"]

    if energy >= 0.6 and valence >= 0.6:
        return "Energetic & Happy"

    if energy >= 0.6 and valence < 0.6:
        return "Energetic & Intense"

    if energy < 0.6 and valence >= 0.6:
        return "Calm & Happy"

    return "Calm & Melancholic"


df["mood"] = df.apply(classify_mood, axis=1)


def get_mood_songs(mood, n=10):
    songs = df[
        (df["mood"].str.lower() == mood.lower()) &
        (df["popularity"] >= 40)
    ].copy()

    songs = songs.sort_values("popularity", ascending=False).head(n)

    return songs[
        [
            "track_name",
            "artists",
            "track_genre",
            "popularity"
        ]
    ].to_dict("records")


def get_hidden_gems(n=10):
    gems = df[
        (df["popularity"] >= 20) &
        (df["popularity"] <= 55)
    ].copy()

    gems["gem_score"] = (
        gems["danceability"] * 20 +
        gems["energy"] * 20 +
        gems["valence"] * 15 +
        gems["acousticness"] * 10 +
        gems["popularity"] * 0.35
    )

    gems = gems.sort_values(
        "gem_score",
        ascending=False
    ).head(n)

    return gems[
        [
            "track_name",
            "artists",
            "track_genre",
            "popularity"
        ]
    ].to_dict("records")


def get_evolution():
    genre_stats = df.groupby("track_genre").agg(
        tracks=("track_name", "count"),
        popularity=("popularity", "mean"),
        energy=("energy", "mean"),
        danceability=("danceability", "mean"),
        valence=("valence", "mean")
    ).reset_index()

    genre_stats = genre_stats.sort_values(
        "popularity",
        ascending=False
    ).head(12)

    genre_stats["popularity"] = genre_stats["popularity"].round(1)
    genre_stats["energy"] = (genre_stats["energy"] * 100).round(1)
    genre_stats["danceability"] = (genre_stats["danceability"] * 100).round(1)
    genre_stats["valence"] = (genre_stats["valence"] * 100).round(1)

    return genre_stats.to_dict("records")


def compare_songs(song_one_name, song_two_name):
    song_one = get_song(song_one_name)
    song_two = get_song(song_two_name)

    if song_one is None or song_two is None:
        return None

    features = [
        "energy",
        "danceability",
        "valence",
        "acousticness",
        "instrumentalness",
        "speechiness"
    ]

    result = {
        "song_one": {
            "name": song_one["track_name"],
            "artists": song_one["artists"],
            "genre": song_one["track_genre"],
            "popularity": round(float(song_one["popularity"]), 1)
        },
        "song_two": {
            "name": song_two["track_name"],
            "artists": song_two["artists"],
            "genre": song_two["track_genre"],
            "popularity": round(float(song_two["popularity"]), 1)
        },
        "features": {}
    }

    for feature in features:
        result["features"][feature] = {
            "one": round(float(song_one[feature]) * 100, 1),
            "two": round(float(song_two[feature]) * 100, 1)
        }

    return result


@app.route("/")
def home():
    return jsonify({"message": "Music Lab API is running"})


@app.route("/api/recommend")
def recommend():
    song = request.args.get("song", "")
    return jsonify(recommend_songs(song))


@app.route("/api/dna")
def dna():
    song = request.args.get("song", "")
    result = get_music_dna(song)

    if result is None:
        return jsonify({"error": "Song not found"}), 404

    return jsonify(result)


@app.route("/api/mood")
def mood():
    mood_name = request.args.get("mood", "")
    return jsonify(get_mood_songs(mood_name))


@app.route("/api/gems")
def gems():
    return jsonify(get_hidden_gems())


@app.route("/api/evolution")
def evolution():
    return jsonify(get_evolution())


@app.route("/api/compare")
def compare():
    song_one = request.args.get("song1", "")
    song_two = request.args.get("song2", "")

    result = compare_songs(song_one, song_two)

    if result is None:
        return jsonify({"error": "One or both songs were not found"}), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)