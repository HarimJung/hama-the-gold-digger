// tax 카테고리 표지 물건 — 동전 깎개 (coin skimmer).
//
// 1초에 읽혀야 한다. 그래서 물건은 하나다: 동전 20닢 탑.
// 날이 85 높이로 지나가며 위 3닢(=15%)을 밀어낸다. 15% 가 숫자가 아니라 그림이다.
// 20닢 중 3닢 — 센 사람과 눈으로 본 사람이 같은 답을 얻는다.
//
// node build.mjs --light     preview-light.html (확인용)
// node build.mjs --svg       object.svg         (표지에 넣을 조각)
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../../.claude/skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "../../../.claude/skills/anatomy/scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));

// 하마 토큰을 아나토미 변수 위에 덮는다. 색 정본은 엔진/template.html 의 :root 다.
// 동전 = 골드(이득·저장), 깎이는 몫과 날 = 로즈(손해), 나머지 구조 = 크림.
const HAMA_CSS = `
.iso{--anatomy-page:#FDF8EC;--anatomy-card:#FDF8EC;--anatomy-text:#6E6859;--anatomy-strong:#2A2622;--anatomy-muted:#8A7F66;
  --anatomy-paper:#FFFFFF;--anatomy-face:#FFFFFF;--anatomy-top:#FFFFFF;
  --anatomy-shade-0:#E4D8BB;--anatomy-shade-1:#EDE3CC;--anatomy-shade-2:#F5EEDC;--anatomy-shade-3:#FBF6EA;
  --anatomy-lit-top:#FFFFFF;--anatomy-lit-shade:#F5EEDC;
  --anatomy-hi:#2A2622;--anatomy-mid:#6E6859;--anatomy-lo:#B9AE93;--anatomy-faint:#E6DCC4;--anatomy-lit:#8E2238;
  --anatomy-halo:#B9A87C;--anatomy-halo-opacity:.30;--anatomy-dot:#2A2622;}
.hm-gold .iso-top{fill:#F7E6B4}
.hm-gold .iso-shade[data-shade="0"]{fill:#C8A445}
.hm-gold .iso-shade[data-shade="1"]{fill:#D6B557}
.hm-gold .iso-shade[data-shade="2"]{fill:#E3BE5A}
.hm-gold .iso-shade[data-shade="3"]{fill:#EFD896}
.hm-gold .iso-fill{fill:#F7E6B4}
.hm-gold .iso-line[data-tone="faint"]{stroke:#B98F2A}
.hm-rose .iso-top{fill:#FCE3E7}
.hm-rose .iso-shade[data-shade="0"]{fill:#D44F68}
.hm-rose .iso-shade[data-shade="1"]{fill:#E05A74}
.hm-rose .iso-shade[data-shade="2"]{fill:#E8637C}
.hm-rose .iso-shade[data-shade="3"]{fill:#F08BA0}
.hm-rose .iso-fill{fill:#FCE3E7}
.hm-rose .iso-line{stroke:#8E2238}
`;


const WIDTH = 1000;
const HEIGHT = 820;

// ── 모델 ─────────────────────────────────────────────────────────────────
const COINS = 20;                 // 배당 한 해치
const CUT = 3;                    // 조약이 안 막아주는 몫
const DISC = 5.4;                 // 한 닢 두께
const KEPT = COINS - CUT;
const SHARE = CUT / COINS;        // 0.15
const BLADE_Z = KEPT * DISC;      // 날 높이 = 남는 몫의 꼭대기

const BASE = { x: -112, y: -86, w: 252, d: 172, r: 10 };
const BASE_H = 15;
const FOOT_H = 6;

const STACK = [-20, 0];
const COIN_R = 40;
const POSTS = [-70, 70];          // 날 기둥의 y
const POST_X = -20;
const BEAM_Z = COINS * DISC + 26;
const GAUGE = [36, 54];          // 눈금 기둥
const CATCH = [104, 6];           // 밀려난 닢이 떨어지는 접시

const P = k.fitProjection(
  [
    ...k.boxCorners(BASE, -BASE_H - FOOT_H, 0),
    [POST_X, POSTS[0], BEAM_Z + 24],
    [POST_X, POSTS[1], BEAM_Z + 24],
    [STACK[0] + COIN_R, STACK[1], COINS * DISC],
    [GAUGE[0], GAUGE[1], COINS * DISC + 10],
    [CATCH[0], CATCH[1], 0],
  ],
  WIDTH,
  HEIGHT,
  { pad: 26, azimuth: 46 },
);

const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (pts) => [...pts].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));

// ── 받침판 ───────────────────────────────────────────────────────────────
function base() {
  const out = [`<path class="iso-halo" d="${k.haloOf(BASE, -BASE_H - FOOT_H, BASE_H, P)}"/>`];
  for (const [x, y] of byDepth(k.corners(BASE, 24))) {
    out.push(S(k.cylinder(x, y, 8.4, -BASE_H - FOOT_H, 2, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 6.4, -BASE_H - FOOT_H + 2, FOOT_H - 2, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(BASE, -BASE_H, BASE_H, P, 10, 1.8), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(BASE, 7), 0, P), { tone: "lo" }));
  const screws = k.corners(BASE, 12);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.5, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.52 }));

  // 동전이 앉는 자리 — 얕은 홈
  out.push(L(k.ring(STACK[0], STACK[1], COIN_R + 5, 0, P, 56), { tone: "faint" }));
  out.push(S(k.cylinder(STACK[0], STACK[1], COIN_R + 3, 0, 1.6, P, 52), { tone: "lo", crease: "none" }));

  // 눈금 띠 — 뒷변
  const strip = { x: BASE.x + 22, y: BASE.y + 7, w: BASE.w - 44, d: 7.5, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.7, P, 3), { tone: "lo", crease: "none" }));
  const t = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 5, 5, strip.y + 1, 0.7, [2.2, 4], P);
  out.push(L(t.minor, { tone: "lo" }), L(t.major, { tone: "mid" }));
  out.push(D([at([strip.x + 2, strip.y + 3.7, 0.7]), at([strip.x + strip.w - 2, strip.y + 3.7, 0.7])], { size: 0.46 }));

  // 라벨판 — 앞변
  const lab = { x: -52, y: BASE.y + BASE.d - 16, w: 104, d: 10, r: 1.6 };
  out.push(S(k.slabOf(lab, 0, 1.2, P, 3, 0.3), { tone: "lo" }));
  for (const f of [0.3, 0.5, 0.7]) {
    out.push(L(k.lineOnTop([lab.x + 8, lab.y + lab.d * f], [lab.x + lab.w - 8, lab.y + lab.d * f], 1.2, P), { tone: "faint", free: true }));
  }
  out.push(D([at([lab.x + 4, lab.y + lab.d / 2, 1.2]), at([lab.x + lab.w - 4, lab.y + lab.d / 2, 1.2])], { size: 0.42 }));
  return out.join("");
}

// ── 동전 한 닢 ───────────────────────────────────────────────────────────
function disc(z, lit) {
  const out = [S(k.cylinder(STACK[0], STACK[1], COIN_R, z, DISC, P, 60, 0.7), { tone: lit ? "hi" : "mid", crease: "lo", lit })];
  out.push(L(k.ring(STACK[0], STACK[1], COIN_R - 4.5, z + DISC, P, 60), { tone: lit ? "lit" : "faint" }));
  return out.join("");
}

// 남는 몫 — 날 아래
function kept() {
  const out = [];
  for (let i = 0; i < KEPT; i++) out.push(`<g class="hm-gold">${disc(i * DISC, false)}</g>`);
  // 다섯 닢마다 테두리를 굵게 — 세지 않아도 양이 읽힌다
  for (let i = 5; i < KEPT; i += 5) {
    out.push(L(k.sideArc(STACK[0], STACK[1], COIN_R, i * DISC, P, 34), { tone: "lo" }));
  }
  return out.join("");
}

// 깎이는 몫 — 날 위. 통째로 움직인다
function cutStack() {
  const out = [];
  for (let i = 0; i < CUT; i++) out.push(`<g class="hm-rose">${disc(BLADE_Z + i * DISC, false)}</g>`);
  return out.join("");
}

// ── 날과 그 구조 ─────────────────────────────────────────────────────────
function gate(back) {
  const out = [];
  const py = back ? POSTS[0] : POSTS[1];
  out.push(S(k.cylinder(POST_X, py, 9.5, 0, 4, P, 30), { tone: "lo" }));
  out.push(L(k.ring(POST_X, py, 9.5, 4, P, 26), { tone: "faint" }));
  out.push(S(k.cylinder(POST_X, py, 7, 4, BEAM_Z - 4, P, 28), { tone: "mid", crease: "none" }));
  // 스프링 — 기둥을 감는 링
  for (let i = 0; i < 9; i++) out.push(L(k.sideArc(POST_X, py, 8.4, 14 + i * 9, P, 18), { tone: "lo" }));
  out.push(D([at([POST_X, py, 4])], { size: 0.5, tone: "lo" }));
  if (back) return out.join("");

  // 상부 빔
  const beam = { x: POST_X - 11, y: POSTS[0] - 11, w: 22, d: POSTS[1] - POSTS[0] + 22, r: 3.5 };
  out.push(S(k.slabOf(beam, BEAM_Z, 13, P, 5, 0.8), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(beam, 4), BEAM_Z + 13, P, 5), { tone: "faint" }));
  out.push(D([POSTS[0] + 3, POSTS[1] - 3].map((y) => at([POST_X, y, BEAM_Z + 13])), { size: 0.5, tone: "lo" }));

  // 조절 나사 — 날 높이를 정하는 것
  out.push(S(k.cylinder(POST_X, 0, 6, BEAM_Z + 13, 13, P, 26), { tone: "mid" }));
  out.push(L(k.knurl(POST_X, 0, 6, BEAM_Z + 13, BEAM_Z + 26, 26, P), { tone: "lo" }));
  out.push(L(k.lineOnTop([POST_X, 0], [POST_X + 6, 0], BEAM_Z + 26, P), { tone: "hi" }));
  out.push(D([at([POST_X, 0, BEAM_Z + 26])], { size: 0.55, tone: "hi" }));

  // 나사에서 날까지 내려오는 대
  out.push(S(k.cylinder(POST_X, 0, 3, BLADE_Z + 4, BEAM_Z - BLADE_Z - 4, P, 20), { tone: "mid", crease: "none" }));
  return out.join("");
}

// 날 자체 — 이 그림에서 유일하게 불이 들어온 부품
function blade() {
  // 밀어내는 쪽으로만 길다. 탑을 덮지 않아야 위 세 닢이 보인다
  const plan = { x: STACK[0] - COIN_R - 7, y: -11, w: COIN_R * 2 + 14 + 54, d: 22, r: 4 };
  const out = [`<g class="hm-rose">${S(k.slabOf(plan, BLADE_Z, 3.4, P, 4, 0.5), { tone: "hi" })}</g>`];
  out.push(L(k.planOutline(k.insetPlan(plan, 4), BLADE_Z + 3.4, P, 4), { tone: "lit" }));
  out.push(D([at([plan.x + 6, 0, BLADE_Z + 3.4]), at([plan.x + plan.w - 6, 0, BLADE_Z + 3.4])], { size: 0.5, tone: "lit" }));
  for (const py of POSTS) {
    out.push(S(k.slabOf({ x: POST_X - 6, y: py < 0 ? py : py - 8, w: 12, d: 8, r: 2 }, BLADE_Z - 1, 5, P, 2, 0.3), { tone: "mid" }));
  }
  return out.join("");
}

// ── 눈금 기둥: 날이 어디 섰는지 ─────────────────────────────────────────
function gauge() {
  const out = [];
  const [x, y] = GAUGE;
  const top = COINS * DISC + 8;
  out.push(S(k.cylinder(x, y, 9, 0, 5, P, 28), { tone: "lo" }));
  out.push(S(k.slabOf({ x: x - 3.4, y: y - 3.4, w: 6.8, d: 6.8, r: 1 }, 5, top - 5, P, 2, 0.4), { tone: "mid" }));
  // 틱 — 닢마다 하나, 다섯째마다 길게
  const ticks = [];
  const majors = [];
  for (let i = 0; i <= COINS; i++) {
    const z = i * DISC;
    const a = at([x - 3.4, y, z]);
    const b = at([x - 3.4 - (i % 5 ? 3.4 : 7), y, z]);
    (i % 5 ? ticks : majors).push(`M${a[0].toFixed(2)} ${a[1].toFixed(2)}L${b[0].toFixed(2)} ${b[1].toFixed(2)}`);
  }
  out.push(L(ticks.join(""), { tone: "lo" }), L(majors.join(""), { tone: "mid" }));
  // 날이 선 자리를 가리키는 침
  out.push(`<g class="hm-rose">${S(k.slabOf({ x: x - 13, y: y - 2, w: 11, d: 4, r: 1 }, BLADE_Z - 1, 2.6, P, 2, 0.3), { tone: "hi" })}</g>`);
  out.push(D([at([x - 13, y, BLADE_Z + 0.3])], { size: 0.55, tone: "lit" }));
  out.push(D([at([x - 3.4, y, 0]), at([x - 3.4, y, COINS * DISC])], { size: 0.46, tone: "lo" }));
  return out.join("");
}

// ── 받는 접시: 깎인 몫이 가는 곳 ────────────────────────────────────────
function catcher() {
  const out = [];
  const [x, y] = CATCH;
  out.push(S(k.cylinder(x, y, 30, 0, 8, P, 48), { tone: "mid" }));
  out.push(L(k.ring(x, y, 30, 8, P, 48), { tone: "lo" }));
  out.push(L(k.ring(x, y, 24, 8, P, 48), { tone: "faint" }));
  out.push(S(k.cylinder(x, y, 24, 2.4, 1.6, P, 44), { tone: "lo", crease: "none" }));
  out.push(D([at([x - 30, y, 8]), at([x + 30, y, 8])], { size: 0.46, tone: "lo" }));
  return out.join("");
}

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    `A stack of ${COINS} coins on a base plate. A blade on two sprung posts sits at the height of ${KEPT} coins, so the top ${CUT} ride above it. The screw on the beam sets that height, a gauge column beside the stack reads it, and the ${CUT} coins above the blade slide off into a catch dish. ${CUT} of ${COINS} is ${Math.round(SHARE * 100)} percent.`,
  body: [
    base(),
    gate(true),
    gauge(),
    catcher(),
    kept(),
    blade(),
    `<g data-part="cut">${cutStack()}</g>`,
    gate(false),
  ],
});

if (process.argv.includes("--svg")) {
  writeFileSync(join(HERE, "object.svg"), svg);
  console.log("wrote object.svg");
} else {
  const theme = process.argv.includes("--light") ? "light" : "dark";
  const live = `
const P=${JSON.stringify(P)};
const CATCH=${JSON.stringify(CATCH)},STACK=${JSON.stringify(STACK)},BLADE_Z=${BLADE_Z},CUT=${CUT},COINS=${COINS};
const stage=document.querySelector(".iso-stage"),svg=stage.querySelector("svg");
const cut=svg.querySelector('[data-part="cut"]');
const readout=document.querySelector("[data-readout]");
let t=0,frame=0,last=0,visible=false;
const ease=(u)=>u<=0?0:u>=1?1:1-Math.pow(1-u,3);
function draw(){
  const u=ease(((t%6)-2.6)/1.6);
  const dx=(CATCH[0]-STACK[0])*u, dy=(CATCH[1]-STACK[1])*u, dz=-(BLADE_Z-9)*u*u;
  cut.setAttribute("transform",translateAlong(P,[dx,dy,dz]));
  const text=u>0.95?CUT+" of "+COINS+" gone · "+(COINS-CUT)+" left":"blade set at "+(COINS-CUT)+" of "+COINS;
  if(readout&&readout.textContent!==text)readout.textContent=text;
}
function tick(now){const dt=last?Math.min((now-last)/1000,1/30):1/60;last=now;t+=dt;draw();frame=visible?requestAnimationFrame(tick):0;}
new IntersectionObserver((e)=>{visible=e[e.length-1].isIntersecting;if(visible&&!frame){last=0;frame=requestAnimationFrame(tick);}},{rootMargin:"120px 0px"}).observe(stage);
draw();
`;
  const body = k.plateHtml({
    fig: "Fig 1",
    title: "Coin skimmer",
    hint: "Watch the top come off",
    readout: `blade set at ${KEPT} of ${COINS}`,
    keys: [
      { mark: "lit", label: `The blade, and the ${CUT} coins riding above it` },
      { mark: "raised", label: `${KEPT} coins stay under the blade` },
    ],
    caption:
      `A stack of ${COINS} coins. The blade sits at the height of ${KEPT}, so the top ${CUT} ride above it and slide off. ${CUT} of ${COINS} is ${Math.round(SHARE * 100)} percent, and the gauge column reads where the blade stands.`,
    body: `<style>${HAMA_CSS}</style><div class="iso-stage">${svg}</div>`,
  });
  writeFileSync(
    join(HERE, theme === "light" ? "preview-light.html" : "preview.html"),
    k.pageHtml({ title: "Coin skimmer", theme, body, script: kitScript() + live }),
  );
  console.log("wrote", theme === "light" ? "preview-light.html" : "preview.html");
}
