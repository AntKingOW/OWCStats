import argparse
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE = Path(r"C:\Users\user\Documents\Playground\OWCStats")
DEFAULT_OUTPUT_ROOT = BASE / "temp_video" / "vod_ingest"


@dataclass
class SegmentSpec:
    label: str
    start: str
    end: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download or register an OWCS VOD and prepare optional map clips."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source-url", help="YouTube or other VOD URL")
    source_group.add_argument("--input-file", help="Existing local VOD file")
    parser.add_argument(
        "--vod-id",
        help="Stable ID for the VOD. Defaults to the YouTube ID or input filename stem.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where manifests, source files, and clips are stored.",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=720,
        help="Maximum download height for source-url mode.",
    )
    parser.add_argument(
        "--segment",
        action="append",
        default=[],
        metavar="LABEL,START,END",
        help="Optional clip definition, for example map1,01:11:30,01:35:42",
    )
    parser.add_argument(
        "--copy-input-file",
        action="store_true",
        help="Copy --input-file into the ingest run directory instead of referencing it in place.",
    )
    parser.add_argument(
        "--copy-clips",
        action="store_true",
        help="Use stream copy for clips instead of accurate re-encoding.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing outputs for the same VOD ID.",
    )
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def run_passthrough(command: list[str]) -> None:
    subprocess.run(command, check=True)


def extract_youtube_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=|/shorts/|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def normalize_vod_id(args: argparse.Namespace) -> str:
    if args.vod_id:
        return args.vod_id
    if args.source_url:
        youtube_id = extract_youtube_id(args.source_url)
        if youtube_id:
            return youtube_id
    if args.input_file:
        return Path(args.input_file).stem
    raise ValueError("Could not determine a VOD ID.")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def parse_segment(text: str) -> SegmentSpec:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"Invalid --segment value: {text}")
    return SegmentSpec(label=parts[0], start=parts[1], end=parts[2])


def parse_timestamp_to_seconds(value: str) -> float:
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise ValueError(f"Invalid timestamp: {value}")
    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return float(total)


def probe_media(file_path: Path) -> dict:
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(file_path),
        ]
    )
    data = json.loads(result.stdout)
    media_format = data.get("format", {})
    return {
        "duration_seconds": float(media_format.get("duration", 0.0)),
        "size_bytes": int(media_format.get("size", 0)),
    }


def download_vod(source_url: str, output_path: Path, resolution: int, force: bool) -> None:
    if output_path.exists() and not force:
        return
    ensure_dir(output_path.parent)
    temp_pattern = output_path.with_suffix(".%(ext)s")
    command = [
        "yt-dlp",
        "-f",
        f"bv*[height<={resolution}]+ba/b[height<={resolution}]",
        "--merge-output-format",
        "mp4",
        "-o",
        str(temp_pattern),
        source_url,
    ]
    run_passthrough(command)
    merged_output = output_path
    if not merged_output.exists():
        raise FileNotFoundError(f"Expected merged output was not created: {merged_output}")


def register_local_file(
    input_path: Path, output_path: Path, copy_input_file: bool, force: bool
) -> Path:
    resolved_input = input_path.resolve()
    if not copy_input_file:
        return resolved_input
    if output_path.exists() and not force:
        return output_path
    if resolved_input == output_path.resolve():
        return resolved_input
    ensure_dir(output_path.parent)
    shutil.copy2(input_path, output_path)
    return output_path


def build_clip(
    source_file: Path,
    clip_path: Path,
    segment: SegmentSpec,
    copy_clips: bool,
    force: bool,
) -> dict:
    if clip_path.exists() and not force:
        clip_probe = probe_media(clip_path)
        return {
            "label": segment.label,
            "start": segment.start,
            "end": segment.end,
            "start_seconds": parse_timestamp_to_seconds(segment.start),
            "end_seconds": parse_timestamp_to_seconds(segment.end),
            "clip_path": str(clip_path),
            **clip_probe,
        }

    ensure_dir(clip_path.parent)
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        str(source_file),
        "-ss",
        segment.start,
        "-to",
        segment.end,
    ]
    if copy_clips:
        command.extend(["-c", "copy"])
    else:
        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
            ]
        )
    command.append(str(clip_path))
    run_passthrough(command)

    clip_probe = probe_media(clip_path)
    return {
        "label": segment.label,
        "start": segment.start,
        "end": segment.end,
        "start_seconds": parse_timestamp_to_seconds(segment.start),
        "end_seconds": parse_timestamp_to_seconds(segment.end),
        "clip_path": str(clip_path),
        **clip_probe,
    }


def main() -> None:
    args = parse_args()
    vod_id = normalize_vod_id(args)
    output_root = Path(args.output_root)
    run_root = output_root / vod_id
    source_dir = run_root / "source"
    clips_dir = run_root / "clips"
    manifest_path = run_root / "manifest.json"
    source_file = source_dir / f"{vod_id}_source_720.mp4"

    ensure_dir(run_root)
    ensure_dir(source_dir)
    ensure_dir(clips_dir)

    if args.source_url:
        download_vod(args.source_url, source_file, args.resolution, args.force)
        source_mode = "downloaded"
    else:
        input_path = Path(args.input_file).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")
        source_file = register_local_file(
            input_path, source_file, args.copy_input_file, args.force
        )
        source_mode = "registered_local_file"

    source_probe = probe_media(source_file)
    segment_specs = [parse_segment(item) for item in args.segment]
    clips = []
    for index, segment in enumerate(segment_specs, start=1):
        safe_label = re.sub(r"[^a-zA-Z0-9_-]+", "_", segment.label).strip("_") or f"clip_{index}"
        clip_path = clips_dir / f"{index:02d}_{safe_label}.mp4"
        clips.append(
            build_clip(
                source_file=source_file,
                clip_path=clip_path,
                segment=segment,
                copy_clips=args.copy_clips,
                force=args.force,
            )
        )

    manifest = {
        "created_at_utc": utc_now_iso(),
        "vod_id": vod_id,
        "source_mode": source_mode,
        "source_url": args.source_url,
        "input_file": args.input_file,
        "source_file": str(source_file),
        "resolution_cap": args.resolution,
        "source_duration_seconds": source_probe["duration_seconds"],
        "source_size_bytes": source_probe["size_bytes"],
        "clips": clips,
        "notes": [
            "Provide --segment values when match or map boundaries are known.",
            "Use re-encoded clips by default for more accurate boundaries.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved manifest: {manifest_path}")
    print(f"Source file: {source_file}")
    print(f"Duration seconds: {source_probe['duration_seconds']:.3f}")
    print(f"Clips created: {len(clips)}")


if __name__ == "__main__":
    main()
