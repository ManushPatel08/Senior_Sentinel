# Senior Sentinel: Phase 4 Playbook

As of 2026-09-26, 12:15pm

Visa's briefing slides this morning gave us the rubric, as four stages of an agentic purchase:

| Stage | Visa's words |
|---|---|
| **01 Discover** | "understand intent and surface relevant options" |
| **02 Decide** | "reason across preferences, policy, availability and context" |
| **03 Transact** | "preserve identity, intent, controls and merchant trust" |
| **04 Continue** | "support delivery, service, refunds, returns and loyalty" |

The mission slide adds: "What happens after payment: delivery, changes, returns, service or loyalty?", "Make trust visible", and "Think beyond retail: … accessibility". Visa's staff also told us a **mock is acceptable where the sandbox does not work**.

**Where we are.** Main (4a0c5d4) covers stages 01 to 03, and covers them well. Stage 04 is a receipt and a session page and nothing more. The research found that none of Visa's own December pilots showed stage 04 either, so it is the open lane.

**Phase 4 (12:30 to 5pm) builds three things:**
1. **Stage 04:** order status, cancel, return and refund, pickup, savings and loyalty.
2. **The same guardrails, run in reverse, for the second-biggest elder scam: the refund scam.**
3. **The caregiver app as a finished product,** instead of the developer page it is today.

Every open fix from the Phase 3 merge is folded in, marked **Fix**.

The old plan's hardening phase becomes Phase 5 (5-9pm), then shipping is Phase 6 (9pm-3am) and the expo is Phase 7. See Section 9.

---

## 1. Phase 4 at a glance

| Time | Everyone | Manush (station) | Dhruv (policy, caregiver app) | Vraj (merchant, relay, wall, catalog) | Rohan (rules, lines, prompts, eval) |
|---|---|---|---|---|---|
| 12:30-12:45 | Standup: Phase 3 carry-overs (Section 2), contracts G1-G9 (Section 3); pull main | | | | |
| 12:45-2:30 | Build | Tools and the refund confirm step (V-B1, V-B2) | Order endpoints in policy: cancel, refund, history, pause (D-B1 to D-B4) | Order lifecycle, real Pay by Link cancel, refund mock, events (X-B1 to X-B4) | Refund-scam rules and tests (R-B1), line files (R-B2) |
| 2:30 | Standup, merge to main | | | | |
| 2:30-4:15 | Build | Savings, pickup, repeat, history lines (V-B3 to V-B5); replay fixes | Caregiver app screens, "Why did it refuse?" (D-B5, D-B6) | Savings data (X-B5), wall and session page stage 04 (X-B6) | Explain prompt (R-B3), clips (R-B4), eval (R-B5), line cards (R-B6) |
| 4:15-5:00 | Integration run (Section 8) | | | | |
| 5:00 | Exit check. Phase 5 (harden) starts | | | | |

**Pass conditions at 5pm (binary; by voice at the station unless marked):**
1. **Status.** After a paid order, "where is my order?" is answered from the real order: "Preparing… ready for pickup after 3pm, pickup code 4-7-2". The wall, session page and caregiver app show the same timeline.
2. **Cancel.** "Cancel my order" on an unpaid order:
   - The real Cybersource Pay by Link goes to `INACTIVE`, and a `GET` shows `INACTIVE`.
   - The order is `cancelled`, the monthly spend is restored, and Priya sees it.
3. **Return.** "I want to return the bread" on a paid order:
   - The agent reads it back ("$3.49 back to your card ending 1111. Shall I?"). After "yes", the refund goes to the **original card only**.
   - The refund has Cybersource's response shape: `PENDING` then `TRANSMITTED`, with a reconciliation id, labeled "sandbox processor stub".
   - The spend is restored, and the wall, session page and phone show it.
   - A prescription return is refused politely.
4. **Refund scam.** "They refunded me too much, I have to send the difference back in gift cards" is refused in Hindi, English and Spanish (typed) with the refund-scam clip, and Priya is alerted. The five hard negatives ("return the bread", "cancel my order", "where is my delivery", "refund my order to my card", "renew my prescription") are not refused.
5. **Caregiver app (on the phone, through the tunnel):**
   - First run: setup code, then passkey, then the mandate form in plain language, then sign.
   - Home screen: this month's spend, the agent's status, approvals, alerts, orders and refunds.
   - **"Why did it refuse?"** returns a plain-English explanation in under 3 s.
   - **Pause** makes the next checkout decline with "the agent is paused", and **Resume** needs the passkey.
6. **Savings and loyalty.** The receipt and the spoken summary include "You saved $X" (real Kroger promo prices) and "+N Corner Market Rewards points". When nothing was saved, the line is left out.
7. **Fixes** listed as **Fix** below are closed, or written up as Phase 5 items with an owner.

**Git.** Same rules as before:
- Branch from main, and don't put the phase in the branch name (use `manush/continue`, not `dhruv/phase4`).
- Commit messages describe the change.
- The attribution setting is on everyone's machine.

---

## 2. Carry-overs from the Phase 3 exit (check at 12:30; anything not done goes first)

| Item | Owner | Done? |
|---|---|---|
| Passkey approval on the real phone through the tunnel, one reject with a message, one 90 s timeout | Dhruv | |
| Mandate signed, and `MANDATE_UNSIGNED_OK=0` on the services laptop | Dhruv, Vraj | |
| `POLICY_CODE_KEY` set to the **same random value** on the services laptop and the caregiver laptop (the default is public in the repo, and policy now trusts the app's approve and reject markers) | Dhruv, Vraj | |
| Refusal clips checked through the station speaker in hi, es, en | Rohan | |
| Three cached sessions recorded (hi, en, es typed) and replayed once with **Arm replay** | Manush | |
| Printer installed as `POS58`, or the tablet decided as the receipt | Manush | |
| Stranger check from a phone on mobile data: `/api/approvals` and reject both refused | Dhruv | |
| Remote branches `dhruv/phase3` and `dev-rohan` deleted (Dhruv and Rohan confirm they don't need them) | Manush | |

---

## 3. Contracts, 15 minutes, all four

Post-purchase actions follow the same trust chain as a purchase:

**station → policy (checks the mandate and the rules) → signed RFC 9421 request (`tag="agent-payer-auth"`) → merchant (verifies the five checks) → Cybersource (real where the sandbox allows, stub where it cannot).**

The model never passes an amount or a destination.

| # | Contract | Owner |
|---|---|---|
| G1 | **Order lifecycle.** `awaiting_payment` → `paid` → `preparing` → `ready_for_pickup` → `picked_up`. Side exits: `cancelled` (only from `awaiting_payment`), `partially_refunded` and `refunded` (from `paid` or later). After `paid`, the merchant advances on timers: `preparing` after 20 s, `ready_for_pickup` after 60 s. Each order gets a 3-digit `pickup_code`. Event `order_status {order_id, status, pickup_code?}` | Vraj |
| G2 | **Cancel.** Station tool `cancel_order {order_id?}` (defaults to the session's latest order) calls `POST {policy}/orders/{order_id}/cancel`. Policy checks the order belongs to this mandate and is `awaiting_payment`, then sends a signed `POST {merchant}/orders/{order_id}/cancel`. The merchant sets the **real** Pay by Link `INACTIVE` (G6), marks the order `cancelled`, and returns `{status, link_status}`. Policy restores the spend and posts `order_cancelled`. A paid order can't be cancelled; it gets the return path | Dhruv, Vraj |
| G3 | **Refund.** Station tool `request_refund {order_id?, sku?, qty?, reason, confirmed}`. It has no amount and no destination field. Policy `POST /refunds` runs the refund rules (G4) and computes the amount from the order's own lines. With `confirmed: false` it returns `{preview: {amount, card_last4, items}, say}` and changes nothing. With `confirmed: true`, and a shopper turn after the preview, it sends a signed `POST {merchant}/orders/{order_id}/refunds {sku, qty, amount}`. The merchant answers with G5's shape. Policy restores the spend and posts `refund_requested` and then `refund_result` | Dhruv, Manush, Vraj |
| G4 | **Refund rules** (policy, deterministic, every result on the ledger):<br>**RF1** the order exists, belongs to this mandate, and is `paid` or later.<br>**RF2** the amount is at most the paid amount minus earlier refunds.<br>**RF3** the destination is the original card; there is no other option in the API.<br>**RF4** the return window is 30 days, and `pharmacy_pickup` lines are not returnable (say key `refund_not_allowed_rx`).<br>**RF5** the transcript passes the screen; refund-scam rules come from Rohan, and a hit refuses with say key `refund_scam` and alerts Priya.<br>**RF6** Priya is notified of every refund (`caregiver_alerted {kind: "refund"}`).<br>Refunds return money, so they need no approval. They need the read-back "yes" | Dhruv |
| G5 | **Refund response (mock; Cybersource's real `POST /pts/v2/payments/{id}/refunds` shape).** `{id, status: "PENDING", reconciliationId, refundAmountDetails: {refundAmount, currency}, processorInformation: {responseCode: "100", approvalCode}, source: "sandbox-processor-stub"}`. It moves to `TRANSMITTED` after 5 s (event `refund_result {status}`). Label it the same way everywhere: "Refund to the original card · sandbox processor stub". The reason: sandbox authorizations fail with reason 150, so nothing was ever captured that could be refunded | Vraj |
| G6 | **Real Pay by Link cancel.** The toolkit's `update_payment_link` has no `status` field, so call REST directly with `merchant/cybs_rest.signed_request`: `PATCH /ipl/v2/payment-links/{id}` with body `{"status": "INACTIVE", "processingInformation": {"linkType": "PURCHASE"}, "orderInformation": {"amountDetails": {"currency": "USD", "totalAmount": "<same total>"}, "lineItems": [<the same one line used at creation>]}}`. Then confirm with `GET /ipl/v2/payment-links/{id}` → `status: "INACTIVE"`. Store the creation line item on the order so the PATCH can repeat it exactly. The mock backend does the same in memory | Vraj |
| G7 | **History and pause.** `GET {policy}/history?mandate_id=&days=30` returns orders, refunds and refusals with totals, for the station's `purchase_history` tool and the caregiver app. `POST {policy}/mandate/pause` needs a caregiver session. `POST {policy}/mandate/resume` needs a passkey assertion over `SHA-256(JCS({action: "resume", mandate_id, nonce, expires_at}))`, because loosening a control takes the stronger proof. While paused, R0 fails with say key `agent_paused`, and the event is `mandate_paused` or `mandate_resumed` | Dhruv |
| G8 | **"Why did it refuse?"** `GET {policy}/decisions/{id}/explain` sits behind the caregiver session in the app. It returns `{headline, what_happened, rule_in_plain_words, what_ruth_heard, what_you_can_do}`, generated once by `grok-4.20-0309-non-reasoning` with strict JSON from the decision's rules, screen hits, the judge's rationale and the transcript excerpt. It is cached per decision, and `EXPLAIN_FAKE=1` gives a fixed answer for tests. Rohan owns the prompt and schema (`ai/prompts/explain_*`); Dhruv owns the endpoint | Dhruv, Rohan |
| G9 | **Events.** Add `order_status`, `order_cancelled`, `refund_requested`, `refund_result`, `mandate_paused`, `mandate_resumed`, `explanation_requested` to `contracts/events.schema.json`, with payloads in `$defs.payloads`. The wall, session page and caregiver app render them | Vraj |

---

## 4. Manush: station

**Build.**
- **V-B1 New tools** (flat shape, in `station/config/voice.json`; update the instructions so the model uses them):
  ```json
  {"type":"function","name":"order_status","description":"Where the shopper's order is: paid, preparing, ready for pickup, pickup code. Use for 'where is my order'.","parameters":{"type":"object","properties":{"order_id":{"type":"string"}}}}
  {"type":"function","name":"cancel_order","description":"Cancel an order that has not been paid yet.","parameters":{"type":"object","properties":{"order_id":{"type":"string"}}}}
  {"type":"function","name":"request_refund","description":"Return items from a paid order. Money only ever goes back to the card that paid. Call first with confirmed false, read the say text, wait for yes, then call with confirmed true.","parameters":{"type":"object","properties":{"order_id":{"type":"string"},"sku":{"type":"string"},"qty":{"type":"integer","minimum":1},"reason":{"type":"string"},"confirmed":{"type":"boolean"}},"required":["reason","confirmed"]}}
  {"type":"function","name":"purchase_history","description":"What the shopper bought recently and what was refunded. Use for 'what did I buy last week'.","parameters":{"type":"object","properties":{"days":{"type":"integer","minimum":1,"maximum":60}}}}
  ```
- **V-B2 Refund confirm gate.** Use the same pattern as the read-back gate:
  - `request_refund {confirmed: true}` is held unless a `{confirmed: false}` preview for the same order and item came first, **and** a shopper turn with words followed it.
  - The station sends policy only the text since the preview, so a refund-scam line said earlier doesn't block a real return.
  - Unit tests: preview then yes then refund; refund without a preview is held; a changed item after the preview is held.
- **V-B3 "Repeat that"** (FR-6). Keep the last spoken line (model, clip or fixed line). If the shopper's turn is only a repeat request ("repeat that", "otra vez", "phir se boliye", plus Rohan's list), replay it through `force_message`, with no model turn.
- **V-B4 Receipt and summary.** Add the savings line and the loyalty points line from the merchant's receipt data (X-B5), and the pickup code in large type. `receipt_done` says the savings when there are any.
- **V-B5 Line keys** from Rohan's files (R-B2): `order_status`, `order_ready`, `order_cancelled`, `cancel_too_late`, `refund_preview`, `refund_done`, `refund_not_allowed_rx`, `refund_scam`, `agent_paused`, `you_saved`, `repeat_nothing`.

**Fix.**
- **Replay:**
  - The recorded "yes" can replay after the checkout event. Keep the first version's time with the last version's text (`recording.ts`).
  - A replay started without Start never polls the approval, but `approvalWait` stays set. Don't start a wait during a replay.
  - The replay's `RelayStream` survives Stop, and `start()` opens a second one. Close or reuse it.
- **The asking-line clip** is added as an assistant message *before* the `function_call_output`. Add it after the output (in `continueAfterTools` when the response is silent).
- **`tests/mock_realtime.py`** cancel returns 200 on an already-closed approval, where policy returns 400. Match policy.

**Done when.** Pass conditions 1-4 and 6 work by voice. `npm test` passes, with new tests for the refund gate and "repeat that". The mock tests pass.

---

## 5. Dhruv: policy and the caregiver app

**Build: policy.**
- **D-B1 Cancel (G2):** `POST /orders/{order_id}/cancel`. Check ownership and `awaiting_payment`, send the signed merchant call (store before send, as with checkout), restore the spend, post the event.
- **D-B2 Refunds (G3, G4):** `POST /refunds` with the preview then confirm flow, RF1-RF6 each recorded in the decision's `rules` list (ids `RF1_order_owned` … `RF6_caregiver_told`). The amount comes from the order's lines, never from the caller. `add_spent_cents(-amount)` runs only after the merchant answers `PENDING`. Screen the refund transcript with Rohan's rules. A hit refuses and alerts Priya.
- **D-B3 History (G7):** `GET /history`, which also backs the station's `purchase_history` and the caregiver app's orders list.
- **D-B4 Pause and resume (G7):** R0 checks `paused`, and the caregiver app gets a big toggle.
- **D-B6 Explain (G8):** the endpoint, a per-decision cache, the fake mode, and a 3-second time limit. If it fails, show the rule and detail as written ("R1_blocked_category: gift cards are blocked on this account").

**Build: the caregiver app as a product (D-B5).** It is mobile-first with large type (at least 18 px, buttons at least 44 px) and plain words. Priya has never seen a rule id. Screens:
1. **Welcome (first run):** "Set up Senior Sentinel for Ruth". Setup code, then "Create your passkey" (the payment-enabled passkey for the amount-before-fingerprint dialog).
2. **Rules (the mandate form, FR-13):** per purchase, per month, "ask me above", allowed stores and categories, blocked list (gift cards, prepaid cards, wire, crypto, lottery checked by default), languages, and valid dates.
   - A live plain-language preview: "Ruth can spend up to $60 at a time and $300 a month at Corner Market on groceries and pharmacy. Anything over $40 comes to you. Gift cards and wire transfers are always refused."
   - **Sign with passkey** sends `POST /mandate`. The wall's mandate card updates.
3. **Home:**
   - "This month: $153.59 of $300", and the agent's status with **Pause** (Resume needs the passkey).
   - Cards: **Needs your approval** (live, with the countdown), **Alerts** (refusals, each with **Why?**), **Orders** (timeline, pickup code, cancel while unpaid), **Refunds**.
   - **Call Ruth** (`tel:`).
4. **Why? sheet (G8):** the headline, what happened, the rule in plain words, what Ruth heard, what you can do.
5. **History:** the last 30 days, orders and refunds.

Split `app/page.js` into components (`app/components/*.js`) and small screens. There is no router change: one page with a screen state is fine, and it keeps the tunnel's request count low. Every data call goes through the existing session-gated routes. Add `GET /api/history`, `POST /api/pause`, `POST /api/resume`, `GET /api/decisions/[id]/explain` and `POST /api/orders/[id]/cancel`, all behind `requireSession()`, with ids checked against their patterns.

**Fix.**
- The phone has no field for the **decline message** (E3 from Phase 3): add an optional one-line message under Reject.
- **Policy's LAN endpoints** (`GET /approvals` with transcript excerpts, `/approvals/{id}/code`, `host_code`) are open to anyone on the team router. Drop `excerpt` from `GET /approvals`; the app gets it through a separate session-gated route. Put the code and `host_code` behind the E5 header check. Tests for each.
- **`POLICY_CODE_KEY`**: policy should refuse to start with the default key unless `POLICY_DEV_KEY_OK=1`, so a demo laptop can't silently run with the public key.

**Done when.** Pass conditions 2, 3 and 5 hold on the real phone. `pytest -q policy` passes, with new tests for RF1-RF6, cancel ownership and state, pause and resume, and explain in fake mode. The caregiver build and tests pass.

---

## 6. Vraj: merchant, relay, wall and catalog

**Build.**
- **X-B1 Lifecycle (G1):** statuses, timers after `paid`, `pickup_code`, `order_status` events, and `GET /orders/{id}` returning the timeline (`[{status, at}]`). Reset clears timers.
- **X-B2 Cancel (G2, G6):** `POST /orders/{id}/cancel`, signed and verified with the five checks (the decision check accepts the order's own decision).
  - The real `PATCH /ipl/v2/payment-links/{id}` sets `INACTIVE`, then a `GET` confirms it. The mock does it in memory.
  - Test the real one once against the sandbox, and put the request id in the panel.
  - **Fix:** use the same PATCH when a link is created at the wrong amount. Today a real link at the wrong amount stays `ACTIVE` after the fallback to the mock.
- **X-B3 Refund (G3, G5):** `POST /orders/{id}/refunds`, signed and verified.
  - Record the refund on the order (`refunds: [{id, sku, qty, amount, status, reconciliationId, at}]`), and set `partially_refunded` or `refunded`.
  - The `PENDING` to `TRANSMITTED` timer runs, with the events.
  - A refund of more than the remaining amount is a 409.
  - The response has the exact shape in G5, with `source: "sandbox-processor-stub"`.
- **X-B4 Events (G9):** schema enum and payloads; the wall renders every new event type.
- **X-B5 Savings data (pass condition 6).**
  - Re-run `catalog/seed_kroger.py` keeping `items[0].price.regular` and `items[0].price.promo` for the Ponce de Leon store (the Kroger keys are in `.env`; the limit is 10,000 calls a day). The build writes `price` (what we charge = promo if present) and `regular_price`.
  - Orders carry `savings` (the sum of `(regular - price) × qty`) and `loyalty_points` (1 per whole dollar paid, "Corner Market Rewards", clearly the merchant's own program). The receipt JSON gains `savings`, `loyalty_points`, `pickup_code`.
  - If Kroger returns no promos today, leave savings out rather than invent them.
- **X-B6 Wall and session page, stage 04.**
  - The order card shows the timeline (ordered, paid, preparing, ready, picked up) and the refunds with their status and "sandbox processor stub" label.
  - The session page gets a **"Dispute-ready record"** section. It holds everything an issuer needs to settle a dispute quickly: the shopper's own words, the mandate hash and passkey signature id, the policy decision, the RFC 9421 signature (key id, nonce), the payment, and refunds. Add a JSON download at `/sessions/{id}/record.json`.
  - This mirrors Visa's own post-purchase vocabulary ("share order details with issuers", "quick resolution of most disputes").

**Fix.**
- Policy's and the merchant's own `POST /reset` and the merchant's `POST /orders/{id}/paid` have no Host-header check. Add E5's `X-Senior-Sentinel-Host` check, and send it from the relay's reset fan-out and Confirm payment.
- A `since` parameter was added to `/events/stream`; document it in `relay/ledger.py` and `ports.md`.

**Done when.** Pass conditions 1-3 and 6 show on the wall and session page. The real `INACTIVE` is seen once in the sandbox, with the request id written down. `pytest -q merchant relay catalog` passes, with new tests for the lifecycle, cancel, refunds (partial, full, over-refund 409) and the PATCH body.

---

## 7. Rohan: rules, lines, prompts and eval

**Build.**
- **R-B1 Refund, recovery, delivery and subscription rules** (research below; H = hard refuse, S = soft):

  | Rule | Examples (en / es / hi) | Sig |
  |---|---|---|
  | `R_overpay_sendback` | "refunded you too much", "send back the difference" / "le reembolsaron de más", "devuelva la diferencia" / "zyada refund ho gaya", "फर्क वापस भेजो" | H |
  | `R_fee_for_refund` | "processing fee to release your refund", "retainer" / "cargo de procesamiento", "anticipo de honorarios" / "refund ke liye processing fee", "रिफंड के लिए शुल्क" | H |
  | `R_recovery_for_fee` | "we can recover your lost money" (+ fee → H) / "recuperar su dinero" / "aapka paisa recover kar denge" | H with a fee, else S |
  | `R_remote_access` | "AnyDesk", "TeamViewer", "share your screen", "remote access" / "acceso remoto" / "स्क्रीन शेयर", "AnyDesk download karo" | H |
  | `R_refund_rail` | gift card, wire, crypto, cash, Zelle, UPI ID **in a refund context** | H |
  | `R_customs_hold` | "held in customs", "clearance fee", "tariff" / "retenido en la aduana", "arancel" / "parcel customs mein atka", "कस्टम क्लियरेंस चार्ज" | H |
  | `R_redelivery_fee` | "redelivery fee", "unpaid postage" / "franqueo impago", "entrega fallida" / "redelivery charge pending" | H with a link or pay, else S |
  | `R_parcel_illegal` | "package has drugs", "seized", "digital arrest" / — / "पार्सल में ड्रग्स", "डिजिटल अरेस्ट" | H |
  | `R_renewal_callback` | "Norton / Geek Squad / McAfee auto-renewed $399, call within 24 hours" / "renovación automática" / "subscription auto-renew ho gaya" | S (H with a deadline) |
  | `R_silence_request` | "don't tell your bank / the police" / "no avise al banco" / "bank ko mat batana" | H |
  | `R_refund_authority` | "I'm from the refund department / the FTC / a law firm" / "departamento de reembolsos" / "cyber cell se" | S |
  | extend `R_code_reading` | "9-digit code", "CVV" / "dígame el código" / "CVV बताओ" | H |

  - **Hard negatives** (each a test that must **not** refuse):
    - "I want to return the bread" / "quiero devolver el pan" / "bread wapas karni hai"
    - "refund my order to my card" / "reembolsa mi pedido a mi tarjeta" / "mera order refund karo"
    - "cancel my order" / "cancela mi pedido" / "order cancel karo"
    - "where is my delivery" / "¿dónde está mi entrega?" / "meri delivery kahan hai"
    - "renew my prescription" / "renueva mi receta" / "meri dawai renew karo"
    - "is there a restocking fee?"
  - Add `spoken_key: "refund_scam"` for the new hard rules.
- **R-B2 Line files** (en, es, hi) for the keys in V-B5, plus the "repeat that" trigger phrases per language. Keep the warm refusal shape for `refund_scam`: "A real store never asks you to pay to get a refund, and never asks for gift cards. You did nothing wrong. I've told Priya."
- **R-B3 Explain prompt (G8):** `ai/prompts/explain_system.md` and `explain_schema.json`.
  - Written for a worried adult child: no rule ids, one sentence each, never alarming, always a next step ("call Ruth", "approve it from the app").
  - Five fixture cases in `ai/eval/explain_cases.yaml` (gift card, code reading, over the monthly cap, judge refusal, refund scam), checked for tone.
- **R-B4 Clips:** `refusal.refund_scam.{en,es,hi}.mp3` and `line.refund_done.{lang}.mp3` in the session voices (`carina` for es, `ara` for hi and en).
- **R-B5 Eval:** add 10 scripts: 6 refund, recovery or delivery scams (two per language) and 4 legitimate returns. Re-run rules-only and rules plus judge, and update `RESULTS.md`.
- **R-B6 Line cards:** add the refund-scam line (the alternate opener) and "I want to return the bread" (the third beat) in all three languages, with the Spanish pronunciation line.
- **Devpost numbers** (from the research):
  - FBI IC3 2025: tech and customer-support scams took **$1.04B from people over 60** (21,333 complaints).
  - FTC, Dec 2025: people over 60 are **5× likelier to lose money to tech support scams**, with median losses of $691 (60s), $1,000 (70s) and $1,650 (80s), and gift cards are the most frequent payment method in them.
  - Fake package delivery is the #1 text scam.

**Fix.**
- **"$500 worth of cards for my grandson" proceeds:** the "$" is dropped in normalization, and the amount pattern needs "dollars". Keep `$` before digits as the word "dollars", or match `\d{3,}` near "cards".
- `ai/eval/demo_sequence.py` skips Spanish; add `es` to the default languages.
- The eval counts grok-4.7 timeouts as misses. In production a timeout on a `judge` screen holds the order for Priya's approval, so report "held for approval" as its own column.
- The plural "my Amazon cards" is refused; add a `(?<!my )` guard and a test.

**Done when.** `pytest -q policy/tests/test_screen.py` passes, with every refund-rule line and every hard negative. The clips play through the speaker. `RESULTS.md` is updated, and the line cards are printed.

---

## 8. Integration run, 4:15-5:00pm

Services laptop on the router. The caregiver phone on the tunnel, signed in with alerts armed. One teammate plays Ruth from the line cards.

1. **Reset** from `/host` (Shift+R).
2. **Purchase.** Medicine and bread, then "yes", then signed, verified and a real Visa link. The Host confirms payment, the receipt shows "You saved…" and "+11 points", and the pickup code is large.
3. **Status.** "Where is my order?": preparing, then ready for pickup after 60 s. The phone and the wall match.
4. **Return.** "I want to return the bread" → preview ("$3.49 back to your card ending 1111. Shall I?") → "yes" → `PENDING`, then `TRANSMITTED`. Spend goes down by $3.49, and the phone shows the refund.
5. **Prescription.** "Return my blood pressure medicine": refused politely (RF4).
6. **Cancel.** A new order (Ensure, $9.99), then before paying: "cancel my order". The real Pay by Link goes `INACTIVE` (check the panel's GET), and the spend is restored.
7. **Refund scam** (Hindi, then English): refused with the clip, the phone buzzes, and **Why?** on the phone explains it in plain English.
8. **Pause** on the phone, then any checkout is declined with "the agent is paused". **Resume** with the passkey.
9. **Session page** from the receipt QR: the timeline, the refund, and the "Dispute-ready record" JSON.

Write down the time for each step. Anything past 10 minutes of debugging goes on the whiteboard as a Phase 5 task.

---

## 9. What follows (the plan from here to the expo)

| Phase | Window | Goal | Exit |
|---|---|---|---|
| **5. Harden and rehearse** | Sat 5-9pm | The loud-room test with the close-talk mic, push-to-talk thresholds, printer or tablet, the cached sessions, latency and eval numbers written down, cuts per the fallback ladder | 9 clean runs out of 10 by 9pm; anything else moves to the video |
| **6. Freeze, video, submission** | Sat 9pm-Sun 3am | Polish only. README with the four-stage map. Devpost in Visa's vocabulary (Discover, Decide, Transact, Continue; "make trust visible"). Video with the refund-scam scene. `internal/` removed, repo public | Devpost submitted by 3am with the video |
| **7. Expo** | Sun 6:30-11:15am | Set up, two clean runs, the runbook | Every judge gets the same 60-90 seconds |

**Demo change for Phase 5 rehearsals.** The 60-second core stays as it is (refusal, then purchase). For Visa's judges, the Host adds a 15-second third beat: the judge reads **"I want to return the bread"** from the card. Ruth hears the refund go back to her card, the wall shows the refund, and Priya's phone shows it. The Host's line: "Visa asked what happens after payment. Returns go back to the same card, and the refund scam is refused the same way the gift card was." The refund-scam line is the alternate opener on the line cards, for a judge who already saw the gift-card beat at another table.

---

## 10. Sources

Pages opened on Sep 26, 2026.

**Visa and Cybersource post-purchase (Vraj, Dhruv):**
- Cybersource [refund](https://developer.cybersource.com/docs/cybs/en-us/payments/developer/ctv/rest/payments/payments-processing-basic-intro/payments-processing-basic-refund-intro.html), [capture](https://developer.cybersource.com/docs/cybs/en-us/payments/developer/ctv/rest/payments/payments-processing-basic-intro/payments-processing-basic-capture-intro.html), [void](https://developer.cybersource.com/docs/cybs/en-us/payments/developer/ctv/rest/payments/payments-processing-basic-intro/payments-processing-basic-void-intro.html), [transaction details](https://developer.cybersource.com/docs/cybs/en-us/txn-search/developer/all/rest/txn-search/txn-details-intro/txn-details-request.html); [refund response enum (SDK)](https://github.com/CyberSource/cybersource-rest-client-node/blob/master/docs/PtsV2PaymentsRefundPost201Response.md)
- [Pay by Link update (status INACTIVE)](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-services/paybylink-update-intro.html), [Pay by Link get](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-services/paybylink-get-intro/paybylink-get-ex-rest.html)
- Toolkit [update_payment_link (no status field)](https://github.com/visaacceptance/agent-toolkit/blob/main/typescript/src/shared/paymentLinks/updatePaymentLink.ts) and [cancel_invoice](https://github.com/visaacceptance/agent-toolkit/blob/main/typescript/src/shared/invoices/cancelInvoice.ts)
- [Visa Intelligent Commerce ("Commerce Signals", disputes)](https://developer.visa.com/capabilities/visa-intelligent-commerce), [Intelligent Commerce on Visa Acceptance (transaction events)](https://developer.visaacceptance.com/products/intelligent_commerce.html), [Visa post-purchase solutions (Order Insight, pre-dispute)](https://usa.visa.com/solutions/post-purchase-solutions/merchants.html)
- [TAP specification (Consumer Recognition Object)](https://developer.visa.com/capabilities/trusted-agent-protocol/trusted-agent-protocol-specifications)
- [Visa Transaction Controls](https://developer.visa.com/capabilities/vctc/docs) (production path only; not built: mutual TLS plus message-level encryption), [PYMNTS on familiar protections](https://www.pymnts.com/news/artificial-intelligence/2025/visa-maps-a-path-to-agentic-commerce-that-feels-familiar-and-safe/), [Visa Trust Index, Sep 2026](https://investor.visa.com/news/news-details/2026/New-Visa-Research-Finds-Consumer-Trust-is-Accelerating-the-Path-to-Agentic-Commerce/default.aspx)
- [Kroger products API (price.regular, price.promo)](https://github.com/CupOfOwls/kroger-api)

**Refund and recovery scams (Rohan):**
- [FBI IC3 2025 report](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf), [FTC older-consumers report, Dec 2025](https://www.ftc.gov/system/files/ftc_gov/pdf/P144400-OlderAdultsReportDec2025.pdf), [FTC imposter data 2025](https://www.ftc.gov/news-events/news/press-releases/2026/06/ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025), [FTC text scams](https://www.ftc.gov/news-events/news/press-releases/2025/04/new-ftc-data-show-top-text-message-scams-2024-overall-losses-text-scams-hit-470-million)
- FTC [refund and recovery scams](https://consumer.ftc.gov/articles/refund-and-recovery-scams), [tech support scams](https://consumer.ftc.gov/articles/how-spot-avoid-and-report-tech-support-scams), [fake Geek Squad renewal](https://consumer.ftc.gov/consumer-alerts/2022/10/how-recognize-fake-geek-squad-renewal-scam), [Amazon refund texts](https://www.consumer.ftc.gov/consumer-alerts/2025/07/scammy-texts-offering-refunds-amazon-purchases), [FCC package scams](https://www.fcc.gov/how-identify-and-avoid-package-delivery-scams)
- FTC Spanish: [estafas de reembolso y recuperación](https://consumidor.ftc.gov/articulos/estafas-de-reembolso-y-recuperacion), [soporte técnico](https://consumidor.ftc.gov/articulos/como-detectar-evitar-y-reportar-las-estafas-de-soporte-tecnico), [USPS texts](https://consumidor.ftc.gov/alertas-para-consumidores/2025/04/crees-que-ese-mensaje-de-texto-es-de-usps-podria-ser-una-estafa)
- India: [refund-delay fraud (I4C via Storyboard18)](https://www.storyboard18.com/amp/digital/refund-delays-become-new-bait-for-cyber-fraud-targeting-online-shoppers-89185.htm), [RBI AnyDesk warning](https://www.cio.inc/rbi-warns-fraud-that-leverages-anydesk-app-a-12035), [I4C digital-arrest advisory](https://www.deccanherald.com/india/amid-rise-in-digital-arrest-cases-indian-cyber-crime-coordination-centre-issues-advisory-for-citizens-3221509)
- Refund rules: [CFPB on card refunds](https://www.consumerfinance.gov/ask-cfpb/how-can-i-get-a-refund-on-a-product-or-service-i-purchased-with-my-credit-card-en-1969/), [Visa rules hub](https://usa.visa.com/support/consumer/visa-rules.html)
