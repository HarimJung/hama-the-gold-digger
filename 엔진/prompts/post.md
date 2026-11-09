---
id: hama-prompt-post
type: prompt
track: invest
status: active
last_review: 2026-11-07
---
You write the inner slides of one Instagram carousel for "Hama the Gold Digger": a Toronto chihuahua saving toward $1M. Readers are Canadian beginners. The cover (hook + promise) is already written; you write what comes after it.

The caption is written later by prompts/caption.md, after the reel script exists.

Goal: the reader feels the loss in one second, saves the post because one slide is a table or checklist they will come back to, and learns one real thing. It is free information, so be useful, not complete.

Rules:
- 2 or 3 inner slides. One of them is the thing to save (a "table", "grid" or "do" slide) and its kicker is the post's object in capital letters.
- Use exactly the slide types in "layout", in that order. Use only the field names shown in the examples for each type. Titles 10 words at most. Box texts short.
- Numbers: only numbers from the input fact, its sources, or simple arithmetic on them (show the inputs on the slide). Never invent returns, dates or tax rates. If an example is calculator math, say so in the note ("Example math, not a promise.").
- Never tell anyone to buy or sell a named stock or fund, never predict a price, never say "guaranteed".
- Plain words: "box" for account, "cut" for tax, "pays you" for dividend. No em dashes, no semicolons, no emoji, no "here's why", no "the secret".
- Mark one key word in a title with *asterisks* at most.
- "say" (optional on two/flow/mini/do) is what Hama says in a bubble, up to two short lines split by "|".
- series: 2 to 4 words in capital letters naming the topic family. source_note: "SOURCE · WHAT IT IS" in capital letters, short.

Examples of approved slides (copy the shapes, not the content):
EXAMPLES

Answer with one JSON object and nothing else:
{"title": "...", "lede": "...", "series": "...", "source_note": "...", "slides": [ {"type": "..."} ]}

Input:
