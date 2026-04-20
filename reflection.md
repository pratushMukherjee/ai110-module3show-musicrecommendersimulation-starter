# Reflection: VibeFinder 1.0 profile comparisons

For each pair of profiles below, I looked at the top-5 output and asked:
what changed, and does the change make sense given the rules?
Written in plain language so it would make sense to someone who has never read the code.

## 1. High-Energy Pop vs. Chill Lofi Study

The pop profile's top five is: Sunrise City, Gym Hero, Festival Horizon, Block Party
Bounce, Rooftop Lights. The lofi profile's top five is: Library Rain, Midnight Coding,
Focus Flow, Spacewalk Thoughts, Coffee Shop Stories.

There is zero overlap between the two lists, which is exactly what you'd hope for.
The pop list has energy values between 0.76 and 0.95 and every track is cheerful; the
lofi list has energy values between 0.28 and 0.42 and every track has a soft, acoustic
feel. The scoring rule is doing its job: a user asking for the loud/happy end of the
catalog and a user asking for the quiet/chill end get two totally different
neighborhoods of songs.

The pop profile rewards songs near 0.9 energy even when they come from adjacent genres
(edm, hip hop, indie pop show up at #3, #4, #5). The lofi profile stays tighter because
lofi + chill + low energy + acoustic all cluster together in the catalog — four of the
top five have acousticness above 0.7.

## 2. Deep Intense Rock vs. Adversarial: Sad but High-Energy

Both profiles ask for rock, and both get rock at #1 and #2. That's the genre weight
dominating — the top of the list is always going to come from the user's favorite genre
if *any* songs in that genre exist in the catalog.

The interesting difference is at #1:

- Intense Rock picks **Storm Runner** (rock, intense, 0.91 energy) — the textbook match.
- Sad + High-Energy picks **Cold Static** (rock, sad, 0.62 energy) — the mood-and-genre
  match wins even though the energy is off by almost 0.3.

This is the clearest example of the "genre + mood outweigh energy" behavior. A user who
said they wanted high-energy got a middle-energy song at #1 because the system decided
matching the *type* of song (sad rock) mattered more than hitting the energy target. A
real listener might agree with this ("I want sad rock and I'll accept whatever energy
sad rock tends to have") or disagree ("I said high energy, mean it"). The model has no
way to know which one the user wants — it just applied the weights.

## 3. High-Energy Pop vs. Adversarial: Acoustic EDM

The EDM user asked for the exact same mood (happy) and a higher energy (0.9) but gave
the model two contradictions: EDM is typically produced-electronic, and EDM fans rarely
chase acoustic textures.

- The pop user's #2 is Gym Hero (loud, electronic, 0.05 acousticness).
- The EDM user's #2 is **Kitchen Sunlight** — a jazz song with 0.82 acousticness and
  only 0.55 energy.

Kitchen Sunlight shouldn't feel right to anyone who asked for EDM. It floated up because
the acoustic bonus fires (+0.5), the mood matches (+1.0), and there are only so many
happy songs in the catalog. This is a real failure mode — the model can't tell that
"EDM" and "acoustic" almost never co-occur in real listening, so it awards the bonus
points even when the combination doesn't make musical sense.

A collaborative recommender would notice that EDM fans don't listen to acoustic jazz,
and would downweight that result even if the attributes look like they match.

## 4. Chill Lofi Study vs. Adversarial: Sad but High-Energy

These two profiles disagree on almost every axis — low energy vs. high energy, relaxed
vs. angry, lofi vs. rock — and the outputs confirm there is no overlap at all. What I
wanted to check was whether the *shape* of the two lists feels consistent with the
rules.

The lofi list is dense: #1 has a near-perfect 4.97 score (every rule fires), and the
scores drop gradually. The sad-rock list is thinner: #1 is 4.20, and by #5 we're at
1.19. That gap at the bottom tells me the catalog has enough lofi variety to support a
full top-5 where every result is genuinely similar, but it only has two rock songs, so
the bottom of the sad-rock list is padded with "intense" and "moody" tracks from
unrelated genres whose only connection is that they're not boring.

The lesson here is that the catalog shape matters as much as the scoring rule. The same
weights produce a satisfying top-5 for a well-represented taste and a noticeably
degraded top-5 for an under-represented taste — which is exactly the "long-tail
underservice" pattern that real recommender systems are criticized for.

---

## Plain-language summary for a non-programmer

Imagine a judge handing out points to each song based on how well it matches what you
said you wanted — 2 points for the right genre, 1 point for the right mood, up to 1
point if the energy is close to what you asked for. Then the judge sorts all the songs
by their total score and hands you the top five.

That's all the system does. It is not "learning." It does not know you. It does not
remember what you skipped. It just takes the few things you told it and does the math.

And yet — when you ask for lofi chill study music, it gives you five lofi chill tracks
and they feel right. That's the part I found unsettling. A system this simple can
produce output that looks thoughtful, which means a more complex system can look
*authoritative* without actually being correct. Whenever "Gym Hero" ends up in your
recommendations even though you said you wanted happy pop, remember that the judge is
just a spreadsheet with weights — not a friend who knows your taste.
