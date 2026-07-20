import {
  AbsoluteFill,
  Composition,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FPS = 30;
const seconds = (value: number) => Math.round(value * FPS);

const fade = (frame: number, duration: number) =>
  interpolate(frame, [0, 12, duration - 12, duration], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const BrandMark = () => (
  <div className="brand-mark">
    <span className="brand-dot" />
    AI STRATEGY FACTORY
  </div>
);

const TitleScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 90}});

  return (
    <AbsoluteFill className="scene title-scene">
      <div className="grid-lines" />
      <div className="orb orb-one" />
      <div className="orb orb-two" />
      <div
        className="title-copy"
        style={{
          opacity: enter,
          transform: `translateY(${interpolate(enter, [0, 1], [40, 0])}px)`,
        }}
      >
        <BrandMark />
        <h1>From synthetic brief<br />to reviewed strategy.</h1>
        <p>Local AI generation. Explicit human control. Durable output.</p>
      </div>
      <div className="title-rule" style={{transform: `scaleX(${enter})`}} />
      <div className="chapter-number">01</div>
    </AbsoluteFill>
  );
};

const InfographicScene = ({mode}: {mode: "flow" | "storage"}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const isFlow = mode === "flow";
  const scale = isFlow ? 1.04 : 1.07;
  const translateY = isFlow
    ? interpolate(progress, [0, 1], [20, -10])
    : interpolate(progress, [0, 1], [-18, -72]);

  return (
    <AbsoluteFill className="scene infographic-scene" style={{opacity: fade(frame, durationInFrames)}}>
      <Img
        src={staticFile("assets/ai-strategy-factory-infographic-v3.png")}
        className="infographic"
        style={{transform: `translateY(${translateY}px) scale(${scale})`}}
      />
    </AbsoluteFill>
  );
};

type ClipSceneProps = {
  file: string;
  eyebrow: string;
  title: string;
  body: string;
  chapter: string;
  startFrom?: number;
  zoom?: number;
  focusX?: number;
  focusY?: number;
};

const ClipScene = ({
  file,
  eyebrow,
  title,
  body,
  chapter,
  startFrom = 0,
  zoom = 1.04,
  focusX = 50,
  focusY = 50,
}: ClipSceneProps) => {
  const frame = useCurrentFrame();
  const {durationInFrames, fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 110}});
  const drift = interpolate(frame, [0, durationInFrames], [0, 0.035], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className="scene clip-scene" style={{opacity: fade(frame, durationInFrames)}}>
      <div className="clip-glow" />
      <div
        className="video-shell"
        style={{
          opacity: enter,
          transform: `translateX(${interpolate(enter, [0, 1], [80, 0])}px)`,
        }}
      >
        <OffthreadVideo
          muted
          startFrom={startFrom}
          src={staticFile(`clips-hq/${file}`)}
          className="workflow-video"
          style={{
            objectPosition: `${focusX}% ${focusY}%`,
            transform: `scale(${zoom + drift})`,
          }}
        />
      </div>
      <div className="clip-copy">
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p>{body}</p>
        <div className="accent-line" />
      </div>
      <div className="chapter-number">{chapter}</div>
    </AbsoluteFill>
  );
};

const EndScene = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 80}});
  return (
    <AbsoluteFill className="scene end-scene">
      <div className="grid-lines" />
      <div className="end-ring" style={{transform: `scale(${enter})`}} />
      <div className="end-copy" style={{opacity: enter}}>
        <BrandMark />
        <h2>Strategy at machine speed.<br />Approval at human speed.</h2>
        <p>Local-first · authenticated · synthetic-data lab</p>
      </div>
    </AbsoluteFill>
  );
};

const CodexCrewScene = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 85}});
  const cards = [
    ["VS Code", "Build · Refactor · Test · Debug"],
    ["ChatGPT web", "Plan · Research · Review"],
    ["ChatGPT on macOS", "Coordinate · Operate · Create video"],
  ];

  return (
    <AbsoluteFill
      className="scene codex-crew-scene"
      style={{opacity: fade(frame, durationInFrames)}}
    >
      <div className="grid-lines" />
      <div className="crew-heading" style={{opacity: enter}}>
        <span className="eyebrow">How I built it</span>
        <h2>One human-directed Codex crew.</h2>
        <p>Codex worked across three surfaces, powered by GPT-5.6 for development.</p>
      </div>
      <div className="crew-cards">
        {cards.map(([title, body], index) => {
          const cardEnter = spring({
            frame: frame - index * 7,
            fps,
            config: {damping: 18, stiffness: 90},
          });
          return (
            <div
              className="crew-card"
              key={title}
              style={{
                opacity: cardEnter,
                transform: `translateY(${interpolate(cardEnter, [0, 1], [36, 0])}px)`,
              }}
            >
              <span className="crew-card-number">0{index + 1}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>
          );
        })}
      </div>
      <div className="crew-outcome">
        <span>Codex + GPT-5.6</span>
        <div className="crew-line" />
        <strong>Architecture · Python · n8n · MCP · Tests · Docs · GitHub · Video</strong>
      </div>
      <div className="chapter-number">07</div>
    </AbsoluteFill>
  );
};

const BuildScopeScene = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 20, stiffness: 85}});
  const scopes = [
    ["Product + architecture", "Idea · Roadmap · Stack · SQLite → PostgreSQL"],
    ["Engineering + operations", "n8n · MCP · FastAPI · Docker · Tests"],
    ["Documentation + delivery", "Docs · Licence research · GitHub · Video"],
  ];

  return (
    <AbsoluteFill
      className="scene build-scope-scene"
      style={{opacity: fade(frame, durationInFrames)}}
    >
      <div className="grid-lines" />
      <div className="scope-heading" style={{opacity: enter}}>
        <span className="eyebrow">From idea to shipped product</span>
        <h2>Codex accelerated the whole build.</h2>
      </div>
      <div className="scope-list">
        {scopes.map(([title, body], index) => {
          const rowEnter = spring({
            frame: frame - index * 8,
            fps,
            config: {damping: 18, stiffness: 90},
          });
          return (
            <div
              className="scope-row"
              key={title}
              style={{
                opacity: rowEnter,
                transform: `translateX(${interpolate(rowEnter, [0, 1], [65, 0])}px)`,
              }}
            >
              <span>0{index + 1}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>
          );
        })}
      </div>
      <div className="scope-control">Human direction, review and final approval throughout</div>
      <div className="chapter-number">08</div>
    </AbsoluteFill>
  );
};

export const StrategyFactoryVideo = () => (
  <AbsoluteFill className="video-root">
    <Sequence durationInFrames={seconds(5)}><TitleScene /></Sequence>
    <Sequence from={seconds(5)} durationInFrames={seconds(7)}><InfographicScene mode="flow" /></Sequence>
    <Sequence from={seconds(12)} durationInFrames={seconds(7)}>
      <ClipScene
        file="02-submit-synthetic-brief.mp4"
        eyebrow="Synthetic intake"
        title="A structured brief enters the workflow engine."
        body="The workflow validates input and coordinates every downstream step."
        chapter="02"
        startFrom={seconds(1)}
      />
    </Sequence>
    <Sequence from={seconds(19)} durationInFrames={seconds(7)}>
      <ClipScene
        file="03-draft-created.mp4"
        eyebrow="Local generation"
        title="The draft is stored before review."
        body="Ollama generates locally through the authenticated FastAPI service."
        chapter="03"
        startFrom={seconds(1)}
      />
    </Sequence>
    <Sequence from={seconds(26)} durationInFrames={seconds(8)}>
      <ClipScene
        file="04-review-strategy.mp4"
        eyebrow="Advisory quality assessment"
        title="Evidence, risks and measures stay visible."
        body="Quality checks inform the reviewer. They never make the approval decision."
        chapter="04"
        startFrom={seconds(5)}
        zoom={1.1}
      />
    </Sequence>
    <Sequence from={seconds(34)} durationInFrames={seconds(7)}>
      <ClipScene
        file="05-approve-strategy.mp4"
        eyebrow="Human decision gate"
        title="Approval remains explicit."
        body="Only a recorded human decision can produce the final deliverable."
        chapter="05"
        startFrom={seconds(10)}
        zoom={1.08}
      />
    </Sequence>
    <Sequence from={seconds(41)} durationInFrames={seconds(7)}><InfographicScene mode="storage" /></Sequence>
    <Sequence from={seconds(48)} durationInFrames={seconds(7)}>
      <ClipScene
        file="06-artifacts-and-architecture.mp4"
        eyebrow="Durable output"
        title="A reviewed strategy becomes an artifact."
        body="Application records remain in PostgreSQL; approved Markdown stays readable."
        chapter="06"
        startFrom={seconds(5)}
        zoom={1.03}
      />
    </Sequence>
    <Sequence from={seconds(55)} durationInFrames={seconds(15)}><CodexCrewScene /></Sequence>
    <Sequence from={seconds(70)} durationInFrames={seconds(15)}><BuildScopeScene /></Sequence>
    <Sequence from={seconds(85)} durationInFrames={seconds(5)}><EndScene /></Sequence>
  </AbsoluteFill>
);

export const MyComposition = () => (
  <Composition
    id="AI-Strategy-Factory"
    component={StrategyFactoryVideo}
    durationInFrames={seconds(90)}
    fps={FPS}
    width={1920}
    height={1080}
  />
);
