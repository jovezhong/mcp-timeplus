"""Environment configuration for the MCP Timeplus server.

This module handles all environment variable configuration with sensible defaults
and type conversion.
"""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class TimeplusConfig:
    """Configuration for Timeplus connection settings.

    This class handles all environment variable configuration with sensible defaults
    and type conversion. It provides typed methods for accessing each configuration value.

    Required environment variables:
        TIMEPLUS_HOST: The hostname of the Timeplus server
        TIMEPLUS_USER: The username for authentication

    Optional environment variables (with defaults):
        TIMEPLUS_PASSWORD: The password for authentication (default: empty string)
        TIMEPLUS_PORT: The port number (default: 8443 if secure=True, 8123 if secure=False)
        TIMEPLUS_SECURE: Enable HTTPS (default: false)
        TIMEPLUS_VERIFY: Verify SSL certificates (default: true)
        TIMEPLUS_CONNECT_TIMEOUT: Connection timeout in seconds (default: 30)
        TIMEPLUS_SEND_RECEIVE_TIMEOUT: Send/receive timeout in seconds (default: 300)
        TIMEPLUS_DATABASE: Default database to use (default: default)
        TIMEPLUS_READ_ONLY: Enable read-only mode (default: true)
    """

    def __init__(self):
        """Initialize the configuration from environment variables."""
        self._validate_required_vars()

    @property
    def host(self) -> str:
        """Get the Timeplus host."""
        return os.getenv("TIMEPLUS_HOST", "localhost")

    @property
    def port(self) -> int:
        """Get the Timeplus port.

        Defaults to 8443 if secure=True, 8123 if secure=False.
        Can be overridden by TIMEPLUS_PORT environment variable.
        """
        if "TIMEPLUS_PORT" in os.environ:
            return int(os.environ["TIMEPLUS_PORT"])
        return 8443 if self.secure else 8123

    @property
    def username(self) -> str:
        """Get the Timeplus username."""
        return os.getenv("TIMEPLUS_USER", "default")

    @property
    def password(self) -> str:
        """Get the Timeplus password."""
        return os.getenv("TIMEPLUS_PASSWORD", "")

    @property
    def database(self) -> Optional[str]:
        """Get the default database name if set."""
        return os.getenv("TIMEPLUS_DATABASE", "default")

    @property
    def secure(self) -> bool:
        """Get whether HTTPS is enabled.

        Default: False
        """
        return os.getenv("TIMEPLUS_SECURE", "false").lower() == "true"

    @property
    def verify(self) -> bool:
        """Get whether SSL certificate verification is enabled.

        Default: True
        """
        return os.getenv("TIMEPLUS_VERIFY", "true").lower() == "true"

    @property
    def connect_timeout(self) -> int:
        """Get the connection timeout in seconds.

        Default: 30
        """
        return int(os.getenv("TIMEPLUS_CONNECT_TIMEOUT", "30"))

    @property
    def send_receive_timeout(self) -> int:
        """Get the send/receive timeout in seconds.

        Default: 300 (Timeplus default)
        """
        return int(os.getenv("TIMEPLUS_SEND_RECEIVE_TIMEOUT", "300"))

    @property
    def readonly(self) -> bool:
        """Get whether only read-only SQL is enabled.

        Default: true
        """
        return os.getenv("TIMEPLUS_READ_ONLY", "true").lower() == "true"

    def get_client_config(self) -> dict:
        """Get the configuration dictionary for timeplus_connect client.

        Returns:
            dict: Configuration ready to be passed to timeplus_connect.get_client()
        """
        config = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "secure": self.secure,
            "verify": self.verify,
            "connect_timeout": self.connect_timeout,
            "send_receive_timeout": self.send_receive_timeout,
            "client_name": "mcp_timeplus",
        }

        # Add optional database if set
        if self.database:
            config["database"] = self.database

        return config

    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set.

        Raises:
            ValueError: If any required environment variable is missing.
        """
        missing_vars = []

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Global instance for easy access
config = TimeplusConfig()
