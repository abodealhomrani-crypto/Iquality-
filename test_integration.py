import json
import sqlite3
from pathlib import Path

import cv2
import numpy as np

from verification import verify_folder


def test_verification_pipeline(tmp_path: Path) -> None:
    database = tmp_path / "iquality.db"
    seed = Path(__file__).with_name("seed.sql").read_text(encoding="utf-8")
    with sqlite3.connect(database) as connection:
        connection.executescript(seed)

    frames = tmp_path / "frames"
    frames.mkdir()

    dark = np.zeros((160, 240, 3), dtype=np.uint8)
    detailed = np.zeros((160, 240, 3), dtype=np.uint8)
    for x in range(0, 240, 20):
        color = (255, 255, 255) if (x // 20) % 2 else (60, 160, 220)
        cv2.rectangle(detailed, (x, 0), (min(x + 10, 239), 159), color, -1)

    assert cv2.imwrite(str(frames / "dark.jpg"), dark)
    assert cv2.imwrite(str(frames / "site.jpg"), detailed)

    report = tmp_path / "results.json"
    results = verify_folder(frames, database, "REBAR-L3", "REBAR-L3", report)

    assert len(results) == 2
    assert {item["status"] for item in results} == {"supported", "not_observed"}
    assert len(json.loads(report.read_text(encoding="utf-8"))) == 2

    with sqlite3.connect(database) as connection:
        count = connection.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        approvals = connection.execute("SELECT COUNT(*) FROM approvals").fetchone()[0]
    assert count == 2
    assert approvals == 2


def test_contradicted_activity(tmp_path: Path) -> None:
    database = tmp_path / "iquality.db"
    seed = Path(__file__).with_name("seed.sql").read_text(encoding="utf-8")
    with sqlite3.connect(database) as connection:
        connection.executescript(seed)

    frames = tmp_path / "frames"
    frames.mkdir()
    detailed = np.zeros((160, 240, 3), dtype=np.uint8)
    for x in range(0, 240, 10):
        cv2.line(detailed, (x, 0), (239 - x, 159), (255, 255, 255), 2)
    assert cv2.imwrite(str(frames / "site.jpg"), detailed)

    results = verify_folder(
        frames, database, "REBAR-L3", "CONC-L3", tmp_path / "results.json"
    )
    assert results[0]["status"] == "contradicted"
