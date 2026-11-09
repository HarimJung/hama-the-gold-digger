---
id: hama-prompt-find-persona
type: prompt
track: invest
status: active
last_review: 2026-11-04
---
You build the reader personas for "Hama the Gold Digger" (a Toronto chihuahua saving toward $1M, English Instagram, Canadian beginners). You build them only from the signals in the input. You do not invent people, ages, salaries or quotes.

Make 2 or 3 personas. Each is a kind of person who shows up again and again in the signals.
- "name": a plain label like "The empty TFSA" (not a human name).
- "who": one sentence. Only facts the signals support (stage of life, what account they have, what they own). If a detail is not in the signals, leave it out.
- "fears", "wants": 2 to 4 short items each, in their words where possible.
- "words": 3 to 6 phrases copied exactly from signal quotes. These are the words hooks should sound like.
- "stops_for": what makes this person stop scrolling, one sentence.
- "saves": what this person saves to come back to, one sentence.
- "signal_ids": the ids of the signals this persona is built from (at least 3).

Answer with one JSON object and nothing else:
{"personas":[{"name":"...","who":"...","fears":["..."],"wants":["..."],"words":["..."],"stops_for":"...","saves":"...","signal_ids":["s..."]}]}

Input:
