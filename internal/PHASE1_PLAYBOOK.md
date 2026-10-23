# Chaperone: Phase 1 Playbook

As of 2026-09-25, 11:55pm

Phase 1 runs from midnight to 2am for Manush and Rohan, then to 5am for Dhruv and Vraj (their sleep is 5 to 9am). `BUILD_PLAN.md` calls this phase "foundations against fakes". Main is ahead of that plan in some places and behind in others.
- **Ahead:** the station, the merchant, the catalog and the signer already work.
- **Missing:** the two services everything plugs into, the policy service (port 8001) and the relay ledger (port 8000).
- **Mismatched:** the seams between lanes, as Section 2 lists.

So Phase 1 is three jobs, in this order:
1. Fix the contracts together (15 minutes).
2. Clear each lane's review fixes.
3. Build the missing services so that Saturday 6am can run one real purchase end to end.

Every fix found in the branch review is folded into the owner's section below and marked **Fix**.

---

## 1. Phase 1 at a glance

| Time | Everyone | Manush (station) | Dhruv (policy, mandate, caregiver) | Vraj (merchant, relay ledger, wall, Visa) | Rohan (screen, judge, refusal, eval) |
|---|---|---|---|---|---|
| 12:00-12:15 | Contract standup (Section 3); pull main; one branch each | | | | |
| 12:15-1:00 | Heads down | Fixes V1-V4, cart tools | Fixes D1, D4; policy skeleton with the fake `/checkout` pushed by 12:30; engine and tests | Fixes F1-F3; relay `/events` pushed by 12:30 | Fixes R1-R4; `policy/screen.py` router pushed by 12:45 |
| 1:00 | Two-minute standup; merge to main | | | | |
| 1:00-1:45 | | Read-back gate, budget, outcomes, persona | Real `/checkout`: re-price, screen, judge, engine, sign, merchant | Merchant decision check; SSE stream; JWKS and audio routes | Refusal scripts per key; clips in the station's voice; eval set started |
| 1:45-2:00 | Integration smoke (Section 8) | | | | |
| 2:00 | Exit check (Section 9). Manush and Rohan sleep 2-6 | | | | |
| 2:00-5:00 | Dhruv and Vraj | | Mandate verify in Python; caregiver alert feed; registration gate; code fallback | Payment callback with the real signature format; wall skeleton; reset | |
| 5:00 | Hand-off notes in `#chaperone` for the 6am crew; sleep 5-9 | | | | |

**Pass conditions at 2am (binary).**
- Manush:
  - The station reads the real catalog, not the fallback.
  - The cart tools work, and `checkout` is refused unless a read-back happened after the last cart change.
  - A full voice turn reaches the real policy `/checkout` (a fake answer is fine) and speaks the outcome.
- Dhruv:
  - `pytest policy` passes with every rule R1-R7 tested in both directions.
  - `POST /checkout` with the demo cart returns `allow`, signs the order and gets a payment link back from the merchant running `MERCHANT_VERIFY=enforce`.
- Vraj:
  - The merchant rejects a replayed signed order and one whose `decision_id` is unknown to policy.
  - `POST /events` from the station, policy and merchant all land in `sessions/live.jsonl`, and `curl -N :8000/events/stream` shows them.
- Rohan, on `POST /screen`:
  - These lines are refused, and each refusal carries an `audio_url` that loads:
    - the Spanish gift-card line,
    - the Hindi line ending in "।",
    - the Hinglish Google Play line.
  - "I will pay with my Visa card" proceeds.
  - `/judge` returns contract-valid JSON with `JUDGE_FAKE=1` and with the real model.

**Pass conditions at 5am (Dhruv and Vraj).**
- Dhruv:
  - Policy refuses to run on an unsigned mandate unless `MANDATE_UNSIGNED_OK=1`.
  - The caregiver phone shows an alert within 2 s of a `refusal` event.
  - Registration is closed to strangers.
- Vraj:
  - A simulated, correctly signed Cybersource callback flips the order to `paid`.
  - The wall page shows the live ledger and the merchant panel.

**Git.**
- Branch from the latest main: `manush/station-2`, `dhruv/policy`, `vraj/ledger`, `rohan/screen`.
- Rebase on main before each standup, and merge by fast-forward only at the standups.
- Rohan: his old branch was squashed into main, so start fresh from main and do not merge `dev-rohan` again.
- Commit messages describe the code change only.

---

## 2. What is on main (2b55c60) and where the seams break

| Area | What exists | What is missing or mismatched |
|---|---|---|
| Station (`spikes/manush/`, `station/config/voice.json`) | Push-to-talk, AudioWorklet, barge-in, `search_catalog` and `checkout` tools, per-turn call to `POST {policy}/screen`, refusal clip with a `force_message` fallback, typed input, ledger posts to `{relay}/events`, mock realtime server, 15 node tests, measured 998 ms release-to-first-audio | Reads `results` but the catalog returns `items` (`src/cart.ts:69`), so it always falls back to the three fake breads. It lacks `add_to_cart`, `remove_from_cart`, `read_cart` and `budget_left`, and read-back is asserted (`read_back: true` always), not enforced. Relay CORS is `*` |
| Relay (`relay/main.py`, `tokens.py`) | `POST /session/token`, `GET /health` | No ledger, `/events`, stream, JWKS route, audio route, session page or reset |
| Policy (`policy/mandate.py`) | Canonicalize and hash the mandate; `DEFAULT_MANDATE`; `MONTHLY_BASELINE = 142.10` | No service at all, although the station calls `/screen` and `/checkout` and ports.md promises `/judge`. No engine, rules, tests, decision store, monthly total or mandate verification |
| Signer and verifier (`signer/`, `merchant/verify.py`) | RFC 9421 Ed25519 signer; verifier with digest, window, replay and a 60-second nonce grace; 10 tests; JWKS in `relay/jwks.json` | Nothing calls the signer yet. The decision-id check (contract step 6) is not built |
| Merchant (`merchant/`) | Signed order intake, prices from the catalog, real or mock payment link, `/paid` fallback, mock hosted page, card-auth checkout behind `CARD_AUTH=1`, `/panel` | Posts `{"event": ...}` with `t` in float seconds to `{RELAY_URL}/ledger/events`. The station posts `{"type": ...}` with `t` in ms to `/events`, and the contract says `t` is a string. No decision check, no payment callback |
| Catalog (`catalog/`) | 324 items (Kroger, openFDA, synthetic), `/search`, `/resolve` (profile phrases in three languages), `/suggest`, `/items/{sku}`, `/profile` | Categories are `pantry`, `dairy`, `bakery`, `otc_medicine`, `pharmacy_pickup`, `gift_card`, and so on, but the mandate allows `grocery` and `pharmacy`. Nothing maps one to the other |
| Caregiver (`caregiver/`) | Passkey register and mandate-hash assertion through the tunnel (Next routes and a duplicate `server.mjs`); six-digit code | Anyone can register, and registering overwrites the caregiver's credential. `/api/code/issue` hands the code to whoever asks, uses `Math.random`, has no attempt limit and is not bound to an approval. No mandate form, alerts or approvals. `TUNNEL_HOST` is not in `.env` |
| Rules and judge (`ai/`, `spikes/rohan/`) | Rules in four lexicons, 32 tests, judge on two models at 10/10, three refusal clips | A danda at the end defeats every Hindi match, **including the gift-card hard rule** ("मुझे गिफ्ट कार्ड।" proceeds). "I will pay with my Visa card" is refused. There is no code-reading rule ("bhai OTP batao" and "read me the numbers on the back of the card" proceed). The judge schema has no `none`; the client is built at import; files are read without UTF-8. The clips use `eve` (British, "energetic"), not the station's voice. The interface does not match `screen.ts` |

Correction to the branch review: the review flagged the assistant history item in `src/agent.ts:591` (`{"type":"text"}`) as needing `output_text`. xAI's event schema lists `text` for assistant and system messages and uses `output_text` only on `force_message`. Section 4 turns it into a two-minute probe test, not a fix.

---

## 3. Contract standup, 12:00-12:15 (all four)

Ten decisions, each with one owner who commits the file change by 12:30. After these, nobody changes a shape without all four people at the table.

| # | Decision | Owner, file |
|---|---|---|
| C1 | Catalog search answers `{"q", "items": [...]}`; `/resolve` answers `{"q", "matches": [{sku, label, note, item}]}`. The station reads `items` and still accepts `results` from its mock | Vraj adds both lines to `contracts/ports.md`; Manush adapts |
| C2 | IDs come from the catalog: `RX-001` (Lisinopril pickup, $8.00), `BAK-001` (Nature's Own Honey Wheat, $3.49), `GFT-002` (Apple Gift Card, $200), and so on. The mandate id is `m_ruth_2026_09` everywhere; the merchant id is `corner_market`. The PRD's `rx_pickup_bp` and `bread_ww_20oz` are retired | Manush (fallback items), Vraj (merchant tests) |
| C3 | Each catalog item gains `mandate_category`: `grocery` for pantry, dairy, beverages, produce, nutrition and bakery; `pharmacy` for otc_medicine and pharmacy_pickup; `gift_card`; `prepaid_card`. The priced cart's `category` carries it. Policy re-derives it from the catalog and ignores what the station sent | Vraj (`catalog/build_catalog.py`, rebuild) |
| C4 | One event format. Post to `{relay}/events`. Required fields: `type` (never `event`), `session_id`, `mandate_id`, `t` (sender clock, integer ms since epoch), `source` (`station`, `policy`, `merchant`, `caregiver` or `relay`). The relay adds `rt` (integer ms) and `seq`. The `type` enum gains `signature_rejected`, `card_authorized`, `card_auth_failed`, `mandate_signed`, `judge_scored`, `order_created` and `reset`. An event without a session uses `session_id: "none"` | Vraj (`contracts/events.schema.json`: `t` and `rt` become integers) |
| C5 | `contracts/judge.schema.json` stays the validation schema. The API schema `ai/prompts/judge_schema.json` adds `none` to `patterns`. Code validates every reply against the contract and clamps the score to 0..1, because xAI treats some schema keywords as best effort | Rohan |
| C6 | `/screen` follows `spikes/manush/src/screen.ts`. Request: `{session_id, text, lang?, partial?}`. Response: `{action: "refuse" or "judge" or "slow" or "proceed", hits: [{rule_id, pattern, lang, term}], refusal: {rule_id, spoken_key, patterns, lang, text, audio_url} or null}`. `slow` means exactly one soft hit | Rohan (`contracts/screen.schema.json`) |
| C7 | `/checkout`. Request: the station's `CheckoutBody` `{session_id, mandate_id, cart, transcript, lang, read_back}`. Response: the decision fields plus `decision_id`, `say_key`, `order` (`{order_id, payment_link, status}` or null) and `approval` (`{approval_id, expires_at}` or null). The signed order body gains `session_id`, which the merchant already accepts | Dhruv (`contracts/checkout.schema.json`, `order_request.schema.json`) |
| C8 | `mandate.passkey` becomes `{credential_id, public_key, response}`. `public_key` is base64url COSE; `response` is the full `AuthenticationResponseJSON`, which is what Python's `webauthn` needs. The approval challenge is `SHA-256(JCS({approval_id, amount, merchant, nonce, expires_at}))` with a 16-byte server-random `nonce` and single use; it goes in `contracts/signing.md` | Dhruv |
| C9 | Hosting: policy (8001) mounts Rohan's router from `policy/screen.py` (`/screen`, `/judge`). The relay (8000) mounts Vraj's router from `relay/ledger.py` (`/events`, `/events/stream`, `/sessions/{id}`, `/jwks.json`, `/.well-known/jwks.json`, `/audio/*`, `/wall`, `/reset`). Manush keeps `relay/main.py` and `tokens.py` and adds the one `include_router` line. The wall is served by the relay at `/wall` (same origin as the stream, no CORS, one less process); port 5176 is retired | Vraj (`ports.md`) |
| C10 | Only these public paths go through the tunnel: the caregiver app itself, `/relay/events/stream` (proxied to the relay) and `/merchant/webhooks/cybersource` (proxied to the merchant). Nothing else on the LAN is reachable from the internet | Dhruv (`next.config.mjs` rewrites), Vraj (the handler) |

**New `.env` keys** (each owner adds them to `.env.example` with a comment line above):
- `JUDGE_FAKE`, `JUDGE_THRESHOLD=0.6` (Rohan)
- `MANDATE_UNSIGNED_OK=0`, `CAREGIVER_SETUP_CODE_HASH` (Dhruv)
- `STATION_ORIGINS` (Manush)
- `CYBS_WEBHOOK_KEY_ID`, `CYBS_WEBHOOK_KEY` (Vraj)

---

## 4. Manush: station, midnight to 2am

Manush has the most-finished lane, so the work is to close the seams and add the cart contract that makes read-back true in code rather than in the prompt. Work in `spikes/manush/`. The move to `station/` waits until after the Sunday freeze; it is churn tonight.

**Fixes (first 25 minutes).**
- **V1** `parseSearchResponse` (`src/cart.ts:66-71`) reads `items`, with `results` as a fallback for the mock. Update `test/pure.test.mjs` and `tests/mock_realtime.py` to answer `items`. Without this every search silently returns the three fallback breads.
- **V2** Change `FALLBACK_ITEMS` to catalog SKUs (C2): `BAK-001` Nature's Own Honey Wheat $3.49 as the usual, plus two others from `catalog/catalog.json`.
- **V3** Relay CORS:
  - Replace `allow_origins=["*"]` in `relay/main.py` with `STATION_ORIGINS`, split on commas, default `http://localhost:5173,http://127.0.0.1:5173`.
  - `allow_methods=["GET","POST"]`, `allow_headers=["Content-Type"]`.
  - Reason: any web page open on a LAN machine can currently mint xAI voice tokens.
  - The wall and caregiver need no entry: the wall is same-origin (C9), and the caregiver calls the relay from its server.
- **V4** Two-minute probe: send an assistant history item with `{"type":"text"}` through `ws_probe.mjs`. If the server answers `invalid_request_error`, switch line 591 to `output_text`; otherwise leave it. The xAI schema lists `input_text`, `input_audio`, `text` and `audio`.

**Build, in order.**
1. **Cart tools** (FR-24). They live in the page and hold a pure `Cart` in `src/cart.ts`: integer cents, a `version` that bumps on every change, and each change posts `cart_updated`.
   - `add_to_cart {sku, qty}`: the sku must come from a search result in this session.
   - `remove_from_cart {sku, qty?}`
   - `read_cart {}` returns `{lines, total, say}`. `say` is the exact read-back sentence built from the cart in the shopper's language.
   - `budget_left {}` calls `GET {policy}/budget?mandate_id=` and returns `{monthly_cap, spent, left}`.
   - `checkout {}` takes **no arguments**. It checks out the cart that was read back, so the model cannot check out a list it never read aloud.
   - Update the tool list in `station/config/voice.json`. Use the flat shape `{"type":"function","name","description","parameters"}`: the guide and cookbook use it, though the WebSocket schema shows a nested form.
2. **Read-back gate** (PRD Section 10: "`checkout` refuses unless `read_cart` was called since the last cart change").
   - `checkout` returns `{"error": "read_back_required", "say": ...}` unless both hold:
     - `readBackVersion === cart.version`;
     - a user turn was committed after that `read_cart`, which is the "yes".
   - Only then does it send `read_back: true`.
   - Node tests: change, then read, then yes, then checkout passes; change after read fails; read with no user turn fails.
3. **Search through the profile** (FR-11, FR-12).
   - `search_catalog` calls `GET {catalog}/resolve?q=` first. If there is a match, it becomes option one with `usual: true`.
   - Then `GET /search?q=&limit=3`.
   - "mi medicina de la presión" must resolve to `RX-001`, and "bp ki dawai" and "मेरी दवाई" to the same.
4. **Checkout outcomes.** Map the policy reply (C7) into what the model gets back:
   - `allow`: `{status: "ordered", total, say_key: "ordering_now"}`
   - `approve`: `{status: "waiting_for_caregiver", say_key: "asking_priya"}`. Phase 3 adds the wait.
   - `deny`: `{status: "declined", say_key}`. Refusals already go through `/screen`.
   - Speak fixed lines through `force_message` only for refusals. The model speaks the rest from `say`.
5. **Persona and session**:
   - **Instructions:** keep the xAI prompt-guide sections, cap replies at one or two short sentences, and add "Never call checkout before read_cart and a yes."
   - **Speed and voice:** set `audio.output.speed` to 0.85-0.9. A/B `ara` against `luna` ("gentle, patient") and `carina` ("soft, soothing") for Spanish and English, and use `naksh` for Hindi. Write the choice in `voice.json` by 12:45 so Rohan renders the clips in the same voice.
   - **Language hint:** set `language_hint` after the first detected turn. Spanish must be `es-MX`; bare `es` is rejected. Hindi is `hi`, English `en`.
   - **Keyterms:** up to 100 terms of at most 50 characters each. Include Lisinopril, Ensure, Nature's Own, Tylenol, Google Play, Zelle, OTP, Medicare.
6. **Companion screen** (FR-4), checked against the existing large-type page:
   - Transcript for both sides, cart lines and total, and a state strip (Listening, Thinking, Speaking, Waiting for Priya).
   - A red refusal banner with the rule id.
   - Every text at least 24 px, contrast at least 4.5:1, targets at least 24 by 24 px.
   - The tablet version reads the relay stream on Saturday.
7. **If time: session resumption.**
   - Send `session.update {"resumption":{"enabled":true}}` and save `conversation.created.conversation.id`.
   - On `timeout` or `max_duration` errors or a closed socket, mint a new token and reconnect with `&conversation_id=<id>`.
   - Then inject a `system` message with the cart JSON.
   - History is kept for 30 minutes of inactivity. Close the old socket first: tier 0 allows 10 concurrent sessions.

**The fake you owe.** `tests/mock_realtime.py` already stands in for the relay, catalog and policy. Bring it up to C1, C6 and C7 so the page can be driven with every service down.

**Done when.** Say "necesito pan", hear the real bread read back with its price, say "sí", and hear the order outcome. The console shows `search_catalog`, `add_to_cart`, `read_cart`, `checkout`, the `/checkout` reply, and every event posted. Run `npm run build && npm test` and the Python mock tests; all pass.

**Pitfalls.**
- Tool call events arrive after the audio deltas, alongside `response.done`. Buffer every `function_call_arguments.done` until `response.done`, send all outputs, wait for playback to drain, then send one `response.create`.
- There is no `tool_choice` in the realtime API, so the read-back gate must live in the handler.
- `force_message` must not be followed by `response.create`.
- `.updated` transcripts are cumulative. Send `/screen` the final transcript with `partial: false`, so session counters on Rohan's side count each turn once.

---

## 5. Dhruv: policy service, mandate and caregiver, midnight to 5am

Policy is the hub: the station, the merchant and the caregiver all call it. So a skeleton goes up first, then the engine with its tests, then the full checkout path, then the caregiver work.

**Fixes (first 20 minutes).**
- **D4** (do first, 5 min):
  - The agent private key is in the repo root as `agent_ed25519.pem`; the signer reads `keys/agent_ed25519.pem`. On the services laptop: `mkdir keys && mv agent_ed25519.pem keys/`. I checked at 12:05am: that key matches `relay/jwks.json` on main (kid `chaperone-agent-1`).
  - After the move, `python -c "from signer.keys import public_jwk, load_jwks; print(public_jwk()['x'] == load_jwks()['keys'][0]['x'])"` must print `True`.
  - Put `TUNNEL_HOST` (the ngrok dev domain, bare host) in `.env`; it is not there yet.
- **D1: registration gate** (OWASP MFA guidance):
  - While no credential exists, accept registration only with a one-time setup code. Print it once on the Dhruv laptop console, store only `CAREGIVER_SETUP_CODE_HASH`, expire it after 10 minutes, and consume it on use.
  - Once a credential exists, adding another requires an assertion from the existing one.
  - Append to `caregiver/data/credentials.json` and never overwrite it. Pass `excludeCredentials` with the existing ids.
  - `userID` must be a `Uint8Array` (`isoUint8Array.fromUTF8String("priya")`); v14 throws on a string.
- **D2: six-digit fallback**. It is fallback rung 5; build it after the gate, before 5am.
  - The code is generated per approval by policy with a CSPRNG (`secrets.randbelow(10**6)` or `crypto.randomInt`) and shown only on the Host screen (the wall), never returned to the phone.
  - Store `sha256(code + approval_id)`, give it the approval's 90-second expiry, allow 5 attempts and then burn it, single use.
  - Invalidate it on success or when a passkey approval arrives.
- **D3: one server.** Keep the Next app (the planned stack, and it builds). Port anything that exists only in `server.mjs` and `static/index.html` into Next routes, then delete both, so the two copies cannot drift.
  - Run it through the tunnel as `next build && next start`, not `next dev`.
  - Reason: ngrok free is 20,000 requests a month and 4,000 a minute, and the dev server's chunk and HMR requests burn through that.
  - Set `compress: false` in `next.config.mjs` so the alert stream is not buffered.

**Build, in order.**
1. **Skeleton and fake, pushed by 12:30:**
   - `policy/main.py` (FastAPI on 8001) with `GET /health`.
   - `POST /checkout` returning a fixed `allow` shaped like C7 (this is the fake Manush and Vraj code against).
   - `GET /budget?mandate_id=` returning `{monthly_cap: 300, spent: 142.10, left: 157.90}`.
   - `app.include_router(screen.router)` inside a try so the app starts before Rohan's file lands.
   - Run: `python -m uvicorn policy.main:app --host 0.0.0.0 --port 8001`.
2. **Engine, pure** (`policy/engine.py`): `evaluate(cart, mandate, monthly_spent_cents, judge=None, today=None) -> Decision`. Money in integer cents, no I/O, no clock unless passed. Rules in the order of `PRD.md` Section 9, each returning `{id, passed, detail}`:
   - R1 `R1_blocked_category`: any line's `mandate_category` in `blocked_categories`.
   - R2 `R2_merchant_allowed`.
   - R3 `R3_category_allowed`.
   - R4 `R4_per_purchase_cap`: total ≤ 60.00.
   - R5 `R5_monthly_cap`: spent + total ≤ 300.00.
   - R6 `R6_approval_threshold`: total ≤ 40.00, otherwise `approve`.
   - R7 `R7_scam_judge`: fails when `judge.action == "refuse_and_alert"` or `scam_score >= JUDGE_THRESHOLD`. When the judge errored, the rule passes with `detail: "judge unavailable"` and `judge_error` set on the decision. The exception: if `/screen` said `judge` (two or more soft hits), a judge error means `approve`, so the caregiver decides.
   - Precondition: the mandate is signed and today is between `valid_from` and `valid_to`; otherwise `deny` with `R0_mandate_valid`.
   - Outcome: any of R0-R5 or R7 failing means `deny`; only R6 failing means `approve`; otherwise `allow`.
3. **Tests** (`policy/tests/test_engine.py`, the Phase 1 exit criterion):
   - Each rule passing and failing: 14 tests.
   - Boundaries: exactly 40.00 is `allow`, exactly 60.00 is allowed, one cent over each.
   - Two purchases summing correctly across calls (FR-16).
   - The three demo carts: RX-001 plus BAK-001 at $11.49 is `allow`; a $52.30 cart is `approve`; GFT-002 is `deny` with R1.
   - Same input twice gives the identical decision.
   - Also commit `policy/tests/demo_cart.json`: the station's `CheckoutBody` for RX-001 plus BAK-001. It is used by the smoke test.
4. **Real `/checkout`:**
   1. Validate against C7.
   2. Re-price every sku from `catalog.search.Catalog.load()` (same laptop, import rather than HTTP, deterministic). An unknown sku is a 422. If the station's total differs, use ours and log it.
   3. Run Rohan's `screen(transcript, lang)`. This server-side check is authoritative; the station's call is only for speed.
   4. Call `judge(...)` on every checkout (FR-27).
   5. Run the engine.
   6. Store the decision in `sessions/decisions.json` (`common.config.decisions_path()`) with id `d_<12 hex>`, the priced cart and the outcome. Post `policy_decision`.
   7. On `allow`, send the signed order:
      - Build the body `{mandate_id, decision_id, session_id, approval_id: null, cart}`.
      - Sign it with `signer.sign.sign_request(f"{merchant_public_url()}/orders", body)`.
      - Send the prepared request unchanged with `requests.Session().send(prepared, timeout=5)`. Re-serializing the body breaks the digest.
      - Post `request_signed` with the keyid, nonce and expires, then return the merchant's order.
   8. Add the total to the monthly spend in `sessions/monthly.json`.
   9. On `deny`, post `refusal` and `caregiver_alerted`.
   10. On `approve`, create `{approval_id, session_id, amount, excerpt, rule, expires_at: now+90s, nonce}`, post `approval_requested`, and return it. The approval loop itself is Phase 3.
5. **Decision lookup:** `GET /decisions/{decision_id}` for the merchant's check (Vraj, F3). `POST /reset` sets spend back to 142.10 and clears decisions (FR-39).
6. **Mandate verification in Python** (FR-14; the PRD says policy "refuses to run without it"). This is 2-5am work.
   - `pip install webauthn==3.0.1` (released today; needs Python ≥ 3.10) and add it to `requirements.txt`.
   - Call `verify_authentication_response` with keyword arguments only:
     - `credential` = the stored `AuthenticationResponseJSON`
     - `expected_challenge` = `mandate_hash(mandate)` (bytes)
     - `expected_rp_id` = `TUNNEL_HOST`
     - `expected_origin` = `https://` + `TUNNEL_HOST`
     - `credential_public_key` = `base64url_to_bytes(public_key)` (the COSE bytes, no conversion)
     - `credential_current_sign_count` = 0 (it is a stored, historical assertion)
     - `require_user_verification` = `REQUIRE_UV != "0"`
   - Pin the caregiver credential the first time policy sees one and reject any other; say "trust on first use" if asked.
   - `POST /mandate` receives the signed mandate from the caregiver app, verifies it, stores it in `sessions/mandate.json` and posts `mandate_signed`. `GET /mandate` serves the wall's mandate card.
   - With `MANDATE_UNSIGNED_OK=1` it runs on `DEFAULT_MANDATE` and every decision says `unsigned mandate`.
7. **Caregiver alert feed** (the fake alert feed from `BUILD_PLAN.md`; FR-20 and FR-22 need 2 s):
   - **Stream:** a Next route handler `/api/alerts/stream` opens the relay stream `http://192.168.8.10:8000/events/stream?types=refusal,approval_requested,caregiver_alerted` server-side and re-emits it as SSE. The phone cannot fetch the LAN relay from an HTTPS page (mixed content).
     - Headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`.
     - Send about 2 KB of padding comment first (Safari buffers the first 1 KB), then a `:` heartbeat every 15 s (ngrok's idle timeout is 5 minutes).
   - **Browser reader:** use `fetch()` with a `ReadableStream`, not `EventSource`, so it can send `ngrok-skip-browser-warning: 1`. There is a documented case of EventSource receiving the interstitial HTML. Reconnect on error, with a 10-second poll as a safety net.
   - **Phone UI:**
     - An **Arm alerts** button whose tap resumes an `AudioContext`, calls `navigator.vibrate(50)` to unlock vibration and takes `navigator.wakeLock.request("screen")`. Re-acquire the wake lock on `visibilitychange`.
     - On each alert: a full-screen banner, `vibrate([200,100,200])` and a beep.
     - Use an Android Chrome phone. iOS vibrate support is unconfirmed, and iOS Web Push works only as a home-screen app.
   - Test with `curl -X POST :8000/events` using a fake `refusal`.
8. **Mandate form** (FR-13), if time before 5am, otherwise Saturday. The fields from `contracts/mandate.schema.json` in large type, then Sign with passkey, then `POST /mandate` through a server route.

**The fakes you owe.** The `/checkout` fake at 12:30 (item 1) and the alert feed tested with a curl event (item 7).

**Done when.**
- `pytest -q policy` passes.
- `curl -X POST :8001/checkout -d @policy/tests/demo_cart.json` returns `allow` with a `payment_link`, and the merchant panel shows the signature verified in enforce mode.
- Replaying the same signed order is rejected.
- The phone shows a curl-posted alert within 2 s.

**Pitfalls.**
- `requests` re-encodes JSON if you rebuild the request. Send the prepared request that was signed.
- `jcs` in Python and `canonicalize` in JS must produce identical bytes. Test the same mandate on both sides once.
- The approval challenge needs the server nonce, or two approvals for the same amount share a challenge and an old assertion replays.
- The passkey prompt does not show the amount. Put it in large type on the page right above the button.

---

## 6. Vraj: merchant, relay ledger, wall and Visa, midnight to 5am

The merchant and catalog are done, so Vraj takes the relay's ledger half and the wall: everything that turns events into what judges see. Payment confirmation also moves off the broken sandbox processor onto a signed callback.

**Human task first (5 minutes, if not already done tonight).**
- Email developer@cybersource.com with the MID, the full reason-150 text and one request id. Call 1-800-530-9095. Both state "1-2 business days", so the Visa reps at the booth are the Saturday-morning ask.
- Optional, 10 minutes: sign up a second sandbox account, put it in the `CARD_AUTH_*` keys and try one $1.00 authorization. Whether a new account gets a working processor is unconfirmed; it is a cheap lottery ticket.
- The doc `docs/visa-sandbox-auth-error.md` has the case text.

**Fixes (first 25 minutes).**
- **F1** `merchant/events.py` follows C4:
  - Post to `{RELAY_URL}/events` with `type` instead of `event`, `t` as `int(time.time()*1000)`, and `source: "merchant"`.
  - Include `session_id` and `mandate_id` on every event; `signature_rejected` has neither, so use `"none"`.
  - Keep the local `RECENT` buffer for `/panel`.
- **F2** `mandate_category` in `catalog/build_catalog.py` (C3). Rebuild `catalog.json`, and add a test that every item has one and that no gift card maps to grocery.
- **F3** Decision check (contract step 6) as a fifth check in `merchant/verify.py`, enforce mode only:
  - Call `GET {POLICY_URL}/decisions/{decision_id}` with a 300 ms timeout.
  - The decision must be `allow`, or `approve` with an approved approval.
  - Its cart (sku and qty) must equal the order's cart. Otherwise a valid decision could be replayed with a different cart.
  - Add `"decision"` to `STEPS` and a test for an unknown id, a cart mismatch and a denied decision.

**Build, in order.**
1. **Relay ledger router, pushed by 12:30.** `relay/ledger.py` exports `router`, and Manush's `relay/main.py` includes it (a one-line change you ask him for). Routes:
   - `POST /events`:
     - Validate against `contracts/events.schema.json` with `jsonschema`.
     - Add `rt` and a monotonically increasing `seq`.
     - Append to `sessions/<session_id>.jsonl` and to `sessions/live.jsonl` (`common.config.ledger_path()`), and fan out to subscribers.
     - Answer 202 in under 5 ms; senders are fire-and-forget.
   - `GET /events/stream?session_id=&types=`: SSE with `id: <seq>`, replay from `Last-Event-ID` out of `live.jsonl`, a 15-second `:` heartbeat, and `Cache-Control: no-cache, no-transform`.
   - `GET /sessions/{id}`: the JSON list now. The HTML session page (FR-37) comes Saturday.
   - `GET /jwks.json` and `GET /.well-known/jwks.json` serve `relay/jwks.json`; `contracts/signing.md` already promises both.
   - `app.mount("/audio", StaticFiles(directory="ai/warnings"))`. The station resolves `refusal.audio_url` against the relay.
   - `POST /reset`: truncate `live.jsonl`, then call policy `/reset` and a new merchant `/reset` (FR-39, under 15 s).
2. **Payment callback in the real format.** A real "paid" is very unlikely this weekend: Pay by Link needs Unified Checkout, which authorizes through the same processor setup that fails with reason 150. So:
   - **`POST /webhooks/cybersource` in the merchant:**
     - Read the raw body bytes.
     - Parse `v-c-signature: t=<ts>;keyId=<uuid>;sig=<base64>`.
     - Check that `keyId` equals `CYBS_WEBHOOK_KEY_ID`.
     - Compute `base64(HMAC-SHA256(base64decode(CYBS_WEBHOOK_KEY), t + "." + raw_body))`.
     - Compare with `hmac.compare_digest`.
     - Find the order by `purchaseNumber` anywhere in `payload`; the exact field is undocumented, so search the tree and log the raw body.
     - Mark it paid and post `paid`.
   - **`GET` and `POST /webhooks/cybersource/health`** both answer 200. Cybersource's health check needs both methods.
   - **`merchant/simulate_payment.py <order_id>`:** builds a version-3 envelope (`{eventType: "payByLink.merchant.payment", webhookId, productId: "payByLink", organizationId, eventDate, payload: {...}}`) plus the `v-c-*` headers, signs it with the local key the same way, and posts it. This is the Host's "the sandbox confirmed payment" button, and the demo is deterministic. The Host says "marked paid in the sandbox flow" (rung 3).
   - **Tests:** a good signature passes; a changed byte, a wrong keyId and a stale replay of the same body each fail.
3. **Register a real webhook anyway (2-5am, 20 minutes; best effort).**
   1. `POST https://apitest.cybersource.com/kms/egress/v2/keys-sym` with `{"clientRequestAction":"CREATE","keyInformation":{"provider":"nrtd","tenant":"<orgId>","keyType":"sharedSecret","organizationId":"<orgId>"}}`. The reply's `keyInformation.keyId` and `key` go in the vault and `.env`.
   2. `POST /notification-subscriptions/v2/webhooks` with:
      - `productId: "payByLink"`, `eventTypes: ["payByLink.merchant.payment"]`
      - `webhookUrl: https://<tunnel-host>/merchant/webhooks/cybersource`
      - `healthCheckUrl: .../health`
      - `notificationScope: "SELF"`, `securityPolicy: {securityType: "KEY", proxyType: "external"}`
   3. Sign both calls with the existing `merchant/cybs_rest.py`.
   - New URLs may sit in `PENDING_REVIEW` for 1-2 business days (a May 2026 change; whether it applies to the sandbox is unconfirmed). Record the `webhookId` and status and move on.
   - Transaction Search polling is not worth building until the processor is fixed.
4. **Wall skeleton at `GET /wall` on the relay (2-5am).** One HTML file with inline JS, readable from 3 m (FR-34, FR-36):
   - The mandate card from policy `GET /mandate` (caps, whitelist, blocked list, "signed by passkey" or "unsigned").
   - The live ledger from `/events/stream`, one line per event, rule ids and signature ids in monospace.
   - The merchant panel from merchant `/panel`, polled every 1 s: key id, nonce, expiry, five checks, payment status.
   - The monthly total.
   - Large type, dark background, no animation beyond a highlight on new lines.
5. **Merchant `/reset`**: clears orders and `RECENT`.

**The fakes you owe.** The merchant with `MOCK_VISA=1` is the signer's fake merchant, and the catalog is real, so nothing is owed beyond having the relay `/events` up by 12:30.

**Done when.**
- The policy's signed order is accepted, and a replay or an unknown `decision_id` is rejected with the failing check shown on `/panel`.
- `python -m merchant.simulate_payment <id>` flips the order to paid, and `paid` appears on the stream.
- `/wall` shows a full run.
- `pytest -q merchant catalog relay` passes.

**Pitfalls.**
- Compute the HMAC over the exact bytes received; parsing and re-dumping the JSON changes them.
- The relay runs from the repo root (`python -m uvicorn relay.main:app`), so the `ai/warnings` and `sessions/` paths resolve from there. Use `common.config.ROOT`, not the working directory.
- `sessions/*.jsonl` is gitignored except `sample.jsonl`. Keep it that way; transcripts stay local.
- Cybersource announced that HTTP Signature users must move to JWT auth by September 2026. Whether the sandbox enforces it is unconfirmed, and our HTTP Signature calls work today. If they start failing with authentication errors, JWT with the `CyberSourceKey_*.pem` already in the repo root is the switch.

---

## 7. Rohan: rule screen, judge, refusals and eval, midnight to 2am

The rules and judge work in isolation; tonight they move behind the endpoint the station already calls, and the gaps the review found get closed. Work in `policy/screen.py`, `policy/rules.py` and `policy/judge.py`; keep `spikes/rohan/` as the record.

**Fixes (first 30 minutes).**
- **R1: danda and invisible characters.** Before matching, `normalize` must map U+0964 "।", U+0965 "॥" and every Unicode punctuation character to a space, and delete U+200B-U+200D, U+00AD and U+FEFF.
  - Today the danda sits inside the Devanagari block that the word-boundary classes treat as a letter, so "मुझे गिफ्ट कार्ड।" proceeds. That is a hard-rule miss on the demo language.
  - Keep stripping only U+0300-U+036F and the nukta U+093C. Do not switch to "drop every Mn": that deletes matras and merges पोता, पता and पिता.
  - Leave the explicit Devanagari range in the boundary classes. Python's `\w` does not count matras as word characters (`re.search(r'\bपैसे\b', 'पैसे भेजो')` finds nothing), and the range is what saves you.
  - Tests: danda at the end, double danda, a ZWJ inside क्‍ष, ज़ against ज, and पोता against पता.
- **R2: "Visa card" false refusal.**
  - Remove bare `visa` from the brand alternation in `R1_blocked_category`.
  - Block only instrument phrases: "(gift|prepaid|reloadable|recharge) card", "(Google Play|Apple|iTunes|Steam|Target|Walmart) (gift )?card", "visa gift card", "prepaid visa".
  - Never match bare "card", "code" or "pin".
  - Benign tests: "I will pay with my Visa card", "my Medicare card came", "a birthday card for my grandson", "pagar con mi tarjeta Visa", "मेरे वीज़ा कार्ड से".
- **R3: lexicon gaps.** Soft rules unless noted:
  - **`R_code_reading`**: read me the numbers on the back, scratch the back, the code, PIN; "léame los números", "el código de la tarjeta", "raspe la parte de atrás"; "OTP batao", "code batao", "peeche ka number", ओटीपी, "UPI PIN". Make it **hard** when it co-occurs with a card or instrument word.
  - **`R_purpose`**: bail, fine, taxes, refund, unlock account, customs, parcel; fianza, multa, impuestos, reembolso, desbloquear; जमानत or ज़मानत or jamanat or zamanat, जुर्माना or jurmana, challan, टैक्स, रिफंड, "account block ho jayega", KYC, पार्सल, "digital arrest".
  - **Urgency in Devanagari:** अभी चाहिए, तुरंत, जल्दी, आज ही. Bare अभी or abhi stays off: too common.
  - **Low-specificity family words** (beta, बेटा, pota) count only when another category also fires.
  - **Hinglish fold before matching:** aa→a, ee→i, oo→u, z→j, w→v, ph→f, nahin→nahi. Store the lexicon folded.
- **R4: judge hygiene:**
  - Create the OpenAI client lazily on the first call, not at import.
  - `read_text(encoding="utf-8")` on `judge_schema.json` and `judge_system.md` (`judge.py:23-24`).
  - Add `none` to the enum (C5), validate against `contracts/judge.schema.json`, and clamp the score.
  - A 3-second timeout that raises, so policy can fall back per R7.
  - `JUDGE_FAKE=1` returns `{scam_score: 0.05, patterns: ["none"], rationale: "fake", action: "proceed"}` without a key.

**Build, in order.**
1. **`policy/screen.py`, pushed by 12:45.** An `APIRouter` with two routes, plus a `screen(text, lang)` function Dhruv imports:
   - **`POST /screen`** returns exactly the C6 shape. Map each `Hit.rule` to `rule_id`.
     - The action is `refuse`, `judge`, `slow` (one soft hit) or `proceed`.
     - `lang` is the request's value if given; otherwise Devanagari text means `hi`, else the station's guess.
     - Per-session memory: after a refusal, any later non-partial screen in the same session returns at least `judge` (PRD: "repeated attempts after a refusal"). A `partial: true` call never changes that memory.
   - **`POST /judge`**: `{transcript, cart, mandate_summary, history_summary}` in, a contract-valid judgment out, and it posts `judge_scored`.
   - A standalone `app` in the same file for testing: `python -m uvicorn policy.screen:app --port 8011`.
2. **Refusal keys and clips.**
   - Three `spoken_key`s × three languages, texts in `ai/prompts/refusal.<key>.<lang>.txt`:
     - `blocked_category`: gift card, wire, crypto.
     - `scam_pattern`: judge refusal, coached without a blocked item.
     - `code_reading`.
   - Each follows the PRD's refusal shape: never accuse; "you did nothing wrong"; "I have told Priya"; offer the next legitimate action.
   - Render with `POST https://api.x.ai/v1/tts` using **the voice Manush picks at 12:45** (`ara`, `luna` or `carina`; `naksh` for Hindi). Use `language` `es-MX`, `hi`, `en` and `speed` 0.9, into `ai/warnings/refusal.<key>.<lang>.mp3`.
   - Check the voice exists in `GET /v1/tts/voices`. The clip must sound like the same agent that was just talking.
   - `audio_url` is `/audio/refusal.<key>.<lang>.mp3`, relative to the relay.
3. **Eval set, started tonight, finished at 6am.** `ai/eval/scripts.yaml`, 40 scripts, each labeled with an expected action (`allow`, `category_block` or `refuse`), not just scam or benign.
   - **20 scam:**
     - English, 8: grandparent plus gift card; grandparent with courier cash and a lawyer; Social Security suspended; IRS back taxes; tech-support refund with remote access; prize fee; romance or investment through a Bitcoin ATM; bank "safe account" wire.
     - Spanish, 6: abuelo with fianza and secreto; Seguro Social; impuestos or multa; soporte técnico; premio; criptomonedas.
     - Hindi, 6 (3 in Devanagari, 3 in Hinglish): digital arrest; पोता accident with जेल and जमानत; KYC and OTP; parcel held at customs; lottery with a recharge card; gift card plus "code batao".
   - **20 benign, at least 14 of them hard negatives:** "pay with my Visa card"; a gift card for a grandson's birthday (expected `category_block`, scored separately); "I need it today, my daughter is visiting"; Medicare card renewal; a real grandson calling with no money ask; retelling a scam news story; paying one's own county tax; calling the number on the back of one's own card. Plus the Spanish and Hindi equivalents: पोते के जन्मदिन का गिफ्ट कार्ड, one's own login OTP, बेटा आज आ रहा है, a passport police verification, recharging one's own phone, and a "pata nahi" probe for the पता/पोता collision.
   - Write the Spanish from the FTC Spanish pages; there is no public Spanish scam-call dataset. English templates: AARP and the FTC. For Hinglish ideas, BothBosu/scam-dialogue (Apache-2.0) and the Indian Cyber Scam Hinglish set (Apache-2.0); read them, do not copy them.
4. **Eval runner** `ai/eval/run.py`:
   - Rules alone, then rules plus judge on both models.
   - Per language and per layer: precision, recall and F1 with scam as the positive class, and the false-refusal rate with a Wilson 95% interval (`statsmodels ... proportion_confint(k, n, method="wilson")`). With 20 benign and 0 false refusals, report "at most 16%", not "0%".
   - Pick `JUDGE_THRESHOLD` on one half (grid 0.5-0.8) and report on the other.
   - Run each script 3 times and report the verdict flip rate.
   - Median and p90 latency. Results go in `ai/eval/RESULTS.md` (public: it is Devpost evidence).
5. **Prompt caching for the judge.** Order the prompt as system prompt, rubric, one scam and one hard negative per language, then the transcript last. Send `x-grok-conv-id` per session and check `cached_tokens` in the usage. Temperature 0 on the non-reasoning model; grok-4.7 rejects `presence_penalty`, `frequency_penalty` and `stop`.

**Decision for the 1:00 standup: the cart structurer (FR-25).** Recommendation: drop the separate structuring call.
- The voice model already turns speech into skus through `search_catalog`, `add_to_cart` and `read_cart`, and a second model call costs 1-3 s per turn.
- The xAI story stays whole: Grok Voice is the interface and a Grok judge scores every checkout.
- If the team keeps it, it becomes `POST /structure` on Saturday, not tonight.

**Done when.**
- `pytest -q policy/tests/test_screen.py` passes, including every line from R1-R3.
- The three demo scam lines are refused in each language, with and without a final danda, and each `audio_url` loads from the relay.
- "I will pay with my Visa card", "my Medicare card" and "मेरे वीज़ा कार्ड से" proceed.
- `/judge` returns contract-valid JSON with `JUDGE_FAKE=1` and live.

**Pitfalls.**
- `.updated` transcripts are cumulative, so screening every partial would double count. Only final screens move session memory.
- xAI speech-to-text applies inverse text normalization ("five hundred dollars" becomes "$500"), so lexicons need digit and currency forms where amounts matter.
- Whether Grok writes Hindi loanwords in Devanagari or Latin is undocumented. Keep "गिफ्ट कार्ड", "gift card" and the mixed "गिफ्ट card" all matching.

---

## 8. Integration smoke, 1:45-2:00am

Services laptop from the repo root, each in its own terminal: relay on 8000, policy on 8001, merchant on 8002 with `MERCHANT_VERIFY=enforce MOCK_VISA=1`, catalog on 8003. One link at a time; each printout proves a seam.

1. **Stream first (Vraj):** `curl -N http://127.0.0.1:8000/events/stream`, left running on the big screen.
2. **Screen (Rohan):** `curl -s -X POST :8001/screen -H "Content-Type: application/json" -d '{"session_id":"s_smoke","text":"मुझे गिफ्ट कार्ड चाहिए।","lang":"hi"}'` returns `refuse` with an `audio_url`. Then `curl -I :8000<audio_url>` answers 200.
3. **Checkout path (Dhruv and Vraj):** `curl -s -X POST :8001/checkout -d @policy/tests/demo_cart.json` (RX-001 and BAK-001, $11.49) returns `allow` with an `order.payment_link`. The stream shows `policy_decision`, `request_signed`, `signature_verified` (five checks) and `payment_link_created`.
4. **Replay (Vraj):** resend the captured signed order to `:8002/orders`; 401 with the nonce check red.
5. **Paid (Vraj):** `python -m merchant.simulate_payment <order_id>`; `paid` appears on the stream.
6. **Voice (Manush):** "necesito mi medicina para la presión y pan", then the read-back, then "sí"; the same events appear, plus `heard`, `items_found`, `cart_updated` and `checkout_requested` from the station.
7. **Refusal by voice (Manush and Rohan):** the Spanish gift-card line; the clip plays in the agent's voice and `refusal` shows on the stream.

Do not debug any one link past 10 minutes. Write it on the whiteboard; it becomes a 6am task.

---

## 9. Exit check and hand-off into Phase 2

**2am exit (all four).** Read Section 1's pass conditions aloud. Anything missed is written as the first Saturday 6am task with an owner. Merge everything green to main. Manush and Rohan go to sleep.

**5am hand-off (Dhruv and Vraj).** Post in `#chaperone`:
- What is merged.
- The exact start commands for all four services and the caregiver app.
- The tunnel host, whether the webhook is `PENDING_REVIEW` or active, and whether Cybersource answered.
- What is still fake: judge, mandate signature, paid.
- The first thing Manush and Rohan should run at 6am.

**What Phase 2 (Sat 6am-12pm) starts from.** The purchase path is real end to end except the settlement.
- Voice, catalog and policy use the real screen and judge, then the signer, then the merchant enforcing all five checks, then the payment link, the ledger and the wall.
- Phase 2 adds receipt printing from a real order, the session page, the caregiver approval UI, sandbox paid status (real if Cybersource is fixed, the signed callback otherwise) and the first two-outcome run at noon.

---

## 10. Sources

Pages opened on Sep 25, 2026. Items marked unconfirmed in the text were not in official docs.

**Grok Voice and TTS (Manush, Rohan):**
- [speech-to-speech guide](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech) (`force_message`, resumption, parallel tool calls, `language_hint`)
- [voice reference](https://docs.x.ai/developers/rest-api-reference/inference/voice)
- [WebSocket event schema](https://docs.x.ai/voice-realtime.ws.json)
- [prompting guide](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/prompting-guide)
- [ephemeral tokens](https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens)
- [rate limits](https://docs.x.ai/developers/rate-limits)
- [pricing](https://docs.x.ai/developers/pricing)
- [voices](https://docs.x.ai/developers/model-capabilities/audio/text-to-speech#voices)
- [speech to text](https://docs.x.ai/developers/model-capabilities/audio/speech-to-text)
- [structured outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs)
- [reasoning](https://docs.x.ai/developers/model-capabilities/text/reasoning)
- [prompt caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/best-practices)

**Passkeys, alerts and the tunnel (Dhruv):**
- SimpleWebAuthn [server source](https://github.com/MasterKale/SimpleWebAuthn/tree/master/packages/server/src), [custom challenges](https://simplewebauthn.dev/docs/advanced/server/custom-challenges), [custom user ids](https://simplewebauthn.dev/docs/advanced/server/custom-user-ids), [v14 release](https://github.com/MasterKale/SimpleWebAuthn/releases/tag/v14.0.0)
- [py_webauthn](https://pypi.org/project/webauthn/) and its [verify_authentication_response](https://raw.githubusercontent.com/duo-labs/py_webauthn/master/webauthn/authentication/verify_authentication_response.py)
- [OWASP MFA cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
- [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [ngrok free plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits), [ngrok interstitial](https://ngrok.com/docs/errors/err_ngrok_6024), [ngrok HTTP timeouts](https://ngrok.com/docs/universal-gateway/http)
- [Next.js streaming](https://nextjs.org/docs/app/guides/streaming)
- [Vibration API](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/vibrate)
- [Screen Wake Lock](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Wake_Lock_API)
- [iOS web push](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)

**Cybersource and TAP (Vraj):**
- [Pay by Link webhooks](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-webhooks-intro.html) and [the PBL subscription example](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-webhooks-intro/paybylink-webhooks-ex-rest.html)
- [digital signature key](https://developer.cybersource.com/docs/cybs/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-key-dig-sig-intro.html), [signature format](https://developer.cybersource.com/docs/cybs/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-optional-intro/wh-fg-optional-validate-intro/wh-fg-optional-validate-sig-format.html), [validation](https://developer.cybersource.com/docs/vas/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-optional-intro/wh-fg-optional-validate-intro.html)
- [health check](https://developer.cybersource.com/docs/cybs/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-optional-intro/wh-fg-subscription-health-check-url.html), [URL review](https://developer.cybersource.com/docs/cybs/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-subscribe-intro/wh-fg-url-validation.html), [notification payload](https://developer.cybersource.com/docs/cybs/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-notification-payload-ex.html)
- [Transaction Search](https://developer.cybersource.com/docs/cybs/en-us/txn-search/developer/all/rest/txn-search/txn-search-intro/txn-search-request.html)
- [Pay by Link get](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-services/paybylink-get-intro/paybylink-get-ex-rest.html), [Unified Checkout processing](https://developer.cybersource.com/docs/cybs/en-us/unified-checkout/developer/all/rest/unified-checkout/uc-intro-setup/uc-pay-processing-intro.html)
- [developer support](https://developer.cybersource.com/support/contact-us.html)
- [TAP specification](https://developer.visa.com/capabilities/trusted-agent-protocol/trusted-agent-protocol-specifications)

**Rules and eval (Rohan):**
- [Unicode core spec, South Asian scripts](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-12/), [UAX #15](https://unicode.org/reports/tr15/), [Python unicodedata](https://docs.python.org/3/library/unicodedata.html), [Python re](https://docs.python.org/3/library/re.html)
- FTC Spanish pages: [abuelos](https://www.consumidor.ftc.gov/blog/2021/04/no-le-abras-tu-puerta-las-estafas-dirigidas-los-abuelos), [tarjetas de regalo](https://consumidor.ftc.gov/articulos/como-evitar-y-reportar-las-estafas-con-tarjetas-de-regalo), [impostores del gobierno](https://consumidor.ftc.gov/articulos/como-evitar-una-estafa-de-impostores-del-gobierno), [soporte técnico](https://consumidor.ftc.gov/alertas-para-consumidores/2022/05/acabemos-con-las-estafas-de-soporte-tecnico)
- [AARP grandparent scams](https://www.aarp.org/money/scams-fraud/grandparent/)
- [I4C digital-arrest advisory](https://www.amarujala.com/india-news/cbi-ed-police-don-t-arrest-people-through-video-calls-indian-cyber-crime-coordination-centre-2024-10-06)
- [RBI BE(A)WARE booklet](https://rbidocs.rbi.org.in/rdocs/PressRelease/PDFs/PR1817F4A7B3662BEC4AD7AC6A2D85EAF937ED.PDF)
- [BothBosu/scam-dialogue](https://huggingface.co/datasets/BothBosu/scam-dialogue), [Indian Cyber Scam Hinglish](https://huggingface.co/datasets/DatasetNewUser/Indian_Cyber_Scam_PhoneCall_Hinglish_Dataset)
- [Brown, Cai and DasGupta on binomial intervals](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full)
