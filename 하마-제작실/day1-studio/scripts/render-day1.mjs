import { bundle } from "@remotion/bundler";
import {
  selectComposition,
  renderMedia,
  renderStill,
} from "@remotion/renderer";
import path from "node:path";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const stills = [
  ["Day1-Mini", "day1-mini"],
  ["Day1-Save", "day1-save"],
  ["Morning-1", "day1-morning-1"],
  ["Morning-2", "day1-morning-2"],
  ["Night-1", "day1-night-1"],
  ["Night-2", "day1-night-2"],
];
for (const [id, name] of stills) {
  const composition = await selectComposition({ serveUrl, id });
  await renderStill({
    serveUrl,
    composition,
    output: `out/${name}.png`,
    imageFormat: "png",
  });
  console.log(`saved ${name}.png`);
}
const composition = await selectComposition({ serveUrl, id: "Day1-Reel" });
for (const frame of [0, 45, 135, 285, 465, 660, 810]) {
  await renderStill({
    serveUrl,
    composition,
    frame,
    output: `out/review-${frame}.png`,
    imageFormat: "png",
  });
}
await renderMedia({
  serveUrl,
  composition,
  outputLocation: "out/day1-reel.mp4",
  codec: "h264",
  crf: 18,
  concurrency: 4,
  onProgress: ({ progress }) => {
    if (Math.round(progress * 100) % 20 === 0) process.stdout.write(".");
  },
});
console.log("\nSaved day1-reel.mp4");
