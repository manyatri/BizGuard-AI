"""
Switch Collaboration Bus Client — handles connection and messaging via Switch/Mattermost or internal event bus.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SwitchClient:
    """
    Connects to Switch agent collaboration bus or falls back honestly if unavailable.
    Does not pretend to be connected if the endpoint cannot be reached.
    """
    def __init__(self, endpoint_url: str = "ws://127.0.0.1:8765/switch-bus"):
        self.endpoint_url = endpoint_url
        self.is_connected = False
        self.error_reason: Optional[str] = None
        self._check_connection()

    def _check_connection(self):
        # We perform an honest socket/connection probe
        import socket
        from urllib.parse import urlparse
        try:
            parsed = urlparse(self.endpoint_url)
            host = parsed.hostname or "127.0.0.1"
            port = parsed.port or 8765
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((host, port))
            s.close()
            self.is_connected = True
            self.error_reason = None
        except Exception as e:
            self.is_connected = False
            self.error_reason = f"Switch bus not reachable at {self.endpoint_url}: {e}"

    def get_status(self) -> Dict[str, Any]:
        return {
            "bus_type": "Switch Collaboration Protocol",
            "endpoint": self.endpoint_url,
            "connected": self.is_connected,
            "status": "CONNECTED" if self.is_connected else "STANDALONE_LOCAL_FALLBACK",
            "message": "Connected to Switch agent collaboration bus" if self.is_connected else (
                f"Notice: Switch service is offline ({self.error_reason}). BizGuard AI is operating in autonomous local event-bus mode."
            )
        }


switch_client = SwitchClient()
