# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0** — a tiny, explainable content-based music recommender.

---

## 2. Intended Use

- **What it is for.** Classroom exploration of how a single-user content-based recommender
  turns a small taste profile into ranked song suggestions. Each recommendation comes with a
  plain-English list of reasons so students can see *why* a song ranked where it did.
- **Who it is for.** AI110 students (and their instructor) learning how data + weights +
  ranking produce something that looks like a "smart" recommendation.
- **Assumptions about the user.** One user at a time, who can state a single favorite genre,
  a single favorite mood, a target energy level (0-1), and optionally a target musical
  positivity (valence) and a preference for acoustic textures.

**Not intended for:** real end users, production recommendations, cross-user personalization,
or any decision where being wrong has real-world stakes.

---

## 3. How the Model Works

Imagine you're sorting a small stack of songs by how well each one fits your mood. For each
song in the stack you ask a few questions:

- "Is this my favorite genre?" If yes, give it two points.
- "Is this the mood I'm in?" If yes, give it one point.
- "How close is its energy level to what I actually want?" If it's right on target, one
  point; the further away, the fewer points (and if it's all the way on the wrong end,
  zero points).
- "Does its overall positivity match what I'm asking for?" Same idea, half a point max.
- "Do I want acoustic stuff right now, and is this song acoustic?" If both yes, a small
  bonus.

Add it all up and you get one number per song. Then you sort the whole stack by that number,
largest first, and hand back the top five.

The important design choice is that **energy and valence use closeness, not magnitude**. A
user asking for chill music does not want the "most energetic song" — they want a song
*near* their target. Using `1 - |song_value - target|` rewards proximity in either direction.

What changed from the starter: the starter returned the first K songs without looking at
them. VibeFinder adds the full scoring rule, a separate ranking step, and an explanation
list so every recommendation is accompanied by "+2.0 genre match, +1.0 mood match, +0.98
energy closeness" so the user can see the reasoning.

---

## 4. Data

- **Size:** 20 songs in `data/songs.csv` (expanded from the starter's 10 to get broader
  genre and mood coverage — added edm, rnb, metal, folk, hip hop, latin, plus songs with
  `sad`, `romantic`, `dreamy`, `melancholy` moods).
- **Features per song:** `id, title, artist, genre, mood, energy, tempo_bpm, valence,
  danceability, acousticness`.
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, edm, rnb,
  metal, folk, hip hop, latin.
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, romantic,
  melancholy, dreamy, sad.
- **What's missing:** non-English-language tradition labels (no k-pop, afrobeats, reggaeton,
  arabic pop, indian classical, etc.); no era labels (no way to say "90s"); no song length;
  no lyrics sentiment. The data also reflects only the starter author's + my invented
  catalog — it is not a representative sample of any listener population.

---

## 5. Strengths

- **Perfectly explainable.** Every recommendation prints the exact rules that fired. A
  student can read "mood match (+1.0)" and know why it was picked.
- **Handles the coherent profiles cleanly.** When a user's genre/mood/energy point the same
  direction (e.g., *lofi / chill / 0.35*), the perfect match appears at #1 with a score
  near the theoretical ceiling, and the runners-up are sensible genre-adjacent tracks.
- **Cold-start-friendly by design.** Because it scores from attributes only, a brand-new
  song with no listener history can appear as a top recommendation the moment it's added
  to the catalog — no warm-up period needed.
- **Simple to tune.** The five weights live at the top of `recommender.py`; flipping one
  and re-running immediately shows the effect in the ranking (see the experiment below).

---

## 6. Limitations and Bias

- **Genre dominance bias.** With `GENRE_WEIGHT=2.0` and `ENERGY_WEIGHT=1.0`, a perfect-energy
  song in the wrong genre will almost always lose to an approximate-energy song in the right
  genre. In the "Sad but High-Energy" adversarial test, the #1 result had energy 0.62 even
  though the user asked for 0.9 — the genre+mood combo simply outvoted the energy miss.
- **Catalog size bias.** Lofi has 3 songs in the catalog; metal, edm, hip hop, folk, and
  latin each have exactly 1. A user with one of the single-entry favorites will always get
  the same song at #1 and then fall back to "mood matches in wrong genre" for the rest. This
  is a classic small-dataset filter bubble.
- **String-label bias.** Genre and mood are single strings. A song is either "pop" or "indie
  pop"; it cannot be both, so the indie-pop track loses half its score against a "pop" user
  even if the human ear would call them siblings. Same for mood: "intense" and "moody" feel
  adjacent but the model treats them as fully distinct categories.
- **Conflicting-preference fragility.** The adversarial "Acoustic EDM" run surfaced jazz at
  #2 because acousticness is wired as a bonus rather than a full matching axis. A profile
  with internally contradictory preferences produces plausible-looking but semantically odd
  rankings.
- **No collaborative signal.** Two users who live in totally different musical worlds but
  share the same `favorite_genre / favorite_mood / target_energy` triple get *identical*
  top-5 lists. Real recommenders fix this with behavior data; VibeFinder cannot.
- **Hand-picked weights.** The weights came from intuition, not from data — they reflect
  my guess about what matters more to listeners. Any user whose actual priorities don't
  match that guess gets a subtly worse experience and has no way to correct it.

### If used in a real product

These biases would translate into: underrepresented genres never getting recommended,
popular genres (the ones with many catalog entries) getting over-recommended, and users
with niche taste being silently nudged toward the mainstream. That pattern is well-studied
in the recommender literature as "popularity bias" and "filter bubble."

---

## 7. Evaluation

- **Profiles tested:** the default "Pop / Happy / high-energy", plus five stress profiles:
  - High-Energy Pop (coherent)
  - Chill Lofi Study (coherent, every rule can fire)
  - Deep Intense Rock (coherent but rare genre in the catalog)
  - Adversarial: Sad but High-Energy (conflicting energy vs mood)
  - Adversarial: Acoustic EDM (conflicting acousticness vs genre norms)
- **What I looked for:** whether #1 felt right by ear; whether songs with the wrong genre
  but the right mood still surfaced; how the model handled profiles where two preferences
  disagreed.
- **Experiment:** halved `GENRE_WEIGHT` and doubled `ENERGY_WEIGHT`, reran the default
  profile, and observed that "Gym Hero" dropped from #2 to #4 while mood-correct songs in
  adjacent genres (indie pop, hip hop) climbed. That confirmed genre was acting as a
  dominant filter in the baseline.
- **Automated tests:** `tests/test_recommender.py` covers two behavioral invariants —
  that the top result for a pop/happy user is in fact pop + happy, and that the
  explanation string is non-empty. Both pass.
- **What surprised me.** How much the output *feels* personalized even though it's
  essentially a weighted sum of four or five matches. That is also the scariest part —
  a transparent system can still look "smart" enough to fool someone into trusting it.

---

## 8. Future Work

- **Multi-label genres and moods.** Allow each song to carry `genres=["pop","indie pop"]`
  and score partial overlaps instead of exact-string equality.
- **Diversity in the top-K.** Penalize consecutive recommendations from the same artist
  or the same genre so the top-5 doesn't collapse into "three LoRoom lofi tracks in a row."
- **Learned weights.** Collect a tiny labeled set ("user rated these songs 1-5") and fit
  the weights with linear regression instead of hand-picking them.
- **Simple collaborative layer.** Cluster profiles by their top-5 overlap and let profiles
  in the same cluster "share" low-scored-but-loved outliers as tiebreakers.
- **Handle sparse genres.** When a user's favorite genre has only one matching song, fall
  back to the *mood-only* ranking for slots 2-5 instead of leaking into unrelated genres.

---

## 9. Personal Reflection

See [`reflection.md`](reflection.md) for per-profile comparisons written in plain language.

**Biggest learning moment.** When I ran the "Sad but High-Energy" profile and the #1 result
came back with energy 0.62 even though I had asked for 0.9. I had to stop and trace the math
— and realized that genre + mood together (+3.0) simply outweigh a perfect energy match
(+1.0). That was the moment the scoring became real to me: the weights aren't abstract
numbers, they're *editorial decisions* about what matters.

**Where AI tools helped, and where I had to double-check.** AI suggestions were useful for
the boilerplate — CSV loading, dataclass scaffolding, mermaid syntax. They were less useful
for the *choice* of weights and for deciding what "closeness" should mean for a numeric
feature. When I asked AI for a scoring formula, it wanted to use raw absolute value without
normalizing; I had to push back and use `1 - |song - target|` so the energy score lands in
a comparable range to genre/mood.

**What surprised me about how simple algorithms can still "feel" like recommendations.**
A hand-picked sum of five rules over 20 songs produces output that looks suspiciously like
a real Spotify "Made For You" row. That is not because the algorithm is smart — it's
because musical taste, at least within one genre, has enough consistency that even a dumb
rule makes reasonable guesses. That raised a warning flag for me: if something this crude
*looks* personalized, a real system with a hundred more features and a neural net on top
can easily *feel* authoritative when it's actually just confidently wrong.

**What I would try next.** Build a tiny "feedback" loop: let the user thumbs-up or
thumbs-down each of the top 5, nudge the weights based on that feedback, and see how many
rounds it takes before the recommendations settle into something that matches the user's
actual intuition. That turns the static scoring rule into a learning system without
requiring any heavy machinery.
