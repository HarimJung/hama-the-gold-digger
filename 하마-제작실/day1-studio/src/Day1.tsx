import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  interpolate,
  Easing,
  Sequence,
} from "remotion";
import machine from "./machine.json";
import "./style.css";
import "./anatomy.css";
const G = "#D4AF37",
  C = "#FFF8E7",
  B = "#111111";
const ease = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.16, 1, 0.3, 1),
} as const;
const mono = '"SF Mono",Menlo,monospace';
export const Shell: React.FC<{
  children: React.ReactNode;
  series: string;
  light?: boolean;
  still?: boolean;
}> = ({ children, series, light = false, still = false }) => (
  <AbsoluteFill
    style={{
      background: light ? C : B,
      color: light ? B : C,
      fontFamily: '"Apple SD Gothic Neo", "Noto Sans KR", sans-serif',
      overflow: "hidden",
    }}
  >
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity: 0.08,
        backgroundImage: `radial-gradient(${light ? B : C} 1px, transparent 1px)`,
        backgroundSize: "24px 24px",
      }}
    />
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 76,
        top: still ? 60 : 185,
        height: 88,
        display: "flex",
        alignItems: "center",
        gap: 20,
        borderBottom: `1px solid ${light ? "#11111125" : "#fff8e730"}`,
        paddingBottom: 24,
      }}
    >
      <Img
        src={staticFile("hama.png")}
        style={{ width: 65, height: 84, objectFit: "contain" }}
      />
      <div style={{ fontSize: 27, fontWeight: 800, letterSpacing: 2 }}>
        {series}
      </div>
      <div style={{ marginLeft: "auto", fontFamily: mono, fontSize: 21 }}>
        NOV 02 / 2026
      </div>
    </div>
    {children}
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 76,
        bottom: still ? 50 : 230,
        display: "flex",
        justifyContent: "space-between",
        fontSize: 21,
        letterSpacing: 1.4,
        opacity: 0.7,
      }}
    >
      <span>@hamathegolddigger</span>
      <span>TORONTO · DAY 01</span>
    </div>
  </AbsoluteFill>
);
const Hama: React.FC<{ size?: number; style?: React.CSSProperties }> = ({
  size = 500,
  style,
}) => {
  const f = useCurrentFrame();
  return (
    <Img
      src={staticFile("hama.png")}
      style={{
        width: size,
        objectFit: "contain",
        translate: `0 ${Math.sin(f / 22) * 6}px`,
        ...style,
      }}
    />
  );
};
const Label: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      fontFamily: mono,
      color: G,
      fontSize: 23,
      letterSpacing: 4,
      marginBottom: 24,
    }}
  >
    {children}
  </div>
);
const Head: React.FC<{ children: React.ReactNode; size?: number }> = ({
  children,
  size = 92,
}) => (
  <div
    style={{
      fontSize: size,
      lineHeight: 1.13,
      letterSpacing: -4,
      fontWeight: 850,
      whiteSpace: "pre-line",
    }}
  >
    {children}
  </div>
);
const Copy: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div
    style={{
      fontSize: 40,
      lineHeight: 1.55,
      letterSpacing: -1.2,
      whiteSpace: "pre-line",
      ...style,
    }}
  >
    {children}
  </div>
);
const Pill: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      display: "inline-flex",
      padding: "12px 24px",
      border: `1px solid ${G}`,
      borderRadius: 50,
      color: G,
      fontSize: 26,
      fontWeight: 700,
    }}
  >
    {children}
  </div>
);
export const Machine: React.FC<{ phase?: number; freeze?: boolean }> = ({
  phase = 0,
  freeze = false,
}) => {
  const frame = useCurrentFrame();
  const f = freeze ? 90 : frame;
  const lid = interpolate(f, [0, 38], [0, -160], ease);
  const reveal = interpolate(f, [8, 45], [0, 1], ease);
  const drop = interpolate(f, [18, 65], [-105, 0], ease);
  return (
    <div className="iso hama-machine" style={{ width: 930, height: 620 }}>
      <svg
        viewBox="0 0 900 600"
        width="100%"
        height="100%"
        role="img"
        aria-label="원금에 수익이 더해져 다음 계산의 바탕이 되는 구조 비유"
      >
        <g dangerouslySetInnerHTML={{ __html: machine.base }} />
        <g dangerouslySetInnerHTML={{ __html: machine.tray }} />
        {machine.principal.map((s, i) => (
          <g key={i} dangerouslySetInnerHTML={{ __html: s }} />
        ))}
        {phase >= 1 &&
          machine.earned.map((s, i) => (
            <g
              key={i}
              opacity={reveal}
              transform={`translate(0 ${drop - i * 3 * (1 - reveal)})`}
              dangerouslySetInnerHTML={{ __html: s }}
            />
          ))}
        <g
          transform={`translate(0 ${lid})`}
          opacity={1 - reveal}
          dangerouslySetInnerHTML={{ __html: machine.lid }}
        />
        {phase >= 2 && (
          <g opacity={reveal}>
            <path
              d="M 220 420 C 100 320, 180 150, 340 150"
              fill="none"
              stroke={G}
              strokeWidth="6"
              strokeDasharray="600"
              strokeDashoffset={interpolate(f, [15, 70], [600, 0], ease)}
            />
            <path
              d="M 321 133 L 345 150 L 321 168"
              fill="none"
              stroke={G}
              strokeWidth="6"
              opacity={interpolate(f, [50, 70], [0, 1], ease)}
            />
          </g>
        )}
      </svg>
    </div>
  );
};
const Reveal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        opacity: 1,
        translate: `0 ${interpolate(f, [0, 18], [22, 0], ease)}px`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
const Hook = () => (
  <Reveal>
    <div style={{ position: "absolute", left: 80, top: 340 }}>
      <Label>HAMA'S MONEY LAB / 01</Label>
      <Head>시간은 돈을{`\n`}어떻게 바꿀까?</Head>
      <Copy style={{ marginTop: 32, color: G }}>
        하마가 그림으로 보여줄게요.
      </Copy>
    </div>
    <div
      style={{
        position: "absolute",
        right: 100,
        top: 820,
        width: 600,
        height: 600,
        borderRadius: "50%",
        border: "1px solid #d4af3755",
        background: "radial-gradient(#d4af3726,transparent 70%)",
      }}
    />
    <Hama
      size={580}
      style={{ position: "absolute", left: 265, top: 790, rotate: "-4deg" }}
    />
    <div style={{ position: "absolute", left: 80, top: 1505 }}>
      <Pill>복리 · 시간 · 돈의 구조</Pill>
    </div>
  </Reveal>
);
const Scene: React.FC<{
  step: string;
  title: string;
  body: string;
  phase: number;
}> = ({ step, title, body, phase }) => (
  <Reveal>
    <div style={{ position: "absolute", left: 80, top: 340 }}>
      <Label>{step}</Label>
      <Head size={84}>{title}</Head>
    </div>
    <div style={{ position: "absolute", left: 65, top: 760 }}>
      <Machine phase={phase} />
    </div>
    <div style={{ position: "absolute", left: 80, top: 1375, right: 160 }}>
      <Copy>{body}</Copy>
      <div style={{ fontSize: 23, opacity: 0.5, marginTop: 25 }}>
        구조 설명용 그림 · 블록 개수는 금액·수익률이 아니에요.
      </div>
    </div>
    <Hama size={210} style={{ position: "absolute", right: 145, top: 580 }} />
  </Reveal>
);
const Risk = () => (
  <Reveal>
    <div style={{ position: "absolute", left: 80, top: 345 }}>
      <Label>ONE THING TO REMEMBER</Label>
      <Head>시간만으로{`\n`}보장되진 않아요.</Head>
      <Copy style={{ marginTop: 50 }}>
        수익률과 비용에 따라 결과는 달라져요.{`\n`}손실이 나면 돈이 줄어들 수도
        있어요.
      </Copy>
    </div>
    <div
      style={{
        position: "absolute",
        left: 80,
        top: 1020,
        right: 150,
        padding: 45,
        borderTop: `2px solid ${G}`,
        borderBottom: `1px solid #fff8e730`,
      }}
    >
      <div style={{ fontSize: 30, color: G }}>하마의 오늘 한 줄</div>
      <Head size={65}>시간 + 재투자{`\n`}그리고 실제 결과</Head>
    </div>
    <Hama size={240} style={{ position: "absolute", right: 150, top: 1270 }} />
  </Reveal>
);
const End = () => (
  <Reveal>
    <div style={{ position: "absolute", left: 80, top: 345 }}>
      <Label>SAVE THE IDEA</Label>
      <Head>수익이 다시{`\n`}바탕이 되는 구조.</Head>
      <Copy style={{ marginTop: 35 }}>그림으로 기억해둬요.</Copy>
    </div>
    <Hama size={480} style={{ position: "absolute", left: 300, top: 820 }} />
    <div style={{ position: "absolute", left: 80, top: 1450 }}>
      <Pill>내일 · ETF 바구니를 열어볼게요</Pill>
    </div>
  </Reveal>
);
export const Day1Reel = () => (
  <Shell series="복리 · 시간">
    <Sequence durationInFrames={90} name="01 훅">
      <Hook />
    </Sequence>
    <Sequence from={90} durationInFrames={150} name="02 원금">
      <Scene
        step="01 / START"
        title={"먼저, 시작한 돈."}
        body={"처음 넣은 돈이 계산의 바탕이에요."}
        phase={0}
      />
    </Sequence>
    <Sequence from={240} durationInFrames={180} name="03 수익 재투자">
      <Scene
        step="02 / REINVEST"
        title={"생긴 수익을\n다시 더하면."}
        body={"수익을 빼지 않고 다시 더하는 경우예요."}
        phase={1}
      />
    </Sequence>
    <Sequence from={420} durationInFrames={180} name="04 다음 계산">
      <Scene
        step="03 / NEXT ROUND"
        title={"다음 계산의\n바탕이 달라져요."}
        body={
          "원금과 쌓인 수익을 바탕으로\n다음 수익을 계산하는 구조가 복리예요."
        }
        phase={2}
      />
    </Sequence>
    <Sequence from={600} durationInFrames={150} name="05 결과의 조건">
      <Risk />
    </Sequence>
    <Sequence from={750} durationInFrames={150} name="06 저장과 예고">
      <End />
    </Sequence>
  </Shell>
);
export const Mini = () => (
  <Shell series="ETF 조합" light still>
    <div style={{ position: "absolute", left: 76, top: 215 }}>
      <Label>SKETCH TO ETF / PREVIEW</Label>
      <Head size={87}>이름보다 먼저,{`\n`}역할 세 칸.</Head>
      <Copy style={{ fontSize: 32, marginTop: 23 }}>
        하마의 ETF 조합을 채워갈 빈 틀이에요.
      </Copy>
    </div>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 76,
        top: 560,
        display: "flex",
        gap: 20,
      }}
    >
      {["01", "02", "03"].map((n) => (
        <div
          key={n}
          style={{
            flex: 1,
            height: 390,
            border: "1px solid #11111135",
            borderRadius: 16,
            padding: 24,
            background: "#fff8e7",
          }}
        >
          <div style={{ fontFamily: mono, fontSize: 26, color: "#8d721f" }}>
            ROLE {n}
          </div>
          <div style={{ marginTop: 38, fontSize: 29 }}>역할 [ ]</div>
          <div style={{ marginTop: 30, fontSize: 26, opacity: 0.6 }}>
            ETF [ ]
          </div>
          <div style={{ marginTop: 18, fontSize: 26, opacity: 0.6 }}>
            비중 [ ]
          </div>
          <div style={{ marginTop: 32, width: 75, height: 2, background: G }} />
        </div>
      ))}
    </div>
    <div style={{ position: "absolute", left: 76, top: 1020 }}>
      <Copy style={{ fontSize: 31 }}>
        실제 종목·비중은 확인하고 채울게요.{`\n`}내일은 이 스케치를 그림으로
        펼쳐봐요.
      </Copy>
    </div>
    <Hama size={190} style={{ position: "absolute", right: 80, top: 1000 }} />
    <div
      style={{
        position: "absolute",
        left: 76,
        top: 1190,
        fontSize: 22,
        opacity: 0.55,
      }}
    >
      입력 전 템플릿 · 추천 포트폴리오가 아니에요.
    </div>
  </Shell>
);
export const SaveCard = () => (
  <Shell series="복리 · 시간" light still>
    <div style={{ position: "absolute", left: 76, top: 215 }}>
      <Label>KEEP THIS / DAY 01</Label>
      <Head size={88}>수익도 다시,{`\n`}다음의 바탕으로.</Head>
    </div>
    <div style={{ position: "absolute", left: 50, top: 480 }}>
      <Machine phase={2} freeze />
    </div>
    <div style={{ position: "absolute", left: 76, top: 1030 }}>
      <Copy style={{ fontSize: 36 }}>
        처음 넣은 돈 + 다시 더한 수익{`\n`}→ 다음 계산의 바탕
      </Copy>
      <div style={{ marginTop: 30, fontSize: 24, opacity: 0.65 }}>
        양의 수익 재투자 구조를 단순화한 그림.{`\n`}금액·수익률 예측이 아니며
        실제 결과는 달라져요.
      </div>
    </div>
  </Shell>
);
export const Morning: React.FC<{ page: number }> = ({ page }) => (
  <Shell series="하마의 아침">
    <div style={{ position: "absolute", left: 80, top: 350 }}>
      <Label>MORNING / {page === 1 ? "01" : "02"}</Label>
      <Head>
        {page === 1
          ? "오늘의 가격,\n같이 볼까요?"
          : "하마랑\n그림으로 돈 공부."}
      </Head>
      <Copy style={{ marginTop: 36 }}>
        {page === 1
          ? "BTC · ETH 가격 기록"
          : "오늘 저녁엔 복리의 구조를 볼게요."}
      </Copy>
    </div>
    {page === 1 ? (
      <>
        <div style={{ position: "absolute", left: 80, right: 160, top: 880 }}>
          {["BTC", "ETH"].map((n) => (
            <div
              key={n}
              style={{
                padding: "32px 0",
                borderTop: "1px solid #fff8e740",
                display: "flex",
                justifyContent: "space-between",
                fontFamily: mono,
                fontSize: 60,
              }}
            >
              <span>{n}</span>
              <span style={{ color: G }}>[ 가격 ]</span>
            </div>
          ))}
          <div
            style={{
              fontSize: 26,
              lineHeight: 1.7,
              opacity: 0.6,
              marginTop: 30,
            }}
          >
            통화 [ ] · 확인 시각 [ ] ET{`\n`}출처 [ ]
          </div>
        </div>
        <div
          style={{
            position: "absolute",
            left: 80,
            top: 1470,
            fontSize: 26,
            color: G,
          }}
        >
          입력 전 시안 · 가격 확인 후 발행
        </div>
      </>
    ) : (
      <>
        <Hama
          size={400}
          style={{ position: "absolute", left: 340, top: 850 }}
        />
        <div
          style={{
            position: "absolute",
            left: 80,
            right: 160,
            top: 1420,
            padding: 30,
            border: `1px solid ${G}`,
            borderRadius: 20,
          }}
        >
          <div style={{ fontSize: 32 }}>복리, 그림으로 보면 쉬울까요?</div>
          <div
            style={{
              display: "flex",
              gap: 20,
              marginTop: 25,
              fontSize: 31,
              color: G,
            }}
          >
            <span>그림으로 볼래요</span>
            <span>이미 알아요</span>
          </div>
        </div>
      </>
    )}
  </Shell>
);
export const Night: React.FC<{ page: number }> = ({ page }) => (
  <Shell series="하마의 밤">
    <div style={{ position: "absolute", left: 80, top: 350 }}>
      <Label>NIGHT / {page === 1 ? "01" : "02"}</Label>
      <Head>
        {page === 1 ? "하마는\n오늘도 공부 중." : "내일은\nETF 바구니."}
      </Head>
    </div>
    {page === 1 ? (
      <>
        <div
          style={{
            position: "absolute",
            left: 80,
            top: 770,
            width: 800,
            height: 700,
            borderRadius: 25,
            overflow: "hidden",
          }}
        >
          <Img
            src={staticFile("trench.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              filter: "sepia(.65) saturate(.45)",
            }}
          />
        </div>
        <Copy
          style={{ position: "absolute", left: 80, top: 1510, fontSize: 34 }}
        >
          트렌치 하마와 마무리하는 하루.
        </Copy>
      </>
    ) : (
      <>
        <Hama
          size={450}
          style={{ position: "absolute", left: 315, top: 820 }}
        />
        <Copy style={{ position: "absolute", left: 80, top: 1390 }}>
          스케치 옆에 완성본을 놓고,{`\n`}하나씩 열어볼게요.
        </Copy>
        <div
          style={{
            position: "absolute",
            left: 80,
            top: 1560,
            fontSize: 28,
            color: G,
          }}
        >
          궁금한 ETF 용어가 있나요? → 질문 스티커
        </div>
      </>
    )}
  </Shell>
);
