# Project Overview

## Purpose
Audio file transcription and splitting tool using OpenAI Whisper.
Transcribe audio → edit segments in GUI → export split audio files.

## Tech Stack
- Backend: Python (uv for package management)
- Frontend: JavaScript (Flask-served)
- Python 3.10-3.12 (3.13+ not supported)

## Architecture
- Core layer: `src/` (no print, returns data, raises exceptions)
- CLI layer: `transcribe.py`, `split.py`, `export_edit.py`, `edit.py`
- GUI layer: `gui/` (Flask backend + JS frontend)

## Key Files
- `transcript.json`: export settings + exported segments
- `edit_segments.json`: all segments for editing
- `docs/`: specification documents

## Commands
- `uv run transcribe.py <audio>`: transcribe
- `uv run split.py <dir>`: split/export
- `uv run edit.py <dir>`: launch GUI
- `uv sync`: install dependencies
