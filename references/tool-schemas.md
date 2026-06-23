# Tool Schemas (Travaso MCP)

> ⚠️ The exact tool surface is **discovered at runtime** via MCP's
> `tools/list` method. The schemas below describe the tools currently
> advertised on
> [elitetravelsales.com/tokens/setup](https://elitetravelsales.com/tokens/setup).
> Always verify against the live server on connect.

Use `mcporter list https://elitetravelsales.com/api/backend/mcp` or the
native MCP client's `list_tools()` to confirm the current surface
before writing production code against these.

---

## `search_competitive_hotel_quotes`

Find commissionable hotels for a destination + date range. Returns
`recommendationId` values that you pass to `create_offer_checkout_link`.

**Inputs:**

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `location` | string | yes | City name (e.g. `"Santa Monica"`) |
| `checkIn` | string (ISO date) | yes | `YYYY-MM-DD` |
| `checkOut` | string (ISO date) | yes | `YYYY-MM-DD` |
| `adults` | integer | yes | Number of adult guests |
| `rooms` | integer | yes | Number of rooms |
| `firstName` | string | yes | Traveler first name |
| `lastName` | string | yes | Traveler last name |
| `email` | string | yes | Traveler email |
| `phoneNumber` | string | yes | E.164 format (e.g. `+141****0124`) |
| `maxResults` | integer | no | Default 5 |
| `isLuxury` | boolean | no | Filter to luxury inventory |

**Returns:** Array of 2-4 hotel options, each with `recommendationId`,
public price, Travaso cost, profit, and a fit-reason sentence.

---

## `create_offer_checkout_link`

Build a Stripe-backed tracked checkout URL. **This is the only step
that attributes the booking to your agent key — commission only pays
on bookings made through this link.**

**Inputs:**

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `recommendationId` | string | yes | From `search_competitive_hotel_quotes` |
| `location` | string | yes | Same as the search |
| `checkIn` | string | yes | Same as the search |
| `checkOut` | string | yes | Same as the search |
| `adults` | integer | yes | Same as the search |
| `rooms` | integer | yes | Same as the search |
| `firstName` | string | yes | Same traveler |
| `lastName` | string | yes | Same traveler |
| `email` | string | yes | Same traveler |
| `phoneNumber` | string | yes | Same traveler |

**Returns:**

```
{
  "offerId": "of_xyz789",
  "checkoutUrl": "https://checkout.stripe.com/c/pay/cs_test_...",
  "expiresAt": "2026-08-21T22:00:00Z",
  "estimatedCommission": "112.00"
}
```

Display `checkoutUrl` **exactly as returned**. Don't rewrite it,
don't prettify it, don't send the user to the hotel's direct site
instead.

---

## `get_offer_status`

Check payment, booking, earning, and payout readiness for an offer.

**Inputs:** `offerId` (string, required)

**Returns:** `{ "status": "pending|paid|booked|staying|completed|cancelled|refunded", "earning": ..., "payoutReadyAt": ..., ... }`

Key statuses:
- `paid` — Stripe checkout completed, commission is tracked
- `booked` — hotel reservation confirmed
- `staying` — traveler is currently at the property
- `completed` — stay finished, payout unlocked
- `cancelled` / `refunded` — commission forfeit

---

## `cancel_offer`

Cancel an eligible offer. **Only call when the operator (you, the
agent owner) explicitly asks.** Auto-cancelling is a footgun.

**Inputs:** `offerId` (string, required)

**Returns:** Cancellation confirmation or error explaining why the
offer is not cancellable.

---

## REST fallbacks

For platforms that can't speak MCP. Same `Authorization` header.

- `POST /api/backend/agent/hotel-quotes` — same args as
  `search_competitive_hotel_quotes`
- `POST /api/backend/agent/checkout-link` — same args as
  `create_offer_checkout_link`
- `GET /api/backend/agent/portal/stats` — sales, bookings, earned
  commission, payout readiness. Web UI: https://elitetravelsales.com/agents/stats

---

## Adding new tools

If Travaso ships new tools after you install this skill, they'll
appear in the MCP client's tool list automatically (prefixed
`mcp_travaso_*`). You don't need to update this skill to use them —
just call them.

If a tool name changes or the protocol version moves, the connection
will fail with a clear error. Re-run `health_check.py` and update any
hardcoded tool references in your agent code.