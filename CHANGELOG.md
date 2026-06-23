# Changelog

## 1.1.0 — 2026-06-23
- **Endpoint fix:** switched from `https://elitetravelsales.com/mcp` to
  the production URL `https://elitetravelsales.com/api/backend/mcp`.
  The bare `/mcp` path returns 404; the backend MCP route lives under
  `/api/backend/mcp` and requires `Authorization: Bearer <...en>`.
- **Tool rename:** `search_hotels` → `search_competitive_hotel_quotes`.
  Now returns `recommendationId` values (used to be `hotel_id`).
- **New tool:** `cancel_offer` (operator-initiated cancellation only).
- **Tool rename:** `get_booking_status` → `get_offer_status`.
- **New required fields on quote:** traveler `firstName`, `lastName`,
  `email`, `phoneNumber`. Quoting without these fails Stripe checkout.
- **New UX rule:** wait for explicit traveler approval of a specific
  option before calling `create_offer_checkout_link`. Auto-creating
  before pick is wrong.
- **New UX rule:** commission is tracked from quote but payout
  unlocks when the traveler finishes their stay. Tell users.
- **Auth header fallback:** `x-travaso-agent-token: <token>` works
  for MCP clients that can't set `Authorization`.
- **REST endpoints documented:** `/api/backend/agent/hotel-quotes`,
  `/api/backend/agent/checkout-link`, `/api/backend/agent/portal/stats`.
- **New reference doc:** `references/agent-brief.md` (canonical
  system-prompt snippets to paste into new agents).
- **Health check:** now defaults to the production URL, returns a
  clear 401 (vs 404) when probing the live server, and prints the
  endpoint it actually hit.

## 1.0.0 — 2026-06-22
- Initial public release
- SKILL.md covers setup, conversion loop, tool surface, fallbacks
- `health_check.py` script for endpoint smoke-tests
- `references/tool-schemas.md` documents the advertised tool surface
- `references/fallbacks.md` covers what to do when the MCP server is down