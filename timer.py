from fastmcp import FastMCP
from resonate import Resonate

mcp = FastMCP("timer")
resonate = Resonate.remote()


@resonate.register
def timer(ctx, timer_name, seconds):
    print(f"Timer started: {timer_name} for {seconds} seconds")
    yield ctx.sleep(int(seconds))  # Convert seconds to milliseconds
    return "complete"


@mcp.tool()
def set_timer(timer_name, seconds):
    """
    Set a timer with the given name and duration in seconds.

    Args:
        timer_name (str): The name of the timer.
        seconds (int): The duration of the timer in seconds.

    Returns:
        dict: A dictionary containing the promise ID of the timer.
    """

    _ = timer.run(timer_name, timer_name, seconds)
    return {"promise_id": timer_name}


@mcp.tool()
def get_timer_status(timer_name):
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
    handle = resonate.get(promise_id)
    if not handle.done():
        return {"status": "running"}
    return {"status": handle.result()}


def main():  
    mcp.run(transport='streamable-http', host='127.0.0.1', port=5001)
    # mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
