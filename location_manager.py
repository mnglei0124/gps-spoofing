import asyncio
import logging
from typing import Optional

from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pymobiledevice3.services.simulate_location import DtSimulateLocation
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
from pymobiledevice3.exceptions import NoDeviceConnectedError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class LocationManager:
    """
    Version-aware GPS spoofing manager.
    - iOS < 17: Uses DtSimulateLocation via USB lockdown.
    - iOS 17+: Uses DVT LocationSimulation via RSD tunnel.
    """

    def __init__(self):
        self.lockdown = None
        self.rsd: Optional[RemoteServiceDiscoveryService] = None
        self.dvt_provider: Optional[DvtProvider] = None
        self.location_service = None
        self.ios_version: Optional[str] = None
        self.device_name: Optional[str] = None

    async def connect(self, rsd_host: str = None, rsd_port: int = None):
        """Connect to device, auto-detecting iOS version."""

        if rsd_host and rsd_port:
            # iOS 17+ path: connect via RSD tunnel
            logger.info(f"Connecting via RSD tunnel at {rsd_host}:{rsd_port}...")
            self.rsd = RemoteServiceDiscoveryService((rsd_host, rsd_port))
            await self.rsd.connect()
            self.ios_version = self.rsd.product_version
            self.device_name = self.rsd.all_values.get("DeviceName", "Unknown")
            logger.info(f"Device: {self.device_name} | iOS {self.ios_version}")

            # Open DVT provider on top of RSD, then open LocationSimulation channel
            self.dvt_provider = DvtProvider(self.rsd)
            await self.dvt_provider.connect()
            self.location_service = LocationSimulation(self.dvt_provider)
            await self.location_service.connect()
        else:
            # Legacy path: connect via USB lockdown
            logger.info("Scanning for USB-connected device...")
            try:
                self.lockdown = await create_using_usbmux()
            except NoDeviceConnectedError:
                raise ConnectionError(
                    "No iOS device found via USB.\n"
                    "Make sure the device is plugged in and you tapped 'Trust'.\n"
                    "(Windows: iTunes/Apple Devices must be installed. macOS needs nothing extra.)"
                )

            self.ios_version = self.lockdown.product_version
            self.device_name = self.lockdown.all_values.get("DeviceName", "Unknown")
            logger.info(f"Device: {self.device_name} | iOS {self.ios_version}")

            major = int(self.ios_version.split(".")[0])
            if major >= 17:
                raise ConnectionError(
                    f"iOS {self.ios_version} detected — this version requires an RSD tunnel.\n"
                    "Step 1: Run in a separate admin terminal (Windows: Administrator, macOS: sudo):\n"
                    "    python -m pymobiledevice3 remote start-tunnel\n"
                    "Step 2: Re-run this script with the host/port it prints:\n"
                    "    python spoof.py --rsd-host <HOST> --rsd-port <PORT>"
                )

            # iOS < 17: use the direct simulate-location lockdown service
            self.location_service = DtSimulateLocation(self.lockdown)

    async def set_location(self, lat: float, lon: float):
        """Set the simulated GPS location."""
        if self.location_service is None:
            raise RuntimeError("Not connected. Call connect() first.")
        await self.location_service.set(lat, lon)

    async def clear_location(self):
        """Remove the simulated location (restore real GPS)."""
        if self.location_service is not None:
            logger.info("Clearing simulated location...")
            await self.location_service.clear()

    async def close(self):
        """Tear down connections."""
        if self.dvt_provider:
            await self.dvt_provider.close()
        if self.rsd:
            await self.rsd.close()
