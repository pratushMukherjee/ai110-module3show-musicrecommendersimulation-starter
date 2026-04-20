"""Phase 4 data experiment.

Reruns the default "Pop / Happy / high-energy" profile under two weight regimes:
1. Baseline (the weights defined in recommender.py).
2. Shifted: energy doubled, genre halved.

Run from the project root:

    python -m src.experiment
"""

from src import recommender
from src.recommender import load_songs, recommend_songs


PROFILE = {"genre": "pop", "mood": "happy", "energy": 0.8}


def print_top(label: str, songs: list) -> None:
    print("=" * 72)
    print(label)
    print(
        f"(GENRE_WEIGHT={recommender.GENRE_WEIGHT}, "
        f"ENERGY_WEIGHT={recommender.ENERGY_WEIGHT})"
    )
    print("-" * 72)
    for rank, (song, score, reasons) in enumerate(
        recommend_songs(PROFILE, songs, k=5), start=1
    ):
        print(f"{rank}. {song['title']} -- {song['artist']}  (score {score:.2f})")
        print(f"   genre={song['genre']}  mood={song['mood']}  energy={song['energy']:.2f}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    print_top("BASELINE weights", songs)

    recommender.GENRE_WEIGHT = 1.0
    recommender.ENERGY_WEIGHT = 2.0
    print_top("SHIFTED weights (genre halved, energy doubled)", songs)


if __name__ == "__main__":
    main()
