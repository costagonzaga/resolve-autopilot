import React from "react";
import { Composition } from "remotion";
import { TitleHighlight, TitleHighlightProps } from "./TitleHighlight";

// Defaults are overridden by resolve-autopilot with --props (text, size, fps and duration of the clip).
const defaults: TitleHighlightProps = {
  lead: "o segredo é",
  highlight: "CONSISTÊNCIA",
  durationSeconds: 2.5,
  fps: 24,
  width: 1080,
  height: 1920,
};

export const Root: React.FC = () => (
  <Composition
    id="TitleHighlight"
    component={TitleHighlight}
    durationInFrames={Math.round(defaults.durationSeconds * defaults.fps)}
    fps={defaults.fps}
    width={defaults.width}
    height={defaults.height}
    defaultProps={defaults}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.max(1, Math.round(props.durationSeconds * props.fps)),
      fps: props.fps,
      width: props.width,
      height: props.height,
    })}
  />
);
