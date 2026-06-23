# Day-1 Checklist

Use this checklist to connect a new operator agent to Travaso MCP and run one fake booking flow before the first real traveler.

## 1. Request a free key

Open the token page and request a free key:

```bash
open https://elitetravelsales.com/tokens
```

## 2. Save the token

Save the key as `TRAVASO_AGENT_TOKEN`. The skill also checks `TRAVASO_TOKEN` and `TRAVASO_API_KEY` as fallbacks.

```bash
export TRAVASO_AGENT_TOKEN="tk_live_travaso_REPLACE_WITH_YOUR_TOKEN"
export TRAVASO_TOKEN="$TRAVASO_AGENT_TOKEN"
export TRAVASO_API_KEY="$TRAVASO_AGENT_TOKEN"
```

## 3. Install the skill

Hermes Agent: copy this repo's skill files into the Hermes MCP skill directory, then restart Hermes.

```bash
mkdir -p ~/.hermes/skills/mcp/travaso-mcp
cp -R SKILL.md skill.json references scripts ~/.hermes/skills/mcp/travaso-mcp/
```

Claude Desktop: add this MCP server block to the Claude Desktop MCP config and restart Claude Desktop.

```json
{
  "mcpServers": {
    "travaso": {
      "url": "https://elitetravelsales.com/api/backend/mcp",
      "headers": {
        "Authorization": "Bearer tk_live_travaso_REPLACE_WITH_YOUR_TOKEN"
      }
    }
  }
}
```

Cursor: save this as `.cursor/mcp.json`, then restart Cursor.

```bash
mkdir -p .cursor
cat > .cursor/mcp.json <<'JSON'
{
  "mcpServers": {
    "travaso": {
      "url": "https://elitetravelsales.com/api/backend/mcp",
      "headers": {
        "Authorization": "Bearer tk_live_travaso_REPLACE_WITH_YOUR_TOKEN"
      }
    }
  }
}
JSON
```

Custom backend: keep the token server-side and connect your MCP client to the Travaso Streamable HTTP endpoint.

```json
{
  "mcp_servers": [
    {
      "type": "url",
      "name": "travaso",
      "url": "https://elitetravelsales.com/api/backend/mcp",
      "authorization_token": "tk_live_travaso_REPLACE_WITH_YOUR_TOKEN"
    }
  ],
  "tools": [
    {
      "type": "mcp_toolset",
      "mcp_server_name": "travaso"
    }
  ]
}
```

## 4. Run the health check

Run the unauthenticated probe first, then verify your token.

```bash
python3 scripts/health_check.py
TRAVASO_AGENT_TOKEN="tk_live_travaso_REPLACE_WITH_YOUR_TOKEN" python3 scripts/health_check.py --auth
```

## 5. Do a fake booking end-to-end

Search with fake traveler details. Use the returned `recommendationId` in the checkout request, but do not pay the Stripe checkout during a fake run.

```bash
curl -X POST https://elitetravelsales.com/api/backend/agent/hotel-quotes \
  -H "Authorization: Bearer ${TRAVASO_AGENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Santa Monica",
    "checkIn": "2026-08-21",
    "checkOut": "2026-08-24",
    "adults": 2,
    "rooms": 1,
    "firstName": "Avery",
    "lastName": "Stone",
    "email": "avery@example.com",
    "phoneNumber": "+14155550124",
    "maxResults": 5,
    "isLuxury": true
  }'
```

```bash
curl -X POST https://elitetravelsales.com/api/backend/agent/checkout-link \
  -H "Authorization: Bearer ${TRAVASO_AGENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendationId": "rec_from_hotel_quotes",
    "location": "Santa Monica",
    "checkIn": "2026-08-21",
    "checkOut": "2026-08-24",
    "adults": 2,
    "rooms": 1,
    "firstName": "Avery",
    "lastName": "Stone",
    "email": "avery@example.com",
    "phoneNumber": "+14155550124"
  }'
```

## 6. Add the conversion loop to your agent's system prompt

Paste this snippet from `references/agent-brief.md` into the hotel-selling agent's system prompt.

```text
You help travelers book hotels through Travaso's live inventory. When
a traveler asks about hotels in a destination, you:

1. Capture destination, check-in, check-out, adults, rooms, traveler
   first/last name, email, and phone.
2. Call search_competitive_hotel_quotes with all fields. Show 2-4
   results, each with public price, Travaso price, profit, and a
   fit-reason sentence.
3. Wait for the traveler to pick one.
4. Call create_offer_checkout_link with the chosen recommendationId
   and the full traveler payload. Send the returned Stripe URL in
   your next message.
5. Track the offerId. Tell the traveler commission is tracked from
   quote but payout unlocks when they finish their stay.
6. Use get_offer_status on follow-ups. Use cancel_offer only when
   the operator explicitly asks.

Never:
- Make up prices.
- Send the user to the hotel's direct website instead of the
  tracked checkout URL.
- Promise payout before the stay is finished.
- Show commission to the traveler.
- Expose the bearer token.
```

## 7. Ship to first real user

Before sending the first real quote, run the authenticated health check and ask the traveler for the required fields.

```text
I can check live hotel rates for you. Please send destination,
check-in date, check-out date, number of adults, rooms, traveler
first and last name, email, and phone.
```

```bash
TRAVASO_AGENT_TOKEN="tk_live_travaso_REPLACE_WITH_YOUR_TOKEN" python3 scripts/health_check.py --auth
```
