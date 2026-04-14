"""
iOS GPS Spoofing Utility
========================
Automatically detects your iOS version and uses the right method:
  - iOS < 17  → direct USB (just plug in & trust)
  - iOS 17+   → requires an RSD tunnel (see --help)

Usage:
  python spoof.py                                   # auto-detect via USB
  python spoof.py --rsd-host fd7b::1 --rsd-port 123 # iOS 17+ tunnel
  python spoof.py --lat 35.6762 --lon 139.6503       # custom coords (Tokyo)
"""

import argparse
import asyncio
import random
import sys

from location_manager import LocationManager

# Default: Target location
DEFAULT_LAT = 51.27711753915927
DEFAULT_LON = 30.214674706106198


def generate_jitter(coord: float, amount: float = 0.00005) -> float:
    """Small random offset to mimic natural GPS drift."""
    return coord + random.uniform(-amount, amount)


async def run_simulation(manager: LocationManager, lat: float, lon: float):
    print(f"\n🛰️  Simulating GPS at {lat:.6f}, {lon:.6f}")
    print("Press Ctrl+C to stop and restore real location.\n")

    try:
        if manager.lock_mode:
            print("  🔒 Jitter disabled. Locking location.")
            await manager.set_location(lat, lon)
            while True:
                await asyncio.sleep(3600)  # Just wait long-term
        else:
            while True:
                j_lat = generate_jitter(lat)
                j_lon = generate_jitter(lon)
                print(f"  📍 {j_lat:.6f}, {j_lon:.6f}")
                await manager.set_location(j_lat, j_lon)
                await asyncio.sleep(random.uniform(3, 7))
    except asyncio.CancelledError:
        pass


async def main():
    parser = argparse.ArgumentParser(
        description="iOS GPS Spoofing Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python spoof.py\n"
               "  python spoof.py --lat 35.6762 --lon 139.6503\n"
               "  python spoof.py --rsd-host fd7b::1 --rsd-port 12345\n",
    )
    parser.add_argument("--lat", type=float, default=DEFAULT_LAT, help="Target latitude")
    parser.add_argument("--lon", type=float, default=DEFAULT_LON, help="Target longitude")
    parser.add_argument("--rsd-host", help="RSD tunnel host (iOS 17+)")
    parser.add_argument("--rsd-port", type=int, help="RSD tunnel port (iOS 17+)")
    parser.add_argument("--lock", action="store_true", help="Disable jitter and lock location")
    args = parser.parse_args()

    manager = LocationManager()
    manager.lock_mode = args.lock

    # ── Connect ──────────────────────────────────────────────
    try:
        await manager.connect(rsd_host=args.rsd_host, rsd_port=args.rsd_port)
    except ConnectionError as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Connected to {manager.device_name} (iOS {manager.ios_version})")

    # ── Simulate ─────────────────────────────────────────────
    try:
        await run_simulation(manager, args.lat, args.lon)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping…")
    finally:
        await manager.clear_location()
        await manager.close()
        print("✅ Location restored. Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExited.")