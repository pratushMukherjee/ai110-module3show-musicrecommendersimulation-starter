"""Content-based music recommender (VibeFinder 1.0).

Provides:
- Song, UserProfile dataclasses and OOP Recommender (used by tests)
- load_songs, score_song, recommend_songs (used by src/main.py)

Both paths share the same scoring rule so dataclass-based and dict-based
callers produce identical rankings.
"""

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

# Scoring weights — see README "Algorithm Recipe"
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
VALENCE_WEIGHT = 0.5
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6


@dataclass
class Song:
    """A single track and its numeric / categorical attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """A single user's stated taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _get(song, key):
    """Read an attribute from either a Song dataclass or a dict row."""
    if isinstance(song, dict):
        return song[key]
    return getattr(song, key)


def _score(user_prefs: Dict, song) -> Tuple[float, List[str]]:
    """Shared scoring core used by both the functional and OOP paths."""
    score = 0.0
    reasons: List[str] = []

    fav_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    if fav_genre is not None and _get(song, "genre") == fav_genre:
        score += GENRE_WEIGHT
        reasons.append(f"genre match ({fav_genre}) +{GENRE_WEIGHT}")

    fav_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    if fav_mood is not None and _get(song, "mood") == fav_mood:
        score += MOOD_WEIGHT
        reasons.append(f"mood match ({fav_mood}) +{MOOD_WEIGHT}")

    target_energy = user_prefs.get("energy")
    if target_energy is None:
        target_energy = user_prefs.get("target_energy")
    if target_energy is not None:
        energy_closeness = 1.0 - abs(_get(song, "energy") - float(target_energy))
        energy_points = ENERGY_WEIGHT * energy_closeness
        score += energy_points
        reasons.append(
            f"energy closeness ({_get(song, 'energy'):.2f} vs target "
            f"{float(target_energy):.2f}) +{energy_points:.2f}"
        )

    target_valence = user_prefs.get("valence") or user_prefs.get("target_valence")
    if target_valence is not None:
        valence_closeness = 1.0 - abs(_get(song, "valence") - float(target_valence))
        valence_points = VALENCE_WEIGHT * valence_closeness
        score += valence_points
        reasons.append(
            f"valence closeness ({_get(song, 'valence'):.2f} vs target "
            f"{float(target_valence):.2f}) +{valence_points:.2f}"
        )

    likes_acoustic = user_prefs.get("likes_acoustic", False)
    if likes_acoustic and _get(song, "acousticness") >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(
            f"acoustic bonus (acousticness={_get(song, 'acousticness'):.2f}) "
            f"+{ACOUSTIC_BONUS}"
        )

    return score, reasons


class Recommender:
    """OOP wrapper over the scoring logic, for Song/UserProfile callers."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _user_to_prefs(self, user: UserProfile) -> Dict:
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs for this user, sorted by descending score."""
        prefs = self._user_to_prefs(user)
        scored = [(song, _score(prefs, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable, non-empty reason string for one song."""
        prefs = self._user_to_prefs(user)
        score, reasons = _score(prefs, song)
        if not reasons:
            return f"No matching features, but returned as a fallback (score {score:.2f})."
        return f"Score {score:.2f} — " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs.csv into a list of dicts with numeric fields cast to float/int."""
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}
    rows: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row: Dict = {}
            for key, value in raw.items():
                if key in int_fields:
                    row[key] = int(value)
                elif key in float_fields:
                    row[key] = float(value)
                else:
                    row[key] = value
            rows.append(row)
    return rows


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return (score, reasons) for one song against one user preference dict."""
    return _score(user_prefs, song)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, List[str]]]:
    """Score every song, sort descending, return top k as (song, score, reasons)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
