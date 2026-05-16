#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.yt-dlp-venv"
DOWNLOAD_ROOT="$ROOT_DIR/downloads"
AUDIO_DIR="$DOWNLOAD_ROOT/audio"
VIDEO_DIR="$DOWNLOAD_ROOT/video"

have_js_runtime() {
  command -v node >/dev/null 2>&1 \
    || command -v deno >/dev/null 2>&1 \
    || command -v qjs >/dev/null 2>&1
}

usage() {
  cat <<'EOF'
Download YouTube media for private testing into the local downloads folder.

Usage:
  ./download_youtube.sh audio <youtube-url> [extra yt-dlp args...]
  ./download_youtube.sh video <youtube-url> [extra yt-dlp args...]

Examples:
  ./download_youtube.sh audio "https://www.youtube.com/watch?v=..."
  ./download_youtube.sh video "https://www.youtube.com/watch?v=..."
  ./download_youtube.sh audio "https://www.youtube.com/watch?v=..." --download-sections "*00:30-01:00"
EOF
}

MODE="${1:-}"
URL="${2:-}"

if [[ -z "$MODE" || -z "$URL" ]]; then
  usage
  exit 1
fi

shift 2

if [[ ! -x "$VENV_DIR/bin/yt-dlp" ]]; then
  echo "Preparing download environment in $VENV_DIR ..."
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
  "$VENV_DIR/bin/pip" install -e "$ROOT_DIR" yt-dlp
fi

mkdir -p "$AUDIO_DIR" "$VIDEO_DIR"

if ! have_js_runtime; then
  echo "Note: no supported JavaScript runtime was found (node, deno, or qjs)."
  echo "yt-dlp may still work, but some YouTube downloads can warn or fail until one is installed."
  echo "Recommended on Ubuntu: sudo apt install nodejs"
fi

case "$MODE" in
  audio)
    if ! command -v ffmpeg >/dev/null 2>&1; then
      echo "ffmpeg is required for MP3 conversion. On Ubuntu: sudo apt install ffmpeg"
      exit 2
    fi

    exec "$VENV_DIR/bin/yt-dlp" \
      --newline \
      --no-playlist \
      --restrict-filenames \
      --extract-audio \
      --audio-format mp3 \
      --audio-quality 0 \
      --embed-metadata \
      -o "$AUDIO_DIR/%(title)s [%(id)s].%(ext)s" \
      "$URL" "$@"
    ;;
  video)
    exec "$VENV_DIR/bin/yt-dlp" \
      --newline \
      --no-playlist \
      --restrict-filenames \
      -f "bv*+ba/b" \
      --merge-output-format mp4 \
      --embed-metadata \
      -o "$VIDEO_DIR/%(title)s [%(id)s].%(ext)s" \
      "$URL" "$@"
    ;;
  *)
    echo "Unknown mode: $MODE"
    usage
    exit 1
    ;;
esac
