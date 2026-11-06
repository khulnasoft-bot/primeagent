"""Entry point for the PrimeAgent MCP server.

Usage:
    python -m wfx.mcp
    # or via console script:
    wfx-mcp

Environment variables:
    PRIMEAGENT_SERVER_URL: PrimeAgent server URL (default: http://localhost:7860)
    PRIMEAGENT_API_KEY: API key for authentication (skips login)
"""

from wfx.mcp.server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
