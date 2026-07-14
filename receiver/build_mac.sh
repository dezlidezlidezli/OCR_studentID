#!/usr/bin/env bash
# build_mac.sh — builds ID Wedge.app from wedge_app.py
# Run from this directory: bash build_mac.sh

set -e
cd "$(dirname "$0")"

echo "=== ID Wedge macOS build ==="
echo ""

# ── 1. Install build deps ─────────────────────────────────────────────────────
echo "→ Installing dependencies…"
pip install --quiet paho-mqtt cryptography pynput pyinstaller

# ── 2. PyInstaller ────────────────────────────────────────────────────────────
echo "→ Building .app bundle…"
pyinstaller \
    --name "ID Wedge" \
    --windowed \
    --noconfirm \
    --clean \
    --osx-bundle-identifier "com.idwedge.receiver" \
    wedge_app.py

# ── 3. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "✓  dist/ID\ Wedge.app is ready"
echo ""
echo "To distribute: zip the .app and share it."
echo ""
echo "⚠  Recipients need to do this once on first launch:"
echo "   1. Right-click the app → Open  (bypasses 'unidentified developer' warning)"
echo "   2. System Settings → Privacy & Security → Accessibility"
echo "      → enable 'ID Wedge'  (required so it can type into other apps)"
echo ""
