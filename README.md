# Travaso MCP — AI Agent Skill

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Version: 1.2.0](https://img.shields.io/badge/version-1.2.0-green.svg)]() [![Install with npx skills](https://img.shields.io/badge/npx%20skills-Tarzelf%2Ftravaso--mcp--skill-black?logo=npm)](https://skills.sh/tarzelf/travaso-mcp-skill)

**Sell hotels from any AI agent. Earn 3–20% commission per booking.**

This is the public skill for [Travaso MCP](https://elitetravelsales.com/tokens),
the commerce layer that lets any MCP-compatible agent search live hotel
rates, compare against public pricing, and issue attributed checkout
links.

## Install

### `npx skills` (Vercel's open skill registry)

```bash
npx skills install travaso-mcp
# or, install directly from this repo:
npx skills add Tarzelf/travaso-mcp-skill
```

### Hermes Agent

Drop the `SKILL.md` into `~/.hermes/skills/mcp/travaso-mcp/` (already
there if you're using this repo as a starter). Restart Hermes.

### Claude Desktop / Cursor / any MCP client

Add to your MCP client config:

```json
{
  "mcpServers": {
    "travaso": {
      "url": "https://elitetravelsales.com/api/backend/mcp",
      "headers": {
        "Authorization": "Bearer tk_live_travaso_..."
      }
    }
  }
}
```

### Claude Code terminal install

```bash
claude mcp add --transport http travaso https://elitetravelsales.com/api/backend/mcp \
  --header "Authorization: Bearer tk_live_travaso_..."
```

Get a key at [elitetravelsales.com/tokens](https://elitetravelsales.com/tokens).
Free tier earns 3% commission. Monthly/Annual earns 10–20%.

## ⚠️ Endpoint notes

- The MCP server is hosted at `/api/backend/mcp` (canonical URL).
  The bare `/mcp` path **307-redirects** to the canonical URL, so
  older configs and snippets keep working — prefer the canonical URL
  directly when wiring a new integration.
- Production pages: `/tokens`, `/tokens/setup`, `/agents/stats`. The
  pages `/pricing`, `/stats`, `/docs` return 404 — those are not the
  current route names. Use `/tokens` for pricing and `/agents/stats`
  for the agent dashboard.

## Auth

The canonical env var name is `TRAVASO_AGENT_TOKEN`. The skill also
accepts `TRAVASO_TOKEN` and `TRAVASO_API_KEY` as fallbacks for clients
that already standardised on a different name.

Header format: `Authorization: Bearer *** Some MCP clients can't set `Authorization` — Travaso
also accepts `x-travaso-agent-token: <token>` with the same value.

## What's in this repo

| Path | What it is |
|------|------------|
| `SKILL.md` | The skill itself — drop into your skills directory |
| `references/tool-schemas.md` | Tool signatures and return shapes |
| `references/agent-brief.md` | Canonical agent prompts to paste in |
| `references/fallbacks.md` | What to do when the MCP endpoint is down |
| `scripts/health_check.py` | Smoke-test that Travaso MCP is reachable |

## Run the health check

```bash
# Unauthenticated probe (verifies the server is up at the URL)
python3 scripts/health_check.py

# Authenticated probe (verifies your key works end-to-end)
TRAVASO_TOKEN=*** python3 scripts/health_check.py --auth
```

Returns:
- `✅ OK` — Travaso MCP is responding
- `❌ Auth rejected (HTTP 401)` — your key is bad, get a new one
- `❌ Endpoint not found (HTTP 404)` — wrong URL. The correct URL is
  `/api/backend/mcp`, not `/mcp`.

## Commission tiers

| Tier | Commission | When to use |
|------|------------|-------------|
| Free | 3% | Sandbox, demos, agent dev |
| Monthly | 10–20% | Live selling |
| Annual | 10–20% | Same as monthly, prepaid |

Commission is **tracked from quote** but **payout unlocks when the
traveler finishes their stay**. Tell the user this — it sets
expectations and reduces chargebacks.

## Tools (current)

| Tool | Purpose |
|------|---------|
| `search_competitive_hotel_quotes` | Quote hotels and return `recommendationId` values |
| `create_offer_checkout_link` | Create a Stripe-backed tracked checkout URL |
| `get_offer_status` | Check payment, booking, earning, payout readiness |
| `cancel_offer` | Cancel eligible offers (operator-initiated only) |

## Use cases

- **Concierge agents** — give users a real-time "I just checked,
  here's the best rate I can get you" answer with a checkout link
- **Itinerary planners** — sell the hotel as part of a multi-day plan
  instead of just recommending "you should check Booking.com"
- **Travel MVPs** — skip building a booking engine; Travaso handles
  inventory, Stripe checkout, and attribution
- **Multi-agent marketplaces** — every agent on your platform gets
  its own key, its own tracked bookings, its own payouts

## What this skill does NOT do

- It does not book flights, cars, or vacation rentals (hotels only)
- It does not auto-charge the user — checkout is a real Stripe link
  the user clicks
- It does not give commission mechanics to the user — that's your
  business
- It does not bypass price-fluctuation. Always re-call
  `search_competitive_hotel_quotes` immediately before sending the
  link.

## License

MIT — use it, fork it, ship it.
