<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/banner-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="./assets/banner-light.png">
    <img alt="Agent Tool Background Job — Resonate example" src="./assets/banner-dark.png">
  </picture>
</p>

# Async timer AI Agent tool | Resonate example application

This example shows a minimal example of Resonate + MCP.

To use Resonate in an MCP Server, the MCP Server needs to be run using "streamable-http" as the transport.

Therefore, you need a stdio -> streamable-http proxy running for Claude to talk to.

### proxy

```python
from fastmcp import FastMCP

# Create a proxy to a remote server
proxy = FastMCP.as_proxy(
    "http://localhost:5001/mcp",  # URL of the remote server
    name="Remote Server Proxy"
)


if __name__ == "__main__":
    proxy.run()  # Runs via STDIO for Claude Desktop
```

To run the proxy:

```shell
uv run proxy.py
```

### claude_desktop_config.json

Make sure Claude's config points at the proxy.

```json
{
  "mcpServers": {
    "timer": {
      "command": "uv", // or /opt/homebrew/bin/uv
      "args": [
        "--directory",
        "/FULL/PATH/TO/YOUR/TOOL/DIRECTORY/example-agent-tool-async-timer",
        "run",
        "proxy.py"
      ]
    }
  }
}
```

You should restart Claude desktop after changing this config.

On the MCP Server, make sure you return a promise ID - instead of blocking on a result.
Claude can then use the promise ID to check for the result at any point later on.

### timer mcp server

The function that runs in the background is registered with `resonate.register(timer)`.

**timer function**

```python
async def timer(ctx: Context, timer_name: str, seconds: int) -> str:
    print(f"Timer started: {timer_name} for {seconds} seconds", flush=True)
    await ctx.sleep(int(seconds))
    return "complete"

resonate.register(timer)
```

The functions that Claude interacts with are decorated with `@mcp.tool`

**set timer tool**

```python
@mcp.tool()
def set_timer(timer_name: str, seconds: int) -> dict:
    # tool description

    resonate.run(timer_name, timer, timer_name, seconds)
    return {"promise_id": timer_name}
```

**get timer status tool**

```python
@mcp.tool()
async def get_timer_status(timer_name: str) -> dict:
    # tool description

    promise_id = f"{timer_name}"
    handle = await resonate.get(promise_id)
    if not handle.done():
        return {"status": "running"}
    return {"status": await handle.result()}
```

To run the MCP server:

```shell
uv run timer.py
```
