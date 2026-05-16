#!/usr/bin/env bash
# Render demo_assets/diagrams/architecture.mmd → demo_assets/output/architecture.png
# Requires mermaid-cli (one-time install: npm i -g @mermaid-js/mermaid-cli)
# Or paste the .mmd source into https://mermaid.live for a quick view.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT_DIR="$ROOT/output"
mkdir -p "$OUT_DIR"

if ! command -v mmdc >/dev/null 2>&1; then
    echo "mmdc not found. Install with: npm i -g @mermaid-js/mermaid-cli" >&2
    echo "Or paste demo_assets/diagrams/architecture.mmd into https://mermaid.live" >&2
    exit 1
fi

mmdc \
    -i "$ROOT/diagrams/architecture.mmd" \
    -o "$OUT_DIR/architecture.png" \
    -w 1920 -H 1080 \
    -b transparent

echo "wrote $OUT_DIR/architecture.png"
