from __future__ import annotations

import json
import math
import struct
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def write_ppm_as_png_named(path: Path, offset: int) -> None:
    width, height = 160, 90
    rows = []
    for y in range(height):
        for x in range(width):
            lane = 255 if abs((x + offset) - (width // 2 + int(20 * math.sin(y / 18)))) < 2 else 30
            rows.append(bytes([min(255, x + offset), min(255, y * 2), lane]))
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + b"".join(rows))


def main() -> None:
    root = PROJECT_ROOT / "data/sample/perception"
    image_dir = root / "images"
    pc_dir = root / "pointcloud"
    image_dir.mkdir(parents=True, exist_ok=True)
    pc_dir.mkdir(parents=True, exist_ok=True)
    timestamps = []
    for index in range(4):
        write_ppm_as_png_named(image_dir / f"{index:06d}.ppm", index * 4)
        timestamps.append(str(index * 0.1))
        points = []
        for point in range(64):
            points.extend([point * 0.1, index * 0.05, math.sin(point), 1.0])
        (pc_dir / f"{index:06d}.bin").write_bytes(struct.pack(f"{len(points)}f", *points))
    (root / "timestamps.txt").write_text("\n".join(timestamps), encoding="utf-8")
    (root / "calibration.json").write_text(json.dumps({"fx": 120.0, "fy": 120.0, "cx": 80.0, "cy": 45.0}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
