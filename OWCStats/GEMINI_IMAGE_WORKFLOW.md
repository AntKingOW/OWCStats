# Gemini Image Workflow

This project can use Gemini image editing to enhance low-resolution scoreboard frames before reading small numbers.

## Purpose

Use Gemini to improve readability of:

- player stat tables
- small scoreboard digits
- hero/role icons

The prompt is designed to preserve the original frame rather than creatively alter it.

## Current best source frame

- `C:\Users\user\Documents\Playground\OWCStats\temp_video\m1g1_frame_05.jpg`

## Setup

Set one of these environment variables in PowerShell:

```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

or

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

## Run

```powershell
python "C:\Users\user\Documents\Playground\OWCStats\gemini_upscale_image.py" `
  "C:\Users\user\Documents\Playground\OWCStats\temp_video\m1g1_frame_05.jpg" `
  -o "C:\Users\user\Documents\Playground\OWCStats\temp_video\single_frames\m1g1_frame_05_gemini.png"
```

## Notes

- Default model: `gemini-2.5-flash-image`
- The script sends the local image inline to Gemini with a readability-preserving edit prompt.
- Output is saved as a PNG.
- If Gemini returns only text and no image, the script prints the text response.

## Official references

- Google AI for Developers: Image generation with Gemini
- Google AI for Developers: Gemini vision/image understanding
