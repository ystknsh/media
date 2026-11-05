// Models for the 3D reenactment, written in ShapeScript (MulmoTerminal's 3D plugin, @gui-chat-plugin/shapescript)
// and exported to GLB with the plugin's own shapeScriptToGlb. One GLB per moving part; units are metres, +Y up,
// the camera looks down -Z, so "front" is +Z.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

// The plugin is not a dependency of this repo: it lives in MulmoTerminal's npx cache, under a hash that varies per
// machine and version. SHAPESCRIPT_ENTRY names its dist/index.js when there is more than one cached copy.
const findShapeScriptEntry = () => {
  if (process.env.SHAPESCRIPT_ENTRY) return process.env.SHAPESCRIPT_ENTRY;
  const npxCache = path.join(os.homedir(), ".npm", "_npx");
  const entries = fs
    .readdirSync(npxCache)
    .map((hash) => path.join(npxCache, hash, "node_modules/@gui-chat-plugin/shapescript/dist/index.js"))
    .filter((entry) => fs.existsSync(entry));
  if (entries.length !== 1) throw new Error(`expected one shapescript in ${npxCache}, found ${entries.length}; set SHAPESCRIPT_ENTRY`);
  return entries[0];
};
const ss = await import(findShapeScriptEntry());

const HERE = path.dirname(new URL(import.meta.url).pathname);
fs.mkdirSync(path.join(HERE, "models"), { recursive: true });

// rounded box as the hull of eight spheres: w h d outer size, r corner radius
const rbox = (w, h, d, r, col, x = 0, y = 0, z = 0) => {
  const pts = [];
  for (const sx of [-1, 1]) for (const sy of [-1, 1]) for (const sz of [-1, 1])
    pts.push(`    sphere {\n        position ${x + sx * (w / 2 - r)} ${y + sy * (h / 2 - r)} ${z + sz * (d / 2 - r)}\n        size ${r * 2}\n        detail 16\n    }`);
  return `hull {\n    color ${col}\n${pts.join("\n")}\n}`;
};
const cyl = (d, h, col, x, y, z, extra = "") => `cylinder {\n    position ${x} ${y} ${z}\n    size ${d} ${h}\n    color ${col}\n    detail 40\n${extra}}`;

const MODELS = {
  // serving robot body: wheeled base, white pole, three round trays with raised rims
  robot_body: [
    cyl(0.62, 0.16, "#3a3f45", 0, 0.08, 0),
    cyl(0.5, 0.04, "#22262b", 0, 0.17, 0),
    rbox(0.16, 1.2, 0.1, 0.04, "#f4f4f2", 0, 0.76, -0.24),   // column at the back, so the trays are clear in the middle
    ...[0.45, 0.72, 0.99].flatMap((y) => [
      cyl(0.62, 0.035, "#ececea", 0, y, 0),
      `difference {\n    color #d8d8d6\n${cyl(0.62, 0.05, "#d8d8d6", 0, y + 0.03, 0)}\n${cyl(0.57, 0.08, "#d8d8d6", 0, y + 0.03, 0)}\n}`,
    ]),
  ].join("\n"),
  // cat head: rounded white shell with two ears; the face screen is drawn in three.js so it can change expression
  robot_head: [
    rbox(0.56, 0.4, 0.34, 0.13, "#f7f7f5", 0, 0, 0),
    `cone {\n    position -0.17 0.24 0\n    size 0.15 0.2\n    color #f7f7f5\n    detail 24\n}`,
    `cone {\n    position 0.17 0.24 0\n    size 0.15 0.2\n    color #f7f7f5\n    detail 24\n}`,
    `cone {\n    position -0.17 0.235 0.035\n    size 0.08 0.12\n    color #ffb3b3\n    detail 24\n}`,
    `cone {\n    position 0.17 0.235 0.035\n    size 0.08 0.12\n    color #ffb3b3\n    detail 24\n}`,
    rbox(0.44, 0.27, 0.06, 0.05, "#1c2026", 0, -0.01, 0.15),
  ].join("\n"),
  // seated diner, torso + head + hair; arms are separate so they can move
  person_a: null,
  person_b: null,
  // an arm reaching along +X from the shoulder at the origin: sleeve, forearm, hand
  arm_a: null,
  arm_b: null,
  // four-seat table with a portable stove and a shabu-shabu pot in the middle
  table: [
    rbox(1.3, 0.05, 0.8, 0.02, "#7a4a2a", 0, 0.72, 0),
    ...[[-0.58, -0.33], [0.58, -0.33], [-0.58, 0.33], [0.58, 0.33]].map(([x, z]) => cyl(0.05, 0.7, "#4a2d19", x, 0.35, z)),
    cyl(0.34, 0.06, "#2b2e33", 0, 0.775, 0),
    `difference {\n    color #a9b0b6\n    metallicity 0.8\n    roughness 0.3\n${cyl(0.36, 0.12, "#a9b0b6", 0, 0.865, 0)}\n${cyl(0.33, 0.12, "#a9b0b6", 0, 0.885, 0)}\n}`,
    cyl(0.33, 0.02, "#d9a441", 0, 0.885, 0),
  ].join("\n"),
  // bench behind a table
  bench: [
    rbox(1.3, 0.12, 0.45, 0.04, "#8a2f2a", 0, 0.42, 0),
    rbox(1.3, 0.6, 0.12, 0.05, "#7a2925", 0, 0.75, -0.2),
    rbox(1.2, 0.36, 0.4, 0.02, "#3a2416", 0, 0.18, 0),
  ].join("\n"),
  // plate of premium marbled beef: four slices fanned out
  plate: [
    cyl(0.34, 0.02, "#f7f3ea", 0, 0.01, 0),
    cyl(0.28, 0.02, "#eee7d8", 0, 0.015, 0),
    ...[0, 1, 2, 3].flatMap((i) => [
      `cube {\n    position ${-0.06 + i * 0.04} ${0.03 + i * 0.006} 0\n    orientation 0 ${0.08 - i * 0.05} 0\n    size 0.07 0.012 0.2\n    color #c9304a\n}`,
      `cube {\n    position ${-0.06 + i * 0.04} ${0.0365 + i * 0.006} 0.02\n    orientation 0 ${0.08 - i * 0.05} 0\n    size 0.05 0.002 0.12\n    color #f3c3c8\n}`,
    ]),
  ].join("\n"),
  // paper lantern pendant lamp
  lamp: [
    cyl(0.01, 0.8, "#222222", 0, 0.4, 0),
    `sphere {\n    position 0 0 0\n    size 0.34 0.42 0.34\n    color #ffe0a8\n    glow #ffb347\n    detail 32\n}`,
  ].join("\n"),
};

const person = (shirt) => [
  rbox(0.46, 0.6, 0.3, 0.14, shirt, 0, 0.78, 0),
  `sphere {\n    position 0 1.22 0\n    size 0.27 0.3 0.27\n    color #e9c39f\n    detail 32\n}`,
  `difference {\n    color #2b1d16\n    sphere {\n        position 0 1.25 -0.01\n        size 0.29 0.31 0.29\n        detail 32\n    }\n    cube {\n        position 0 1.12 0.12\n        size 0.4 0.24 0.3\n    }\n}`,
  rbox(0.4, 0.14, 0.42, 0.06, "#33363c", 0, 0.5, 0.12),
  `sphere {\n    position -0.048 1.235 0.122\n    size 0.032 0.04 0.02\n    color #1a1a1a\n}`,
  `sphere {\n    position 0.048 1.235 0.122\n    size 0.032 0.04 0.02\n    color #1a1a1a\n}`,
].join("\n");
const arm = (sleeve) => [
  `cylinder {\n    position 0.2 0 0\n    orientation 0.5\n    size 0.11 0.42\n    color ${sleeve}\n    detail 24\n}`,
  `cylinder {\n    position 0.55 0 0\n    orientation 0.5\n    size 0.085 0.32\n    color #e9c39f\n    detail 24\n}`,
  `sphere {\n    position 0.74 0 0\n    size 0.12 0.08 0.11\n    color #e9c39f\n    detail 24\n}`,
  `sphere {\n    position 0 0 0\n    size 0.12\n    color ${sleeve}\n    detail 24\n}`,
].join("\n");
MODELS.person_a = person("#3f5a80");
MODELS.arm_a = arm("#3f5a80");
MODELS.person_b = person("#9a4a3e");
MODELS.arm_b = arm("#9a4a3e");

for (const [name, src] of Object.entries(MODELS)) {
  fs.writeFileSync(path.join(HERE, "models", `${name}.shape`), src + "\n");
  const out = await ss.shapeScriptToGlb(src);
  const u8 = out instanceof Uint8Array ? out : new Uint8Array(out);
  fs.writeFileSync(path.join(HERE, "models", `${name}.glb`), u8);
  console.log(name.padEnd(12), u8.byteLength, "bytes");
}
