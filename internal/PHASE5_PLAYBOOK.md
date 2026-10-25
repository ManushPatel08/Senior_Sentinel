# Senior Sentinel: Phase 5 Playbook

As of Sat Sep 26, 5:00pm. Phase 5 runs **5:00–7:30pm**.

Read `PRODUCT_V2.md` first, at least Sections 0, 2 and 3. It explains why we're changing course: the four guards (Ask, Card, Agent, Family) and how Senior Sentinel stops real scams. This playbook is the first build step of v2.

**What Phase 5 is for.** Two things:
1. Prove every risky new piece with **one real round trip**: the card network sandbox, the scam radar, the phone line, several Visa sandbox merchants, and Visa's agent-mandate and card-controls APIs.
2. Lay the foundations everyone builds on in Phase 6: the contracts, mandate v2, the merchant registry, the design system, and the filler fix.

Every open fix from Phases 1–4 and from today's audit is folded in, marked **Fix**.

At 7:30 we decide go or no-go on each risky piece. Anything red takes its fallback (`PRODUCT_V2.md` Section 8) and Phase 6 builds on what's green.

---

## 1. Phase 5 at a glance

| Time | Everyone | Manush (Ruth's voice, services laptop) | Rohan (Ask guard) | Dhruv (Card and Family guards) | Vraj (Agent guard, Visa) |
|---|---|---|---|---|---|
| 5:00–5:25 | Kickoff: read `PRODUCT_V2.md` 0, 2 and 3; agree the contracts (Section 3); open accounts (Section 1.1); pull main | | | | |
| 5:25–6:15 | Build | Tunnel and passkey on the services laptop (V5-1); filler fix (V5-2) | Radar probe (R5-1); risk state (R5-3) | Lithic round trip (D5-1); design tokens (D5-4) | Merchant registry and sandbox accounts (X5-1); Visa probes (X5-4) |
| 6:15 | 5-minute check-in: design tokens pushed; the tunnel URL shared | | | | |
| 6:15–7:15 | Build | Persona v2 and tool stubs (V5-3); phone line trial (V5-4) | `/scam-check` v0 (R5-2); rules and eval (R5-4) | Card decisions (D5-2); mandate v2 (D5-3) | Biller (X5-2); catalog across stores (X5-3) |
| 7:15–7:30 | Go/no-go (Section 8); push branches | | | | |
| 7:30 | Phase 6 starts; I merge Phase 5 into main while you build | | | | |

### 1.1 Accounts to open at 5:00 (each takes under 10 minutes)

| Account | Who | Where | Put in `.env` (never commit) |
|---|---|---|---|
| Lithic sandbox | Dhruv | app.lithic.com/signup → Settings → API keys | `LITHIC_API_KEY` |
| ngrok static domain on the **services laptop's own** ngrok account | Manush | dashboard.ngrok.com → Domains (one free static domain per account) | `TUNNEL_HOST` |
| Extra Cybersource sandbox merchants (pharmacy, household, power company) | **Manush, Rohan, Dhruv: one each** (the signup has a CAPTCHA); send the keys to Vraj privately | Section 7.1 | `CYBS_PARKSIDE_*`, `CYBS_MAINST_*`, `CYBS_PEACHTREE_*` |
| xAI phone number (Voice Agent Builder) | Manush | console.x.ai → Voice → Agents | Section 4, V5-4 |
| Visa Developer project (for Visa Transaction Controls) | Vraj | developer.visa.com → Dashboard → Create project | cert files in `keys/visa/` (gitignored) |

### 1.2 Pass conditions at 7:30 (binary)

1. **Topology.** On the services laptop's own tunnel, Priya's phone signs in with a newly registered passkey and **sees an order placed at the station**. This is the fix for "my friend can't see the order".
2. **Filler.** A five-turn shopping session has no "One moment", "Un momento" or "एक मिनट". A soft sound plays while tools run. Release-to-first-sound is written down.
3. **Card.** A Lithic simulated swipe reaches our `/card/asa` through the tunnel with its HMAC verified:
   - A $20 grocery swipe (MCC 5411) is **approved**.
   - A gift-card store swipe (MCC 6540) is **declined** with `UNAUTHORIZED_MERCHANT`.
   - The decision takes under 300 ms, and the Lithic transaction shows the result.
4. **Cool-down.** After a `/scam-check` returns `scam`, a $45 pharmacy swipe (MCC 5912) that normally passes is **declined**, with reason `card_cooldown`.
5. **Radar.** The grandparent, power-company and tech-support stories each get a cited verdict in under 12 s (or from the cache), with sources listed.
6. **Merchants.** Corner Market, Parkside Pharmacy, Main Street Home and Peachtree Power have each created one real Visa sandbox Pay by Link. Separate accounts or one account with descriptors is fine; write down which.
7. **Phone line.** A call to the number is answered by Grok in the Senior Sentinel persona and one of our tools runs. Otherwise the line is cut, with the reason written down.
8. **Visa probes.** The Intelligent Commerce path probe (`/icc` and `/acp`), Decision Manager and Visa Transaction Controls are each marked *works*, *not enabled* (with the HTTP status) or *dropped*.
9. **Contracts on branches.** `contracts/merchants.json`, mandate v2 schema, event types, and the public routes in `ports.md`.
10. **Design tokens** pushed: `design/tokens.css`, logo and shield icon.
11. **Fixes** (Section 2) closed, or written up as Phase 6 items with an owner.

**Git.** Same rules as before:
- Branch from main with no phase in the name (e.g. `vraj/merchants`).
- Commit messages describe the change.
- The attribution setting is on.
- **Build at least part of your work in Cursor** and screenshot it (an xAI challenge requirement).

---

## 2. Fixes carried over from Phases 1–4 and today's audit

| # | Owner | Fix | Done when |
|---|---|---|---|
| F1 | Manush | **Commit the shared TLS context.** It's written but uncommitted on the services laptop: `common/tls.py`, used by relay, merchant events, merchant verify and policy screen. Creating an httpx client cost about 0.5 s on that laptop, which made the relay answer in 1–5 s, the station mark it DOWN, and a relay timing test fail. Say "commit & push" and I'll do it. | On main; the relay answers `/health` in under 10 ms with the wall open |
| F2 | Manush | Priya's passkey and the tunnel run on the **services laptop's own ngrok domain**. The old domain belongs to another account and can't start here. V5-1. | Pass condition 1 |
| F3 | All | `POLICY_CODE_KEY`: policy refuses to start without it. Set it on the services laptop (done) and **copy the same value** to any laptop that runs the caregiver app. | Policy starts; approvals work from the phone |
| F4 | Manush | Re-record the cached replay sessions. The fix for the late "yes" only applies when saving. | Moves to Phase 7 (with the new demo) |
| F5 | Manush | `purchase_history` returns no `say`, though the prompt says to say it. Add a short summary `say`. | Station test |
| F6 | Manush | "Where is my order?" says only "Your order is paid." Add the pickup code and "ready after 3 pm" for paid and preparing orders. | Station test |
| F7 | Manush | Minor: `speakFixed` sets `lastSpoken` before it may bail out; the asking-clip history item is lost if Ruth presses the button before playback drains. | Station test |
| F8 | Manush | Retitle and close PR #1; delete stale remote branches (`dhruv/phase3`, `dhruv/phase4`, `dev-rohan`, `rohan/p2`, `rohan/p3`, `manush/p2`, `manush/p3` and the other merged ones). Only you can do this. | GitHub |
| F9 | Rohan | Re-run the eval on the narrowed refund-scam rules (the Phase 4 merge changed `rules_v1.yaml`). | New eval table in `ai/eval/RESULTS.md` |
| F10 | Rohan | `ai/eval/run.py` counts "held" as caught, and silently cuts the error list at 10. | Fixed; the table matches the error list |
| F11 | Rohan | The judge's score never reaches the ledger in the real flow: `policy/checkout.py:149` calls `judge()` directly, so `judge_scored` is only posted by the standalone `/judge` route. Post it from checkout. | Wall shows `judge_scored` after a checkout |
| F12 | Rohan | Soft screen results (`slow`, `judge`) are never posted. Post a `caution` event (contract C8). | Ledger shows caution rows |
| F13 | Rohan | Refusals from the station's screen post no `caregiver_alerted` and carry no `decision_id`, so Priya gets no "Why?". Ruth still hears "I have told Priya". Post the alert with an id that `/decisions/{id}/explain` can resolve. | Priya's app gets a "Why?" for a screen refusal |
| F14 | Dhruv | Policy's `/refunds`, `/orders/{id}/cancel`, `/history` and `/decisions/{id}/explain` are open to anyone on the LAN. Allow them only from the LAN (`_lan_only`) or with the caregiver marker; explain requires the marker (each call can cost an xAI request). | Test: a proxied request gets 403; the caregiver app still works |
| F15 | Dhruv | When the judge is down, the decision becomes "approve" and goes to Priya with no explanation. Add a plain reason ("the safety check was unavailable, so I asked Priya"). | Approval card shows the reason |
| F16 | Dhruv | Caregiver app, all to be rebuilt in Phase 6, but fix now if you touch them: money prints "$142.1"; "Call Ruth" has an empty `tel:`; a debug `<pre>` log is shown to Priya; the approval card shows the raw merchant id and no items; alerts say "Priya was alerted" on Priya's own phone. | Phase 6 acceptance |
| F17 | Vraj | Nothing calls `/orders/{id}/picked-up`. Add a Host button (U). | Host page |
| F18 | Vraj | Loyalty points aren't reduced after a refund; the wall shows "+N points" before payment. | Receipt and wall |
| F19 | Vraj | Write the real Pay by Link cancel into `docs/visa-sandbox-auth-error.md` or the Visa write-up: `ACTIVE → INACTIVE` confirmed by GET, PATCH correlation id `64bbe6f1-084d-4c95-a2e5-f8692d4dcae2`. | Doc line |
| F20 | Vraj | The wall's mandate panel ignores `paused` and shows the raw id `corner_market`. This folds into the Trust Ledger redesign. | Phase 6 |
| F21 | Vraj | The session page's `<meta refresh=5>` resets scroll position and disrupts screen readers. Replace it with SSE or a 30 s refresh. | Phase 6 |
| F22 | Someone logged in | Confirm on live.hexlabs.org: the submission deadline (8am vs Devpost's noon), the sponsor-challenge cap (2?), and whether we get one general track. | Posted in the team chat |

---

## 3. Contracts (agree at 5:00; each owner commits theirs by 6:15)

Each contract gets a file in `contracts/` or a section in `ports.md`. **Nobody changes a contract after 6:15 without telling the other three.**

### C1. Merchant registry: `contracts/merchants.json` (Vraj)

```json
{
  "merchants": [
    {"id": "corner_market",     "name": "Corner Market",     "kind": "store",   "mcc": "5411", "categories": ["grocery"],                             "cybs_env": "VISA_ACCEPTANCE_"},
    {"id": "parkside_pharmacy", "name": "Parkside Pharmacy", "kind": "store",   "mcc": "5912", "categories": ["pharmacy", "pharmacy_pickup", "grocery"], "cybs_env": "CYBS_PARKSIDE_"},
    {"id": "main_street_home",  "name": "Main Street Home",  "kind": "store",   "mcc": "5251", "categories": ["household"],                           "cybs_env": "CYBS_MAINST_"},
    {"id": "peachtree_power",   "name": "Peachtree Power",   "kind": "biller",  "mcc": "4900", "categories": ["utility_bill"],                        "cybs_env": "CYBS_PEACHTREE_"},
    {"id": "quickgift_cards",   "name": "QuickGift Cards",   "kind": "blocked", "mcc": "6540", "categories": ["gift_card"],                           "cybs_env": null}
  ],
  "card_terminal_stores": [
    {"acceptor_id": "FIVEPTSDRUG01", "name": "Five Points Drug", "mcc": "5912", "city": "ATLANTA", "state": "GA"},
    {"acceptor_id": "CORNERMKT01",   "name": "Corner Market",    "mcc": "5411", "city": "ATLANTA", "state": "GA"},
    {"acceptor_id": "GIFTCARDMALL1", "name": "GiftCard Kiosk",   "mcc": "6540", "city": "ATLANTA", "state": "GA"},
    {"acceptor_id": "COINATM0001",   "name": "Coin ATM",         "mcc": "6051", "city": "ATLANTA", "state": "GA"}
  ]
}
```

- Each merchant with a `cybs_env` uses `<prefix>MERCHANT_ID`, `<prefix>API_KEY_ID` and `<prefix>SECRET_KEY`. If those are missing, it falls back to the main account with a per-merchant descriptor. The wall labels which.
- The names are fictional; the products are real.
- `card_terminal_stores` are physical stores for the card demo only. The agent never buys there.

### C2. Catalog across stores (Vraj)

- Every catalog item's `merchant` becomes real: pharmacy and over-the-counter items move to `parkside_pharmacy`, household items go to `main_street_home`, and Parkside also carries about 20 grocery basics at its own prices.
- `GET /search?q=&store=` adds an optional `store` filter.
- Every result gets `merchant`, `store` (the display name) and `elsewhere: [{merchant, store, sku, price}]`, which lists the same product group at the other stores.
- **Ordering:** Ruth's usual first, then price. Never "store brand first".
- `BILL-peachtree_power` is a pseudo-sku that policy prices from the biller (C7), not from the catalog.

### C3. Mandate v2 (Dhruv; `contracts/mandate.schema.json`)

The v1 fields stay. These fields are added, and all are optional in the schema so a v1 mandate still validates:

```json
{
  "allowed_merchants": ["corner_market", "parkside_pharmacy", "main_street_home", "peachtree_power"],
  "allowed_categories": ["grocery", "pharmacy", "household", "utility_bill"],
  "billers": [{"merchant_id": "peachtree_power", "account_ref": "PP-2231-0098", "monthly_cap": 200}],
  "card": {
    "blocked_mccs": ["4829", "6051", "6540", "7995"],
    "category_caps": {"5411": 150, "5912": 80, "5310": 100, "5311": 100, "5251": 100},
    "default_cap": 60,
    "atm_daily_cap": 100,
    "unusual_multiplier": 3,
    "cooldown": {"hours": 24, "caps": {"5912": 25, "5310": 25, "5311": 25, "6011": 0, "default": 25}}
  },
  "trusted_contacts": [
    {"name": "Priya", "relation": "daughter", "phone": "+1-404-555-0142"},
    {"name": "Alex",  "relation": "grandson", "phone": "+1-404-555-0187"}
  ],
  "cosign": {"shopper": {"method": "voice", "said": "Sí, estoy de acuerdo", "lang": "es", "at": "2026-09-26T19:05:00Z"}}
}
```

- **Card caps are in dollars, per swipe, by MCC.**
  - `unusual_multiplier` declines a swipe more than 3 times Ruth's median at that MCC (median from the card history, default $30).
  - During a cool-down, `cooldown.caps` replace `category_caps`.
  - ATM (6011) is capped at $0 during a cool-down.
- **Visa view:** `GET /mandate/visa` returns the same rules in Visa Intelligent Commerce's exact `mandates[]` shape, one entry per store or biller. The fields are from the Cybersource spec:
  ```json
  {"consumerPrompt": "Ruth's groceries, medicine, household items and her power bill, within the rules she and Priya signed",
   "mandates": [
     {"mandateId": "m_ruth_2026_09-corner_market", "preferredMerchantName": "Corner Market",
      "merchantCategory": "Grocery Stores, Supermarkets", "merchantCategoryCode": "5411",
      "declineThreshold": {"amount": "60.00", "currencyCode": "USD"},
      "effectiveUntilTime": "1798761599", "description": "Groceries for Ruth, per purchase"}
   ]}
  ```
  `effectiveUntilTime` is a Unix epoch string, and `mandateId` is at most 50 characters. The wall shows this. Visa's instruction API can't be called for real tonight (X5-4).
- **Signing:** the passkey still signs the canonical mandate. The pause stays in its own file. Ruth's co-sign is a recorded spoken "yes" at the station (demo level), shown on the Rules screen. From Phase 6, changing the rules needs both.

### C4. Scam check: `POST /scam-check` (Rohan, in policy)

**Request:**
```json
{"session_id": "s_…", "mandate_id": "m_ruth_2026_09", "lang": "es", "channel": "station",
 "story": "Mi nieto Alex llamó, está en la cárcel y necesita 2000 dólares para la fianza, dijo que no le diga a mamá",
 "caller": {"org": null, "name": "Alex", "phone": null}}
```

`channel` is `station` or `line`.

**Response:**
```json
{"check_id": "sc_…", "verdict": "scam", "pattern": "grandparent_emergency",
 "say": "Ruth, esto es una estafa muy común; la voz se puede copiar. Por favor cuelgue. ¿Quiere que llame a Alex a su número de siempre?",
 "actions": ["hang_up", "call_trusted:Alex", "tell_priya"],
 "facts_checked": [{"fact": "Alex's number on file", "result": "+1-404-555-0187, different from the caller"}],
 "sources": [{"title": "FTC: Family emergency scams", "url": "https://consumer.ftc.gov/…", "published": "2026-…"}],
 "cooldown_until": "2026-09-27T19:05:00Z", "ms": 6120, "from_cache": false}
```

- `verdict` is `scam`, `unsure` or `ok`.
- **Order of work:**
  1. The rule screen. A hard hit answers now, and Grok adds sources afterwards.
  2. The facts: the biller balance (C7), trusted contacts (C3) and recent orders.
  3. Grok Responses with `x_search` and `web_search`: a 12 s budget, then the cache, then a rules-only verdict.
- **Events:** `scam_checked`. For `scam`, also `caregiver_alerted` with a `check_id`, and a `risk_changed` (C5).
- **Speech:** `say` is always in `lang` and gives one clear action. When Grok is late, the fixed line from `lines.<lang>.json` is used.

### C5. Risk state (Rohan writes, Dhruv reads; `policy/risk.py`)

- `set_cooldown(mandate_id, hours, reason, source_event)` and `load_risk(mandate_id) -> {cooldown_until, reason, source_event}`.
- `GET /risk?mandate_id=` for the UIs; `POST /risk/clear` with the caregiver marker.
- Stored in `sessions/risk.json` and cleared on reset.
- Event: `risk_changed {cooldown_until, reason}`.

### C6. Card decisions (Dhruv, in policy; `policy/card.py`)

| Route | Who calls it | What it does |
|---|---|---|
| `POST /card/asa` | Lithic, through the tunnel at `https://<tunnel>/card/asa` | Verify the `webhook-*` HMAC. Answer `{"result": "APPROVED" \| "UNAUTHORIZED_MERCHANT" \| "VELOCITY_EXCEEDED" \| "SUSPECTED_FRAUD", "token": <request token>}` within **300 ms** (Lithic declines after 6 s). |
| `POST /card/simulate` | The card terminal page (LAN, Host header) | `{acceptor_id, amount_cents}` → calls Lithic `simulate/authorize` with the registry store's descriptor and MCC → returns `{token, result, reason_key, reason}` once Lithic has the result |
| `POST /card/holds/{hold_id}/allow` | The caregiver app (marker `card`) | Opens a **10-minute** one-time pass for that card, store and amount (or less). The next swipe there is approved and the pass is used up. |
| `GET /card/state` | UIs | The recent decisions, the open holds and the cool-down |

- **Reason keys** (also line keys for Ruth and Priya):
  - `card_blocked_category`, for MCC 4829, 6051, 6540 or 7995
  - `card_over_cap`
  - `card_unusual_amount`
  - `card_cooldown`
  - `card_atm_cap`
- **Lithic result per reason:**
  - `card_blocked_category` → `UNAUTHORIZED_MERCHANT`
  - `card_over_cap` and `card_atm_cap` → `VELOCITY_EXCEEDED`
  - `card_cooldown` and `card_unusual_amount` → `SUSPECTED_FRAUD`
- **Events:**
  - `card_decision {card_last4, store, mcc, amount, result: approved|declined, reason_key, reason, hold_id?, cooldown, network, provider: "lithic"}`
  - `card_hold_released {hold_id, store, max_amount, allowed_until}`
- **Rule:** no model and no human sits in the synchronous path. The decision is a lookup over the mandate, the risk state and the card history.

### C7. Biller (Vraj, in merchant)

- `GET /billers/peachtree_power/accounts/PP-2231-0098` →
  ```json
  {"biller": "Peachtree Power", "account_ref": "PP-2231-0098", "balance_due": "86.40", "due_date": "2026-10-15",
   "past_due": false, "autopay": false, "last_payment": {"amount": "91.12", "at": "2026-09-12"},
   "disconnect_notice": false}
  ```
- **Paying:** the agent puts `BILL-peachtree_power` in the cart. Policy prices it from `balance_due` and caps it by `billers[].monthly_cap`. From there it's the normal read-back, signed order, and a Pay by Link on Peachtree Power's merchant.
- **For the scam story:** "Your real bill is $86.40, due October 15, not past due. They don't cut power with one phone call."

### C8. New event types (`contracts/events.schema.json`; Vraj merges them)

| Type | Source | Payload |
|---|---|---|
| `scam_checked` | policy | `check_id, verdict, pattern, sources[], ms, channel` |
| `caution` | policy (screen) | `rule_ids[], action: slow\|judge, words` |
| `risk_changed` | policy | `cooldown_until, reason, source_event` |
| `card_decision` | policy | as in C6 |
| `card_hold_released` | policy | as in C6 |
| `bill_checked` | merchant | `biller, balance_due, due_date, past_due` |
| `line_call` | line | `call_id, phase: started\|ended, from_last4, seconds?` |

The existing `card_authorized` and `card_auth_failed` (the checkout page's authorization) stay as they are. The new card guard uses `card_decision`.

### C9. Voice tools v2 (Manush; station `voice.json`, and the same set on the line)

| Tool | Args | Returns |
|---|---|---|
| `search_catalog` | `query`, `store?` | Items with `store`, `price`, `usual`, `elsewhere[]` |
| `scam_check` | `story` (required, her words), `caller_org?`, `caller_phone?` | C4 response; the model says `say` exactly |
| `bill_status` | `biller?` | C7 facts plus a `say` |
| `add_to_cart` | as today; `sku` can be `BILL-peachtree_power` | — |
| `read_cart`, `checkout`, `budget_left`, `order_status`, `cancel_order`, `request_refund`, `purchase_history` | as today | — |

- The cart can hold lines from several stores. `checkout` places **one signed order per merchant**, and the read-back names each store.
- Card events are not a tool. The station subscribes to `card_decision` (declined) and speaks the line (Phase 6).

### C10. Public routes through the tunnel (update `ports.md`)

Only the caregiver app is public. It rewrites these paths to the LAN services:

| Public path | Goes to | Protection |
|---|---|---|
| `/card/asa` | policy `/card/asa` | Lithic `webhook-signature` HMAC (5-minute tolerance) |
| `/line/*` | the line service (V5-4) | xAI webhook signature, or a bearer token for MCP |
| `/merchant/webhooks/cybersource` | merchant (exists) | Cybersource signature (exists) |

Nothing else is added. `/card/simulate` and `/card/holds` stay on the LAN, or go through the caregiver app's own session and marker.

### C11. Design system (Dhruv; `design/`)

- `design/tokens.css`: colors (light and dark), type scale with a 20px base and 28–40px for Ruth's surfaces, spacing, radius, and the states `--protected`, `--caution`, `--declined` and `--ok`.
- `design/logo.svg` and `design/shield.svg`.
- The relay serves them at `/design/*`. The station imports `/design/tokens.css`; the caregiver app copies them at build (`prebuild` script); the wall and session page link them.

---

## 4. Manush: Ruth's voice and the services laptop

### V5-1. The services laptop runs everything, on its own tunnel (5:25, 20 min) (**Fix F2, F3**)

This fixes "my friend can't see the order". Today the caregiver app runs on another laptop whose `POLICY_URL` points at its own machine, or can't reach this one, because services bind to 127.0.0.1 and eduroam blocks laptop-to-laptop traffic.

1. dashboard.ngrok.com → sign in with **this laptop's** account → Domains → claim the free static domain. Set `TUNNEL_HOST=<that domain>` in `.env`.
2. Stop the services. Move these aside; the old passkey belongs to the old domain and can't sign in on a new one:
   - `caregiver/data/credentials.json`
   - `caregiver/data/setup.json`
   - `sessions/caregiver_credential.json`
   - `sessions/mandate.json`
3. `bash .claude/run.sh all`, then `ngrok http --url=$TUNNEL_HOST 5175`. The caregiver console prints a one-time setup code.
4. On Priya's phone, open `https://$TUNNEL_HOST`: setup code → register the passkey → sign the rules.
5. Place an order at the station; Priya's phone shows it. **Pass condition 1.**
6. **Fix F1:** say "commit & push" and I'll commit `common/tls.py` and its uses.

### V5-2. No more "One moment" (5:45, 30 min)

1. In `station/config/voice.json` `instructions`, delete the sentence "Before searching, say one very short line … ("One moment." …)". Add under Voice: "Call tools right away without announcing them. Never say 'one moment', 'let me check' or anything like it before a tool; the station plays a soft sound while you work."
2. **Earcon** (`spikes/manush/src/audio.ts` or a small new module):
   - A soft two-note tick every ~700 ms at -24 dB while `turn.pendingToolCalls > 0` or a screen wait is running. Hook it where `awaitScreen` increments and decrements (`agent.ts:710-722`) and where tools start and finish (`continueAfterTools`, `agent.ts:1075`).
   - Stop it the moment the model's audio starts.
   - The state strip shows "Checking…".
3. `asking_priya` (with Rohan): drop "One moment, please". New English line: "That's more than your limit for one purchase, so I've sent it to Priya. She usually answers in a minute." Also es and hi; re-render the three clips (`python -m ai.render_clips --only line.asking_priya`).
4. Measure **release to first sound** (the earcon counts) and **release to first word**. Write both in `voice.json` `measured`.

### V5-3. Persona v2 and the new tool stubs (6:15, 40 min, with Rohan)

Replace the instructions with this draft, then tune:

```
## Who you are
You are Senior Sentinel, Ruth's own helper. You work for Ruth, never for a store or for anyone who calls her. You help her shop at her approved stores (Corner Market for groceries, Parkside Pharmacy for medicine, Main Street Home for household things), pay her approved bills (Peachtree Power), and stay safe from scams. Her daughter Priya set the spending rules together with her.

## Safety comes first
If Ruth mentions a phone call, a text, an email, a pop-up or a visitor, or anyone asking her for money, gift cards, a wire, crypto, a "refund", card numbers, codes, or to install something, call scam_check with her own words before anything else. Then say its say text exactly, calmly, and offer its one action. Never scold; she did nothing wrong.
Never ask for or read out card numbers, codes or passwords. If a tool result has refused true, say its say text exactly and nothing else.

## Shopping and bills
Call tools right away without announcing them; the station plays a soft sound while you work.
When Ruth names a product, call search_catalog. Offer at most three options: her usual first, then the best price, always with the store and the price ("Nature's Own bread at Corner Market, three forty-nine").
When she chooses, call add_to_cart. When she has everything, call read_cart and say its say text word for word, then wait for her yes. Only then call checkout.
For a bill, call bill_status and tell her what is really owed. To pay it, add it to the cart and read it back like any order.
After an order: order_status for "where is my order", cancel_order for an unpaid order, request_refund to return items (preview first, then her yes), purchase_history for "what did I buy". Say each result's say text.

## How you speak
One or two short sentences. One question at a time. Plain words. Reply in the language Ruth last spoke. Say prices the way people say them out loud.
```

- Add the tool schemas from C9 to `voice.json`. Until the endpoints exist, `scam_check` and `bill_status` return `{error: "not ready"}` and the model says `store_unavailable`.
- Add `store` to `search_catalog`.
- **Fix F5, F6:** give `purchase_history` a `say`; give `order_status` the pickup code and "ready after 3 pm".

### V5-4. Senior Sentinel Line trial (6:30, timebox 60 min)

**Goal:** a real US number that Ruth, or a judge, can call, answered by Grok as Senior Sentinel, with at least one of our tools running.

The two paths, the exact steps and the fallback are in **Section 4.1**, written from xAI's docs. Pick the path at 6:30 with Rohan. Go/no-go at 7:15:
- **Go:** a call reaches Grok, it speaks in the persona, and `budget_left` or `scam_check` runs and is spoken.
- **No-go:** cut the line and put it in the README as "next".

### V5-5. Carry-overs

- **F7** (minor station edge cases), if time allows.
- **F8** (GitHub cleanup): yours only.
- **F4** (re-recording) moves to Phase 7.

### 4.1 Senior Sentinel Line: the two paths

The facts from xAI's docs:
- The free US number from the **Voice Agent Builder** goes to a hosted Builder agent.
- "Provisioning xAI phone numbers via API is not supported", so we can't point the free number at our own webhook.
- A Builder agent can call our HTTPS endpoints through a **remote MCP server** (Streamable HTTP or SSE) or an **`api_request`** tool. It also has built-in `web_search` and `x_search`.
- Pricing: $0.08/min audio plus $0.01/min telephony.

**Path A (try first; 6:30–7:15): Builder agent plus our MCP server.**

1. console.x.ai → Voice → Agents → **Custom**:
   - Paste the persona v2 text (V5-3) as the playbook.
   - Voice Ara; enable web search and X search.
   - Take the free number.
2. Our MCP server, a new small service `line/` on port 8005, Python `mcp` package:
   ```python
   from mcp.server.fastmcp import FastMCP
   mcp = FastMCP("senior-sentinel-tools")
   @mcp.tool()
   def budget_left(ruth_said: str = "") -> dict: ...   # calls policy /budget; returns {left, say}
   # search_catalog, add_to_cart, read_cart, checkout, scam_check, bill_status, order_status, request_refund
   mcp.run(transport="streamable-http")  # serves /mcp
   ```
   - **Cart:** kept server-side, keyed by the MCP session id (`Mcp-Session-Id`).
   - **Transcript for the judge:** every tool takes an optional `ruth_said`. We keep the words for the checkout judge and the scam check, because the phone path has no station screen.
   - **Read-back gate:** `checkout` is refused unless `read_cart` was the last cart tool call.
3. Public route: the caregiver app rewrites `/line/mcp` → `http://127.0.0.1:8005/mcp` (C10). Require `Authorization: Bearer $LINE_MCP_TOKEN`.
4. In the Builder, add a custom MCP server:
   - `server_url: https://$TUNNEL_HOST/line/mcp`
   - `server_label: senior-sentinel-tools` (no dots)
   - `authorization: Bearer …`
   - header `ngrok-skip-browser-warning: 1`
5. Test "Preview Live" in the browser, then dial the number. **Go** means `budget_left` or `scam_check` runs and is spoken.
6. If the Builder has no MCP field or rejects it, point its **`api_request`** tool at `https://$TUNNEL_HOST/line/api/<tool>` (the same handlers as plain JSON POSTs).

**Path B (only if A is blocked; this is a Phase 6 decision, not Phase 5): our own server answers the call.**

1. A Twilio number with Elastic SIP Trunking. The origination URI is `sip:+1XXXXXXXXXX@sip.voice.x.ai;transport=tls`.
2. Register it: `POST https://api.x.ai/v2/phone-numbers` with `{"origin": "byo_trunk", "phone_number": "+1…", "webhook": {"name": "chaperone-sip", "url": "https://$TUNNEL_HOST/line/sip-webhook"}, "sip_auth": {"allowed_addresses": [...]}}`. Save `webhook.dispatch_signing_secret`; it's returned only once.
3. On `realtime.call.incoming`, verify the Standard Webhooks signature (`pip install standardwebhooks`). Then open `wss://api.x.ai/v1/realtime?call_id=<id>` with `Authorization: Bearer $XAI_API_KEY`. Ephemeral tokens don't work for calls.
4. Then `session.update`: persona, `turn_detection: {"type": "server_vad"}`, the tools. Then `response.create`. Function calls work exactly as in the browser.
5. Transfer to Priya: `POST /v1/realtime/calls/{call_id}/refer {"target_uri": "tel:+1…"}`.

It's worth one quick `curl` at 6:30: `POST /v2/phone-numbers` with `"origin": "xai_provisioned", "webhook": {...}`. The schema allows it but the guide says no. If it works, Path B needs no Twilio.

**For the line in general:** safety is enforced in the tools (`scam_check`, and the judge and mandate at `checkout`), not by the station's screen. Use `force_message` (`interruptible: false`) for the scam warning on Path B.

---

## 5. Rohan: the Ask guard

### R5-1. Radar probe (5:25, 45 min)

Write `ai/radar_probe.py`. It sends one Responses call per story with X search and web search and asks for a structured verdict. The exact request is in **Section 5.1**.

- **Stories:**
  1. Grandparent in jail, voice clone, "don't tell Mom"
  2. Peachtree Power disconnect tonight, pay by gift cards
  3. Microsoft or Amazon tech support
- **Languages:** English first; then the grandparent story in Spanish and Hindi.
- **Write down:** ms per call, the sources returned, whether `say` follows "one action, no scolding", and cost per call.
- **Prompt rules:**
  - Plain words.
  - Never a confidence score. Older adults distrust scores and trust facts (Georgia Tech, CHI 2026).
  - One action.
  - Sources only from what the tools returned.

### R5-2. `POST /scam-check` v0 in policy (6:15, 60 min)

Create `policy/scamcheck.py` and a route in `policy/main.py`, following contract C4.

1. **Rules first:** `screen(story)`. A hard hit answers now; Grok adds sources afterwards.
2. **Facts:**
   - The biller balance, via Vraj's `GET /billers/...` (stub until 7:00).
   - Trusted contacts from mandate v2.
   - Orders from `/history`.
3. **Grok** with a 12 s budget, then the cache (`sessions/radar_cache.json`, keyed by pattern and language), then a rules-only verdict with a fixed line.
4. **Events:** `scam_checked`, plus `caregiver_alerted {check_id}`; for `scam`, call `risk.set_cooldown(24h)`.
5. **Tests:** rules-first latency, the cache path, the fallback path, and the cool-down set.

### R5-3. Risk state (5:55, 20 min)

Create `policy/risk.py` per C5, with tests. Reset clears it. Tell Dhruv when it's on your branch; he reads it in `/card/asa`.

### R5-4. Rules and eval (6:45, 30 min) (**Fix F9, F10**)

- **New families in `rules_v1.yaml`:**
  - Utility disconnect plus pay now
  - "Safe account" / move your money
  - Crypto ATM / Bitcoin machine
  - Courier pickup of cash or gold
  - Grandparent plus secrecy (extend)
  - Remote access (extend)
- **Hard negatives for the new world:**
  - "pay my power bill"
  - "what do I owe Peachtree Power"
  - "my grandson is visiting Sunday"
  - "call my grandson"
  - "put the medicine on my card"
  - "how much is left on my card"
- Fix `run.py` (F10) and re-run the eval (F9).

### R5-5. Make safety visible in the data (7:00, 15 min) (**Fix F11, F12, F13**)

- Post `judge_scored` from checkout.
- Post `caution` for `slow` and `judge` results.
- Post a screen refusal's `caregiver_alerted` with a `decision_id`. Save a small decision document so `/decisions/{id}/explain` works.

### R5-6. Validation interviews (in gaps; aim for 5 by 7:30, 15 by Phase 7)

Ask 5 questions and keep a tally in `internal/validation.md`:
1. Has an older relative of yours been targeted by a scam in the last year? How?
2. Who handles their money or shopping help today?
3. Would you set up rules like these together with them?
4. Would they call a number to ask "is this a scam?"
5. Would you pay $15 a month, or want it from your bank?

Get one quote per person, with consent to use their first name.

### 5.1 The radar request (xAI Responses API)

```json
POST https://api.x.ai/v1/responses
Authorization: Bearer $XAI_API_KEY
{
  "model": "grok-4.20-0309-non-reasoning",
  "instructions": "You protect an older adult from scams. Use the facts given and search X (last 30 days) and the web. Reply only in the schema. 'say' is in the shopper's language, two short sentences, warm, never a score, one clear action.",
  "input": [{"role": "user", "content": "Language: es. Story: <Ruth's words>. Facts: <biller balance, trusted contacts, recent orders>."}],
  "tools": [
    {"type": "x_search", "from_date": "2026-08-27", "to_date": "2026-09-26"},
    {"type": "web_search", "filters": {"allowed_domains": ["consumer.ftc.gov", "ic3.gov", "aarp.org", "bbb.org", "fcc.gov"]}}
  ],
  "max_turns": 3,
  "include": ["no_inline_citations"],
  "text": {"format": {"type": "json_schema", "name": "scam_verdict", "strict": true, "schema": {
    "type": "object", "additionalProperties": false,
    "required": ["verdict", "pattern", "say", "actions", "reported_recently"],
    "properties": {
      "verdict": {"type": "string", "enum": ["scam", "unsure", "ok"]},
      "pattern": {"type": "string"},
      "say": {"type": "string"},
      "actions": {"type": "array", "items": {"type": "string", "enum": ["hang_up", "call_priya", "call_trusted", "do_not_pay", "none"]}},
      "reported_recently": {"type": "string"}
    }}}}
}
```

- **Reading the result:**
  - The verdict JSON is at `output[type=message].content[type=output_text].text`.
  - Sources are that block's `annotations[]` (`url_citation`). There's no top-level `citations` field.
  - Cost is in `usage.server_side_tool_usage_details` and `usage.cost_in_usd_ticks`.
- **Parameter placement:** web search domains go under `filters` (at most 5); X search dates are `YYYY-MM-DD`. Inside a **voice** `session.update`, `allowed_domains` is flat. Don't use the old `search_parameters` (it returns 410).
- **Model:** `grok-4.20-0309-non-reasoning` is the fast choice. `grok-4.7` has no `none` reasoning level, so it's slower. Check on the first call that structured output plus tools works on 4.20; if not, use `grok-4.3` with `reasoning.effort: "low"`.
- **Cost:** about $0.05–0.25 per check. X search is billed per post fetched since Sep 21. Cache by pattern and language.
- **SDK alternative:** `xai_sdk` with `chat.create(model=…, tools=[x_search(...), web_search(...)], max_turns=3)`, then `chat.parse(Model)`. `response.citations` returns the URLs.

---

## 6. Dhruv: the Card and Family guards

### D5-1. Lithic round trip (5:25, 50 min)

The exact calls are in **Section 6.1**. Steps:
1. `pip install lithic`, and set `LITHIC_API_KEY` in `.env`.
2. Create Ruth's virtual card and keep its token and PAN in `sessions/card.json` (gitignored). **Never print the PAN in logs; show the last four only.**
3. Stub `POST /card/asa` in policy. It verifies the HMAC and approves if the MCC isn't blocked.
4. Add the caregiver app rewrite `/card/asa` → policy (C10), and enroll the responder `https://$TUNNEL_HOST/card/asa`. Wait until V5-1 gives you the domain; before that, use a temporary `ngrok http 8001` on your own laptop.
5. `simulate/authorize` a 5411 swipe for $20 and a 6540 swipe for $50. `GET /v1/transactions/{token}` shows APPROVED and declined. Log the ms from request to reply.

### D5-2. Card decisions (6:15, 50 min)

Build `policy/card.py` per C6:
- The rules from mandate v2 `card`, plus `risk.load_risk()`, plus the card history median per MCC.
- The reason keys and their Lithic results.
- Holds and the 10-minute allow-once pass.
- `/card/simulate`, `/card/state`, and the events.
- **Tests:**
  - Blocked MCC
  - Over the cap
  - Unusual amount
  - Cool-down declines what normally passes
  - Allow-once passes exactly one retry
  - Timing under 300 ms with a 1,000-entry history

### D5-3. Mandate v2 (6:50, 30 min)

- Schema additions (C3), a v2 `DEFAULT_MANDATE`, and the engine checks against the multi-merchant `allowed_merchants`.
- `utility_bill` priced from the biller (with Vraj).
- `GET /mandate/visa` (C3).
- The cool-down and pause flags stay outside the signed mandate.
- The caregiver app's `MANDATE` constant gets the new fields; the Rules screen shows stores and card rules read-only until Phase 6.

### D5-4. Design system (5:50, 25 min, pushed by 6:15)

Per C11:
- **Warm and trustworthy:** a deep navy text color, a warm off-white background, a green "protected" state and an amber "caution" state. The declined state is **never alarm red**; older adults read alarm colors as their own mistake.
- **Type:** a 20px base; 28–40px on Ruth's surfaces.
- **Logo:** a shield around a speech bubble, plus the word mark "Senior Sentinel".
- Relay route `/design/*`; the caregiver `prebuild` copy.

### D5-5. Carry-overs

- **F14** (route protection) and **F15** (plain reason when the judge is down): now.
- **F16:** fix now only what you touch; the rest is Phase 6 acceptance.

### 6.1 Lithic calls (sandbox)

- **Base:** `https://sandbox.lithic.com`.
- **Auth header:** `Authorization: <LITHIC_API_KEY>`, with **no "Bearer"**.
- **SDK:** `pip install lithic`.

```python
from lithic import Lithic
client = Lithic(api_key=os.environ["LITHIC_API_KEY"], environment="sandbox")
card = client.cards.create(type="VIRTUAL", memo="Ruth", state="OPEN")          # sandbox returns card.pan
client.responder_endpoints.create(type="AUTH_STREAM_ACCESS", url=f"https://{TUNNEL_HOST}/card/asa")
client.responder_endpoints.check_status(type="AUTH_STREAM_ACCESS")
secret = client.auth_stream_enrollment.retrieve_secret().secret              # "whsec_..."; the first call creates it
sim = client.transactions.simulate_authorization(amount=2000, descriptor="CORNER MARKET", pan=card.pan,
                                                mcc="5411", merchant_acceptor_id="CORNERMKT01")
txn = client.transactions.retrieve(sim.token); print(txn.status, txn.result)  # e.g. SETTLED/PENDING, APPROVED
```

- **Enrollment:**
  - One ASA endpoint per account.
  - If the URL changes: `DELETE /v1/responder_endpoints?type=AUTH_STREAM_ACCESS`, then create it again.
  - Every simulated authorization goes to the enrolled endpoint.
- **Verify every ASA request.** The headers are `webhook-id`, `webhook-timestamp` and `webhook-signature` (Standard Webhooks). Signatures start shortly after the first `retrieve_secret()`.
  ```python
  key = base64.b64decode(secret.removeprefix("whsec_"))
  expected = base64.b64encode(hmac.new(key, f"{h['webhook-id']}.{h['webhook-timestamp']}.".encode() + body, hashlib.sha256).digest()).decode()
  ok = any(hmac.compare_digest(expected, s.split(",", 1)[1]) for s in h["webhook-signature"].split())
  ```
  Reject anything with a timestamp more than 5 minutes old.
- **The request we read:**
  - `token`
  - `amounts.cardholder.amount` in cents (`amount` is deprecated)
  - `merchant.mcc`, `merchant.descriptor` and `merchant.acceptor_id`
  - `card.token` and `card.last_four`
  - `status` (only decide on `AUTHORIZATION`; approve `BALANCE_INQUIRY`)
- **The reply:** HTTP 200 with `{"result": "APPROVED" | "UNAUTHORIZED_MERCHANT" | "VELOCITY_EXCEEDED" | "SUSPECTED_FRAUD", "token": "<request token>"}`.
  - Lithic declines after **6 s** without a reply and suggests replying within 3 s. We aim for 300 ms.
  - On a 5xx it retries at once, so the handler must be idempotent on `token`.
- **Allow once:** Lithic's own Authorization Challenges need account-manager enablement, so don't rely on them. Our pattern:
  1. Decline.
  2. Store the hold (card token, `acceptor_id`, MCC, amount).
  3. Priya allows it.
  4. A 10-minute pass for that card, `acceptor_id` and amount.
  5. The terminal retries with the same `merchant_acceptor_id`.
  6. APPROVED, and the pass is used up.
- **Other simulations:** `simulate_clearing(token=…, amount=0)` settles; `simulate/void` and `simulate/return` exist too.
- **Backup, Stripe Issuing test mode:**
  1. Enable test-mode Issuing in the Dashboard.
  2. Create a cardholder (name, billing address, individual first and last name and date of birth) and a virtual card.
  3. **Fund the test Issuing balance first**; otherwise authorizations decline before our webhook is called.
  4. Set the authorization endpoint in Issuing settings.
  5. Reply 200 `{"approved": true|false}` with the header `Stripe-Version: 2025-03-31.basil`. The budget is **2 s**.
  6. Read `data.object.pending_request.amount` and `merchant_data.category_code`.
  7. Test with `POST /v1/test_helpers/issuing/authorizations card=ic_… amount=… merchant_data[category]=…`.
  8. Verify `Stripe-Signature` with `stripe.Webhook.construct_event`.

---

## 7. Vraj: the Agent guard and Visa

### X5-1. Merchants and sandbox accounts (5:25, 60 min)

1. Commit `contracts/merchants.json` (C1).
2. Three new Cybersource sandbox accounts, for Parkside, Main Street and Peachtree. Signup is instant but has a CAPTCHA, so **each of the other three teammates registers one at 5:00** (Section 7.1). Everyone sends Vraj their keys over a private channel, never in git or the team chat. Vraj puts them in `.env` under each prefix.
   - **Check Pay by Link on the first new account before making the others.** If it isn't enabled, use the main account for all four, tag each link (below), and label it.
3. `merchant/visa.py`: choose credentials by merchant. One MCP toolkit process per account (they're keyed by the credentials passed at start), or the REST path for creating links.
4. The verifier: the order's `merchant` picks the storefront. Nonces are stored per merchant; one JWKS is shared (it's the same agent key).
5. **Done when:** one real Pay by Link per merchant. Write down the link id and the account (or descriptor).

### X5-2. Peachtree Power, the biller (6:25, 30 min)

- `GET /billers/peachtree_power/accounts/{ref}` (C7). Pricing for `BILL-peachtree_power` is in policy, with Dhruv.
- Paying creates a Pay by Link on Peachtree's merchant, with the line "Peachtree Power bill PP-…0098".
- Post `bill_checked`.

### X5-3. Catalog across stores (6:55, 25 min)

- Pharmacy and over-the-counter items move to Parkside.
- **Household seed:** add Kroger terms to `catalog/seed_kroger.py` `TERMS`: paper towels, toilet paper, batteries, light bulbs, dish soap, laundry detergent, trash bags. Assign them to `main_street_home` with category `household`.
- About 20 grocery basics are also sold at Parkside, at its own prices.
- `search` gets `store`, `merchant`, `elsewhere[]`, and ordering "usual first, then price" (C2). Remove the Kroger-first effect.

### X5-4. Visa probes (5:25, in parallel; ~20 min active, then waiting)

The exact requests are in **Section 7.2**. On **our own** sandbox only; never the public testrest credentials.
1. **Intelligent Commerce: path probe only, 10 minutes.**
   - The paths moved from `/acp/v1/*` to `/icc/v1/*` in the SDK (Jul 2026). The instruction calls **require JWT auth plus message-level encryption**, a token requester ID and a relationship ID from an account manager, and passkey enrollment.
   - A working call isn't possible tonight. Send `POST {}` to both paths and write down the statuses for the Devpost ("the mandate is in Visa's `mandates[]` format; the instruction API needs pilot credentials").
   - Our mandate is already shaped exactly like it (C3).
2. **Decision Manager**, 15 minutes: `POST /risk/v1/decisions`. Write down the status. If it returns real decisions, Phase 6 can run each agent order through it and show the score on the ledger.
3. **Visa Transaction Controls**, about 45 minutes; **stop at 7:15 whatever happens.**
   - Steps: a Visa Developer project, two-way SSL, register a test PAN, set rules, call `/decisions`.
   - VTC has **no pharmacy, gift-card or utility category**. Mirror what it has:
     - a per-transaction threshold (`globalControls.declineThreshold`)
     - ATM (`TCT_ATM_WITHDRAW`)
     - e-commerce (`TCT_E_COMMERCE`)
     - gambling (`MCT_GAMBLING`)
     - household (`MCT_HOUSEHOLD`)
   - If it works, Phase 6 shows "Visa VTC: decline" next to our own decision for the $480 drugstore swipe (over the threshold).

### X5-5. Carry-overs

- **F17** (picked-up Host button), **F18** (points after refund, "+N points" before payment) and **F19** (the INACTIVE request id): now.
- **F20** and **F21** go into the Phase 6 Trust Ledger work.
- Merge the event types from C8 into `contracts/events.schema.json`.

### 7.1 New Cybersource sandbox merchants

1. https://developer.cybersource.com/hello-world/sandbox.html:
   - A unique Organization ID (e.g. `chaperone_parkside`), which can't be renamed.
   - Company, name, address, email and phone. "Payment Technology Provider?": **No**.
   - Solve the CAPTCHA.
2. The thank-you page shows the **Merchant ID, Key ID and Shared Secret once. Copy them immediately.** An email follows to set up the test Business Center login.
3. A key can also be made later:
   - Business Center (https://businesscentertest.cybersource.com/ebc2/) → Payment Configuration → Key Management → Generate key.
   - Choose REST – Shared Secret, then download the key.
4. **Pay by Link check**, on the first new account: signed `GET /ipl/v2/payment-links?offset=0&limit=1` on `apitest.cybersource.com`.
   - 200 → use separate accounts.
   - 401, 403 or "not enabled" → one account for all four.
5. **Tagging links on one account.** Pay by Link has no `merchantDescriptor`. Instead:
   - Prefix `purchaseInformation.purchaseNumber` (`PHARM-…`, `HOME-…`, `POWER-…`) and name the store in `lineItems[].productName`.
   - Or create a merchant-defined field once with `POST /ipl/v2/Purchase/merchantDefinedFields {"fieldType": "Text", "label": "Merchant", "merchantDefinedDataIndex": 1, "customerVisible": true, "readOnly": true}`, then send `merchantDefinedFieldValues: [{"definitionId": <id>, "value": "Parkside Pharmacy"}]` on each link.

### 7.2 Visa probes: exact requests

**Intelligent Commerce path probe.** Signed with our existing HTTP-signature keys; `POST {}` to each. Reading the result:
- 404: that path isn't routed.
- 401 or an MLE error: the path exists but needs JWT and encryption.
- 403: the product isn't on our merchant.
- 400 with missing fields: we're past the auth gate.

```
POST https://apitest.cybersource.com/icc/v1/instructions
POST https://apitest.cybersource.com/acp/v1/instructions
```

**Decision Manager.** Use an expiry year of 2030 or later.
```json
POST https://apitest.cybersource.com/risk/v1/decisions
{"clientReferenceInformation": {"code": "senior-sentinel-dm-001"},
 "paymentInformation": {"card": {"number": "4111111111111111", "expirationMonth": "12", "expirationYear": "2031"}},
 "orderInformation": {"amountDetails": {"currency": "USD", "totalAmount": "11.49"},
  "billTo": {"firstName": "Ruth", "lastName": "Test", "address1": "1 Peachtree St", "locality": "Atlanta",
             "administrativeArea": "GA", "postalCode": "30303", "country": "US", "email": "ruth@example.com", "phoneNumber": "4045550100"}}}
```
- Status is one of `ACCEPTED`, `REJECTED`, `PENDING_REVIEW`, …
- `riskInformation.score.result` is the score.
- `errorInformation.reason: INVALID_MERCHANT_CONFIGURATION` means Decision Manager isn't set up. Drop it.

**Visa Transaction Controls** (Visa Developer sandbox, two-way SSL plus basic auth):
1. developer.visa.com → register → Dashboard → Create Project → Visa Transaction Controls.
2. Two-Way SSL → **"Generate a CSR for me"**. **Download the private key right away; it's offered once.** Then download `cert.pem`.
3. Credentials → User ID and Password.
4. Test Data → the PAN prefix plus `0001` (the spec example is `4514170000000001`).
5. Check the project's MLE toggle. Customer Rules is optional MLE in sandbox; if it's off, send plain JSON.
6. Keep the key and cert in `keys/visa/` (gitignored). Never commit them.

```python
import datetime, requests
B = "https://sandbox.api.visa.com"
s = requests.Session(); s.cert = ("keys/visa/cert.pem", "keys/visa/key.pem"); s.auth = (VISA_USER_ID, VISA_PASSWORD)
s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
print(s.get(f"{B}/vdp/helloworld").json())                                   # connectivity
doc = s.post(f"{B}/vctc/customerrules/v1/consumertransactioncontrols", json={"primaryAccountNumber": PAN}).json()["resource"]["documentID"]
rules = {"globalControls": [{"isControlEnabled": True, "shouldDeclineAll": False, "declineThreshold": 60}],
         "transactionControls": [{"controlType": "TCT_ATM_WITHDRAW", "isControlEnabled": True, "declineThreshold": 100},
                                 {"controlType": "TCT_E_COMMERCE", "isControlEnabled": True, "declineThreshold": 150}],
         "merchantControls": [{"controlType": "MCT_GAMBLING", "isControlEnabled": True, "shouldDeclineAll": True}]}
s.put(f"{B}/vctc/customerrules/v1/consumertransactioncontrols/{doc}/rules", json=rules)
dec = {"primaryAccountNumber": PAN, "cardholderBillAmount": 480, "decisionType": "RECOMMENDED", "messageType": "0100",
       "processingCode": "000000", "retrievalReferenceNumber": "000000000480", "transactionID": "480480480",
       "dateTimeLocal": datetime.datetime.utcnow().strftime("%m%d%H%M%S"),
       "merchantInfo": {"name": "Five Points Drug", "merchantCategoryCode": "5912", "countryCode": "USA",
                        "currencyCode": "840", "transactionAmount": 480, "city": "Atlanta", "region": "GA", "postalCode": "30303"}}
print(s.post(f"{B}/vctc/validation/v1/decisions", json=dec).json())          # resource.decisionResponse.shouldDecline
```

If you'd rather make your own CSR: `openssl req -new -keyout privateKey.pem -out certreq.csr`, then strip the passphrase with `openssl rsa -in privateKey.pem -out key.pem` for `requests`.

---

## 8. Go/no-go at 7:15, and the merge

**7:15:** each person reports their pass conditions (Section 1.2) as green, red or dropped.

| Piece | Green | Red → fallback |
|---|---|---|
| Lithic card round trip | Phase 6 builds the terminal and the holds | Stripe Issuing test mode (Section 6.1); last resort, our own simulator with the same `card.py`, labeled "simulated network" |
| Scam radar | Phase 6 wires it into the station and the line | Rules-first plus cached answers; Grok only for sources |
| Senior Sentinel Line | Phase 6 finishes it | Cut; it's "next" in the README |
| Extra merchants | Separate accounts | One account with descriptors, labeled |
| Intelligent Commerce | (Not possible tonight: needs JWT, encryption and pilot IDs) | Mandate shown in Visa's exact `mandates[]` shape; the probe result goes in the Devpost |
| Decision Manager | Each agent order gets a Visa risk score on the ledger | Dropped |
| VTC | Mirror the rules; show a Visa decline | Drop it; say "banks enforce the same rules with VTC" |

**7:30:** push your branches. I review, merge to main, fix the seams, run every test, and write the Phase 6 playbook with what's green.

---

## 9. What Phase 6 picks up (7:30–11:30pm)

`PRODUCT_V2.md` Section 7 has the table. In short:
- **Manush:** the station redesign, the new tools live, spoken card declines, and the full line.
- **Rohan:** the radar in production, the cool-down, lines in three languages, and 10 more interviews.
- **Dhruv:** the full card service, the co-signed mandate, and the caregiver app screens.
- **Vraj:** the card terminal page, the Trust Ledger, checkout across merchants, and Decision Manager and VTC if they're green.

At 11:30 the new demo runs end to end.

---

## 10. Sources

Pages opened on Sep 26, 2026.

**Lithic:**
- [Get an API key](https://docs.lithic.com/docs/get-api-key)
- [Create a card](https://docs.lithic.com/reference/postcards)
- [Auth Stream Access](https://docs.lithic.com/docs/auth-stream-access-asa)
- [Responder endpoints](https://docs.lithic.com/reference/postresponderendpoints)
- [ASA secret](https://docs.lithic.com/reference/getauthstreamsecret)
- [Webhook signatures](https://docs.lithic.com/docs/events-api#verifying-webhooks)
- [ASA request](https://docs.lithic.com/reference/cardauthorizationapprovalrequestwebhook)
- [Simulate authorize](https://docs.lithic.com/reference/postsimulateauthorize)
- [Simulating transactions](https://docs.lithic.com/docs/simulating-transactions)
- [Authorization challenges](https://docs.lithic.com/docs/authorization-challenges)
- [Python SDK](https://github.com/lithic-com/lithic-python/blob/main/api.md)
- [ASA demo](https://github.com/lithic-com/asa-demo-python)

**Cybersource and Visa:**
- [Sandbox signup](https://developer.cybersource.com/hello-world/sandbox.html)
- [Agentic sandbox](https://developer.cybersource.com/hello-world/agentic-sandbox.html)
- [Intelligent Commerce guide (pilot)](https://developer.cybersource.com/docs/cybs/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce.html)
- [Initiate a purchase instruction](https://developer.visaacceptance.com/docs/vas/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce/intelligent-commerce-purchase-initiate-intro.html)
- [SDK releases (`/acp` → `/icc`, v0.0.80)](https://github.com/CyberSource/cybersource-rest-client-node/releases)
- [Pay by Link boarding](https://developer.cybersource.com/docs/cybs/en-us/boarding/user/all/rest/boarding/templates-matrix-intro/templates-matrix-pay-by-link.html)
- [Decision Manager samples](https://github.com/CyberSource/cybersource-rest-samples-python)
- [VTC reference](https://developer.visa.com/capabilities/vctc/reference)
- [Two-way SSL](https://developer.visa.com/pages/working-with-visa-apis/two-way-ssl)
- [Encryption (MLE)](https://developer.visa.com/pages/encryption_guide)
- [VTC Postman collections](https://github.com/jcrosswh/vtc-postman-collections)

**xAI:**
- [SIP](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/sip)
- [Speech to speech](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech)
- [Voice REST reference](https://docs.x.ai/developers/rest-api-reference/inference/voice)
- [Realtime event schema](https://docs.x.ai/voice-realtime.ws.json)
- [Voice Agent Builder](https://x.ai/news/grok-voice-agent-builder)
- [Web search](https://docs.x.ai/developers/tools/web-search)
- [X search](https://docs.x.ai/developers/tools/x-search)
- [Citations](https://docs.x.ai/developers/tools/citations)
- [Structured outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs)
- [Pricing](https://docs.x.ai/developers/pricing)
- [Voice prompting guide](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/prompting-guide)
- [Telephony cookbook (Twilio Media Streams, TypeScript)](https://github.com/xai-org/xai-cookbook/tree/main/voice-examples/agent/telephony)

**Stripe Issuing (backup):**
- [Real-time authorizations](https://docs.stripe.com/issuing/controls/real-time-authorizations)
- [Testing](https://docs.stripe.com/issuing/testing)
- [Test-mode authorization](https://docs.stripe.com/api/issuing/authorizations/test_mode_create)
- [Funding](https://docs.stripe.com/issuing/funding/balance)
