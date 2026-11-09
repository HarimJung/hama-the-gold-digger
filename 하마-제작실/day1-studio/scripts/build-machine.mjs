import fs from "node:fs";
import * as k from "../../../.agents/skills/anatomy/kit/iso-kit.mjs";
const P = k.fitProjection(
  k.boxCorners({ x: -130, y: -80, w: 260, d: 160, r: 6 }, -18, 112),
  900,
  600,
  { pad: 42, azimuth: 42 },
);
let count = 0;
const S = (p, z, h, lit = false) => {
  count++;
  return k.solidSvg(k.slabOf(p, z, h, P, 5, 0.7), {
    tone: lit ? "hi" : "mid",
    lit,
  });
};
const base = [];
for (const [x, y] of [
  [-118, -66],
  [-118, 58],
  [105, -66],
  [105, 58],
])
  base.push(S({ x, y, w: 13, d: 13, r: 2 }, -18, 8));
base.push(S({ x: -130, y: -80, w: 260, d: 160, r: 7 }, -10, 10));
for (const [x, y] of [
  [-120, -70],
  [-120, 66],
  [116, -70],
  [116, 66],
])
  base.push(S({ x, y, w: 4, d: 4, r: 0.4 }, 0, 1));
for (const y of [-52, 46]) {
  base.push(S({ x: -112, y, w: 224, d: 6, r: 1 }, 0, 4));
  for (const x of [-108, 102])
    base.push(S({ x, y: y - 3, w: 8, d: 12, r: 1 }, 4, 5));
}
base.push(S({ x: -105, y: 64, w: 210, d: 6, r: 1 }, 0, 1));
for (let i = 0; i < 15; i++)
  base.push(
    S(
      { x: -100 + i * 14, y: 64, w: 1, d: i % 5 === 0 ? 6 : 3, r: 0.1 },
      1,
      0.3,
    ),
  );
const tray = [];
tray.push(S({ x: -88, y: -41, w: 176, d: 82, r: 4 }, 5, 5));
for (const p of [
  { x: -88, y: -41, w: 176, d: 3, r: 1 },
  { x: -88, y: 38, w: 176, d: 3, r: 1 },
  { x: -88, y: -38, w: 3, d: 76, r: 1 },
  { x: 85, y: -38, w: 3, d: 76, r: 1 },
])
  tray.push(S(p, 10, 4));
for (const [x, y] of [
  [-82, -35],
  [-82, 31],
  [76, -35],
  [76, 31],
])
  tray.push(S({ x, y, w: 6, d: 6, r: 1 }, 10, 2));
const makeTokens = (positions, lit) =>
  positions.map(([x, y, z]) => S({ x, y, w: 28, d: 28, r: 2 }, z, 9, lit));
const principal = makeTokens(
  [
    [-58, -18, 10],
    [-24, -18, 10],
    [10, -18, 10],
  ],
  false,
);
const earned = makeTokens(
  [
    [44, -18, 10],
    [44, -18, 19],
  ],
  true,
);
const lid = S({ x: -91, y: -44, w: 182, d: 88, r: 4 }, 48, 6);
fs.writeFileSync(
  "src/machine.json",
  JSON.stringify({
    base: base.join(""),
    tray: tray.join(""),
    principal,
    earned,
    lid,
    parts: count,
  }),
);
fs.copyFileSync(
  new URL("../../../.agents/skills/anatomy/kit/iso.css", import.meta.url),
  "src/anatomy.css",
);
console.log(`machine: ${count} parts; amount-free explanatory metaphor`);
