import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  interpolate,
  Easing,
  Sequence,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import plan from "./day1-v2.json";
const ink = "#111111",
  paper = "#FFF8E7",
  gold = "#D4AF37";
const timing = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
  easing: Easing.bezier(0.2, 0.8, 0.2, 1),
} as const;
const font = '"Apple SD Gothic Neo", "Noto Sans KR", sans-serif';
const line = "2px solid #111111";
export const Photo: React.FC<{
  src?: string;
  style?: React.CSSProperties;
  caption?: string;
}> = ({ src = "trench.jpg", style, caption }) => (
  <div
    style={{
      padding: 14,
      background: paper,
      border: line,
      boxShadow: "8px 9px 0 #111111",
      ...style,
    }}
  >
    <Img
      src={staticFile(`day1-v2/${src}`)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        display: "block",
      }}
    />
    {caption && (
      <div style={{ fontSize: 24, textAlign: "center", paddingTop: 8 }}>
        {caption}
      </div>
    )}
  </div>
);
export const Frame: React.FC<{
  children: React.ReactNode;
  series: string;
  mini?: boolean;
}> = ({ children, series, mini }) => (
  <AbsoluteFill
    style={{
      background: paper,
      color: ink,
      fontFamily: font,
      overflow: "hidden",
    }}
  >
    <div
      style={{
        position: "absolute",
        left: 64,
        right: 64,
        top: mini ? 46 : 205,
        display: "flex",
        alignItems: "center",
        gap: 16,
        borderBottom: line,
        paddingBottom: 18,
        height: 82,
      }}
    >
      <Img
        src={staticFile("day1-v2/trench.jpg")}
        style={{
          width: 62,
          height: 62,
          objectFit: "cover",
          objectPosition: "50% 55%",
          borderRadius: "50%",
          border: "1.5px solid #111",
        }}
      />
      <b style={{ fontSize: 28 }}>{series}</b>
      <span style={{ marginLeft: "auto", fontSize: 23, fontWeight: 600 }}>
        2026.11.02
      </span>
    </div>
    {children}
    <div
      style={{
        position: "absolute",
        left: 66,
        right: 66,
        bottom: mini ? 43 : 225,
        borderTop: "1px solid #11111150",
        paddingTop: 20,
        display: "flex",
        justifyContent: "space-between",
        fontSize: 22,
      }}
    >
      <span>@hamathegolddigger</span>
      <span>하마의 돈 캐기 · Day 1</span>
    </div>
  </AbsoluteFill>
);
const Title: React.FC<{
  children: React.ReactNode;
  top?: number;
  size?: number;
}> = ({ children, top = 365, size = 94 }) => (
  <div
    style={{
      position: "absolute",
      left: 76,
      right: 140,
      top,
      fontWeight: 850,
      fontSize: size,
      lineHeight: 1.16,
      letterSpacing: -4,
      whiteSpace: "pre-line",
    }}
  >
    {children}
  </div>
);
const Subtitle: React.FC<{
  children: React.ReactNode;
  top?: number;
  size?: number;
}> = ({ children, top = 1390, size = 38 }) => (
  <div
    style={{
      position: "absolute",
      left: 76,
      right: 150,
      top,
      fontSize: size,
      lineHeight: 1.5,
      letterSpacing: -1,
      whiteSpace: "pre-line",
    }}
  >
    {children}
  </div>
);
const Tape: React.FC<{ style?: React.CSSProperties }> = ({ style }) => (
  <div
    style={{
      position: "absolute",
      width: 180,
      height: 45,
      background: gold,
      opacity: 0.75,
      rotate: "-7deg",
      ...style,
    }}
  />
);
const Stamp: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div
    style={{
      position: "absolute",
      padding: "12px 25px",
      border: line,
      borderRadius: 60,
      fontSize: 28,
      fontWeight: 750,
      background: gold,
      ...style,
    }}
  >
    {children}
  </div>
);
const Pickaxe = () => {
  const f = useCurrentFrame();
  return (
    <svg
      viewBox="0 0 140 140"
      style={{
        width: 160,
        height: 160,
        position: "absolute",
        right: 145,
        top: 1210,
        rotate:
          interpolate(f, [0, 10, 23, 45], [-25, -65, 10, -25], timing) + "deg",
      }}
    >
      <path
        d="M64 53 L102 123"
        stroke={ink}
        strokeWidth="19"
        strokeLinecap="round"
      />
      <path
        d="M64 53 L102 123"
        stroke={gold}
        strokeWidth="13"
        strokeLinecap="round"
      />
      <path
        d="M12 73 Q36 15 117 26 L115 39 Q55 37 22 82Z"
        fill={gold}
        stroke={ink}
        strokeWidth="4"
      />
      <path d="M65 41 L74 58" stroke={ink} strokeWidth="4" />
    </svg>
  );
};
const Hero = () => {
  const f = useCurrentFrame();
  return (
    <>
      <Title>복리, 그림으로{`\n`}보면 이렇게.</Title>
      <Subtitle top={620} size={38}>
        하마예요. 시간이 왜 중요한지 볼게요.
      </Subtitle>
      <Photo
        style={{
          position: "absolute",
          left: 170,
          top: 810,
          width: 610,
          height: 660,
          rotate: interpolate(f, [0, 32], [-8, -3], timing) + "deg",
          scale: interpolate(f, [0, 35], [0.88, 1], timing),
        }}
      />
      <Tape style={{ left: 375, top: 790 }} />
      <Stamp style={{ left: 92, top: 1370, rotate: "-8deg" }}>
        어려운 말은 그림으로!
      </Stamp>
      <Pickaxe />
    </>
  );
};
const Calendar = () => {
  const f = useCurrentFrame();
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 86,
          right: 155,
          top: 820,
          display: "flex",
          gap: 24,
        }}
      >
        {["처음", "다음", "그다음"].map((t, i) => (
          <div
            key={t}
            style={{
              position: "relative",
              width: 255,
              height: 290,
              border: line,
              borderRadius: 16,
              background: paper,
              translate: `0 ${interpolate(f, [i * 14, i * 14 + 20], [55, 0], timing)}px`,
              rotate: (i - 1) * 4 + "deg",
              boxShadow: "5px 6px 0 #111",
            }}
          >
            <div
              style={{
                height: 60,
                background: gold,
                borderBottom: line,
                borderRadius: "14px 14px 0 0",
              }}
            />
            <div
              style={{
                position: "absolute",
                top: 135,
                width: "100%",
                textAlign: "center",
                fontSize: 45,
                fontWeight: 800,
              }}
            >
              {t}
            </div>
            <div
              style={{
                position: "absolute",
                left: 35,
                right: 35,
                top: 32,
                display: "flex",
                justifyContent: "space-between",
              }}
            >
              {[0, 1].map((n) => (
                <div
                  key={n}
                  style={{
                    width: 13,
                    height: 56,
                    background: ink,
                    borderRadius: 7,
                    marginTop: -56,
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          position: "absolute",
          left: 270,
          top: 1240,
          fontSize: 90,
          fontWeight: 850,
          rotate: "-3deg",
        }}
      >
        시간만?{" "}
        <span style={{ color: gold, WebkitTextStroke: "2px #111" }}>잠깐!</span>
      </div>
    </>
  );
};
const Problem = () => (
  <>
    <Title>{plan.scenes[1].heading}</Title>
    <Calendar />
    <Subtitle top={1450}>
      달력보다 먼저,{`\n`}돈 안에서 무슨 일이 생기는지 봐요.
    </Subtitle>
  </>
);
const Coin: React.FC<{
  x: number;
  y: number;
  earned?: boolean;
  opacity?: number;
}> = ({ x, y, earned, opacity = 1 }) => (
  <g transform={`translate(${x} ${y})`} opacity={opacity}>
    <ellipse
      cy={13}
      rx={48}
      ry={18}
      fill={earned ? gold : paper}
      stroke={ink}
      strokeWidth={3}
    />
    <path d="M-48 0V13 M48 0V13" stroke={ink} strokeWidth={3} />
    <ellipse
      rx={48}
      ry={18}
      fill={earned ? gold : paper}
      stroke={ink}
      strokeWidth={3}
    />
    <ellipse
      cy={-1}
      rx={35}
      ry={11}
      fill="none"
      stroke={ink}
      strokeWidth={1.5}
    />
  </g>
);
// Deliberately qualitative: tokens represent categories, never portfolio amounts or rates.
const MoneyStructure: React.FC<{
  mode: "open" | "merge" | "summary";
  still?: boolean;
}> = ({ mode, still = false }) => {
  const frame = useCurrentFrame();
  const f = still ? 160 : frame;
  const lid = interpolate(f, [0, 38], [0, -130], timing);
  const earned = interpolate(f, [25, 60], [0, 1], timing);
  const join = mode === "open" ? 0 : interpolate(f, [35, 95], [0, 1], timing);
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        top: 740,
        width: 900,
        height: 620,
      }}
    >
      <svg
        viewBox="0 0 900 620"
        width="900"
        height="620"
        role="img"
        aria-label="원금과 쌓인 이자가 합쳐져 다음 계산의 바탕이 되는 개념 그림"
      >
        <defs>
          <pattern
            id="hatch"
            width="12"
            height="12"
            patternUnits="userSpaceOnUse"
          >
            <path d="M0 12L12 0" stroke={ink} strokeWidth="1" opacity=".12" />
          </pattern>
        </defs>
        <g>
          <path
            d="M100 310L355 185L675 310L420 443Z"
            fill={gold}
            stroke={ink}
            strokeWidth="4"
          />
          <path
            d="M100 310L420 443V520L100 388Z"
            fill={paper}
            stroke={ink}
            strokeWidth="4"
          />
          <path
            d="M420 443L675 310V388L420 520Z"
            fill="url(#hatch)"
            stroke={ink}
            strokeWidth="4"
          />
          <path d="M420 443L675 310V388L420 520Z" fill={gold} opacity=".25" />
        </g>
        <g
          transform={`translate(0 ${lid})`}
          opacity={1 - interpolate(f, [20, 60], [0, 0.8], timing)}
        >
          <path
            d="M88 230L350 102L690 230L426 360Z"
            fill={paper}
            stroke={ink}
            strokeWidth="4"
          />
          <path
            d="M88 230L426 360V379L88 249Z"
            fill={gold}
            stroke={ink}
            strokeWidth="4"
          />
          <path
            d="M426 360L690 230V250L426 379Z"
            fill={gold}
            stroke={ink}
            strokeWidth="4"
          />
          <path
            d="M312 176L355 155L437 187L395 208Z"
            fill={gold}
            stroke={ink}
            strokeWidth="3"
          />
        </g>
        {[0, 1, 2].map((i) => (
          <Coin key={i} x={310 + i * 35} y={330 - i * 30} />
        ))}
        <g
          transform={`translate(${-join * 185} ${join * 130})`}
          opacity={earned}
        >
          <Coin x={710} y={140} earned />
          <Coin x={710} y={110} earned />
        </g>
        <g fill={ink} fontSize="32" fontWeight="800">
          <text x="65" y="590">
            처음 넣은 돈
          </text>
          <text x={600 - join * 100} y={join ? 590 : 45}>
            쌓인 이자
          </text>
        </g>
        {mode !== "open" && (
          <g opacity={interpolate(f, [100, 135], [0, 1], timing)}>
            <path
              d="M730 395C840 325 820 185 770 150"
              fill="none"
              stroke={gold}
              strokeWidth="11"
            />
            <path
              d="M751 177L767 145L796 165"
              fill="none"
              stroke={ink}
              strokeWidth="4"
            />
            <text x="645" y="440" fontSize="28" fontWeight="800">
              다음 계산
            </text>
          </g>
        )}
      </svg>
    </div>
  );
};
const AnatomyScene = () => (
  <>
    <Title>{plan.scenes[2].heading}</Title>
    <MoneyStructure mode="open" />
    <Stamp style={{ left: 92, top: 1390 }}>원금 + 쌓인 이자</Stamp>
    <Subtitle top={1490} size={28}>
      블록 개수·크기는 설명용이에요. 실제 금액이 아니에요.
    </Subtitle>
  </>
);
const ExampleScene = () => {
  const f = useCurrentFrame();
  return (
    <>
      <Title>{plan.scenes[3].heading}</Title>
      <MoneyStructure mode="merge" />
      <div
        style={{
          position: "absolute",
          left: 85,
          right: 150,
          top: 1390,
          padding: "20px 22px",
          border: line,
          fontSize: 36,
          fontWeight: 800,
          background: gold,
          opacity: interpolate(f, [70, 95], [0, 1], timing),
        }}
      >
        원금 [ ] + 쌓인 이자 [ ] → 다음 바탕 [ ]
      </div>
      <Subtitle top={1490} size={28}>
        숫자 대신 구조부터 볼게요. 같은 계산이 반복돼요.
      </Subtitle>
    </>
  );
};
const Summary: React.FC<{ mini?: boolean }> = ({ mini }) => (
  <>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 120,
        top: mini ? 190 : 360,
        fontSize: mini ? 78 : 90,
        fontWeight: 850,
        lineHeight: 1.15,
        letterSpacing: -4,
      }}
    >
      이자가 다시,{`\n`}이자의 바탕으로.
    </div>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 130,
        top: mini ? 475 : 720,
      }}
    >
      {["처음 넣은 돈", "쌓인 이자도 더하기", "다음 계산에 함께 반영"].map(
        (t, i) => (
          <div
            key={t}
            style={{
              position: "relative",
              display: "flex",
              alignItems: "center",
              gap: 22,
              padding: "23px 25px",
              marginBottom: 24,
              border: line,
              borderRadius: 16,
              background: i === 1 ? gold : paper,
              fontSize: mini ? 36 : 43,
              fontWeight: 800,
              boxShadow: "5px 5px 0 #111",
            }}
          >
            <span
              style={{
                width: 44,
                height: 44,
                display: "inline-grid",
                placeItems: "center",
                border: line,
                borderRadius: "50%",
                fontSize: 25,
              }}
            >
              {i + 1}
            </span>
            {t}
          </div>
        ),
      )}
    </div>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 150,
        top: mini ? 920 : 1245,
        fontSize: mini ? 30 : 34,
        lineHeight: 1.5,
      }}
    >
      하마는 ‘시간’만 보지 않고,{`\n`}다시 계산되는 구조를 볼게요.
    </div>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 135,
        top: mini ? 1080 : 1410,
        fontSize: mini ? 24 : 27,
        lineHeight: 1.5,
        borderTop: "2px solid #d4af37",
        paddingTop: 20,
      }}
    >
      시간만으로 투자 수익이 보장되지는 않아요.{`\n`}투자에는 손실이 있을 수
      있어요.
    </div>
  </>
);
const End = () => (
  <>
    <Title>{plan.scenes[5].heading}</Title>
    <Photo
      style={{
        position: "absolute",
        left: 150,
        top: 790,
        width: 500,
        height: 575,
        rotate: "-4deg",
      }}
    />
    <Tape style={{ left: 315, top: 770 }} />
    <div
      style={{
        position: "absolute",
        left: 710,
        top: 930,
        fontSize: 45,
        fontWeight: 800,
        lineHeight: 1.4,
        rotate: "5deg",
      }}
    >
      하마랑{`\n`}다음 그림도{`\n`}같이 봐요.
    </div>
    <Stamp style={{ left: 100, top: 1485 }}>내일도 하마가 풀어줄게요</Stamp>
  </>
);
const SaveScene = () => (
  <>
    <Summary />
    <Stamp style={{ left: 600, top: 1530, rotate: "-5deg" }}>저장해둬요</Stamp>
  </>
);
export const Day1V2Reel = () => {
  const { fps } = useVideoConfig();
  return (
    <Frame series={plan.series}>
      <Sequence durationInFrames={3 * fps} name="01 후킹">
        <Hero />
        <Audio src={staticFile(plan.scenes[0].audio)} />
      </Sequence>
      <Sequence from={3 * fps} durationInFrames={4 * fps} name="02 문제">
        <Problem />
        <Audio src={staticFile(plan.scenes[1].audio)} />
      </Sequence>
      <Sequence from={7 * fps} durationInFrames={7 * fps} name="03 분해 구조">
        <AnatomyScene />
        <Audio src={staticFile(plan.scenes[2].audio)} />
      </Sequence>
      <Sequence
        from={14 * fps}
        durationInFrames={8 * fps}
        name="04 합쳐지는 예시"
      >
        <ExampleScene />
        <Audio src={staticFile(plan.scenes[3].audio)} />
      </Sequence>
      <Sequence from={22 * fps} durationInFrames={5 * fps} name="05 저장 카드">
        <SaveScene />
        <Audio src={staticFile(plan.scenes[4].audio)} />
      </Sequence>
      <Sequence from={27 * fps} durationInFrames={3 * fps} name="06 다음 편">
        <End />
        <Audio src={staticFile(plan.scenes[5].audio)} />
      </Sequence>
    </Frame>
  );
};
export const Day1V2Mini = () => (
  <Frame mini series="ETF 조합">
    <Title top={185} size={88}>
      {plan.mini_title}
    </Title>
    <Subtitle top={420} size={34}>
      이름보다 먼저, 역할부터 적어볼게요.
    </Subtitle>
    <div
      style={{
        position: "absolute",
        left: 76,
        right: 76,
        top: 560,
        display: "flex",
        gap: 22,
      }}
    >
      {["01", "02", "03"].map((n, i) => (
        <div
          key={n}
          style={{
            flex: 1,
            border: line,
            borderRadius: 15,
            padding: 25,
            height: 370,
            background: i === 1 ? gold : paper,
            boxShadow: "5px 5px 0 #111",
          }}
        >
          <div style={{ fontSize: 27, fontWeight: 850 }}>역할 {n}</div>
          <div style={{ fontSize: 52, margin: "32px 0 25px" }}>[　]</div>
          <div style={{ fontSize: 27, lineHeight: 1.9 }}>
            ETF [ ]{`\n`}비중 [ ]
          </div>
        </div>
      ))}
    </div>
    <Photo
      style={{
        position: "absolute",
        right: 95,
        top: 1000,
        width: 190,
        height: 205,
        rotate: "5deg",
      }}
    />
    <Subtitle top={1030} size={32}>
      오늘은 빈 틀부터.{`\n`}내일, 그림으로 펼쳐봐요.
    </Subtitle>
    <Subtitle top={1190} size={23}>
      종목·비중 입력 전 초안 · 매수 추천이 아니에요.
    </Subtitle>
  </Frame>
);
export const Day1V2Save = () => (
  <Frame mini series="복리 · 시간">
    <Summary mini />
    <Subtitle top={1200} size={21}>
      정의 출처: Investor.gov · Compound Interest
    </Subtitle>
  </Frame>
);
export const Day1V2Morning: React.FC<{ page: number }> = ({ page }) => (
  <Frame series="하마의 아침">
    {page === 1 ? (
      <>
        <Title>오늘 가격,{`\n`}같이 기록해요.</Title>
        <Photo
          style={{
            position: "absolute",
            right: 160,
            top: 680,
            width: 230,
            height: 250,
            rotate: "5deg",
          }}
        />
        <div style={{ position: "absolute", left: 76, right: 145, top: 1000 }}>
          {["BTC", "ETH"].map((n) => (
            <div
              key={n}
              style={{
                borderTop: line,
                padding: "24px 0",
                display: "flex",
                justifyContent: "space-between",
                fontSize: 58,
                fontWeight: 850,
              }}
            >
              <span>{n}</span>
              <span>[ 가격 ]</span>
            </div>
          ))}
        </div>
        <Subtitle top={1390} size={29}>
          통화 [ ] · 확인 시각 [ ] ET{`\n`}가격 출처 [ ]
        </Subtitle>
        <Subtitle top={1520} size={24}>
          빈칸을 확인한 뒤 올릴 카드예요.
        </Subtitle>
      </>
    ) : page === 2 ? (
      <>
        <Title>돈을 캐기 전에,{`\n`}구조부터 캐봐요.</Title>
        <Photo
          src="standing.jpg"
          style={{
            position: "absolute",
            left: 175,
            top: 770,
            width: 590,
            height: 660,
            rotate: "-3deg",
          }}
        />
        <Tape style={{ left: 390, top: 750 }} />
        <Stamp style={{ left: 92, top: 1460 }}>오늘 저녁 · 복리 그림</Stamp>
      </>
    ) : (
      <>
        <Title>복리,{`\n`}말로 들으면 어렵죠?</Title>
        <Photo
          src="strawberry.jpg"
          style={{
            position: "absolute",
            left: 230,
            top: 770,
            width: 480,
            height: 520,
            rotate: "4deg",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 76,
            right: 150,
            top: 1390,
            padding: 30,
            border: line,
            borderRadius: 18,
            fontSize: 35,
            fontWeight: 800,
          }}
        >
          <div>하마랑 그림으로 볼까요?</div>
          <div
            style={{ display: "flex", gap: 30, marginTop: 25, fontSize: 29 }}
          >
            <span style={{ background: gold, padding: 12 }}>
              그림으로 볼래요
            </span>
            <span style={{ padding: 12 }}>이미 알아요</span>
          </div>
        </div>
      </>
    )}
  </Frame>
);
export const Day1V2Night: React.FC<{ page: number }> = ({ page }) => (
  <Frame series="하마의 밤">
    {page === 1 ? (
      <>
        <Title>작은 하마의{`\n`}돈 공부 첫날.</Title>
        <Photo
          style={{
            position: "absolute",
            left: 145,
            top: 760,
            width: 650,
            height: 700,
            rotate: "-3deg",
          }}
        />
        <Tape style={{ left: 385, top: 742 }} />
        <Subtitle top={1520} size={34}>
          오늘은 복리의 구조부터 펼쳐봤어요.
        </Subtitle>
      </>
    ) : (
      <>
        <Title>내일은 ETF.{`\n`}스케치부터 열어요.</Title>
        <div
          style={{
            position: "absolute",
            left: 76,
            right: 150,
            top: 850,
            display: "flex",
            gap: 20,
          }}
        >
          {["역할 [ ]", "ETF [ ]", "비중 [ ]"].map((t) => (
            <div
              key={t}
              style={{
                flex: 1,
                height: 200,
                border: line,
                borderRadius: 14,
                fontSize: 31,
                fontWeight: 750,
                display: "grid",
                placeItems: "center",
                background: paper,
                boxShadow: "5px 5px 0 #111",
              }}
            >
              {t}
            </div>
          ))}
        </div>
        <Photo
          style={{
            position: "absolute",
            left: 76,
            top: 1150,
            width: 240,
            height: 270,
            rotate: "-5deg",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 365,
            top: 1200,
            right: 150,
            fontSize: 38,
            lineHeight: 1.4,
          }}
        >
          세 칸을 그림으로{`\n`}펼치는 과정을 보여줄게요.
        </div>
        <Stamp style={{ left: 100, top: 1500 }}>SKETCH TO ETF · 1탄</Stamp>
      </>
    )}
  </Frame>
);
