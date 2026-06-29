from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

from fastmcp import FastMCP
from resonate.resonate import Resonate

if TYPE_CHECKING:
    from resonate.context import Context

mcp = FastMCP("timer")
resonate = Resonate(url=os.environ.get("RESONATE_URL", "http://localhost:8001"))


async def timer(ctx: Context, timer_name: str, seconds: int) -> str:
    print(f"Timer started: {timer_name} for {seconds} seconds", flush=True)
    await ctx.sleep(int(seconds))
    return "complete"


resonate.register(timer)


@mcp.tool()
def set_timer(timer_name: str, seconds: int) -> dict:
    """
    Set a timer with the given name and duration in seconds.

    Args:
        timer_name (str): The name of the timer.
        seconds (int): The duration of the timer in seconds.

    Returns:
        dict: A dictionary containing the promise ID of the timer.
    """
    resonate.run(timer_name, timer, timer_name, seconds)
    return {"promise_id": timer_name}


@mcp.tool()
async def get_timer_status(timer_name: str) -> dict:
    """
    Get the status of a timer by its name.

    Args:
        timer_name (str): The name of the timer.

    Returns:
        dict: A dictionary containing the status of the timer, either "running" or "complete".
    """
    if isinstance(timer_name, dict):
        timer_name = timer_name.get("timer_name", "")
    promise_id = f"{timer_name}"
    handle = await resonate.get(promise_id)
    if not handle.done():
        return {"status": "running"}
    return {"status": await handle.result()}


def main() -> None:
    mcp.run(transport="streamable-http", host="127.0.0.1", port=5001)


if __name__ == "__main__":
    main()
