---
description: A bright stat chart where your number counts up as the line climbs past the moment it took off.
---
Make a short stat animation of this growth story: $ARGUMENTS

## The words

The words describe one metric that grew: a metric name, an optional start value, a final value, an optional time
span and an optional moment that changed things.

- Metric: the words before the first number or the first ":" ("Newsletter subscribers", "Revenue", "App
  downloads"). Show it as typed, first letter capitalised. Add "monthly" before it only if the words say "a month"
  ("Monthly revenue").
- Final value F: the last number, kept exactly as typed with its prefix, separators and suffix ("48,200", "$212K",
  "1.2M"). Start value S: the number before " to " if there is one ("0", "$18K"); otherwise 6% of F, rounded to the
  display step.
- The display format comes from F as typed: the same prefix ("$"), the same suffix (K, M, B, none), the same
  thousands separators, the same number of decimals. The display step is one unit of F's last digit ("48,200" →
  steps of 100, "$212K" → 1K, "1.2M" → 0.1M). Every number shown is rounded to that step in that format, and the
  final frame shows F exactly as typed.
- Span: "in one year" or "in 12 months" → 12 months; "in 2 years" → 24. No span → 24 months. The series ends at
  the end of Dec 2025 and starts span months earlier.
- The moment: the phrase after "after the", "at", "since" or "callout at" ("the redesign", "launch"). Name it as an
  event for the callout title, at most 26 characters: "Redesign ships", "Public launch". With no moment in the
  words, invent the most plausible one for this metric ("Referral program starts" for a newsletter). Also write it
  as a short past-tense phrase for the badge line: "the redesign shipped", "launch", "referrals launched".

## The data (build once at setup, seeded)

- N = 61 points evenly spaced in time across the span. The event point is iE = 37 (62% along). Its value
  E = S + 0.20·(F − S).
- Before the event (i ≤ 37), x = i / 37: v = S + (E − S)·x^1.7. After it (i ≥ 37), x = (i − 37) / 23:
  v = E + (F − E)·(1 − (1 − x)^1.6).
- Noise from mulberry32 seeded with 11, one roll per point (w in −1…1): add (F − S)·a·w·sin(π·x), a = 0.012
  before the event and 0.03 after, so the event and both ends stay exact. Clamp at 0. The last point is exactly F.
- Growth = round((F − E) / E × 100) using E rounded to the display step, shown as "+400%".
- The callout's second line: count the months after the event until the series first reaches 2·E: "2× in 1 month",
  "2× in 4 months". If it never doubles: "+<growth>% in <months left> months".
- The event's month: the month the event point falls in ("AUG 2025").

## What it shows

A crisp, bright analytics chart filling the frame: the metric name, one huge ink number, then a chart whose line
creeps along in slate grey, turns ultramarine at the moment that changed things and climbs. The number always shows
the value at the line's head. A white callout card names the moment, and at the end a growth badge lands. Clean
near-white, deep ink and one accent, ultramarine #2F4BFF, used only for the climb, the head and the payoff. No
tinted washes: the finish is crisp white, sharp ink type and one saturated colour.

The stage is a 1080×1920 portrait div, scaled to fit the browser window (centred, letterboxed), background
linear-gradient(180deg, #FFFFFF, #F8F9FB). Inside it: a 2D canvas 1080×1920 for the chart and, on top, an absolutely
positioned DOM layer for every piece of text. Colours: ink #0E1220, muted #5B6275, faint #8A91A3, accent #2F4BFF.

Layout on the 1080×1920 stage (x from the left edge, y from the top; text boxes use line-height 1 unless said):
- Metric name: "Manrope" 700, 46 px, ink, letter-spacing −0.01em, left x 90, top y 292.
- Span, right-aligned at x 960, top y 300: "Manrope" 600, 30 px, faint, letter-spacing 0.06em, upper case:
  "JAN – DEC 2025" for a one-year span, else "JAN 2024 – DEC 2025".
- The number: left x 84, top y 360, "Bricolage Grotesque" 800 with font-variation-settings "opsz" 96, 290 px, ink,
  letter-spacing −0.03em. Wrap every separator (comma or point) in a span with margin 0 0.03em so it never touches
  the digits beside it. A prefix ("$") and a suffix (K, M, B) are 58% of that size, same font and colour, sitting on
  the baseline, the suffix 6 px after the digits. At setup, measure the final string and, if it is wider than 870 px,
  shrink the size until it fits; keep that size for every frame.
- Badge row (the payoff), top y 700, left x 90: an inline SVG circle 84 px across, fill accent, with a white
  up-right arrow (a line from (30, 54) to (54, 30) and a corner from (34, 30) to (54, 30) to (54, 50) in an 84 px
  box, stroke 7.5, round caps and joins); 22 px to its right, vertically centred on it, "+<growth>%" in
  "Bricolage Grotesque" 800, 88 px, accent, letter-spacing −0.03em. Below, top y 812, left x 90: "after " and the
  past-tense phrase, "Manrope" 600, 42 px, muted.
- The chart plot: x from PL 90 to PR 880, value 0 on the axis at y 1440, Ymax at y 950. Ymax = the smallest of 1,
  1.5, 2, 2.5, 3, 4, 5, 6, 8 (× a power of ten) that is ≥ 1.12·F. Point i sits at x = PL + (PR − PL)·i / 60.
- Gridlines at Ymax·k/5, k = 1…5: dotted, dots radius 1.8 px every 12 px from x 90 to 880, #B7BECB. Each labelled
  in the gutter, right-aligned at x 960 and vertically centred on its line, "Manrope" 600, 30 px, faint, in the
  abbreviated format ("60K", "250K", "1.5M"). Labels never fade or hide.
- The axis: a 2 px line rgba(14,18,32,0.22) at y 1440 from x 90 to 880. Month labels, top y 1458, "Manrope" 600,
  30 px, muted, letter-spacing 0.05em, centred on their x: for a one-year span every second month from JAN ("JAN",
  "MAR" …, at the start of that month); for longer spans every sixth month as "JAN 24", "JUL 24" …. A label is
  hidden while the date tag's centre is within 80 px of it.
- The date tag, top y 1450: the head's month on an ink pill (background #0E1220, radius 12 px, padding 7px 14px),
  "Manrope" 800, 30 px, white, letter-spacing 0.06em: "MAY" for a one-year span, else "MAY 25". It is centred on
  the head's x, kept inside x 90–960, from the first frame.

The chart, drawn on the canvas each frame:
- Before the event the line is #6E768A, 5 px, round joins and caps, with a faint area under it down to the axis:
  a vertical gradient rgba(14,18,32,0.05) at y 950 to transparent at the axis.
- Once the head passes the event:
  - The area under the accent part, down to the axis: a vertical gradient rgba(47,75,255,0.16) at y 950 to
    rgba(47,75,255,0) at the axis.
  - The accent line from the event to the head: #2F4BFF, 9 px, round joins and caps, with a canvas shadow
    rgba(47,75,255,0.40), blur 22, offset y 12, so it floats above the chart.
  - The event rule: a dashed vertical line, 2.5 px rgba(14,18,32,0.45), dash 7/8, from 18 px above the event point
    up to y 920.
  - The event marker: a solid ink (#0E1220) disc radius 11 px inside a 4 px white ring (radius 15), with a soft
    shadow rgba(14,18,32,0.25), blur 10, offset y 4.
- The head: a guide line 2 px rgba(14,18,32,0.14) from 22 px below the head down to the axis (it links the head to
  the date tag). A pulsing halo, a disc radius 20·(1 + 0.8·q), fill rgba(47,75,255,0.22·(1 − q)),
  q = fract(t / 0.9). A white disc radius 17 px with a shadow rgba(47,75,255,0.5), blur 16, offset y 6. On top a
  disc radius 11 px: #6E768A before the event, accent after it.

The callout card (DOM), once the head passes the event: background #FFFFFF, radius 26 px, padding 26px 28px 28px,
shadow 0 18px 44px rgba(14,18,32,0.13), 0 2px 6px rgba(14,18,32,0.06). Its right edge sits 24 px left of the event
rule and its top at y 1000; width = the space from x 96 to there. Inside, left-aligned: the event month in
"Manrope" 800, 30 px, accent, letter-spacing 0.1em; 8 px below, the title in "Bricolage Grotesque" 700, 50 px, ink,
line-height 1.06, wrapping inside the card with text-wrap: balance; 14 px below, the second line in "Manrope" 700,
42 px, muted, on one line.

## Motion (window.duration = 5)

The head position p (0…1 of the series' time span) at time t, with tE = 2.05:
- Creep, 0.40 ≤ t ≤ tE: p = (37/60)·(t − 0.40) / 1.65, constant speed.
- Race, tE ≤ t ≤ 2.75: v = (t − tE) / 0.70 and p = 37/60 + (23/60)·(−1.317·v³ + 1.634·v² + 0.683·v). This keeps
  the creep's speed at the event, speeds up to about twice it, then stops smoothly at 2.75 s. Before 0.40 p = 0,
  after 2.75 p = 1.
- The head is the series interpolated at index p·60, so it reaches the event exactly at tE.

- 0.00–0.33 s: the stage sets. Metric name, span and number fade in 0.00–0.25 (power2.out); grid, labels, axis
  and date tag 0.08–0.33. The number shows S.
- 0.40–2.75 s: the line draws. The number shows the value at the head, so it creeps through the grey part and
  races up the climb. At 2.75 s it is exactly F.
- tE: the event marker pops (scale 0 → 1 over 0.18 s, back.out). tE + 0.05 → tE + 0.30: the event rule draws
  upward (easeOutCubic). tE + 0.10 → tE + 0.40: the card pops from its bottom-right corner (opacity 0 → 1,
  scale 0.9 → 1, back.out(1.6)).
- 2.75–3.05 s: the number lands: scale 1 → 1.04 → 1 (a sine bump) around its left end, on the baseline.
- 2.75–3.35 s: a ring bursts from the head: stroke 4 px, radius 20 → 80 (easeOutCubic), opacity 0.7 → 0, accent.
- 2.70–2.95 s: the badge pops from its left edge (opacity 0 → 1, scale 0.8 → 1, back.out(1.7)); 2.75–3.25 s a
  ring of the same kind (4 px, accent, opacity 0.6 → 0) grows around its circle (centre x 132, y 742) from radius
  42 to 90, drawn on the canvas behind it. 2.80–3.05 s: the "after …" line fades in and slides 12 px right into
  place.
- 3.05–5.00 s: hold; the head's halo keeps pulsing.

## File rules (a renderer depends on these)

- Write ONE self-contained file named animation.html in the current folder, and nothing else. No libraries.
- Fonts: Google Fonts only, this stylesheet:
  https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Manrope:wght@500;600;700;800&display=block
- Plain DOM text positioned with left/top or a 2D transform (translate, scale). No will-change, no 3D transforms, no
  translateZ, no backdrop-filter, no CSS filter: promoted layers rasterise text differently depending on what was
  drawn before, which breaks frame-exact seeking.
- Define window.duration and window.seek at the top level of the script, synchronously, before any await: a renderer
  reads them the moment window.ready exists. window.ready is a Promise that resolves after document.fonts.load() for
  every family and weight used, after the data and the number size are set up, and after drawing window.seek(0).
- window.seek(t) draws the exact state at time t (seconds) from scratch, for any t in any order, synchronously: it
  clears and redraws the canvas and sets every text, opacity and position from t. Never wait for
  requestAnimationFrame inside seek. Everything visible is a pure function of t: no CSS animations or transitions,
  no setTimeout or setInterval, no clocks, and no Math.random (use mulberry32 seeded with 11, rolled once at setup).
- On open it plays once: a requestAnimationFrame loop calls window.seek with the elapsed seconds up to
  window.duration, then holds the last frame. Skip that loop when location.hash is "#render" (a renderer then calls
  window.seek itself).
