---
description: A 3D city at night where a glowing gold route draws itself to your destination and shows the travel time.
---
Make a short 3D map animation of this route: $ARGUMENTS

## The words

The words are a route: "<start> to <destination>, <time> <mode>". Split at the first " to " (any case): the left part
is the start. Split the rest at its last comma: the destination, then the time phrase. The time phrase is a time
("14 min", "1 h 5 min") and optionally a mode, kept exactly as typed ("walk", "by bike", "drive", "by train").

- Show the start and the destination exactly as typed, only the first letter capitalised. A name over 28 characters
  wraps onto a second line; never cut or shrink below the sizes given.
- Distance, one decimal in km, from the time: walk 80 m/min, bike 250 m/min, drive 450 m/min, train or bus
  350 m/min ("14 min walk" → 1.1 km). No mode given: no distance, the callout's second line reads "<time>" then
  "fastest route". No time given: use 12 min walk.
- Invent three district names and one river name that suit these places (a harbour start suggests "Harborside";
  a market suggests "Market Row"). Never generic names like "Downtown" or "City Centre".

## What it shows

A miniature city at night, seen from a drone: deep navy blocks with warm lit windows. A glowing gold route draws
itself along the streets from the start to the destination while the camera follows and rises; a warm light travels
with its head and washes the walls it passes. Then a gold beacon marker drops on the destination, rings of light
spread from it and the streets around it light up, and a dark glass callout shows the trip and the time. One accent,
gold, on a navy night: the line is the brightest thing in the frame and nothing competes.

The stage is a 1080×1920 portrait div, scaled to fit the browser window (centred, letterboxed). Inside it: a WebGL
canvas 1080×1920 (three.js) and, on top, an absolutely positioned DOM layer for all text, the marker and the callout.
Keep every label, the marker and the callout inside x 60–960, y 140–1500.

City, in world units, y up, "north" is −z:
- Street grid: street centrelines at x = 10·i and z = −12·j. A block is the 7×9 rectangle between them (streets
  are 3 wide). Build blocks for i −16…20 and j −8…30 so no edge of the city ever shows.
- Each block: a plinth 7×0.3×9, #1A2240. On it a 2×2 grid of lots (3.2×4.2, 0.6 gaps), so the city reads as calm
  groups of four. Each lot gets a box building unless a seeded roll skips it (4%). Height = 1.5 + 1.5·r (r seeded
  0–1): low, near-uniform near-cubes. Capped at 1.6 for lots that touch a street the route uses. One lot in 30
  (seeded, never beside the route) is 3.6–4.4. No towers.
- Buildings: a unit BoxGeometry translated so its base sits at y 0, with a vertex colour attribute (0.6 on the
  bottom vertices, 1.0 on the top ones) so walls darken towards the ground. Three InstancedMeshes share it, each lot
  going to one of them by a seeded roll, each with a material array in BoxGeometry's face order: walls (+x, −x, +z,
  −z) MeshLambertMaterial #333D5C, vertexColors, emissive #FFFFFF, emissiveIntensity 1.1, emissiveMap = that
  mesh's window texture; roof and floor MeshLambertMaterial #3E4A70, vertexColors. castShadow and receiveShadow.
- Window textures, three, drawn once on 128×128 canvases (colorSpace sRGB) with different seeds: black, with a
  4×4 grid of 16×14 px window rects (30 px pitch, 10 px margin). Each window is lit with probability 0.38: mostly
  #FFE2A8 and #FFC97A, one in six a cool #9FC3FF; unlit windows stay black.
- River: a band 16 wide, centreline z = −42 − 0.06·(x − 20) + 3·sin(x / 30), a flat ribbon at y 0.04,
  MeshPhongMaterial #1B3F73, specular #7F9FE0, shininess 40, so it reads as water: it catches the moonlight and the
  warm head light as the route crosses. Under it a 20-wide bank band #233A63 at y 0.03. Remove every block whose
  centre is within 12.5 (in z) of the centreline.
- Bridge: where the route's third leg crosses the river, a deck 5 wide and 22 long (centred on the crossing),
  0.3 thick, top at y 0.35, MeshLambertMaterial #2A3352, with a thin rail (0.2 × 0.4) along each long edge, so the
  line crosses on something.
- Avenue: the street along z = −60 is 5 wide, #2C2A3A, a flat strip at y 0.03, with street lamps along both edges:
  small spheres radius 0.3, MeshBasicMaterial #FFD08A, 0.6 above the ground, every 5 units.
- Parks: blocks (i, j) = (−1, 1), (3, 1) and (4, 5) are parks instead: a plinth #16302B with 12 small round trees
  (spheres radius 0.8–1.2, #2F6B55 or #3C7F63, seeded spots, sitting on the plinth, castShadow).
- Ground: a 2000×2000 plane at y 0, MeshLambertMaterial #1C2440, receiveShadow.

The route follows street centrelines through grid nodes (i, j) → world (10·i, y, −12·j):
(0,0) → (0,2) → (3,2) → (3,5) → (6,5) → (6,6). Five long legs: it crosses the river on the third and runs along the
avenue on the fourth. Length L = 132. The start is (0,0), the destination (6,6) = world (60, 0, −72).
- One flat ribbon per leg (a thin box 2.6 wide at y 0.4), #FFD27A, MeshBasicMaterial with fog off: a solid warm
  gold that the bloom turns into a glowing line (gold, never white). No extra glow geometry: the bloom does the
  glow. Each leg runs from its start node to the drawn length. A disc of radius 1.3 sits on every node the line has
  passed and on the head, so corners and the head are round.
- An x-ray copy of every ribbon and disc: same colour, opacity 0.8, depthTest false, renderOrder 5, so where a
  building hides the line it still reads as one continuous glowing route.
- The head: a white disc radius 1.4 inside a #FFC24A ring (radius 1.4 to 2.1), flat at y 0.5, depthTest false,
  renderOrder 10. Under it a pulsing glow: a disc at y 0.42 with a radial-gradient texture (drawn once on a canvas,
  rgba(255,181,71,0.55) at the centre to 0 at the edge), additive blending, depthTest true; radius
  4.5·(1 + 0.6·p), opacity 1 − p, p = fract(t / 0.8).
- A warm PointLight #FFB547, intensity 150, distance 45, decay 2, sits 4 above the head and moves with it, so the
  walls beside the line light up as it passes. It fades out with the head.
- The start marker, once the head has left it: a #FFC24A ring (1.1 to 1.7) around a dark #1A2240 disc, flat,
  depthTest false.

Labels and payoff, in the DOM layer, positioned each frame by projecting their world point with the camera
(x = (v.x + 1) / 2 · 1080, y = (1 − v.y) / 2 · 1920):
- Plain DOM elements positioned with left/top or a 2D translate. No will-change, no 3D transforms, no
  translateZ, no backdrop-filter: promoted layers rasterise text differently depending on what was drawn before,
  which breaks frame-exact seeking.
- Font: DM Sans. Districts 44 px 600 #B8C2DE, title case, with a dark halo (text-shadow 0 0 6px #0B1024 repeated
  three times). River name 44 px italic 600 #7FA8E8, same halo. District A at world (40, 0, −34), district B at
  (12, 0, −56), district C at (28, 0, −80); the river name at (6, 0, z of the river centreline at x 6). A label is
  hidden whenever its box would cross the stage edge (x 0–1080), never clamped or cut off.
- Start pill: the start name, 50 px 700 #F4F6FB, a dark glass pill (background rgba(14,20,38,0.88), border 1.5px
  solid rgba(255,231,163,0.35), padding 14px 26px, radius 999px, shadow 0 10px 30px rgba(0,0,0,0.45)), its left edge
  44 px right of the projected start point and vertically centred on it (if it would cross x 960, put it on the left
  side instead). It fades out as the camera leaves it: opacity falls to 0 as its projected y goes from 1380 to 1500.
- Beacon marker (our own, never a teardrop map pin): an inline SVG 80×128 px: a circle 76 px across, white fill, a
  10 px #FFC24A ring and an 18 px #FFC24A centre dot, on a 6 px wide #FFC24A stem 46 px long whose bottom end is the
  projected destination point. Under it a soft glow ellipse 72×20 px, rgba(255,194,74,0.5), blur 6px.
- When it lands, the destination lights up: a second warm PointLight #FFC24A, distance 40, decay 2, 4 above the
  destination, fades from 0 to intensity 180, so the walls and streets around it glow gold.
- Callout: a dark glass card (background rgba(13,19,36,0.92), border 1.5px solid rgba(255,255,255,0.14), radius
  34px, padding 28px 40px 30px, shadow 0 18px 48px rgba(0,0,0,0.5)) with a 30 px triangle tail of the same colour at
  its bottom centre. Line 1: "From " and the start name, 42 px 600 #A7B2CF. Line 2: the destination, 52 px 700
  #F4F6FB, max-width 820 px. Line 3: the time, 92 px 800 #FFD27A, then the mode and distance ("walk · 1.1 km"),
  48 px 600 #A7B2CF, baseline aligned. The tail's tip sits 136 px above the destination point (just above the
  marker); slide the card sideways to keep it inside x 60–960 (the tail stays over the marker).
- The arrival: two thin, bright #FFD27A rings flat on the ground at the destination (MeshBasicMaterial, additive,
  depthTest false, ring width 6% of the radius), each growing from radius 2 to 18 over 0.6 s (easeOutCubic) while
  fading from 1 to 0, the second starting 0.15 s after the first. The bloom makes them glow.

## Look

- Renderer: antialias, preserveDrawingBuffer, pixel ratio 1, size 1080×1920, sRGB output, NoToneMapping, shadow map
  on (PCFSoftShadowMap).
- Bloom: draw through an EffectComposer (pixel ratio 1, size 1080×1920): RenderPass(scene, camera), then
  UnrealBloomPass(new Vector2(1080, 1920), strength 0.55, radius 0.5, threshold 0.6), then OutputPass. seek ends with
  composer.render(), never renderer.render. Only the route, the head, the lamps and the brightest windows
  cross the threshold, so the glow stays on what matters.
- Background and fog #121933. Fog near = 1.4 × camera distance, far = 3.2 × camera distance, updated every frame:
  the far city sinks into the night, and no horizon line or city edge ever shows.
- HemisphereLight sky #AFC2FF, ground #141B30, intensity 1.3. A moonlight DirectionalLight #C8D4FF intensity 0.9
  from the upper left and behind the city (direction (−0.5, 1, −0.45)), castShadow, map 4096², orthographic shadow
  camera ±150 around the route's middle, bias −0.0004, normalBias 0.6. These numbers are tuned for three.js r159's
  default physically based lights: don't rescale them.
- The result to aim for: roofs ≈ #444663 catching the moon, walls ≈ #2A2C41 dotted with warm windows, streets
  ≈ #1A1C33, the river a cooler #2D3661 band, the line a hot gold glow. Rich and lit, never a dark empty frame.

## Camera (PerspectiveCamera fov 45, near 1, far 900)

Spherical around a ground target: position = target + r·(cos el·sin az, sin el, cos el·cos az), lookAt target.
az 0 looks north. The camera is turned 22–34° off the street grid, so streets run on the diagonal and the route's
right angles read as a zigzag with depth.
- Start: r 64, el 28°, az −34°: low, close to the start, the far city sinking into the dark at the top.
- Fit (work this out once at setup): with el 46°, az −22° and target T = the middle of the bounding box of the
  route nodes from the second one on, rFit = the smallest r (step 1 from 60) at which those nodes and the marker's head
  (destination + (0, 10, 0)) project inside x 110–970, y 560–1500. The start is left out on purpose: it slides off
  the bottom, so the route enters from the bottom edge and zigzags up the whole frame.
- Every frame, with k = easeInOutSine(clamp(t / 2.7)) and s = smoothstep(1.8, 5.0, t):
  el = mix(28, 46, k); az = mix(−34, −25, k) + 3·s; r = mix(64, 1.1·rFit, k) − 0.1·rFit·s; target =
  mix(follow, T, smoothstep(0.9, 2.7, t)), where follow = the average of the route points at 12 even distances from
  D − 12 to D + 20 (clamped to 0…L) and D is the drawn distance. So the camera tracks the head smoothly through the
  corners, rises to show the whole route, and keeps a slow push-in through the payoff and the hold: it never stops
  dead.

## Motion (window.duration = 5)

- 0.00–0.25 s: the head pops in (scale 0 → 1, back.out). The start pill fades in and rises 14 px, 0.10–0.40 s.
- 0.00–2.40 s: the route draws from the first frame: D = L · easeInOutSine(t / 2.4). The camera follows (above).
- 0.5–1.9 s: labels fade in and rise 14 px over 0.35 s each: district A at 0.5, B at 0.9, the river at 1.3, C at 1.7.
- 2.35–2.65 s: the beacon marker drops from 240 px above onto the destination (easeOutBounce), its glow growing
  from 0.4 to 1, and squashes on the first impact (scaleX 1.12, scaleY 0.86 from its bottom, back to 1 over 0.12 s).
  The head, its glow and its light fade out 2.35–2.55 s; the destination light fades in 2.45–2.85 s.
- 2.50–3.25 s: the two arrival rings.
- 2.55–2.95 s: the callout pops: opacity 0 → 1 and scale 0.86 → 1 (back.out(1.6)), from its tail.
- 2.95–5.00 s: hold on the full route, marker and callout while the camera keeps its slow push-in.

## File rules (a renderer depends on these)

- Write ONE self-contained file named animation.html in the current folder, and nothing else.
- three.js from cdn.jsdelivr.net at exactly three@0.159.0, through an importmap and one module script:
  "three": "https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.module.js" and
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.159.0/examples/jsm/". Import EffectComposer, RenderPass,
  UnrealBloomPass and OutputPass from "three/addons/postprocessing/<Name>.js". No other libraries, no controls, no
  images or textures from the web (canvas textures drawn in the page are fine).
- Fonts: Google Fonts only, this stylesheet:
  https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&display=block
- Define window.duration and window.seek at the top level of the module script, synchronously, before any await: a
  renderer reads them the moment window.ready exists. window.ready is a Promise that resolves after
  document.fonts.load() for every weight and style used, after the scene is built, and after drawing window.seek(0).
- window.seek(t) draws the exact state at time t (seconds) from scratch, for any t in any order, synchronously: it
  sets every transform, opacity and DOM position from t, then calls composer.render(). Never wait for
  requestAnimationFrame inside seek. Everything visible is a pure function of t: no CSS animations or transitions,
  no setTimeout or setInterval, no clocks, and no Math.random (use mulberry32 seeded with 7, rolled once at setup).
- On open it plays once: a requestAnimationFrame loop calls window.seek with the elapsed seconds up to
  window.duration, then holds the last frame. Skip that loop when location.hash is "#render" (a renderer then calls
  window.seek itself).
