import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-flash-image"
DEFAULT_PROMPT = (
    "Enhance this esports scoreboard screenshot for readability only. "
    "Preserve the exact layout, colors, text, numbers, icons, and proportions. "
    "Do not invent or change any digits, names, or UI elements. "
    "Increase sharpness and legibility of small text and table numbers. "
    "Keep the image as a faithful restoration of the original frame."
)


def load_image_as_inline_part(image_path: Path) -> dict:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "image/png"
    data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": data,
        }
    }


def build_request_payload(image_path: Path, prompt: str) -> dict:
    return {
        "contents": [
            {
                "parts": [
                    load_image_as_inline_part(image_path),
                    {"text": prompt},
                ]
            }
        ]
    }


def extract_first_image(response_json: dict) -> bytes | None:
    candidates = response_json.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            inline_data = part.get("inline_data") or part.get("inlineData")
            if inline_data and inline_data.get("data"):
                return base64.b64decode(inline_data["data"])
    return None


def extract_text_parts(response_json: dict) -> list[str]:
    texts: list[str] = []
    candidates = response_json.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            text = part.get("text")
            if text:
                texts.append(text)
    return texts


def call_gemini(api_key: str, model: str, payload: dict) -> dict:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a local image to Gemini image editing and save the enhanced result."
    )
    parser.add_argument("input_image", help="Path to the source image")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to save the enhanced image. Defaults next to the input file.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Editing prompt to send with the image.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "Missing API key. Set GOOGLE_API_KEY or GEMINI_API_KEY before running.",
            file=sys.stderr,
        )
        return 1

    input_path = Path(args.input_image).expanduser().resolve()
    if not input_path.exists():
        print(f"Input image not found: {input_path}", file=sys.stderr)
        return 1

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}_gemini.png")
    )

    payload = build_request_payload(input_path, args.prompt)

    try:
        response_json = call_gemini(api_key=api_key, model=args.model, payload=payload)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"Gemini API request failed: HTTP {exc.code}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Gemini API request failed: {exc}", file=sys.stderr)
        return 1

    image_bytes = extract_first_image(response_json)
    if not image_bytes:
        print("Gemini returned no image output.", file=sys.stderr)
        texts = extract_text_parts(response_json)
        if texts:
            print("\n".join(texts), file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
