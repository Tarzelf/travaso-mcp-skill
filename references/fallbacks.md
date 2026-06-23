# Fallback Behaviour When the MCP Endpoint Is Down

The Travaso MCP server is the only way to issue **attributed** checkout
links that pay you a commission. If it's unreachable, you can't earn
commission on a booking. That doesn't mean you stop helping the user —
it means you help without commission, and tell them when the commerce
layer is back.

## Don'ts

- **Don't fabricate prices.** No "Booking.com shows $X" without the
  API confirming it. The user may click your fake quote and book
  somewhere else, then blame you.
- **Don't promise a checkout link you can't issue.** If the endpoint
  is down, `create_offer_checkout_link` will error. Don't tell the
  user "here's your link" — generate it via the API, or say "I'll
  send the link once our booking system is back online."
- **Don't try to "fake it" with a third-party booking widget.** The
  whole Travaso value is attribution. A Stripe checkout URL pointed
  at a non-Travaso inventory, or a direct hotel link, doesn't
  attribute back to you and may not be a better deal than what the
  user would find themselves.
- **Don't hit `/mcp`.** The server lives at `/api/backend/mcp`.
  Hitting `/mcp` returns 404. If your health check is hitting `/mcp`,
  fix the URL before assuming the server is down.

## Dos

- **Acknowledge the gap honestly.** "Our booking system is having a
  moment — I'll point you to the hotel's direct page so you can
  still grab the room." Honesty beats fabricated savings.
- **Send the user to the hotel's direct booking page** if the
  property is well-known. They lose the comparison but they don't
  lose the room.
- **Add the request to a retry queue.** When the endpoint is back,
  the user may still be shopping. Send a follow-up with a live quote
  if they opted in.
- **Notify the operator.** If `health_check.py` fails three times in
  a row, that's a deploy problem. Ping the operator (or post to
  whatever status channel Travaso maintains).

## How to detect a soft failure

A 200 OK with an empty/error JSON-RPC payload is also a failure mode.
The `health_check.py` script handles this — it expects either `result`
or `error` in the payload. If you see neither, treat it as
unreachable.

Common soft failures:
- CORS or auth misconfiguration → endpoint loads but rejects every
  call
- Rate-limit on a free key during a spike
- The MCP server has the wrong protocol version advertised

In all of these cases, fall back to "point at hotel direct page"
and notify the operator. Don't try to work around silently.

## Recovery test

After the endpoint recovers, re-run:

```bash
TRAVASO_TOKEN=<your-...n python3 ~/.hermes/skills/mcp/travaso-mcp/scripts/health_check.py --auth
```

Then send the user a follow-up with the live quote and a real
checkout link. Most travel searches have a 24-72 hour purchase
window — staying in touch during downtime is how you keep the
conversion.

## Auth header gotcha

If the client platform can't set `Authorization` (some MCP clients
restrict custom headers), Travaso also accepts `x-travaso-agent-token:
<token>` with the same token value. Use whichever the client
supports.