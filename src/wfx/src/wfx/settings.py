"""Settings constants for wfx package."""

import os

# Development mode flag - can be overridden by environment variable
DEV = os.getenv("PRIMEAGENT_DEV", "false").lower() == "true"
