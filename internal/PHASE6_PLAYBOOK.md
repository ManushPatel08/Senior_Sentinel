# Senior Sentinel: Phase 6 Playbook

As of Sat Sep 26, 9:00pm. Phase 6 runs **9:00pm–12:30am**, with a merge at **10:45pm**.

**What Phase 6 is for.** Phase 5 proved every new piece works: the card network sandbox, the scam radar, four Visa merchants, Visa's card controls and the phone line. Nearly all of it is still invisible. The station opens in operator view with raw ids. The card never reaches the station or Priya's phone. The wall ignores the new events. There's no card terminal to tap. Phase 6 turns the parts into **the product a judge sees**: the new demo (`PRODUCT_V2.md` Section 6) running end to end on the services laptop. Everything left open from the Phase 5 reviews is folded in, marked **Fix**.

Read `PRODUCT_V2.md` Sections 0 and 2 if you haven't. This playbook assumes the four guards (Ask, Card, Agent, Family).

---

## 1. Phase 6 at a glance

| Time | Everyone | Manush (Ruth's station, the line) | Rohan (Ask guard, lines, evidence) | Dhruv (Priya's app, Family guard) | Vraj (terminal, Trust Ledger, Visa) |
|---|---|---|---|---|---|
| 9:00–9:15 | Pull main and start **new** branches (Section 2); agree the contracts (Section 3) | | | | |
| 9:15–10:45 | Build | Kiosk view, Protected card, store-aware cart and read-back (V6-1 to V6-3) | Radar timing and alerts, lines and clips (R6-1 to R6-4) | App shell, Home, Safety, Approvals with card holds (D6-1 to D6-4) | Card terminal, protected-dollars route, Decision Manager per order (X6-1, X6-3, X6-6) |
| 10:45 | Push; I merge to main and fix seams; 5-minute check-in | | | | |
| 10:45–12:00 | Build | Card events at the station, co-sign, line hardening (V6-4 to V6-8) | Eval, interviews, landing copy (R6-5 to R6-7) | Activity, Rules, co-sign, card fixes, onboarding (D6-5 to D6-9) | Visa card-controls mirror, Trust Ledger, session page (X6-2, X6-4, X6-5) |
| 12:00–12:30 | Integration run on the services laptop (Section 8) | | | | |
| 12:30 | Exit check; Phase 7 starts | | | | |

### 1.1 Pass conditions at 12:30am (binary; on the services laptop)

1. **Ask.** A judge reads the grandparent line at the station, in English or Spanish:
   - Within 12 s, a **full-screen Protected card** appears and Senior Sentinel speaks the verdict with one action.
   - Priya's **Safety** tab shows the check with its sources and a working **Why?**.
   - The wall shows the cool-down.
2. **Card.** On the terminal tablet, $480 at Five Points Drug is **DECLINED** with a plain reason.
   - The station speaks the decline in Ruth's language, and the wall's Card lane shows it (with "Visa VTC: decline" if X6-2 is green).
   - Priya sees the hold with **Allow once**. A gift-card-kiosk hold shows "stays blocked" and no Allow button.
   - After Allow once, the retry is approved.
3. **Agent.** "Order my blood pressure medicine and pay my power bill":
   - The read-back names each store.
   - Two signed orders are placed, one at Parkside Pharmacy and one at Peachtree Power, with real Visa links. Each gets a Decision Manager score on the ledger.
   - One Host press pays both, and a receipt prints per store. The bill receipt has no pickup line.
4. **Family.** Priya's app:
   - Has **tabs**, and no debug or operator text.
   - Home shows protected dollars and spend by store.
   - Rules lists the four stores and shows **"Ruth agreed by voice"**.
   - An approval for a non-Corner-Market store works, including the Secure Payment Confirmation path.
5. **Trust Ledger.** The wall shows the protected-dollars counter, the four guard lanes, plain-English rows and the Visa-shaped mandate. Nothing says "Corner Market" in the header.
6. **Line.** A real phone call to the xAI number:
   - The PIN is asked before any purchase.
   - A scam story on the phone gets the radar's verdict.
   - `line_call` shows on the wall.
7. **Fixes.** Section 2 items are closed or moved to Phase 7 with an owner.

---

## 2. Before you start, and fixes carried over

**Branches.** Start Phase 6 from main, on a new branch: `git fetch && git switch -c <name>/guards-ui origin/main`.
- Don't merge your old Phase 5 branch into it. Vraj's and Rohan's commits were reworded on main, so the old branches look unmerged but aren't.
- After this merge, delete `vraj/merchants`, `rohan/scam-radar`, `dhruv/guards` and the other old branches (Manush, **Fix F8** from Phase 5 still open).

**The services laptop (Manush's) is the demo machine.** It runs main with:
- Every key in `.env`.
- Priya's signed rules for all four stores.
- Lithic sending card swipes to its tunnel (`https://<TUNNEL_HOST>/card/asa`).

Rules for that machine:
- **Dhruv: live Lithic swipes now reach Manush's laptop, not yours.** Test the card code with signed fake requests (`policy/tests/test_card.py` shows how) and run live swipes on the services laptop.
- **After any restart of the services, close and reopen Priya's app on the phone.** A page opened before the restart keeps the old code; that's how the Corner-Market-only rules got signed at 8:38pm.

| # | Owner | Fix | Done when |
|---|---|---|---|
| F1 | Dhruv | The Secure Payment Confirmation approval hard-codes the payee "Corner Market" (`caregiver/app/page.js:269`) and the decide route enforces it (`caregiver/app/api/approvals/[id]/decide/route.js:37`). Approvals for Parkside, Main Street or Peachtree would be mislabeled or refused. Use the approval's stores. | An approval for a Parkside cart passes by SPC |
| F2 | Dhruv | `rulesSentence.js:12` always says "at Corner Market on groceries and pharmacy". The footer "Approval codes are printed on the host screen…" (`page.js:475`) and the status line (`page.js:476`) show to Priya. | Phase 6 app acceptance |
| F3 | Dhruv | `card_decision.store` is Lithic's descriptor, not the registry name. `allow_hold` posts the default mandate id. Store names are copied into `mandate.VISA_STORES`, `Home.js` and `Rules.js`. | One source: `contracts/merchants.json` |
| F4 | Dhruv | No committed Lithic setup. Write `python -m policy.card_setup`: create Ruth's card if none, enroll `https://$TUNNEL_HOST/card/asa`, check the secret against `.env`, write `sessions/card.json`. (I did this by hand on the services laptop at 8:30pm.) | The script re-points Lithic in one command |
| F5 | Dhruv | No tests for the 403 on `/refunds` and cancel from a proxied or non-LAN caller. | Tests |
| F6 | Rohan | Scam-check alerts carry no `decision_id`, so Priya's "Why?" can't explain them. `GET /scam-check/{id}` has no caregiver check. | R6-3 |
| F7 | Rohan | Facts run before Grok with no overall budget (up to ~13–14 s), and the station gives up at 14 s. A late Grok answer is thrown away. | R6-1 |
| F8 | Rohan | The per-pattern cache replays one story's details for another ("…Alex in jail after a car accident"). | R6-1 |
| F9 | Rohan | The story markers are broad. "Buy a $100 gift card for someone at church" routes to `scam_check`, so Ruth hears "please hang up" and a 24 h cool-down starts. | R6-2 |
| F10 | Rohan | Priya gets two alerts per refusal (the station's `refusal` and policy's `caregiver_alerted`). | R6-3, with Dhruv's Safety feed |
| F11 | Manush | The line keeps every word of the call and sends it to checkout, so an early scam story refuses a later honest purchase. The read-back gate doesn't need a new utterance. There's no caller check: anyone who dials can shop as Ruth. | V6-7 |
| F12 | Manush | Station edge cases: no tick during the typed-input screen wait; a bill quantity isn't clamped to 1; `toolScamCheck` doesn't reset `requestStart`; a partial-screen refuse can't be upgraded to `scam_check`; `asking_priya` says "over your limit" when the real reason is "the safety check was unavailable". | V6-8 |
| F13 | Manush | `line/README.md` still says calls are joined "within 5 minutes" (it's now 120 s). Nothing records a completed end-to-end call. | V6-7 |
| F14 | Vraj | `bill_checked` is posted on every price lookup with session "none". The biller ignores the mandate's `account_ref`. Gift cards belong to `corner_market`, so the blocked shop's 403 never fires. `store=home` finds nothing. The webhook verifier holds one key, so a real webhook from the three new accounts won't verify. Points sit inside the savings row. | X6-6 |
| F15 | Vraj | The session page still has `<meta refresh=5>`, omits every new event type, and says "Corner Market" in its header. | X6-5 |
| F16 | All | **Decide the two sponsor challenges** by 10:45: Visa + Aramco, or Visa + SpaceXAI. If SpaceXAI, Dhruv (the Cursor user) keeps screenshots, and the radar and line work is built or touched in Cursor. | Written in the team chat |
| F17 | Someone logged in | Confirm on live.hexlabs.org: the submission deadline (8am or Devpost's noon), the 2-sponsor cap (announced), and one general track (Oracle of the Deep). | Team chat |

---

## 3. Contracts (9:00–9:15; commit by 9:45)

**C12. New events** (`contracts/events.schema.json`; Vraj merges them):

| Type | Source | Payload |
|---|---|---|
| `vtc_decision` | policy or relay (X6-2) | `token, store, mcc, amount, should_decline, rule` |
| `risk_scored` | merchant (X6-3) | `order_id, merchant, status, score` |
| `cosigned` | policy (D6-7) | `by: "ruth", method: "voice", said, lang, mandate_hash` |

`line_call` exists already; Manush starts posting it.

**C13. Policy routes:**
- `GET /scam-checks?mandate_id=&limit=20` (caregiver marker; Rohan) returns `[{check_id, decision_id, verdict, pattern, story_excerpt, say, sources[], amount?, at}]`.
- Every scam check is saved as a decision document, so `/decisions/{decision_id}/explain` works.
- `POST /mandate/cosign {session_id, said, lang}` (LAN, from the station; Dhruv). It stores `{by: "ruth", method: "voice", said, lang, at, mandate_hash}` in `sessions/cosign.json`, never inside the signed file, and posts `cosigned`.
- `GET /mandate` adds `cosign` when it matches the current mandate's hash.

**C14. Caregiver API routes** (Dhruv), all behind `requireSession()`:

| Route | Calls |
|---|---|
| `GET /api/card` | policy `GET /card/state` |
| `POST /api/card/holds/[id]/allow` | policy `POST /card/holds/{id}/allow` with marker `(id, "card")` |
| `GET /api/scam-checks` | policy `GET /scam-checks` (C13) |
| `GET /api/risk` and `POST /api/risk/clear` | policy `/risk` and `/risk/clear` (clear exists) |
| `GET /api/protected` | relay `GET /wall/data/protected` (C17) |

The alert stream (`api/alerts/stream/route.js:11`) adds these types:
- `scam_checked`
- `card_decision`
- `card_hold_released`
- `risk_changed`
- `mandate_paused`
- `cosigned`

**C15. Card terminal** (Vraj):
- The relay serves `GET /terminal` (LAN only, like `/host`).
- `POST /host/api/swipe {acceptor_id, amount_cents}` requires the Host header and calls policy `/card/simulate`. It returns `{result, reason_key, reason, ms, store}` (policy already returns these).

**C16. Line PIN** (Manush):
- `LINE_PIN` in `.env` (4 digits).
- A new tool, `verify_pin(pin)`, marks the call verified for 10 minutes.
- `checkout`, `cancel_order`, `request_refund` and adding a bill refuse an unverified call with `say: line_pin_ask`.
- Read-only tools (search, budget, status, history, scam_check) never need it.

**C17. Protected dollars** (Vraj; relay `GET /wall/data/protected`), computed from the ledger since the last reset:
- `dollars`: declined `card_decision` amounts with reason `card_blocked_category`, `card_cooldown` or `card_unusual_amount`, plus refused checkout totals where the refusal came from the screen, the judge or a blocked category, plus the `amount` of `scam_checked` events with verdict `scam` (Rohan extracts it from the story).
- `scams_stopped`: the count of scam checks and refusals.
- `card_declines`: the count of declined swipes.

**C18. Store names everywhere come from `contracts/merchants.json`:**
- Python: `common/merchants.py`.
- Station: a Vite JSON import, like `lines.ts` does for `ai/prompts`.
- Caregiver app: extend `scripts/copy-design.mjs` to copy the registry into `lib/`.
- No new hard-coded "Corner Market" anywhere.

**C19. New line keys** (Rohan writes en, es and hi; Manush speaks them; slots in braces):

| Key | Line (English) |
|---|---|
| `card_declined_blocked` | "I stopped a {amount} charge at {store}. Your card never pays that kind of store. If someone asked you to buy gift cards or send money, that's a scam." |
| `card_declined_cooldown` | "I stopped a {amount} charge at {store}, because of the scam call earlier. If it's real, Priya can allow it once." |
| `card_declined_over_cap`, `card_declined_unusual`, `card_declined_atm` | One sentence each, with "Priya can allow it once" |
| `card_allowed_once` | "Priya allowed that charge once. Please try the card again." |
| `cooldown_on` | "For the next day I'll take extra care with your card." |
| `bill_due`, `bill_past_due`, `bill_paid` | Move from the station's built-ins into the files |
| `refund_not_allowed_bill` | "A bill payment can't be returned. If something is wrong with the bill, Priya can call Peachtree Power." |
| `receipt_done`, `receipt_on_screen`, `order_ready` | Take `{store}` and `{pickup}`. `{pickup}` is empty for bills. |
| `line_pin_ask`, `line_pin_wrong` | The phone PIN lines |

---

## 4. Manush: Ruth's station and the line

### V6-1. The station as a kiosk (9:15, 40 min)

- **Shopper view by default.** Operator view only with `?operator` (flip `main.ts:135`). Hide the view toggle (`index.html:14`) in shopper view.
- **Move behind `.dev`** (visible in operator view only):
  - The status line (`#status`, e.g. "Token received…", "WebSocket error…")
  - The raw rule banner (`ui.ts:146-157`)
  - The order and decision ids in the outcome box (`ui.ts:238`)
  - The receipt ids and "Paid in the Visa sandbox" (`ui.ts:304`, `receipt.ts:149`)
  - "sandbox processor stub" in refund notices (`agent.ts:1545`)
  - "(fallback items…)" (`ui.ts:166`)
- The typed input stays visible, since it's the loud-room fallback. Its placeholder becomes the language-neutral "Type here".
- **One state, in words:** "Press and hold to talk", "Listening…", "Checking…", "Asking Priya…", "Protected". Drop the raw state pill.
- **Design tokens.** Map `style.css` onto `design/tokens.css` (`--ch-*`) or stop linking it. Right now tokens.css loads after style.css and makes `--ok` dark green on a dark background. Ruth's text is 28–40px.

### V6-2. The Protected moment (10:00, 30 min)

A full-screen card, not the inline notice (`agent.ts:824`, `1399`), for three moments: a scam refusal, a `scam_check` with verdict `scam`, and a card decline (V6-5).
- A shield icon and one sentence in Ruth's language, the `say` text or the line.
- "Priya has been told" with a check mark, and the one action ("Please hang up").
- **Protected** is green. **Be careful** (`unsure`) is amber. **Never alarm red**: older adults read red as their own mistake.
- Dismissed by the next button press, and posted to the ledger as before.

### V6-3. Cart by store, read-back by store (10:15, 30 min)

- `CartLineView` gets `store` (from the `search_catalog` result's `store`/`merchant`), and `ui.cart` groups lines under store names.
- `readBackSay` (`cart.ts:295`) names the stores: "From Parkside Pharmacy: Lisinopril, eight dollars. From Peachtree Power: your bill, eighty-six forty. Total ninety-four forty. Shall I?"
- Checkout sends each line's `merchant`. Stop forcing `priced(VOICE.merchant)` (`agent.ts:1295`) as the only store.
- Several receipts **stack** (one per store's `paid`) instead of replacing each other.

### V6-4. Store-aware receipts (10:45, 25 min, with Vraj's X6-6 data)

- `receipt.ts:69/72/87/90` and `station/printer.py:133/184/225/639` take the store name and pickup from the receipt (C18), with no Corner Market fallback.
- A bill prints "Paid to Peachtree Power · account …0098" and no pickup line.
- The spoken receipt uses `receipt_done` with `{store}` and `{pickup}` (C19).

### V6-5. Card events at the station (11:10, 30 min)

- Subscribe to `card_decision`, `card_hold_released`, `risk_changed`, `mandate_paused` and `mandate_resumed`. Add them to the `RelayStream` types at `agent.ts:308` and `1862`.
- **Declined swipe:** speak the matching `card_declined_*` line (`speakFixed`, never through the model) in Ruth's last language, and show the Protected card with the store and amount.
- **`card_hold_released`:** speak `card_allowed_once`.
- **`risk_changed` (cool-down on):** a calm banner, "Extra care on your card until 9:05pm tomorrow", and `cooldown_on` spoken once.
- **Paused:** a banner "Priya has paused shopping". Checkout isn't offered.

### V6-6. Ruth agrees by voice (11:40, 20 min, with Dhruv's D6-7)

- On `mandate_signed`, the station reads the rules in plain words ("Priya set your rules: up to $60 a trip at your four stores…") and asks, "Do you agree?".
- On a yes turn, `POST /mandate/cosign` (C13) with her words.
- The wall and Priya's app then show "Ruth agreed by voice".

### V6-7. Line hardening (in gaps; timebox 45 min) (**Fix F11, F13**)

- **PIN.** Add `verify_pin` and the refusals from C16. Tell the Builder persona to ask for the PIN before any purchase. The PIN is not the token.
- **Trim `call.heard`** after a `scam_check` verdict and after a checkout, like the station's `requestStart`. A scam story must not refuse a later honest purchase.
- **Read-back gate:** `checkout` needs a new `ruth_said` after `read_cart`.
- **Destructive tools** (cancel, refund) never use the 120 s fallback call. They need an explicit `call_id` or `order_id`.
- **Post `line_call`** `{phase: started|ended, from_last4?}`.
- **README:** say 120 s, describe the PIN, and don't include the number.
- **Make one real call** (Builder preview, then dial). Write down each tool that ran and the times in `line/README.md`.

### V6-8. Station fixes (**Fix F12**)

- Tick during the typed-input screen wait.
- Clamp a bill's quantity to 1.
- `toolScamCheck` resets `requestStart`.
- Upgrade a partial-screen `refuse` to `scam_check` when the final transcript is a story.
- `asking_priya` reads the approval's `reason` when the judge was unavailable.

---

## 5. Rohan: the Ask guard, lines and evidence

### R6-1. Radar timing and cache (9:15, 40 min) (**Fix F7, F8**)

- **One budget end to end: 11 s.**
  - Run the facts (biller, orders, contacts) **concurrently** with Grok, and give Grok whatever is left.
  - The station and line give up at 14 s; keep that.
  - A Grok answer that arrives late is **cached** for the next check of the same story.
- **Cache:**
  - The per-story key keeps the full `say`.
  - The **per-pattern** fallback returns only the generic line for that pattern, never another story's details.
- **`say` length:** at most 2 short sentences and 30 words, validated. If it's longer, use the fixed `scam_check_scam` line and keep Grok's sources.
- **`amount`:** pull a dollar amount from the story ("2000 dólares", "$480", "दो हज़ार") into the check's `amount`, for the protected counter (C17).

### R6-2. Narrower story markers (10:00, 25 min) (**Fix F9**)

- A story routes to `scam_check` only with a **contact cue** (called, texted, emailed, pop-up, "a man said", "the caller") **and** a money or payment ask.
- Bare "someone" or "somebody" isn't a contact cue.
- "Buy a $100 gift card for someone at church" stays a plain gift-card refusal: the `blocked_category` line, Priya alerted, **no** "hang up" and **no** cool-down.
- Add these as tests, alongside the grandparent and power-company true positives in en, es and hi.

### R6-3. One alert, a real "Why?" (10:25, 30 min) (**Fix F6, F10**)

- Save each scam check as a decision document with a `decision_id`, and carry it on `scam_checked` and `caregiver_alerted`.
- `/decisions/{id}/explain` answers from the story, verdict, pattern and sources, in plain words with no rule ids.
- `GET /scam-checks` (C13), and the caregiver marker on `GET /scam-check/{id}`.
- **One alert per refusal.** Policy's `caregiver_alerted` is the alert; the station's `refusal` is a ledger row. Tell Dhruv, so the Safety feed shows alerts only.

### R6-4. Lines and clips (10:55, 40 min)

- Add every C19 key in en, es and hi, and update `LINES.md` and the parity test.
- **Store-aware receipt lines:** `receipt_done` and `receipt_on_screen` use `{store}` and `{pickup}`; `order_ready` uses `{store}`; points use the store's program name, or drop the store name.
- **Clips** for the demo lines (`python -m ai.render_clips --only …`):
  - `scam_check_scam`
  - `card_declined_cooldown`
  - `card_declined_blocked`
  - `card_allowed_once`
  
  Spanish in carina; English and Hindi in ara.

### R6-5. Eval (11:35, 25 min)

- Scripts for the six new families (utility shut-off, safe account, crypto ATM, courier, grandparent secrecy, remote access), in en, es, hi and Hinglish.
- Hard negatives: outage talk, paying bills, grandson visits.
- Run rules plus judge, and update `RESULTS.md`.
- Radar latency p50 and p90 over 10 live calls, plus cost per check. These numbers go in the Devpost.

### R6-6. Validation (in gaps)

- 10 more interviews (15 total) in `internal/validation.md`.
- Three quotes with first-name consent, and the two numbers for the Devpost ("N of 15 have a relative who got a scam call this year"; "N would set this up").

### R6-7. Landing page copy (12:00, for Phase 7)

`internal/landing_copy.md`:
- Hero line.
- The before/after of `PRODUCT_V2.md` 2.2, in 3 steps.
- The four guards.
- For families ($14.99/mo) and for banks (Visa Transaction Controls).
- The numbers with sources.
- "What Senior Sentinel can't do".

Dhruv builds the page in Phase 7.

---

## 6. Dhruv: Priya's app and the Family guard

### D6-1. App shell (9:15, 30 min) (**Fix F2**)

- **Bottom tabs:** Home, Safety, Approvals, Activity, Rules. Badges on Safety and Approvals.
- If the `cg_session` cookie is valid, skip Welcome (today it always starts at `"welcome"`, `page.js:102`).
- Components on `design/tokens.css`: button, card, pill, banner. Replace the inline styles in `styles.js`.
- **Remove** the footer (`page.js:475`) and the status line (`page.js:476`). Use a short toast instead.
- Money through `Intl.NumberFormat("en-US", {style: "currency", currency: "USD"})` everywhere, including History (today raw).
- "Call Ruth" uses `RUTH_PHONE` from the app config, not the hard-coded number at `Home.js:30`.

### D6-2. Home (9:45, 25 min)

- **Status hero:** "Mom is protected". During a cool-down: "Extra care on her card until 9:05pm tomorrow", with **Clear** (`/api/risk/clear`).
- **This month:** spend by store, as bars in store names (C18), and the budget left.
- **Protected** (C17): dollars stopped, scams stopped and card declines.
- **This week** digest: errands done, bills paid, attempts stopped. Quiet, no buzz.

### D6-3. Safety tab (10:10, 30 min)

- **One feed:**
  - Scam checks: story excerpt, verdict in plain words, pattern as words not slugs, **sources as links**, time, **Why?**
  - Refusals, with Why?
  - Card declines: store, amount, reason.
- The alert stream adds the C14 types. Alerts come only from `caregiver_alerted` (R6-3), so each refusal shows once.
- Beep and vibrate only for a scam, a decline or an approval. Normal purchases stay quiet.

### D6-4. Approvals tab (10:40, 25 min) (**Fix F1**)

- **Agent approvals:** items grouped by store, the amount, the reason ("over $40", or "the safety check was unavailable"), a countdown, **Approve with passkey or SPC**, and **Reject with a note**.
- **Fix F1:** the SPC `payeeName` comes from the approval's store names, and the decide route checks it against the approval rather than a fixed string.
- **Card holds** (`/api/card`): store, amount and reason, with **Allow once (10 min)** and **Keep blocked**. A `card_blocked_category` hold shows "Gift cards stay blocked" and no Allow button (policy refuses it with 409 anyway).

### D6-5. Activity tab (11:05, 20 min)

- Orders per store with formatted money and status in words (not raw ids or `awaiting_payment`). Bills are their own rows. Refunds show the card last 4.
- Cancel for unpaid orders, as today.

### D6-6. Rules tab (11:25, 25 min)

- **Stores as toggles** from the registry (C18), with the categories that follow, the limits and the blocked categories.
- Card rules in plain words ("Gift-card shops, crypto, wires: always blocked. Drugstores: up to $80…").
- Trusted contacts.
- `rulesSentence` is built from the mandate's stores and categories (**Fix F2**).
- **Co-sign status:** "Ruth agreed by voice at 11:52pm", or "Waiting for Ruth". Signing new rules asks Ruth again (V6-6).

### D6-7. Co-sign in policy (11:50, 15 min)

`POST /mandate/cosign` and the `cosign` field on `GET /mandate` (C13), plus the `cosigned` event, with tests.

### D6-8. Card and policy fixes (in gaps) (**Fix F3, F4, F5**)

- The registry store name on `card_decision`.
- The real mandate id on `allow_hold`.
- `VISA_STORES` from `common/merchants.py`.
- `python -m policy.card_setup` (F4).
- The 403 tests (F5).

### D6-9. Onboarding polish (Phase 7 if short on time)

Welcome, then passkey, then rules in plain words, then Sign, then "Now Ruth agrees at her station".

---

## 7. Vraj: the terminal, the Trust Ledger and Visa

### X6-1. Card terminal (9:15, 45 min)

The relay serves `GET /terminal` (LAN only). It's a tablet page that looks like a store's card reader:
- A store picker from `card_terminal_stores`: Five Points Drug, Corner Market, GiftCard Kiosk and Coin ATM.
- An amount keypad with presets ($20, $45, $480).
- A big **Tap card** button that calls `POST /host/api/swipe` (C15).
- A full-screen result: **APPROVED** in green, or **DECLINED** in neutral dark with the plain reason. Show the ms.
- The last five swipes, and the "Visa VTC: decline" badge from `vtc_decision` when it arrives.
- This is the physical prop at the table: the judge taps it.

### X6-2. Visa card-controls mirror (10:45, 40 min)

- On `mandate_signed` (and at startup), mirror Ruth's card rules to her Visa Transaction Controls test PAN:
  - The global per-swipe threshold from `card.default_cap`
  - ATM from `atm_daily_cap`
  - E-commerce
  - Gambling blocked
- After each swipe decision, **off the synchronous path**, call `/vctc/validation/v1/decisions` with the same amount and MCC. Post `vtc_decision` (C12).
- Errors never block a swipe; log them and move on.
- The certs are in `keys/visa/` on the services laptop.

### X6-3. Decision Manager per agent order (9:55, 30 min)

- At order creation, call `/risk/v1/decisions` on that store's own account, asynchronously with a 2 s budget.
- Put `risk_score` and `status` on the order and post `risk_scored` (C12). The wall and session page show "Visa risk score 32 · accepted".

### X6-4. Trust Ledger (the wall; 11:25, 60 min) (**Fix Phase 5 F20**)

- **Header:** "Senior Sentinel · Trust Ledger · Visa sandbox". No "Corner Market", and no fake `$142.10` fallback (`wall.html:72`, `245`).
- **Protected-dollars counter** (C17), big.
- **Four lanes:**
  - **Ask:** scam checks with verdict and sources.
  - **Card:** decisions, holds, allow-once, VTC badges.
  - **Agent:** orders per store, with signature checks, DM scores and payment links.
  - **Family:** approvals, mandate signed and co-signed, pause.
- **Plain-English rows.** Raw ids go in an expandable detail. Every new type from C8 and C12 has a summary; none shows as a bare type name.
- **The mandate card** comes from `GET /mandate/visa` (Visa's `mandates[]` shape), with a "signed by Priya · agreed by Ruth" badge.
- Uses the design tokens.

### X6-5. Session page (in gaps) (**Fix F15**)

- SSE or a 30 s refresh instead of `meta refresh=5`.
- `TITLES` (`session_view.py:14-33`) covers the new types.
- Per-store orders and bills.
- No "Corner Market" in the header.
- The dispute record includes card decisions and scam checks.

### X6-6. Merchant fixes and the protected route (10:25, 30 min) (**Fix F14**)

- The receipt carries the `store` name and `pickup` (none for bills; C18 and C19).
- `bill_checked` only when `bill_status` is asked, never on price lookups.
- The biller uses the order decision's mandate `account_ref`.
- Gift cards move to `quickgift_cards`, so the blocked store's 403 is real.
- `store=home` is an alias.
- Webhook keys per account.
- Points get their own receipt row.
- `GET /wall/data/protected` (C17).

---

## 8. Merge at 10:45, and the integration run at 12:00

**10:45:** push your branches. I merge in the order Vraj, Dhruv, Rohan, Manush, fix the seams, run every test and a live smoke on spare ports, and push main. Pull main after the check-in.

**12:00–12:30 on the services laptop** (reset from `/host` first; reopen the phone page after restarting). Write down the time for each step:

1. **Grandparent opener** (the judge reads the card; es, then en):
   - The Protected card appears and the verdict is spoken.
   - Priya's Safety tab shows the sources and Why?
   - The cool-down banner shows at the station and on the wall.
2. **The store:** tap $480 at Five Points Drug.
   - DECLINED; the station speaks `card_declined_cooldown`; the VTC badge shows.
   - Priya taps Allow once; the station says `card_allowed_once`; the retry is approved.
3. **Gift-card kiosk:** $50 is DECLINED, and the hold shows "stays blocked".
4. **Everyday:** "Order my blood pressure medicine and pay my power bill".
   - The read-back names both stores, and two real Visa links are created with DM scores.
   - One Host press pays both, and two receipts print. The bill has no pickup.
5. **Return beat (Visa):** "I want to return the bread" (buy bread first if needed).
   - Refund `PENDING` then `TRANSMITTED`, and "a bill can't be returned" for the bill.
6. **Phone:** dial the number, give the PIN, and tell the Peachtree Power story. Hear the verdict; `line_call` shows on the wall.
7. **The wall:** the protected counter, all four lanes, and the mandate "signed by Priya · agreed by Ruth".

Anything past 10 minutes of debugging goes on the whiteboard as a Phase 7 task.

---

## 9. What follows

| Phase | Window | Goal |
|---|---|---|
| **7. Integrate, polish, rehearse** | 12:30–3:00am | Landing page (Dhruv, from Rohan's copy); demo runbook and line cards rewritten for the new demo; re-record cached sessions; 10 rehearsals; judges dial the line; loud-room test; freeze at 3:00 |
| **8. Ship** | 3:00–5:30am | Video (before/after, then the table demo); Devpost in each judge's words with real vs. simulated labeled; README with the four guards; remove `internal/`; make the repo public; submit (check F17 for the deadline) |
| **9. Expo** | 7:00–11:15am | Table: station, terminal tablet, phone for the line, Priya's phone, printer, wall |

---

## 10. Sources

- The Phase 5 reviews and today's survey of main, in this conversation. File and line references are as of commit `d3e7c30`.
- `PRODUCT_V2.md` (the four guards, the demo, the business).
- `PHASE5_PLAYBOOK.md` (contracts C1–C11; Lithic, xAI, Cybersource and VTC API details, with their sources).
- `docs/visa-probes.md` (Decision Manager and VTC results from the Visa sandbox).
- `line/README.md` (Builder hookup).
