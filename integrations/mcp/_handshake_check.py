"""CI smoke test: connect to the Waypoint MCP server over stdio and assert it
advertises its four tools. Run from the Waypoint root:
    .venv/bin/python integrations/mcp/_handshake_check.py
Exits non-zero if the server fails to start or a tool is missing.
"""
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECT = {"waypoint_doctor", "waypoint_scan", "waypoint_beacons", "waypoint_dark_zone"}


async def main():
    params = StdioServerParameters(command="bash", args=["bin/waypoint-mcp"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            names = {t.name for t in (await session.list_tools()).tools}
            missing = EXPECT - names
            assert not missing, f"MCP server missing tools: {missing}"
            print("MCP handshake OK:", sorted(names))


if __name__ == "__main__":
    asyncio.run(main())
