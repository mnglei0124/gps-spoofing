#!/usr/bin/env bash
#
# One-shot macOS launcher: starts the iOS 17+ RSD tunnel (needs sudo),
# waits for it to come up, then runs the spoofer against it. Shuts the
# tunnel down automatically on exit.
#
# Usage (run ./setup_mac.sh first):
#   ./spoof_mac.sh                      # default coords, with jitter
#   ./spoof_mac.sh --lock               # lock to default coords
#   ./spoof_mac.sh --lat 48.8584 --lon 2.2945 --lock
#
# Any arguments are passed straight through to spoof.py.

set -euo pipefail
cd "$(dirname "$0")"

VENV_PY=".venv/bin/python"
PATTERN="pymobiledevice3 remote start-tunnel"

if [ ! -x "$VENV_PY" ]; then
    echo "[ERROR] .venv not found. Run ./setup_mac.sh first." >&2
    exit 1
fi

TUNNEL_LOG="$(mktemp -t gps-spoof-tunnel)"

cleanup() {
    echo
    echo "Shutting down tunnel..."
    sudo pkill -f "$PATTERN" 2>/dev/null || true
    rm -f "$TUNNEL_LOG"
}
trap cleanup EXIT INT TERM

echo "=========================================="
echo "        GPS Spoofer (macOS launcher)"
echo "=========================================="
echo "Starting the RSD tunnel requires admin rights."
sudo -v

echo "[1/2] Starting tunnel..."
# --script-mode prints a single line: "<RSD_HOST> <RSD_PORT>"
sudo "$VENV_PY" -m pymobiledevice3 remote start-tunnel --script-mode \
    >"$TUNNEL_LOG" 2>&1 &

RSD_HOST=""
RSD_PORT=""
for _ in $(seq 1 60); do
    # First whitespace-separated line that looks like "<host> <port>".
    read -r RSD_HOST RSD_PORT < <(grep -E '^[^[:space:]]+[[:space:]]+[0-9]+$' "$TUNNEL_LOG" | head -1) || true
    if [ -n "$RSD_HOST" ] && [ -n "$RSD_PORT" ]; then
        break
    fi
    sleep 1
done

if [ -z "$RSD_HOST" ] || [ -z "$RSD_PORT" ]; then
    echo "[ERROR] Tunnel did not start. Output was:" >&2
    cat "$TUNNEL_LOG" >&2
    echo >&2
    echo "Checklist: iPhone unlocked, trusted, and Developer Mode ON." >&2
    exit 1
fi

echo "      Tunnel up → host=$RSD_HOST port=$RSD_PORT"
echo "[2/2] Starting spoofer (Ctrl+C to stop and restore real location)..."
echo

"$VENV_PY" spoof.py --rsd-host "$RSD_HOST" --rsd-port "$RSD_PORT" "$@"
