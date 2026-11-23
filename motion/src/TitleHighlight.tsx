import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/google-fonts/Poppins";

const { fontFamily } = loadFont("normal", { weights: ["400", "800"], subsets: ["latin", "latin-ext"] });

export type TitleHighlightProps = {
  lead: string;
  highlight: string;
  durationSeconds: number;
  fps: number;
  width: number;
  height: number;
};

// Small white lead line and one big yellow word, no box, transparent background.
// The word springs in, holds, then fades out in the last 0.3 s.
export const TitleHighlight: React.FC<TitleHighlightProps> = ({ lead, highlight }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 140 } });
  const leadIn = spring({ frame: frame - 3, fps, config: { damping: 200 } });
  const fadeFrames = Math.round(fps * 0.3);
  const fadeOut = interpolate(frame, [durationInFrames - fadeFrames, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fit the big word inside 88% of the width (Poppins ExtraBold is about 0.68 em per capital).
  const bigSize = Math.min(width * 0.2, (width * 0.88) / Math.max(1, highlight.length * 0.68));
  const shadow = "0 6px 24px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.8)";

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: fadeOut }}>
      <div style={{ fontFamily, textAlign: "center", lineHeight: 1.05 }}>
        <div
          style={{
            color: "#fff", fontWeight: 400, fontSize: bigSize * 0.38, textShadow: shadow,
            marginBottom: bigSize * 0.14,
            opacity: leadIn, transform: `translateY(${interpolate(leadIn, [0, 1], [24, 0])}px)`,
          }}
        >
          {lead}
        </div>
        <div
          style={{
            color: "#FFD400", fontWeight: 800, fontSize: bigSize, textShadow: shadow,
            transform: `scale(${interpolate(enter, [0, 1], [0.6, 1])})`, opacity: Math.min(1, enter * 1.5),
          }}
        >
          {highlight}
        </div>
      </div>
    </AbsoluteFill>
  );
};
