import argparse
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
DEFAULT_OUTPUT_ROOT = BASE / "temp_video" / "hud_frames"
OWCS_KOREA_720P_REGIONS = {
    "full_frame": None,
    "left_team_hud": {"x": 0, "y": 0, "w": 400, "h": 150},
    "center_objective": {"x": 420, "y": 0, "w": 440, "h": 110},
    "right_team_hud": {"x": 880, "y": 0, "w": 400, "h": 150},
    "kill_feed": {"x": 720, "y": 60, "w": 560, "h": 220},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract full frames and HUD regions from an OWCS gameplay clip."
    )
    parser.add_argument("--input-file", required=True, help="Path to a local mp4 clip")
    parser.add_argument(
        "--clip-id",
        required=True,
        help="Stable name for the extracted frame set",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root folder for extracted frames",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frame sampling rate. Phase 1 defaults to one frame per second.",
    )
    parser.add_argument("--start", default="00:00:00", help="Optional clip start timestamp")
    parser.add_argument("--end", help="Optional clip end timestamp")
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def run_passthrough(command: list[str]) -> None:
    subprocess.run(command, check=True)


def parse_timestamp_to_seconds(value: str) -> float:
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise ValueError(f"Invalid timestamp: {value}")
    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return float(total)


def probe_duration(file_path: Path) -> float:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(file_path),
        ]
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def extract_region_frames(
    input_file: Path,
    output_pattern: Path,
    fps: float,
    start: str,
    duration_seconds: float,
    crop: dict | None,
) -> None:
    vf_parts = [f"fps={fps}"]
    if crop:
        vf_parts.append(f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']}")
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-nostdin",
        "-ss",
        start,
        "-t",
        f"{duration_seconds:.3f}",
        "-i",
        str(input_file),
    ]
    command.extend(
        [
            "-vf",
            ",".join(vf_parts),
            "-q:v",
            "2",
            str(output_pattern),
        ]
    )
    run_passthrough(command)


def build_index(
    region_dir: Path,
    fps: float,
    absolute_start_seconds: float,
) -> list[dict]:
    frames = sorted(region_dir.glob("*.jpg"))
    index = []
    for idx, frame_path in enumerate(frames):
        timestamp_seconds = absolute_start_seconds + (idx / fps)
        index.append(
            {
                "frame_number": idx + 1,
                "timestamp_seconds": round(timestamp_seconds, 3),
                "file_path": str(frame_path),
            }
        )
    return index


def main() -> None:
    args = parse_args()
    input_file = Path(args.input_file).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    output_root = Path(args.output_root)
    clip_root = output_root / args.clip_id
    clip_root.mkdir(parents=True, exist_ok=True)

    source_duration = probe_duration(input_file)
    start_seconds = parse_timestamp_to_seconds(args.start)
    end_seconds = parse_timestamp_to_seconds(args.end) if args.end else source_duration
    if end_seconds <= start_seconds:
        raise ValueError("End timestamp must be greater than start timestamp.")

    expected_frames = math.floor((end_seconds - start_seconds) * args.fps) + 1
    region_indexes = {}

    for region_name, crop in OWCS_KOREA_720P_REGIONS.items():
        region_dir = clip_root / region_name
        region_dir.mkdir(parents=True, exist_ok=True)
        output_pattern = region_dir / "%06d.jpg"
        extract_region_frames(
            input_file=input_file,
            output_pattern=output_pattern,
            fps=args.fps,
            start=args.start,
            duration_seconds=end_seconds - start_seconds,
            crop=crop,
        )
        region_indexes[region_name] = build_index(
            region_dir=region_dir,
            fps=args.fps,
            absolute_start_seconds=start_seconds,
        )

    manifest = {
        "created_at_utc": utc_now_iso(),
        "clip_id": args.clip_id,
        "input_file": str(input_file),
        "fps": args.fps,
        "profile": "owcs_korea_720p_v1",
        "start": args.start,
        "end": args.end,
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "expected_frames_per_region": expected_frames,
        "regions": OWCS_KOREA_720P_REGIONS,
        "frame_indexes": region_indexes,
    }
    manifest_path = clip_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved frame manifest: {manifest_path}")
    print(f"Clip id: {args.clip_id}")
    print(f"Regions extracted: {len(OWCS_KOREA_720P_REGIONS)}")
    print(f"Sample rate fps: {args.fps}")


if __name__ == "__main__":
    main()
