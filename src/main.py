"""CLI runner for VibeFinder 1.0.

Run from the project root:

    python -m src.main

Prints the top 5 recommendations for a default profile, plus a set of diverse
and adversarial profiles used in the Phase 4 stress tests.
"""

from src.recommender import load_songs, recommend_songs


DEFAULT_PROFILE = {
    "name": "Default: Pop / Happy / high-energy",
    "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8},
}

STRESS_PROFILES = [
    {
        "name": "High-Energy Pop",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.9,
            "target_valence": 0.85,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Chill Lofi Study",
        "prefs": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "target_valence": 0.55,
            "likes_acoustic": True,
        },
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "target_valence": 0.45,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Adversarial: Sad but High-Energy",
        "prefs": {
            "genre": "rock",
            "mood": "sad",
            "energy": 0.9,
            "target_valence": 0.2,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Adversarial: Acoustic EDM",
        "prefs": {
            "genre": "edm",
            "mood": "happy",
            "energy": 0.9,
            "target_valence": 0.9,
            "likes_acoustic": True,
        },
    },
]


def print_recommendations(profile_name: str, prefs: dict, songs: list, k: int = 5) -> None:
    print("=" * 72)
    print(f"Profile: {profile_name}")
    print(f"Prefs:   {prefs}")
    print("-" * 72)
    recommendations = recommend_songs(prefs, songs, k=k)
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} -- {song['artist']}  (score {score:.2f})")
        print(f"   genre={song['genre']}  mood={song['mood']}  energy={song['energy']:.2f}")
        if reasons:
            for reason in reasons:
                print(f"   - {reason}")
        else:
            print("   - (no feature matched; ranked by proximity only)")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    print_recommendations(DEFAULT_PROFILE["name"], DEFAULT_PROFILE["prefs"], songs)

    print("\n\n########## STRESS TESTS ##########\n")
    for profile in STRESS_PROFILES:
        print_recommendations(profile["name"], profile["prefs"], songs)


if __name__ == "__main__":
    main()
