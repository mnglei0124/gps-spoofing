# GPS Spoofer 🛰️

A professional, standalone GPS simulation utility for iOS devices. Designed for Windows users to easily override their iPhone's location for app testing and development.

Supports all iOS versions, including **iOS 17 and iOS 18**.

## Features
- **Auto-Detection**: Standard mode for iOS < 17.
- **RSD Tunneling**: Integrated support for the new iOS 17+ Remote Service Discovery (RSD) protocol.
- **Lock Mode**: Stay at a static coordinate without jitter.
- **Portable**: Includes a one-click setup script for Windows.

---

## 🛠️ Installation (Windows)

### 1. Prerequisites
- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/windows/). Make sure to check **"Add Python to PATH"** during installation.
- **iTunes (standard version)**: Ensure the classic Apple Mobile Device drivers are installed. Use the executable from Apple.com, not the Microsoft Store version if possible.

### 2. Setup
1. Clone or download this repository.
2. Double-click **`setup_windows.bat`** to automatically install all required Python libraries.

## 🍎 Installation (macOS)

1. Install Python 3.10+ (`brew install python` or from [python.org](https://www.python.org/)). No iTunes needed.
2. Run the setup script **once**:
   ```bash
   chmod +x setup_mac.sh && ./setup_mac.sh
   ```
3. After setup, just run the single launcher. It starts the iOS 17+ tunnel (prompts for your admin password), runs the spoofer, and tears the tunnel down on exit — no second terminal needed:
   ```bash
   ./spoof_mac.sh                 # default coords
   ./spoof_mac.sh --lock          # lock to default coords
   ./spoof_mac.sh --lat 48.8584 --lon 2.2945 --lock
   ```
   Any arguments are passed straight through to `spoof.py`.

   > Prefer the manual two-step flow instead? Start the tunnel with `sudo .venv/bin/python -m pymobiledevice3 remote start-tunnel`, then run `.venv/bin/python spoof.py --rsd-host <HOST> --rsd-port <PORT>`.

---

## 🚀 How to Use

### For iOS < 17
1. Connect your iPhone via USB.
2. Tap "Trust" on the phone if prompted.
3. Run:
   ```bash
   python spoof.py
   ```

### For iOS 17 & 18 (RSD Tunnel)
Due to Apple's security changes, iOS 17+ requires a two-step process:

**Step 1: Start the Tunnel (Admin Terminal)**
1. Open a terminal as **Administrator**.
2. Run:
   ```bash
   python -m pymobiledevice3 remote start-tunnel
   ```
3. Look for the `Created tunnel` line. It will show a **Host** (e.g., `fde2:2fb0...`) and a **Port** (e.g., `57116`).

**Step 2: Start Spoofing**
1. Open a **new terminal** (no admin needed).
2. Run the script with the host and port from Step 1:
   ```bash
   python spoof.py --rsd-host <HOST> --rsd-port <PORT> --lock
   ```

---

## 📍 Usage Examples
- **Lock to a location**:
  `python spoof.py --rsd-host fdab:33c7:271e::1 --rsd-port 57116 --lock`
- **Use custom coordinates**:
  `python spoof.py --lat 48.8584 --lon 2.2945` (Eiffel Tower)
- **Use default location (configured in script)**:
  `python spoof.py`

---

## ⚠️ Troubleshooting
- **Device not connected**: Ensure your phone is unlocked and "Developer Mode" is ON (Settings > Privacy & Security > Developer Mode).
- **RSD Browse is empty**: Ensure the **Bonjour Service** is running in Windows Services and your firewall isn't blocking Python.

## License
MIT License. See [LICENSE](LICENSE) for details.
