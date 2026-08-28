"""Extract timestamped evidence frames from a site-walk video."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2


def extract_frames(video_path: str | Path, output_dir: str | Path, every_seconds: float = 2.0) -> list[Path]:
    """Extract one JPEG every ``every_seconds`` and return the saved paths."""
    if every_seconds <= 0:
        raise ValueError("every_seconds must be greater than zero")

    source = Path(video_path)
    if not source.exists():
        raise FileNotFoundError(f"Video not found: {source}")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {source}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    interval = max(1, round(fps * every_seconds))
    saved: list[Path] = []
    frame_number = 0

    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_number % interval == 0:
                timestamp_ms = int(capture.get(cv2.CAP_PROP_POS_MSEC))
                path = destination / f"frame_{timestamp_ms:010d}ms.jpg"
                if not cv2.imwrite(str(path), frame):
                    raise OSError(f"Could not save frame: {path}")
                saved.append(path)
            frame_number += 1
    finally:
        capture.release()

    if not saved:
        raise ValueError("The video contained no readable frames")
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="Path to the site-walk video")
    parser.add_argument("--output", default="frames", help="Output folder")
    parser.add_argument("--every-seconds", type=float, default=2.0)
    args = parser.parse_args()

    frames = extract_frames(args.video, args.output, args.every_seconds)
    print(f"Extracted {len(frames)} frame(s) to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
