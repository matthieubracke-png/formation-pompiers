---
description: A 3D timeline in perspective draws down your story's years as dated cards flip up; the newest lands in red.
---
Make a short 3D timeline animation of this story: $ARGUMENTS

## The words

The words name whose story it is and over what span ("Year one of our bakery", "Road to launch, March to
October", "Five years of our studio"). They may list milestones; usually they don't.

- **BRAND:** the business, app or studio the words name, exactly as typed ("Hearth & Crumb"). Its first letter is
  the brand mark.
- **Units:** a span inside about a year uses months ("JAN" … "DEC", three-letter caps); with no year in the words,
  the year is 2026. A span of several years uses years ("2021"). S = the number of units from the first milestone
  to the last: 4 ≤ S ≤ 11 (a longer story keeps its last 11 years). Months run on past DEC into JAN.
- **Milestones:** exactly four, oldest first, on units d = 0, round(0.3·S), round(0.65·S) and S. The fourth is the
  newest, at the end of the span: the payoff. Use any the words give, as typed; invent the rest, specific to the
  words and consistent with each other, with real-sounding numbers rising toward the fourth. Each has:
  - a date: its unit ("MAY", or "2023"); the fourth's card shows the month with the year ("NOV 2026"), or the year;
  - a title: 2–4 words, at most 18 characters for milestones 1–3 and 24 for the fourth (for a gym, say: "Ten
    regulars", "Night classes added");
  - a note: one concrete fact, at most 40 characters (the fourth: 36), often with a number ("62 members, most
    from the block");
  - an icon from the kit below, by meaning.
  The examples only show the form: never reuse them. Write each title in its own words, never a stock pattern
  ("First …", "… opens", "… sold out", "… ships worldwide").
- **Kicker:** "BRAND · FEB – NOV 2026" for months, "BRAND · 2021 – 2026" for years.
- **Headline:** the story's title in the words' own terms, at most 30 characters, no full stop ("Year one of Hearth
  & Crumb", "Tidepool's road to launch"), never the "From … to …" pattern. Its last 1–3 words (the brand, or the
  story's key phrase) are in the accent.

## What it shows

A light, premium product infographic in real 3D. Under a kicker and a heavy two-tone headline, a year line runs in
perspective from far up-left to near down-right, past camera-facing date labels that grow as they come closer. A
thick accent line draws down it to each milestone, and as it arrives the milestone's white card flips up on a
hinge into a staircase of cards, each a little nearer. The newest card lands filled with the accent and a black
"NOW" pill pops onto its corner, while the camera settles. Cool light-grey ground, crisp white cards with soft
shadows, near-black type, one accent: red #E0313B.

### The page

- A 1080×1920 portrait stage div, scaled to fit the browser window (centred, letterboxed), overflow hidden,
  background #E4E7EB. Inside it: the WebGL canvas (1080×1920, display none: it is only read from), the visible
  output canvas (a 2D canvas 1080×1920 at left 0, top 0), then the two text blocks below as plain DOM on top.
- **Kicker:** left 90, top 236, a flex row (align-items center, gap 16 px, white-space nowrap): the brand mark, a
  38×38 px square, radius 10, background #111318, the brand's first letter centred in "Geist" 700 22 px #FFFFFF;
  then the kicker text in "Geist Mono" 600 26 px, letter-spacing 0.14em, #7A8191, upper case.
- **Headline:** left 86, top 290, "Geist" 800, 72 px, letter-spacing −0.05em, line-height 1.02, #0E1116,
  white-space nowrap, ONE line, its accent words in a span coloured #E0313B. At setup, step the size down by 2 px
  while its scrollWidth is over 900 (never below 52 px).

### The 3D scene (three.js)

- WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true }), pixel ratio 1, size 1080×1920,
  outputColorSpace SRGBColorSpace. Each rendered frame is copied onto the output canvas with drawImage (see Motion
  blur).
- **The ground** is scene.background: a CanvasTexture (colorSpace SRGBColorSpace) of a 1080×1920 canvas drawn once:
  a vertical linear gradient #EEF0F3 (0) → #E4E7EB (0.55) → #D9DCE1 (1); over it a radial gradient centred (420,
  620), radius 900, rgba(255,255,255,0.55) at 0 → transparent at 0.7; then a vignette: save, translate(540, 860),
  scale(0.8667, 1), a radial gradient radius 1500 from rgba(28,34,48,0) at 0.55 to rgba(28,34,48,0.10) at 1, filled
  over the whole canvas, restore. So every frame is opaque.
- PerspectiveCamera(30, 1080/1920, 10, 20000). D = 960 / tan(15°) ≈ 3582.7. A Group "world" holds everything.
- Helper W(sx, sy, z) = Vector3((sx − 540)·(D − z)/D, (960 − sy)·(D − z)/D, z): the world point at depth z that
  sits at stage pixel (sx, sy) when the camera rests at (0, 0, D) looking at the origin.
- Every material is MeshBasicMaterial with transparent: true, depthWrite: false and depthTest: false, so the draw
  order is set only by renderOrder (given per object below). Colours through new Color("#hex").
- Every canvas texture: CanvasTexture, colorSpace SRGBColorSpace, anisotropy = renderer.capabilities
  .getMaxAnisotropy(), minFilter LinearMipmapLinearFilter, premultiplyAlpha true, and its material
  premultipliedAlpha: true. Draw every canvas once at setup, after the fonts load.
- Rounded rects: ctx.roundRect. Letter spacing in canvas: ctx.letterSpacing, always in px; reset it to "0px" after.

### The year line (inside a Group "ruler" in world)

- A = W(207, 716, −1910), B = W(479, 1440, 150): the first and the last milestone. U = (B − A)/S; P(k) = A + k·U.
  The far end is 1.6× as far from the camera as the near end: that perspective is the look, keep these numbers.
  PHI = atan2(272, 724) (the line's screen angle from vertical); perp = (cos PHI, sin PHI, 0).
- Segments are CylinderGeometry(r, r, 1, 20, 1, true) translated by (0, 0.5, 0); to span a → b, position = a,
  quaternion = setFromUnitVectors((0, 1, 0), (b − a) normalised), scale (1, |b − a|, 1).
- **Base line:** a segment r 2.0, #B9BFCA, from P(−0.36·S) to P(1.22·S); then five tail segments of 0.04·S each
  from P(1.22·S) on, opacity 0.8, 0.64, 0.48, 0.32, 0.16. renderOrder 1.
- **Progress:** a segment r 7.5 in the accent from P(0) to the head, and a CircleGeometry(7.5, 24) cap at P(0).
  renderOrder 2.
- **Ticks:** for k = 0 … S + 1, a PlaneGeometry(1, 1) at P(k), rotation.z = PHI, scale (26, 2.5) on a
  milestone's unit and (18, 2.5) on the others, #B9BFCA; once the head has reached it, the accent's dark shade
  (each RGB channel × 0.73: #A4242B). Faint notches, never heavy dashes. renderOrder 3.
- **Labels:** for k = 0 … S + 1, the unit's name (month or year; k = S + 1 is the future unit, the one after the
  last milestone). Draw it on its own canvas at 3× scale: "Geist" 700 44 px #0E1116 on a milestone's unit, "Geist"
  600 40 px #B4BAC5 otherwise (nearly as big and bold: only the colour sets them apart), letterSpacing (−0.02 × the font px)px, the canvas measureText width + 8 px wide and 1.3 × the size
  tall, text right-aligned and vertically centred. A PlaneGeometry(width, height) translated by (−width/2, 0, 0)
  so its right-centre is the origin, at P(k) + perp·(−24), rotation.z = PHI. renderOrder 3. They face the camera
  and grow by perspective alone: near units big, far ones small.
- **Head:** at the head point H: a white CircleGeometry(30, 64) at opacity 0.7 inside a hairline RingGeometry(29.4,
  30.6, 72) #C3C9D2 (both renderOrder 5), a white CircleGeometry(15, 40) (renderOrder 6), an accent
  CircleGeometry(9.5, 40) (renderOrder 7). Lift each 2–3 units in z off the line.
- **Ripples:** two pale rings at P(S), each a Group holding a white CircleGeometry(1, 72) and a hairline
  RingGeometry(0.975, 1, 96) #141A28, both renderOrder 0 (under the line).

### The cards (each a pivot Group in world)

Slots in stage pixels, by the card's bottom-left corner, at rest:

| card | x | bottom | z | w | h |
|---|---|---|---|---|---|
| 1 | 186 | 606 | 0 | 464 | 206 |
| 2 | 252 | 833 | 50 | 474 | 206 |
| 3 | 347 | 1063 | 100 | 486 | 206 |
| 4 (payoff) | 455 | 1355 | 150 | 498 | 258 |

- The pivot sits at W(x, bottom, z). Inside it a Group scaled (D − z)/D holds, in its own pixel units: the card,
  a PlaneGeometry(w, h) centred at (w/2, h/2, 0), renderOrder 11 + 2i; its shadow, a PlaneGeometry(w + 160,
  h + 160) at (w/2, h/2, −1), renderOrder 10 + 2i (i = 0 … 3). So the hinge is the card's bottom edge.
- **Card canvas** (2w × 2h pixels, ctx.scale(2, 2), drawn in card pixels): clip to roundRect(0, 0, w, h, 22) (the payoff 26) and fill a vertical
  gradient #FFFFFF → #F3F5F8 (the payoff: the accent → the accent with each channel × 0.88, #C52B34).
  - Icon square: 92 px (the payoff 100), left 24, vertically centred, radius 18 (22), filled #E9ECF1; card 2's
    is the accent mixed 87% toward white with the icon in the accent; the payoff's is rgba(255,255,255,0.16) with
    the icon in #FFFFFF; the others' icons #4A5262. The icon: translate to the square's corner + 18% of its size,
    scale by size·0.64/64, lineWidth 3.2, round caps and joins, ctx.stroke(new Path2D(path)).
  - Text column from x = 24 + square + 24, width w − that − 24, left-aligned, as one block centred vertically:
    the date in "Geist Mono" 600, 24 px (the payoff 26), letterSpacing 1.5px, in the accent (the payoff
    rgba(255,255,255,0.78)); 12 px gap; the title in "Geist" 700, 38 px (the payoff 46), letterSpacing (−0.03 × its px)px,
    #0E1116 (the payoff #FFFFFF), line height 1.06: ONE line on cards 1–3 (step down 2 px until it fits, never
    below 30), at most 2 lines on the payoff (step down to 38); 12 px gap; the note in "Geist" 500, 26 px (the
    payoff 28), #697080 (the payoff rgba(255,255,255,0.82)), at most 2 lines, line height 1.24. Word-wrap by
    measureText, balanced: when a title or note needs 2 lines, break it between the two words that make the
    longer line as short as possible, so no line is a lone word ("1,200 orders, / 3 bakers on nights"). With df, tf, nf the three sizes and nT, nN the line counts: blockH = df + 12 + nT·tf·1.06 + 12 +
    nN·nf·1.24; the date baseline is (h − blockH)/2 + 0.82·df; the first title baseline is 0.18·df + 12 + 0.92·tf
    below it; the first note baseline is 0.14·tf + 12 + 0.95·nf below the last title baseline.
  - Then unclip and stroke a rim: roundRect inset 0.75 px, 1.5 px rgba(255,255,255,0.95) (the payoff 0.22), then
    a 0.5 px rgba(20,26,40,0.10) outline.
- **Shadow canvas** ((w + 160)×(h + 160)), cards 1–3: filter blur(26px), fill rgba(24,32,52,0.17) in
  roundRect(90, 102, w − 20, h − 10, 24); then filter blur(6px), fill rgba(24,32,52,0.10) in roundRect(84, 86,
  w − 8, h − 4, 22). The payoff, deeper so it lifts off the page: filter blur(30px), fill rgba(121,16,24,0.42) in
  roundRect(90, 112, w − 20, h − 6, 24); then filter blur(8px), fill rgba(20,24,40,0.20) in roundRect(84, 86,
  w − 8, h − 4, 22). Soft and wide, never a dark halo.
- **NOW pill:** a 128×48 canvas at 3×: roundRect(0, 0, 128, 48, 24) #0C0E13, a dot at (28, 24) radius 6 in the
  accent, "NOW" in "Geist Mono" 600 22 px, letterSpacing 2px, #FFFFFF, textBaseline middle, at (44, 25). A
  PlaneGeometry(128, 48) inside a Group at (w − 70, h − 2, 2) in the payoff card's group, renderOrder 30: it sits
  on the card's top-right corner, inside its right edge.

### The icon kit (SVG path strings in a 64×64 box, for Path2D; each is one string on one line)

- store: "M12 26 L16 14 H48 L52 26 Z M16 26 V50 H48 V26 M27 50 V38 H37 V50"
- box: "M32 12 L52 22 V44 L32 54 L12 44 V22 Z M12 22 L32 32 L52 22 M32 32 V54"
- people: "M23 21 A5 5 0 1 0 13 21 A5 5 0 1 0 23 21 M37 21 A5 5 0 1 0 27 21 A5 5 0 1 0 37 21 M51 21 A5 5 0 1 0 41 21 A5 5 0 1 0 51 21 M10 50 V39 Q10 31 18 31 Q26 31 26 39 V50 M24 50 V39 Q24 31 32 31 Q40 31 40 39 V50 M38 50 V39 Q38 31 46 31 Q54 31 54 39 V50"
- chart: "M12 52 H52 M17 52 V38 H25 V52 M29 52 V28 H37 V52 M41 52 V16 H49 V52"
- flag: "M18 54 V10 M18 13 H48 L41 22 L48 31 H18"
- star: "M32 11 L38 25 L53 26 L41 36 L45 51 L32 43 L19 51 L23 36 L11 26 L26 25 Z"
- moon: "M41 13 A20 20 0 1 0 51 41 A16 16 0 1 1 41 13 Z"
- cup: "M14 24 H44 V40 Q44 52 32 52 H26 Q14 52 14 40 Z M44 28 H48 Q54 28 54 34 Q54 40 48 40 H44 M22 10 V17 M30 10 V17 M38 10 V17"
- phone: "M24 9 H40 Q46 9 46 15 V49 Q46 55 40 55 H24 Q18 55 18 49 V15 Q18 9 24 9 Z M28 48 H36"
- pin: "M32 55 Q14 37 14 27 A18 18 0 0 1 50 27 Q50 37 32 55 Z M38 27 A6 6 0 1 0 26 27 A6 6 0 1 0 38 27"
- spark: "M32 9 L36.5 27.5 L55 32 L36.5 36.5 L32 55 L27.5 36.5 L9 32 L27.5 27.5 Z"
- bolt: "M36 8 L16 36 H31 L27 56 L48 26 H33 Z"
- heart: "M32 52 Q10 38 10 24 Q10 13 21 13 Q28 13 32 21 Q36 13 43 13 Q54 13 54 24 Q54 38 32 52 Z"
- leaf: "M14 50 Q14 16 50 14 Q50 48 16 50 M16 48 L38 28"
- globe: "M52 32 A20 20 0 1 0 12 32 A20 20 0 1 0 52 32 Z M12 32 H52 M32 12 Q20 32 32 52 M32 12 Q44 32 32 52"

## Motion (window.duration = 5)

Easings, u clamped to 0–1: eo2 = 1 − (1 − u)², eo3 = 1 − (1 − u)³, backOut(u, s) = 1 + (s + 1)(u − 1)³ +
s(u − 1)². mix(a, b, k) = a + (b − a)·k.

- **The camera settles** (his pan, roll and push, all on one curve): r = 1 − eo3(t / 3.6), dl = 480·r.
  world.rotation.z = −0.12·r, world.position = (0, −360·dl/D, 0), camera at (0, 0, D − dl) looking at
  (−180·r, 0, 0). The whole 3D group slides left, unrolls and settles up into place; it comes to rest at 3.6 s and
  holds still. The header never moves with it.
- **0.00–0.42 s, the page sets.** Kicker: opacity eo3(t / 0.32), rising 16 px into place. Headline: the same over
  0.05–0.41 s, rising 20 px. Base line and tails: opacity × eo2((t − 0.02) / 0.4). Label k and tick k: opacity
  eo3((t − 0.06 − 0.025·k) / 0.3).
- **The head.** From T0 = 0.30 s to T4 = 2.40 s it runs from P(0) to P(S): H = P(S·f), f = 1 − (1 − u)^1.3,
  u = (t − T0)/(T4 − T0). That is near-constant on screen, easing into the last date. Before T0 the progress line
  and the head are hidden. Milestone i (unit d_i) is reached at tA_i = T0 + (T4 − T0)·(1 − (1 − d_i/S)^(1/1.3)).
- **Each card flips up as the head reaches its date** (from tA_i, hidden before): u = (t − tA_i) / 0.48 (the
  payoff 0.65). pivot.rotation.x = −1.40·(1 − backOut(u, 1.3)): it starts lying back almost flat, the top edge
  away from the camera, and swings up on its bottom hinge, a touch past upright and back. pivot scale =
  mix(0.62, 1, backOut(u, 1.9)) (the payoff: mix(0.5, 1, backOut(u, 2.2)), about 8% overshoot). The card is
  fully opaque from tA_i (no fade: its first frame is a thin, solid sliver); its shadow's opacity is eo2(u).
- **The payoff (T4 = 2.40 s):** the payoff card flips as above; two ripples at P(S): ripple j's u = (t − T4 −
  0.18·j) / 0.7, shown only while 0 < u < 1, scale 16 + 34·eo3(u), the white disc at opacity 0.6·(1 − u), its
  hairline at 0.56·(1 − u).
- **The NOW pill:** u = (t − T4 − 0.36) / 0.30, hidden at u = 0, scale backOut(u, 2.2).
- **Motion blur**, as a real shutter. seek(t) first decides if anything flips: t inside (tA_i, tA_i + the card's
  flip time) for any card, or inside (T4 + 0.36, T4 + 0.66). If so, it renders K = 6 sub-frames at times
  t − (5 − k)·SH/5 for k = 0 … 5, SH = 0.5/30 s: each sets the whole scene for that time, calls renderer.render,
  then draws the WebGL canvas onto the output canvas with globalAlpha = 1/(k + 1) (a running average; the last
  sub-frame is t itself). Otherwise it sets the scene for t, renders once and draws it at globalAlpha 1. Reset
  globalAlpha to 1 after. The flips then smear like a camera's, and stills stay razor sharp.
- **3.0–5.0 s: hold.** The camera finishes its settle by 3.6 s.

## File rules (a renderer depends on these)

- Write ONE self-contained file named animation.html in the current folder, and nothing else.
- three.js from cdn.jsdelivr.net at exactly three@0.159.0 through an importmap ("three":
  "https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.module.js") and one module script. No other libraries,
  no images or textures from the web (canvases drawn in the page are fine).
- Fonts: Google Fonts only, this stylesheet:
  https://fonts.googleapis.com/css2?family=Geist:wght@500;600;700;800&family=Geist+Mono:wght@600&display=block
- Define window.duration and window.seek at the top level of the module script, synchronously, before any await
  (seek does nothing until the scene exists). window.ready is a Promise that resolves after document.fonts.ready
  and document.fonts.load() for every face used ("500 26px Geist", "600 40px Geist", "700 44px Geist",
  "800 72px Geist", "600 26px 'Geist Mono'"), then fits the headline, draws every canvas, builds the scene and draws
  window.seek(0).
- window.seek(t) draws the exact state at time t (seconds) from scratch, for any t in any order, synchronously: it
  sets every transform, opacity, colour and visibility from t, sets the DOM header's opacity and transform, and
  renders (once, or six times for motion blur) onto the output canvas. Never wait for requestAnimationFrame inside seek. Everything visible is a pure function
  of t: no CSS animations or transitions, no setTimeout or setInterval, no clocks, no Math.random.
- The header is plain DOM text with 2D transforms only: no will-change, no 3D transforms, no backdrop-filter, no
  CSS filter on text.
- On open it plays once: a requestAnimationFrame loop calls window.seek with the elapsed seconds up to
  window.duration, then holds the last frame. Skip that loop when location.hash is "#render" (a renderer then calls
  window.seek itself).
