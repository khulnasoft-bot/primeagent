"""Entry point for running the PrimeAgent Agentic MCP server.

This allows running the server with:
    python -m primeagent.agentic.mcp
"""

from primeagent.agentic.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
