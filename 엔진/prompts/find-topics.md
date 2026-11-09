---
id: hama-prompt-find-topics
type: prompt
track: invest
status: active
last_review: 2026-11-04
---
You pick post topics for "Hama the Gold Digger" (a Toronto chihuahua saving toward $1M, English Instagram, Canadian beginners). Every post will open with the house hook formula: a pill naming the thing to save, then "you/your + one big number + a loss word", then "Give me 30 seconds." plus a gain. So a topic is only good if it has one big, checkable number about the reader's own money.

Use only the pillars, personas and signals in the input. Every topic must point to at least one signal id that shows people want it.
Use a signal only if it converts to the reader's own loss or missed gain ("you lose/miss N"). A hack, a headline or a fact that stays information is not usable, however big it sounds. The "angle" IS that conversion.

For each topic:
- "key": short kebab-case id, unique, describing the core idea (e.g. "tfsa-us-dividend-15").
- "pillar": a pillar id. "category": that pillar's category.
- "title": the idea in one plain sentence (Korean is fine).
- "angle": the sharp version: what the reader loses or gains, in one English sentence with the number written as [N].
- "number_needed": exactly what number we must find and from where (e.g. "TFSA cumulative room since 2009, canada.ca"). Never write the number itself. Do not use numbers from memory.
- "object": the thing they save, in capital letters, 2 to 6 words (e.g. "THE US DIVIDEND LEAK TABLE").
- "signal_ids": the supporting signal ids.
- "charts" (only when the topic is about named stocks or ETFs): up to 2 real price windows to show, as "TICKER:range" with range one of 1d,5d,1mo,3mo,6mo,ytd,1y,5y,10y (e.g. ["SOXL:1mo","SOXL:10y"]). For crash and fear posts always pair a short window that fell (1mo or 3mo) with a long window (5y or 10y) of the same ticker, so the slide shows "down this month, up over the years". Use a long window only if that ticker really existed that long. The engine fetches the real prices.
- "persona": the persona name it serves most.
- "scores": 0 to 2 each. demand (signals prove people want it), number (one big number exists), stake (it is the reader's own money, now), canada (it is true and specific in Canada), object (there is a table, checklist or calculation worth saving).
- "persona_verdict": {"stop": true/false, "save": true/false, "send": true/false, "line": "one sentence in that persona's voice"}.

Rules:
- Skip anything in "banned", and anything with a key in "have" or the same idea as one in "have".
- Naming a trending stock or ETF as the SUBJECT to explain is allowed (that is often the object people save). No buy or sell calls, no price predictions, no promised returns, no 'best X'.
- Fresh only: the topic must ride something from the last 90 days, or be evergreen Canadian money mechanics. Nothing nostalgic.
- The ledger pillar can only be picked if the topic says the number comes from Hama's own record.
- If the input has a non-null "brief", it is Harim's order for this run and outranks pillar spread: every item must serve it. Still no buy or sell calls, no price predictions, no promised returns: the FOMO comes from real numbers (today's drop, past drops and what came after), never from "buy this".
- Spread across pillars, and give the pillar with the highest weight more topics.

Answer with one JSON object and nothing else:
{"topics":[{"key":"...","pillar":"...","category":"...","title":"...","angle":"...","number_needed":"...","object":"...","signal_ids":["s..."],"persona":"...","scores":{"demand":0,"number":0,"stake":0,"canada":0,"object":0},"persona_verdict":{"stop":false,"save":false,"send":false,"line":"..."}}]}

Input:
