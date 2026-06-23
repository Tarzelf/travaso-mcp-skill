#!/usr/bin/env python3
"""
Travaso MCP health check.

Verifies that the Travaso MCP endpoint is reachable and responds to a
JSON-RPC initialize. Use this:
  - After wiring Travaso into a new agent
  - Before sending quotes to users (so you don't fabricate rates off a dead endpoint)
  - When users report "the agent gave me a weird error"

Exit codes:
  0 = healthy
  1 = endpoint unreachable / non-MCP response
  2 = endpoint responds but rejects the key (401 / 403)

Auth:
  - By default, sends an unauthenticated initialize so you can verify
    the server is up at the URL.
  - Pass --auth to include the bearer token from env
    (`TRAVASO_AGENT_TOKEN`, with `TRAVASO_TOKEN` and `TRAVASO_API_KEY`
    accepted as fallbacks) to verify your key works end-to-end.
"""
import json
import os
import sys
import urllib.request
import urllib.error

ENDPOINT = os.environ.get(
    "TRAVASO_MCP_URL",
    "https://elitetravelsales.com/api/backend/mcp",
)

INIT_PAYLOAD = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "travaso-health-check", "version": "1.0.0"},
    },
}


def main() -> int:
    body = json.dumps(INIT_PAYLOAD).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "travaso-health-check/1.1",
        },
        method="POST",
    )
    if "--auth" in sys.argv:
        token = (
            os.environ.get("TRAVASO_AGENT_TOKEN")
            or os.environ.get("TRAVASO_TOKEN")
            or os.environ.get("TRAVASO_API_KEY")
        )
        if not token:
            print("❌ --auth passed but no token found in env")
            print("   Set one of: TRAVASO_AGENT_TOKEN, TRAVASO_TOKEN, TRAVASO_API_KEY")
            return 2
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"❌ Auth rejected: HTTP {e.code}")
            print("   Your key is invalid, expired, or missing.")
            print("   Request a new one at https://elitetravelsales.com/tokens")
            print(f"   Endpoint: {ENDPOINT}")
            return 2
        if e.code == 404:
            print(f"❌ Endpoint not found: HTTP 404 on {ENDPOINT}")
            print("   Travaso MCP server is not deployed at this URL.")
            print("   The correct production URL is:")
            print("     https://elitetravelsales.com/api/backend/mcp")
            print("   (The bare /mcp path 307-redirects to that URL too,")
            print("    but if you're seeing 404 you've mistyped the path.)")
            print("   Notify the operator. Do NOT quote rates until it recovers.")
            return 1
        print(f"❌ HTTP {e.code} from {ENDPOINT}: {e.reason}")
        return 1
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach {ENDPOINT}: {e.reason}")
        return 1
    except TimeoutError:
        print(f"❌ Timeout talking to {ENDPOINT}")
        return 1

    if status != 200:
        print(f"❌ Unexpected status {status}")
        print(raw[:500])
        return 1

    # Strip SSE `data:` prefix if present, then parse JSON.
    if raw.startswith("data:"):
        raw = raw[len("data:"):].strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(f"❌ Non-JSON response from {ENDPOINT}:")
        print(raw[:500])
        return 1

    if "result" in payload or "error" in payload:
        server = (payload.get("result") or {}).get("serverInfo") or {}
        name = server.get("name", "unknown")
        version = server.get("version", "?")
        print(f"✅ OK — Travaso MCP responding at {ENDPOINT}")
        print(f"   server: {name} v{version}")
        return 0

    print("❌ Response did not contain JSON-RPC result/error:")
    print(json.dumps(payload, indent=2)[:500])
    return 1


if __name__ == "__main__":
    sys.exit(main())