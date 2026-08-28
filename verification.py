"""Quality-gated demonstration of iQuality evidence verification."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np


def frame_metrics(image: np.ndarray) -> dict[str, float]:
    """Return simple quality metrics used by the MVP gate."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return {
        "brightness": float(gray.mean()),
        "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
        "detail": float(gray.std()),
    }


def detect_markers(image: np.ndarray) -> list[int]:
    """Return visible ArUco marker IDs when OpenCV contrib is available."""
    if not hasattr(cv2, "aruco"):
        return []
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    _, ids, _ = detector.detectMarkers(image)
    return [] if ids is None else [int(value) for value in ids.flatten()]


def classify_frame(
    image: np.ndarray,
    claimed_activity_code: str,
    recognized_activity_code: str | None,
) -> tuple[str, float, str, dict[str, float], list[int]]:
    """Verify evidence; replace the supplied recognition with a trained model later."""
    metrics = frame_metrics(image)
    markers = detect_markers(image)
    if metrics["brightness"] < 25:
        return "not_observed", 0.95, "Frame is too dark", metrics, markers
    if metrics["brightness"] > 245:
        return "not_observed", 0.95, "Frame is overexposed", metrics, markers
    if metrics["sharpness"] < 20 or metrics["detail"] < 8:
        return "not_observed", 0.90, "Insufficient visual detail", metrics, markers
    if not recognized_activity_code:
        return "not_observed", 0.80, "No activity recognized", metrics, markers

    confidence = min(0.99, 0.60 + metrics["sharpness"] / 1000)
    if recognized_activity_code != claimed_activity_code:
        reason = f"Recognized {recognized_activity_code}, not {claimed_activity_code}"
        return "contradicted", confidence, reason, metrics, markers
    return "supported", confidence, "Recognized activity matches claimed code", metrics, markers


def verify_folder(
    frames_dir: str | Path,
    database: str | Path,
    claimed_activity_code: str,
    recognized_activity_code: str | None,
    output_json: str | Path = "verification_results.json",
) -> list[dict]:
    """Verify all JPEG/PNG frames, persist observations and write a JSON report."""
    folder = Path(frames_dir)
    paths = sorted([*folder.glob("*.jpg"), *folder.glob("*.jpeg"), *folder.glob("*.png")])
    if not paths:
        raise ValueError(f"No image frames found in: {folder}")

    connection = sqlite3.connect(database)
    try:
        exists = connection.execute(
            "SELECT 1 FROM activity_codes WHERE code = ?", (claimed_activity_code,)
        ).fetchone()
        if not exists:
            raise ValueError(f"Unknown claimed activity code: {claimed_activity_code}")
        if recognized_activity_code:
            recognized_exists = connection.execute(
                "SELECT 1 FROM activity_codes WHERE code = ?", (recognized_activity_code,)
            ).fetchone()
            if not recognized_exists:
                raise ValueError(f"Unknown recognized activity code: {recognized_activity_code}")

        results: list[dict] = []
        for path in paths:
            image = cv2.imread(str(path))
            captured_at = datetime.now(timezone.utc).isoformat()
            if image is None:
                status, confidence, reason, metrics, markers = (
                    "not_observed", 1.0, "Unreadable image", {}, []
                )
            else:
                status, confidence, reason, metrics, markers = classify_frame(
                    image, claimed_activity_code, recognized_activity_code
                )

            record = {
                "claimed_activity_code": claimed_activity_code,
                "recognized_activity_code": recognized_activity_code,
                "frame_path": str(path),
                "captured_at": captured_at,
                "status": status,
                "confidence": round(confidence, 3),
                "reason": reason,
                "marker_ids": markers,
                "approval_status": "pending",
                "metrics": {key: round(value, 2) for key, value in metrics.items()},
            }
            results.append(record)
            cursor = connection.execute(
                """INSERT INTO observations
                   (activity_code, frame_path, captured_at, status, confidence,
                    reason, marker_ids, approval_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
                (
                    claimed_activity_code, str(path), captured_at, status,
                    confidence, reason, json.dumps(markers),
                ),
            )
            connection.execute(
                "INSERT INTO approvals (observation_id) VALUES (?)", (cursor.lastrowid,)
            )
        connection.commit()
    finally:
        connection.close()

    Path(output_json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", help="Folder containing extracted frames")
    parser.add_argument("--database", default="iquality.db")
    parser.add_argument("--claimed-activity-code", required=True)
    parser.add_argument(
        "--recognized-activity-code",
        help="Demo/model output. Omit it to record not_observed.",
    )
    parser.add_argument("--output", default="verification_results.json")
    args = parser.parse_args()

    results = verify_folder(
        args.frames,
        args.database,
        args.claimed_activity_code,
        args.recognized_activity_code,
        args.output,
    )
    supported = sum(item["status"] == "supported" for item in results)
    not_observed = sum(item["status"] == "not_observed" for item in results)
    contradicted = sum(item["status"] == "contradicted" for item in results)
    print(
        f"Verified {len(results)} frame(s): {supported} supported, "
        f"{contradicted} contradicted, {not_observed} not observed; QS approval pending"
    )


if __name__ == "__main__":
    main()
