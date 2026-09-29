# Scene brief — AI Short Film Fes 2025 trailer remake

Each beat of `../filmfes2025_remake.json` is one html page that mulmocast renders frame by frame
(`html_tailwind` with `animation`). A scene is two files here:

- `scenes/<beat>.html` — the markup inside the 1280×720 stage
- `scenes/<beat>.js` — the script; it must define `async function render(frame, totalFrames, fps)`

`../build.py` wraps them (read it: `B()` and `scene_files()`): it prepends the fonts, the CSS, the three.js r147
CDN scripts (`THREE_CDN`: three.min, EffectComposer, RenderPass, ShaderPass, UnrealBloomPass, CopyShader,
LuminosityHighPassShader), the shared helpers `COMMON_JS` and `THREE_JS`, and these constants:

- `D` — the beat's length in seconds; `C` — the start time (s) of each spoken phrase in the beat (see table)
- `TOTAL_FRAMES` — frames in the whole film

and appends a black `#bf` layer that `beatFade(t, D, fadeIn, fadeOut)` drives. Put
`// requires: objects/Water, objects/Sky` (comma separated, paths under `three@0.147.0/examples/js/`, no `.js`) on the
**first line** of the .js to load extra modules for that beat only. Available and checked: objects/Water, objects/Sky,
objects/Reflector, environments/RoomEnvironment, math/SimplexNoise, geometries/RoundedBoxGeometry,
geometries/TextGeometry, loaders/FontLoader, postprocessing/BokehPass + shaders/BokehShader, postprocessing/FilmPass +
shaders/FilmShader, shaders/FXAAShader, shaders/VignetteShader, postprocessing/AfterimagePass + shaders/AfterimageShader.
Local files live in `../assets/`: `assets/waternormals.jpg` (three.js water normals) and `assets/judge.png`.
mulmocast rewrites **only `src="..."` attributes in the html** to absolute `file://` paths (relative to the script
folder); a relative path inside JavaScript does not resolve. So put the file in the .html as a hidden
`<img id='tex_x' src='assets/…' style='display:none' alt=''>` and load it in JS from that element:
`await new THREE.TextureLoader().loadAsync(el('tex_x').src)` (inside setup, before the first frame).

## Rules the renderer imposes (measured on this project — do not work around them differently)

1. Everything is a pure function of `t = frame / fps`. No `Date.now()`, no `Math.random()` (use `rnd(n)` from
   COMMON_JS), no requestAnimationFrame, no physics that integrates over frames. Frames are rendered in order,
   but each must look right from `t` alone.
2. `render()` may be async; mulmocast awaits it, then screenshots. Build heavy things once (`if (!S) S = setup()`).
3. WebGL: `new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true })`,
   `setPixelRatio(1)`, `setSize(1280, 720, false)`. `alpha: false` matters: with an alpha channel, half-transparent
   pixels let the layer underneath show through. `makeRenderer()` in THREE_JS already does this.
4. Text drawn into a canvas texture and shown in 3D: keep its colour below the bloom threshold or bloom smears it.
   Crisp typography in HTML overlays on top of the WebGL canvas is fine and often better.
5. mulmocast re-seeks every `<video>` to the beat's own time after `render()` returns — do not use `<video>`.
6. Fonts: 'Inter Tight' (400/600/800/900), 'JetBrains Mono' (400/600), 'Instrument Serif' (italic) are loaded;
   `await waitFonts()` before drawing text into a canvas.
7. Keep a frame under ~1.5 s to render on a laptop with software GL (SwiftShader): no more than ~1–2 M triangles,
   no huge shadow maps, particle counts in the tens of thousands at most.
8. No gamma pass. The renderer's output already goes to the screen as display values; a finishing pass that does
   `pow(c, 1/2.2)` (or sets textures to sRGBEncoding and re-encodes) applies gamma twice and lifts every black to
   grey — round 1 of every scene looked like pale clay because of exactly this. Leave textures at the default
   encoding and do colour grading without a gamma curve.
9. Call `beatFade(t, D, 0.2, 0.25)` at the end of render (fade in/out between beats).

## Look

Cinematic film-festival trailer. Gold (#e9c46a / #f6e0a0) and deep blue-black (#05070b), with cyan (#7fd8ff)
for "AI". Real depth: perspective cameras that move, lighting, reflections (RoomEnvironment for PBR metal),
atmosphere (fog, bloom, dust), depth of field where it helps. The bar is the Claude Opus 5.5 motion work people
post on X: 3D scenes that read as crafted, not diagrams. Every beat must still make its narration line obvious.
### Art direction (added after the first round — the first renders all looked like pale clay product shots)

- **Night-time cinematic, not a studio.** Background and fog are near-black blue (#04060b–#0c1422), never light
  grey. `FogExp2` with a dark colour. No bright white floors or white haze: floors are dark and glossy
  (colour ~#070b12, roughness 0.2–0.4) and only glow where a light hits them.
- **Contrast.** One key light (warm or cool) plus a rim light plus practical glows; about 70 % of the frame is in
  shadow. `ACESFilmicToneMapping`, exposure 0.8–1.0. Bloom only on highlights (threshold ≥ 0.8).
- **Gold is metal.** colour #c99a3c–#f0c060, metalness 1, roughness 0.2–0.35, env map from
  `PMREMGenerator(renderer).fromScene(new THREE.RoomEnvironment())`, envMapIntensity 1–1.5, and a rim light so
  edges glint. Never beige or matte.
- **Scale.** The hero object fills the frame (at least ~40 % of the frame height); nothing important is small in
  the middle of empty space. The camera always moves a little (dolly, orbit, push).
- **Type.** Large and readable, with contrast against what is behind it (add a soft dark scrim if needed).
- **Landscapes look photographic.** Sky shader with a real sun, atmospheric perspective, layered terrain ridges
  fading into haze (noise-displaced planes with enough segments), water where it fits, light shafts.

It is a remake of a 2025 trailer: never show a real date or amount — dates and prizes are shown as `XX`.

## Check your frames

Chrome cannot start inside your sandbox (it aborts), so you cannot render frames yourself. Check what you can
(`python3 ../build.py`, `node --check scenes/<beat>.js`), and reason carefully about camera framing, exposure and
timing. The lead renders your beat and sends the frames back as images for a revision round.

## Beats (id · narration · what to show)

Each beat's length `D` and phrase cues `C` are measured from the narration and live only in `../build.py`
(`TIMING`, `CUES`) — read them there. "C0", "C1"… below mean `C[0]`, `C[1]`…; write cue times as `C[i]` (plus small
offsets), never as literal seconds, so a re-recorded line only needs the numbers in build.py to change.

| id | narration | show |
|---|---|---|
| open | Imagine it, and you can see it. When AI can make movies, what will you make? | A drifting 3D nebula of warm particles; on "Imagine it" (C0) they gather into the word *Imagine* in 3D; on "When AI can make movies" (C2) they reform into a floating 16:9 screen with a play mark; on C3 the line "What will you make?" |
| title | AI Short Film Fes 2025. Powered by MulmoCast. | The title "AI SHORT FILM FES 2025" as real gold (reflective, bevelled) in 3D with light sweeping across it, dust, lens flare; "POWERED BY MULMOCAST" on C1 |
| theme | The theme: films made by people and AI, together. | Two things meet in 3D: an organic warm hand-drawn ribbon (people) and a precise cool crystalline path (AI); they touch on "together" (C2) with a burst |
| rules | Any genre, up to three minutes long, and open to everyone. | Three statements in sync (C0/C1/C2): ANY GENRE (several screens showing different kinds of film), UP TO 3:00 (a clock/ring), OPEN TO EVERYONE (a crowd lighting up) |
| prizes | There's prize money for the Grand Prix, plus Visual, Animation, Documentary, and Promotion awards. | A gold Grand Prix trophy and four award plates arriving on their names (C0..C4), PBR gold, amounts shown as ¥XX, "PRIZE POOL ¥XX" |
| judge | Chairing the jury: Satoshi Nakajima of Singularity Society. | `assets/judge.png` (a real photo of the chair — keep it undistorted and respectful) with "CHAIR OF THE JURY", the name on C1, "Singularity Society" on C2 |
| criteria | Entries are judged on creativity, structure, technical craft, and how convincingly you build a world with AI. | CREATIVITY / STRUCTURE / TECHNICAL CRAFT / A CONVINCING WORLD appearing on their cues, connected as one structure |
| dates | Send in your film before the deadline. Winners are announced online. | A real 3D split-flap board: ENTRIES CLOSE XX.XX (settles after C0), WINNERS ANNOUNCED XX.XX ONLINE (after C1) |
| experiment | It's a film festival. It's also an experiment. | Film (a strip of frames) and a lab/circuit world in one image; "A FILM FESTIVAL." on C0, "AN EXPERIMENT." on C1 |
| open_q | Technology and ethics are still full of open questions. That's exactly where the surprises are. | A maze (open questions) that, on C1, gives way to a wide real landscape at sunrise (the surprises) |
| prompt | Type a prompt. It's the first step in turning your imagination into film. Now, bring your world to life. | A prompt box types "At dawn by the sea, particles of light melt into the waves" (C0..C2); on "Now" (C2) the letters break into light and the scene becomes that sea at dawn — a real ocean with the sun on the water |
| together | The future of film begins with you and AI, together. | A warm and a cool light braiding together into one |
| close | AI Short Film Fes 2025, powered by MulmoCast. Take your first step onto the screen. | The festival screen (a hologram screen with the title and small films) in a real space; "POWERED BY MULMOCAST" on C1; the camera steps toward it from C2, ending with the title still readable; small "2025 REMAKE" on it |
