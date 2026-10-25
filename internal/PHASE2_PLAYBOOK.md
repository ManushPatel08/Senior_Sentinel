# Senior Sentinel: Phase 2 Playbook

As of 2026-09-26, 1:30am

`BUILD_PLAN.md` names Phase 2 "the purchase path" (Saturday 6am to noon). Its exit is one real purchase end to end at noon, with "signature verified" on the wall and a printed receipt. Most of that path already runs.

**Working at 1am on main (1dad048), on real services:**
- **Voice:** Grok Voice in Hindi, the rule screen, catalog search through the shopper's profile, the read-back gate, and checkout.
- **Policy:** R0-R7 with the real Grok judge. Policy signs the order and the merchant verifies it with all five checks green.
- **Payment and ledger:** a real Cybersource sandbox Pay by Link, the signed payment callback, the ledger and the wall.
- **Refusal:** the Hindi gift-card line gets its refusal clip 104 ms after the button is released.

**Still missing for the noon run:**
- the printed receipt,
- the caregiver approval loop,
- a real signed mandate,
- the session page behind the receipt's QR code,
- cached sessions,
- reset.

The branch reviews and the live runs also left about forty open fixes. Every one of them is folded into its owner's section below and marked **Fix**; security fixes come first.

Dhruv and Vraj are awake until 5am, so their Phase 2 starts now. Manush and Rohan start at 6am.

---

## 1. Phase 2 at a glance

| Time | Manush (station) | Dhruv (policy, mandate, caregiver) | Vraj (merchant, relay, wall, Visa) | Rohan (screen, judge, lines, eval) |
|---|---|---|---|---|
| Now-5am | asleep from 2 | Security fixes D-F1 to D-F5; the approval loop in policy (B1) | Webhook and decision fixes F1 to F3; the receipt endpoint (B5); the session page (B1) | asleep from 2 |
| 5am | | Hand-off note in `#chaperone`; sleep 5-9 | Hand-off note; sleep 5-9 | |
| 6-9am | Fixes V1 to V7; approval wait (B1); paid to receipt (B2, B3) | asleep | asleep | Fixes R1 to R9; spoken lines per language (B1) |
| 9:00 | Standup (all four), merge to main, pull | | | |
| 9-11am | Printer on the station laptop; cached sessions (B4); reset key (B5) | Caregiver approval UI (B2); real signed mandate (B3); remaining fixes | Host page (B2); reset fan-out (B4); wall per the D2 payloads (F8); the router move (B6) | End-to-end false-refusal run (B2); native-speaker review (B3); line cards (B4) |
| 11:15-12:00 | Noon rehearsal (Section 8), all four | | | |
| 12:00 | Exit check (Section 9) | | | |

**Pass conditions at noon (binary, each run once in Hindi and English, with Spanish through the typed box):**
1. The gift-card line is refused with the clip in under 1 s. The phone shows the alert within 2 s, and the wall shows the rule.
2. Medicine and bread go through: read back, "yes", signed, verified (five checks), payment link, paid, and **a receipt printed within 5 s of `paid`**. Scanning its QR code with a phone that is not on our network opens the session page.
3. A $49.95 cart goes to the caregiver. The phone shows the amount and the shopper's words, and a passkey approval turns it into an order, then paid, then a receipt.
4. A second cart over $40 left unanswered holds after 90 s, and the agent says so.
5. Reset takes under 15 s and leaves a clean wall, a new session and spend back at $142.10.
6. The mandate on the wall says "signed by passkey" (the `MANDATE_UNSIGNED_OK` flag is off).

**Git after the history rewrite.**
- Branch fresh from the current main (`git fetch && git checkout -B <you>/p2 origin/main`).
- Nobody pushes a branch created before 1:15am.
- Everyone who uses Claude Code has `{"attribution": {"commit": "", "pr": ""}}` in `~/.claude/settings.json`.
- Commit messages describe the code change only.

---

## 2. Measured tonight, and what is missing

**Numbers** (write them into the Devpost evidence as they firm up):

| Measure | Result |
|---|---|
| Release to first audio, voice turns | 826-1065 ms, n=4 |
| Release to refusal clip | 104-352 ms |
| Screen call | about 40 ms |
| Checkout to payment link | 3.3-5 s: about 2 s for the Grok judge plus about 1 s for the Visa link |
| Merchant checks | 5/5 green |

| Area | Missing or broken | Owner |
|---|---|---|
| Receipt | Nothing prints. No receipt data endpoint, no trigger on `paid`, no tablet fallback | Manush (print), Vraj (data) |
| Approval | Policy has only a stub `GET /approvals/{id}` and a code route that never places the order. The station sets `waitingForCaregiver` and never checks again. The phone shows raw alert text with no approve or reject | Dhruv, Manush |
| Mandate | Runs unsigned on `MANDATE_UNSIGNED_OK=1`. Policy trusts the public key inside a posted mandate | Dhruv |
| Session page and QR | The relay's `/sessions/{id}` is JSON only, and nothing public serves it | Vraj, Dhruv |
| Cached sessions, reset key | Neither built | Manush, Vraj |
| Wall | Blank detail on `cart_updated` and `request_signed`. Five "heard" lines per sentence. `policy_decision` twice | Manush, Vraj, Dhruv (D2) |

---

## 3. Cross-lane decisions (Dhruv and Vraj settle them now; Manush and Rohan read them at 6am)

| # | Decision | Owner |
|---|---|---|
| D1 | **Approval contract.** `GET /approvals/{id}` returns `{approval_id, state, expires_at, amount, merchant, excerpt, rule, decision_id, order}`. `state` is `pending`, `approved`, `rejected` or `expired`, and expiry is computed on read, 90 s after creation. `POST /approvals/{id}/decide {approved, response}` takes a passkey assertion (`AuthenticationResponseJSON`) over `SHA-256(JCS({approval_id, amount, merchant, nonce, expires_at}))`, with `nonce` = 16 random bytes in base64url. On approval, policy signs and sends the order with `approval_id` set and stores it on the approval. The station polls `GET /approvals/{id}` every 1 s over the LAN (no tunnel quota involved). Events: `approval_requested` and `approval_result {approved, method: "passkey" or "code" or "timeout"}` | Dhruv (`contracts/approval.schema.json`) |
| D2 | **Event payloads the wall renders** (the wall ignores anything else). One `heard` line per spoken turn: the wall replaces the line with the same `item_id`. `policy_decision` comes from policy only; the station stops posting it. Per-type payloads in the table below | Vraj (`contracts/events.schema.json`), Manush, Dhruv |
| D3 | **Receipt.** `GET {merchant}/orders/{id}/receipt` returns `{merchant, items: [{name, qty, price}], total, pickup: "after 3pm", order_id, decision_id, paid_at, session_url, lang}`. The station prints when it sees `paid` for its session on the relay stream (`/events/stream?session_id=`), then posts `receipt_printed`. Printing goes through a helper on the station laptop, `station/printer.py` on `127.0.0.1:8004` (new port; add it to `ports.md`); see Section 4a | Vraj (endpoint), Manush (print) |
| D4 | **Public session page.** `https://<tunnel-host>/s/<session_id>`, served read-only by the caregiver app from the relay's HTML session view. It is the only new public path. Remove the raw `/relay/events/stream` rewrite: it exposes every transcript to anyone with the tunnel URL | Dhruv (route), Vraj (HTML view) |
| D5 | **Reset.** Relay `POST /reset` fans out to policy (spend back to 142.10, decisions, approvals, the screen's session memory), the merchant (orders) and the relay's own live ledger. It then posts `reset`, and the station answers with a new session id and a cleared cart and gate. Under 15 s | Vraj (fan-out), Dhruv (policy), Rohan (screen), Manush (station) |
| D6 | **Host controls stay off the wall.** A LAN-only relay page `/host` holds Confirm payment, Reset, Arm replay and the six-digit fallback code. Approval codes never go into the ledger or the stream, because the stream is visible on the table | Vraj |

**D2 payloads, one row per event type:**

| Type | Payload |
|---|---|
| `heard` | `{role, text, lang, item_id}` |
| `items_found` | `{query, items: [{sku, name, price}]}` |
| `cart_updated` | `{lines: [{sku, name, qty, price}], total}` |
| `checkout_requested` | `{total}` |
| `refusal` | `{rule_id, rule_ids, spoken_key, lang}` |
| `policy_decision` | `{decision, decision_id, rules_failed, total}` |
| `request_signed` | `{keyid, nonce, expires}` |
| `approval_requested` | `{approval_id, amount, rule, expires_at}` |
| `approval_result` | `{approval_id, approved, method}` |
| `receipt_printed` | `{order_id, via: "printer" or "screen"}` |
| `paid` | `{order_id, total, via}` |

---

## 4. Manush: station, 6am to noon

**Fixes (first hour).**
- **V1** After a partial refusal, still screen the final transcript with `partial: false` and ignore the answer. Rohan's repeat-attempt memory only records non-partial refusals. The `.completed` branch in `src/agent.ts` skips the screen once `screenResult` is `refuse`.
- **V2** Post events in the D2 shapes. `cart_updated` sends `lines` and `total`, not `{cart, version}`; `refusal` sends `rule_id`; `items_found` sends `items`. Add `item_id` to `heard` so the wall shows one line per turn, and delete the station's own `policy_decision` post.
- **V3** Add Rohan's `blocked_category`, `scam_pattern` and `code_reading` keys, and policy's `over_monthly_cap`, to the `SAY` table in `src/cart.ts`. Once Rohan's line files land, load the texts from them (Rohan B1).
- **V4** In `runTool`, check `this.cancelled` again after `awaitScreen` returns (it can wait up to 1.5 s), so a barge-in during the screen wait cannot still check out.
- **V5** Count a turn toward `userTurns` (the read-back "yes") only once its transcript is non-empty. Today an empty or noise press arms the gate.
- **V6** Bring `tests/mock_realtime.py` back to the contracts. `spoken_key: "blocked_gift_card"` should be a real key, `refusal.gift_card.es.mp3` should be a real clip, and `expires_at` should be an ISO string.
- **V7** After a refusal, the longer transcript that arrives later shows up as a new line. Update the turn's existing line instead.

**Build.**
1. **Waiting for the caregiver** (FR-21, D1). On an `approve` reply:
   - Say the `asking_priya` line, then poll `GET {policy}/approvals/{id}` every 1 s for up to 95 s.
   - `approved` with an order: say `ordering_now` and carry on to paid and the receipt.
   - `rejected`: say the caregiver's message, or `caregiver_declined`.
   - `expired`: say the `caregiver_timeout` line ("Priya did not answer; I have kept your cart") and keep the cart.
   - The button stays live. A new request cancels the wait and returns to the read-back.
2. **Paid to receipt** (FR-5, D3).
   - Open an `EventSource` on `{relay}/events/stream?session_id=<id>`. It is same-origin through the Vite proxy; add `merchant: 8002` to the proxy in `vite.config.ts`.
   - On `paid` for this session: fetch `{merchant}/orders/{id}/receipt`, print it (Section 4a), post `receipt_printed`, and speak the fixed receipt line in the shopper's language through `force_message` (no `response.create` after it).
   - If printing fails or takes over 5 s, show the receipt full-screen in large type and post `via: "screen"`.
3. **Receipt layout.**
   - Store name, each item and price, the total, "Pickup after 3 pm", the order and decision ids in small type, and "Paid in the Visa sandbox. No real money."
   - A QR code to `https://<tunnel-host>/s/<session_id>`.
   - Item lines and the total at about 24 pt, in the session's language.
4. **Cached sessions** (FR-8).
   - During the 9-11am rehearsals, record one full two-outcome session per language. Save every `response.output_audio.delta` (the PCM is already in hand), each transcript line and tool event with its offset in ms, and the refusal clip name, to `sessions/cached/<lang>.json`, which is gitignored.
   - Replay mode, a Host shortcut (for example Ctrl+Shift+P), plays it through the same player and drives the screen. Show **REPLAY** in large type and post events with `replay: true` so the wall labels them.
   - It never replays the purchase itself. Policy, signing and the ledger run live.
5. **Reset key** (FR-39, D5). Ctrl+Shift+R, or the relay's `reset` event, gives a new session id and clears the cart, gate, transcript and screen. Under 15 s including the relay fan-out.
6. **Printer on the station laptop.** Install the driver, print a Windows test page, set the paper to 58 mm, and keep the tablet as the fallback. Section 4a has the exact steps.
7. **Numbers.** Record the median release-to-first-audio over 10 voice turns per language in `station/config/voice.json` `measured`.

### 4a. Printing the receipt

**Decision: a small Python print helper on the station laptop.** `station/printer.py` is a FastAPI app on `127.0.0.1:8004` (port 8004 is new; add it to `ports.md`), reached through the Vite proxy as `/svc/printer`. It prints with `python-escpos` 3.1 through the Windows print queue in RAW mode (`Win32Raw`), with no driver swap.

It beat the alternatives because it is the only option that gives Hindi, large type, a QR code **and** a failure signal together:
- **Chrome silent printing** (`--kiosk-printing`) cannot report a failed print. `@page { size: 58mm auto }` is also invalid CSS.
- **Node `node-thermal-printer`** needs a native printer module that may not build on Node 22.
- **WebUSB** needs the printer's driver swapped for WinUSB through Zadig, after which the Windows queue stops working.

**Setup on the station laptop (30 minutes, once the printer is plugged in).** On Sep 26 at 1:40am this laptop had **no thermal printer installed**, only the PDF and OneNote queues. Confirm the printer is actually in hand.
1. Install the vendor POS-58 driver. If there is none: Add printer, then Add manually, then Local printer, port `USB001`, "Generic / Text Only".
2. `Rename-Printer -Name "<whatever it installed as>" -NewName "POS58"`. Queue names vary ("POS-58", "XP-58"), and another USB port can create a "(Copy 1)" queue, so always pass the name explicitly.
3. `pip install "python-escpos[win32]==3.1" qrcode` into the repo `.venv`. Pillow 12.2 is already there. Check that the unrelated `escpos` package is **not** installed, since it shadows `python-escpos`.
4. Check Hindi shaping: `python -c "from PIL import features; print(features.check('raqm'))"` must print `True`. On this laptop it already does, because `libfribidi-0.dll` is on PATH through the GTK3 runtime. On another laptop, put that DLL on PATH. `C:\Windows\Fonts\Nirmala.ttc` covers Devanagari.

**How the helper prints:**
- **Everything as an image.** Every line (English, Spanish, Hindi) is rendered by Pillow with the RAQM layout engine, in Nirmala UI at 60 px, onto a 1-bit image 384 dots wide. That width is the 48 mm printable area of 58 mm paper at 203 dpi. 60-70 px lines are about 24 pt.
- **No code-page problems.** Rendering to an image sidesteps code pages entirely: many clones default to Chinese double-byte mode and garble ñ and á in text mode, and ESC/POS has no Devanagari at all.
- **The rest of the receipt:**
  - The QR code: `p.qr(session_url, size=8, center=True)`, which prints as an image and so works on printers without native QR.
  - Four blank lines to tear against, because most POS-58 printers have no cutter.
  - Profile `POS-5890`.
- **Failure check.** Windows reports status only while a job is being sent, so an empty queue always looks "ready". Note the job id from `p.current_job`, call `p.close()`, then poll `win32print.EnumJobs` every 200 ms:
  - The job leaving the queue means success.
  - A status of error, offline, paper out, blocked or user intervention, or the job still queued after 4 s, means failure. Delete the job with `JOB_CONTROL_DELETE` and return `{ok: false}`.
  - Confirm the exact pywin32 dictionary keys on the real printer; the research agent could not test them.
- **Speed.** Rendering took 224 ms cold on this laptop. Printing is about 1.7 s for a 150 mm receipt at 90 mm/s. Load the fonts and imports at startup so the first receipt is not slow.

**Station side.** On `paid`, POST the receipt JSON (D3) to `/svc/printer/print`.
- `{ok: true}` within 5 s: post `receipt_printed {via: "printer"}`.
- Otherwise: show the same receipt full-screen in large type with the QR code, plus a **Reprint** button, and post `via: "screen"`.
- The receipt is **always** shown on screen as well, so the printer is a bonus, not the only copy.

**If Hindi shaping is missing on the day,** render the receipt on a 384 px canvas in the station page (Chrome shapes Devanagari itself) and POST the PNG, which the helper passes to `p.image()`.

**Done when.**
- The noon run's steps 2-4 print a receipt within 5 s of `paid`, and the QR code opens the session page on a phone using mobile data.
- A $49.95 cart waits, is approved on the phone, orders and prints.
- An unanswered one holds after 90 s.
- Reset gives a fresh session.
- `npm test` and the mock tests pass.

**Pitfalls.**
- `force_message` must not be followed by `response.create`.
- Your laptop is the station at the table. The printer driver belongs on it, not on the services laptop.
- Keep `EventSource` same-origin through the proxy so no CORS entry is needed.

---

## 5. Dhruv: policy, mandate and caregiver, now to 5am, then 9am to noon

**Fixes, security first (now to 3am).**
- **D-F1 Registration can be bypassed.** The expected challenge comes from the client's `wa_challenge` cookie, which is not signed, so anyone can mint their own challenge and register.
  - Keep challenges on the server, in a `Map` keyed by a random httpOnly session id. Each entry holds `{challenge, purpose: "register" or "mandate" or "approval", gatePassed, expires}`, is single-use and lasts 5 minutes.
  - `verify-registration` and `verify-authentication` read from the Map only.
  - The setup-code path read from `CAREGIVER_SETUP_CODE_HASH` must also expire after 10 minutes, be consumed on use, and allow 5 attempts.
- **D-F2 Anyone can post a self-signed mandate.** `policy/verify_mandate.py` checks the assertion against the `public_key` inside the posted mandate.
  - Pin the first caregiver credential policy sees, stored in `sessions/caregiver_credential.json`, and reject any other.
  - Check `credential_id == response.id`, and validate the body against `contracts/mandate.schema.json`.
  - The caregiver's `/api/mandate` forwards only after its own session check.
- **D-F3 Six-digit code.** `GET /decisions/{id}` returns the approval's `code_hash` and `nonce`, and six digits under an unsalted SHA-256 fall to brute force in under a second.
  - Serve a public projection without secrets.
  - Store `HMAC(server_key, code + approval_id)`.
  - Check `expires_at`, put a lock around the attempt counter, and write `decisions.json` atomically (write a temp file, then `os.replace`).
  - Show the code only on the relay's `/host` page (D6).
- **D-F4 Cart validation.** Reject qty below 1 or above 24 (the merchant's `MAX_QTY`) and an empty cart with 422. A negative line currently lowers the total under R4 and R6 and comes back `allow`. A `mandate_id` other than the active mandate's is also a 422: `checkout.py:106` takes the station's value today.
- **D-F5** Enforce `read_back === true` with 409 `read_back_required`. Today the gate exists only in the browser.

**Fixes, correctness and wall (3-5am, or 9-10am).**
- **D-F6** Skip the judge when R1 already fails (a blocked category). It adds up to 3 s to a refusal, and the PRD says blocked categories never reach it.
- **D-F7** The approval nonce becomes 16 bytes. `secrets.token_hex(8)` is 8, while `contracts/signing.md` says 16.
- **D-F8** `/reset` calls Rohan's `policy.screen.reset_sessions()` (D5), and `/budget` uses the stored mandate's cap, not `DEFAULT_MANDATE`.
- **D-F9 Alert stream.** Pass `request.signal`, and clear the upstream reader and the 15-second timer in `cancel()`. The phone reader needs reconnect with backoff, a 10-second safety poll, and a wake-lock re-acquire on `visibilitychange`.
- **D-F10** Remove the `/relay/events/stream` rewrite from `next.config.mjs` (D4).
- **D-F11** `instrumentation.js` breaks `next dev` with "Can't resolve 'crypto'". Use `if (process.env.NEXT_RUNTIME === "nodejs") { await import("./instrumentation-node.js") }` and move the setup-code call into that file.
- **D-F12 Events carry their details** (D2):
  - `request_signed` gets `keyid`, `nonce`, `expires`.
  - `policy_decision` gets `decision`, `rules_failed`, `total`.
  - `approval_requested` gets `amount`, `rule`, `expires_at`.
- **D-F13 Say keys and rules** (D2):
  - An R5 denial says `over_monthly_cap`.
  - A screen-based denial adds a failed `S_screen_<rule>` entry, so the ledger shows why instead of every rule passing.
  - R0's detail reads "unsigned (demo flag)" when unsigned.
- **D-F14 Blocking and lost updates.**
  - `events.py` posts on a background thread, or asynchronously, so 3-4 blocking posts no longer sit on each checkout.
  - A lock guards the monthly spend.
  - Checkout passes `today` to the engine.
- **D-F15 Tests:**
  - a judge error without a `judge` screen fails open;
  - R0 outside its validity dates;
  - the setup code expiring;
  - approve then order;
  - a replayed approval assertion rejected.

**Build.**
1. **The approval loop in policy (D1), now to 5am.**
   - Store the approval with its nonce.
   - `GET /approvals/{id}` computes the state.
   - `POST /approvals/{id}/decide` verifies the assertion with `webauthn.verify_authentication_response(...)`:
     - `expected_challenge` = the approval hash;
     - the pinned credential public key;
     - `credential_current_sign_count` = the stored counter; save `new_sign_count`;
     - `require_user_verification=True`.
   - On approval, `send_signed_order` goes out with `approval_id` and the same store-before-send order as checkout. Post `approval_result`.
   - The code route (D-F3) reaches the same end state with `method: "code"`.
2. **Caregiver approval page** (FR-20 to FR-22, 9-11am).
   - An `approval_requested` alert opens a full-screen card: amount, merchant, the shopper's words, the rule, and a 90-second countdown.
   - **Approve with passkey**, **Reject** and **Call Ruth** (`tel:`).
   - Approve fetches the approval, builds the same JCS object, and calls `startAuthentication({ optionsJSON })` with that challenge and `allowCredentials` set to Priya's credential, then posts the result through a server route to policy `decide`.
   - Show the amount in large type right above the button, because the passkey prompt does not show it.
   - **Stretch, not before noon: Secure Payment Confirmation (SPC).**
     - SPC shows a browser-native dialog with the payee, the amount and the payment method before the biometric check, and signs exactly those values into `clientDataJSON`. That fixes "the passkey prompt does not show the amount".
     - Visa has shown usability tests of this exact Chrome Android dialog at the W3C, which makes it a strong Visa point.
     - Support: Chrome on Android (M109+), Windows and Mac. No iOS, Safari or Firefox. The spec is a W3C Candidate Recommendation, and no flag is needed.
     - Build:
       - Re-register Priya with `authenticatorAttachment: "platform"`, `residentKey: "required"`, `userVerification: "required"` and `extensions: { payment: { isPayment: true } }`. SimpleWebAuthn v14 passes extensions through; cast the TypeScript type.
       - Call `new PaymentRequest([{ supportedMethods: "secure-payment-confirmation", data: { credentialIds, challenge, rpId, instrument: { displayName: "Ruth's Visa (sandbox)", icon: <same-origin or data: URL> }, iconMustBeShown: false, payeeName: "Corner Market", payeeOrigin: "https://<tunnel-host>", timeout: 90000 } }], { total: { label: "Total", amount: { currency: "USD", value: "49.95" } } })`, then `show()` straight from the tap. Fetch the challenge before the tap, or Chrome may drop the user activation.
       - Serialise `response.details` by hand, because `startAuthentication` does not cover it, then call `response.complete("success")`.
     - Verify in the caregiver server with `verifyAuthenticationResponse({ ..., expectedType: "payment.get" })`. Then decode `clientDataJSON` and compare `payment.total`, `payeeName` and `payeeOrigin` with the stored approval: the library does not check them.
     - Python's `webauthn` 3.0.x only accepts `webauthn.get`. So either the caregiver server verifies and posts a signed result to policy, or policy checks the signature itself with `webauthn.helpers` (the COSE key decode and signature check exist there; confirm the names).
     - Detection: `PaymentRequest.securePaymentConfirmationAvailability()` (Chrome 139+). If it is not `available`, or `show()` rejects with `NotAllowedError`, use the plain passkey flow above with the same challenge.
     - Estimate 2.5-3.5 hours, all testing on the real phone. Timebox it to Phase 3 and drop it if the dialog is not working on the demo phone within the box.
3. **The real signed mandate** (FR-14, by 11am).
   - On the demo Android phone, through `https://<TUNNEL_HOST>` (production build: `npm run build && npm start`): register with the setup code, then sign the mandate.
   - Policy pins the credential and verifies the mandate.
   - Set `MANDATE_UNSIGNED_OK=0` on the services laptop, and check that the wall's mandate card says signed.
4. **Public session route (D4).** A `/s/[id]` page in the caregiver app fetches the relay's HTML session view server-side and returns it read-only, with no other relay access.

**Done when.**
- Registering without the setup code fails.
- A self-signed mandate is rejected.
- `/decisions/{id}` shows no code material.
- A $49.95 checkout creates an approval, the phone shows it within 2 s, and a passkey approval places the order.
- A rejection and a 90-second timeout each end the approval cleanly.
- The mandate is signed, and `pytest -q policy` passes.

**Pitfalls.**
- The approval challenge must be built from exactly the fields policy stored, in the same JCS form on both sides. Test the Python `jcs` and JS `canonicalize` bytes once.
- `startAuthentication` needs `{ optionsJSON }`.
- Keep the caregiver app on the production build through ngrok. The free tier allows 20,000 requests a month, and `next dev` spends them fast.

---

## 6. Vraj: merchant, relay, wall and Visa, now to 5am, then 9am to noon

**Human task (5 minutes).** Check the Cybersource case and the webhook subscription status (`PENDING_REVIEW` or active). If the processor is fixed, try one real hosted-page payment with `4111 1111 1111 1111`. Otherwise the Host's Confirm payment button (D6) is the paid step, and the Host says "marked paid in the sandbox flow".

**Fixes (now to 3am).**
- **F1 The webhook can mark the wrong order paid.** The signature covers only `payload`, but `merchant/orders.py:247` searches the whole envelope and `:251` reads `eventType` from the unsigned part. The reviewer showed a notification signed for order A marking order B paid.
  - Search and read only the signed `payload`.
  - Make duplicates idempotent: no second `mark_paid`, answer 200 with `duplicate: true`.
  - Sign the raw body for the primary variant, as the Cybersource docs specify.
  - Compare digests as bytes. `hmac.compare_digest` on a non-ASCII `str` raises and turns into a public 500.
  - Tests: a tampered envelope, a non-ASCII `keyId`, a replay.
- **F2 One decision, one order.** The smoke test re-signed an order with an already-used `decision_id` and got a second order. The merchant must refuse any later order for that decision with 409.
- **F3 Decision check.** Move `raise_for_status()` and `.json()` inside the `try` and raise `DecisionError`, so a policy 5xx no longer shows as a failed signature check. Use `httpx.AsyncClient` so the check does not block the event loop.
- **F4 Session ids.** Add the pattern `^[A-Za-z0-9_-]{1,64}$` to `events.schema.json` and reserve `live`. Session files move to `sessions/by-id/`, because `session_id: "live"` currently writes into `live.jsonl`.
- **F5 SSE.** Send the heartbeat based on time since the last write, not the last queue event. A filtered stream (the phone's) otherwise never gets one. When a subscriber's queue overflows, close the stream so the client reconnects with `Last-Event-ID`, instead of silently dropping events.
- **F6 Planning words.** Remove them from comments: "(fallback rung 3)" in `merchant/simulate_payment.py:6` and "FR-39" in `relay/ledger.py`.
- **F7 Catalog search.** "my blood pressure medicine" returns Cetirizine and Acetaminophen because the token "medicine" matches every OTC item. Down-weight generic tokens (medicine, pills, dawai, medicina) and prefer items whose group matches a profile phrase. The station already guards against this, but the catalog should not rely on it.
- **F8 Wall.**
  - Render the D2 payloads.
  - Replace `heard` lines by `item_id`.
  - Add `approval_requested` and `approval_result` lines with the countdown.
  - Show REPLAY on `replay: true` events.
  - Keep the merchant card in step with `paid` from the stream, not only from the 1-second poll.

**Build.**
1. **Session view (FR-37, now to 5am).** `GET /sessions/{id}?format=html`: large type, the transcript (one line per turn), every rule fired, signature id and nonce, the five checks, payment status, and the receipt. It must load in under 2 s. Dhruv's public route (D4) serves it.
2. **The `/host` page (D6), LAN only:**
   - Confirm payment for the latest awaiting order (calls `simulate_payment`).
   - Reset.
   - Arm replay (posts `replay_armed`, which Manush's station listens for).
   - The current approval's fallback code.
   - Keyboard shortcuts for each.
3. **Paid status.** If Cybersource fixed the processor, Confirm payment is not needed: the hosted page completes and the webhook (or the Host checking the Business Center) marks it paid. Keep both paths.
4. **Reset fan-out (D5).** Relay `/reset` calls policy and the merchant, truncates the live ledger, and posts `reset`. Time it end to end; it must be under 15 s.
5. **Receipt data (D3).** `GET /orders/{id}/receipt` in the shape D3 gives, with `session_url` built from `TUNNEL_HOST`.
6. **Network (9-10am).**
   - Move the services laptop to the team router at `192.168.8.10`.
   - Bind every service to `0.0.0.0`. `.claude/run.sh` on Manush's laptop uses 127.0.0.1, so on the services laptop use the README commands.
   - Allow ports 8000-8003 through the Windows firewall on the private network only.
   - Set `SERVICES_HOST=192.168.8.10` on the station laptop, and check each service from there.

**Done when.**
- The tampered-envelope test passes.
- A second order on one decision gets 409.
- A policy 5xx shows as a decision failure.
- The session page opens from the receipt QR code through the tunnel.
- `/host` confirms payment and resets.
- The wall shows one line per spoken turn with details.
- `pytest -q merchant catalog relay` passes.

---

## 7. Rohan: screen, judge, spoken lines and eval, 6am to noon

**Fixes (6-8am).**
- **R1 Hindi misses** (all verified to proceed today):
  - "गिफ्ट कार्ड्स" (plural), "गिफ्टकार्ड", "gift कार्ड";
  - "Google Play ka card", "गूगल प्ले का कार्ड";
  - "tarjeta regalo" without "de";
  - "card ke peeche ka number", because the Hinglish fold turns "peeche" into "piche" while the pattern expects "chh".
  - The fix: `re:(?:गिफ्ट|gift) ?(?:कार्ड|card)(?:्स|स|s)?`, the possessive forms, and a pattern that matches after folding.
- **R2 False refusals.**
  - "my Apple Card", "Target card", "Amazon card" and "Visa card" are real credit cards: require gift or prepaid context before a brand plus "card" is blocked.
  - Bare ओटीपी needs a verb next to it (batao, bolo, bhejo, share) before code-reading fires.
  - Tests: "मेरे वीज़ा कार्ड से, मेरा ओटीपी आ गया" proceeds; "pay with my Visa card… read me the numbers on the soup label" proceeds.
- **R3** Weak terms match only in their own language. The English "son" fires on Spanish "son las tres", and "mi hija viene hoy mismo" goes to the judge.
- **R4** "my Medicare card came" should be `proceed`, and the test should say so again. Bare `medicare` counts as authority only next to threat words.
- **R5 Eval leakage.**
  - `judge_examples.md` has near-copies of `hi_digital_arrest` and `es_seguro_social`, and two benign examples mirror test scripts. Rewrite the few-shot examples with different scenarios.
  - Score every language row on the held-out half only.
  - Re-run and update `ai/eval/RESULTS.md`.
- **R6 Judge robustness.**
  - Drop unknown patterns instead of raising (today an unknown pattern counts as "judge unavailable").
  - Enforce a hard 3-second total deadline, not per phase.
  - `/judge` accepts a cart as a list or a dict.
- **R7** `hits[].term` shows the original text that matched, not the folded form ("gugle play card", "fianja"), because the wall prints it.
- **R8 Housekeeping.**
  - Bound `_refused_sessions` (LRU or a TTL) and expose `reset_sessions()` for D5.
  - Remove "Phase 0 record" from `spikes/rohan/README.md` and the fix labels from the `test_screen.py` headers.
  - `spikes/rohan/tts.py` still reads deleted `refusal.{lang}.txt` files.
- **R9 The demo's second half.** After a refusal, policy now sends the judge the purchase that follows in the same session.
  - Pass a `history_summary` ("a gift-card request was refused earlier in this session").
  - Calibrate so an ordinary follow-up purchase scores low.
  - Run the demo sequence (refusal, then "medicine and bread") 10 times on the real model in Hindi and English; all 10 must allow.

**Build.**
1. **Spoken lines, single source**, in `ai/prompts/lines.<lang>.json` for es, hi and en.
   - Keys: `ordering_now`, `asking_priya`, `caregiver_approved`, `caregiver_declined`, `caregiver_timeout`, `receipt_done` ("Done. $X at Corner Market, pickup after 3 pm. I printed your receipt."), `checkout_unavailable`, `over_monthly_cap`, `read_back_required`.
   - Manush's `SAY` table loads these. Also render clips for `asking_priya` and `receipt_done` in the session voice (`carina` for Spanish, `ara` for Hindi and English).
2. **False refusals through the whole station.** Run the 20 benign scripts through the station's typed box end to end, not just the rules, and report the false-refusal rate with a Wilson interval next to the rules-only number.
3. **Native-speaker review.** Hindi wording by the team. For Spanish, ask the HackGT help desk or volunteers Saturday morning for a native speaker to read the refusal, approval and receipt lines once. Fix what they flag.
4. **Line cards for the table**, since none of us speaks Spanish. Three columns: English, Hindi (Devanagari with a romanized line under it), and Spanish with a pronunciation line under it. The gift-card line, the purchase line, "yes", and the $49.95 Ensure line. Two copies of each, printed.
5. **Numbers for Devpost.** Release to refusal audio (median of 10 per language), judge p50 and p90, the false-refusal upper bound, and the rules-only versus rules-plus-judge table.

**Done when.**
- `pytest -q policy/tests/test_screen.py` passes with every line from R1-R4.
- The demo sequence allows 10 of 10.
- `RESULTS.md` has held-out numbers.
- The line files are loaded by the station.
- The line cards are printed.

---

## 8. Noon rehearsal, 11:15am-12:00

Services laptop on the router. Station laptop with the button, mic, speaker and printer. Caregiver phone on the tunnel with alerts armed. Wall on the big screen. One teammate plays Ruth and reads from the line cards.

1. **Reset from `/host`.** New session; the wall is empty; spend is $142.10.
2. **Hindi gift-card line.** Refusal clip in under 1 s. The phone buzzes and shows the alert. The wall shows the rule.
3. **"Medicine and bread", then "yes":**
   - the read-back is exact;
   - the order is signed and passes all five checks;
   - a payment link comes back;
   - the Host presses Confirm payment and the order is paid;
   - the receipt prints within 5 s and the agent says `receipt_done`;
   - the QR code, scanned on a phone using mobile data, opens the session page.
4. **"Five Ensure shakes" ($49.95).** The agent asks Priya. The phone shows the approval card, Priya approves with her passkey, and the order goes through to paid and a receipt.
5. **Another cart over $40, left unanswered.** After 90 s the agent says the cart is held.
6. **Spanish through the typed box:** steps 2 and 3.
7. **Reset.** Under 15 s, timed.

Do not debug any one step past 10 minutes. Write it on the whiteboard; it becomes the first Phase 3 task.

---

## 9. Exit check at noon and what Phase 3 starts from

Read Section 1's six pass conditions aloud, then write down:
- the numbers,
- which fallback each step used (printer or screen, passkey or code, real paid or Host-confirmed),
- anything that failed.

Phase 3 (noon to 3pm) then only has to:
- harden the approval and refusal paths in the loud room,
- add the second language by voice,
- run the two-outcome loop cleanly.

Everything it depends on is built in Phase 2.

---

## 10. Sources

Pages opened on Sep 26, 2026. Items marked unconfirmed in the text were not in official docs.

**Receipt printing (Manush):**
- [python-escpos installation](https://python-escpos.readthedocs.io/en/latest/user/installation.html), [printers (Win32Raw)](https://python-escpos.readthedocs.io/en/latest/user/printers.html), [API](https://python-escpos.readthedocs.io/en/latest/api/escpos.html), [printer profiles (POS-5890)](https://python-escpos.readthedocs.io/en/latest/printer_profiles/available-profiles.html), [Win32Raw source](https://github.com/python-escpos/python-escpos/blob/master/src/escpos/printer/win32raw.py)
- [Pillow raqm and FriBiDi](https://pillow.readthedocs.io/en/stable/installation/building-from-source.html)
- [Nirmala UI](https://learn.microsoft.com/en-us/typography/font-list/nirmala-ui)
- [Windows printer and job status](https://learn.microsoft.com/en-US/troubleshoot/windows/win32/printer-print-job-status), [PRINTER_INFO_2](https://learn.microsoft.com/en-us/windows/win32/printdocs/printer-info-2)
- [ESC/POS DLE EOT](https://download4.epson.biz/sec_pubs/pos/reference_en/escpos/dle_eot.html)
- [XP-58 specification](https://manuals.plus/xprinter/xp-58iih-thermal-receipt-printer-manual)
- [CSS @page size](https://developer.mozilla.org/en-US/docs/Web/CSS/@page/size), [Chrome default printer policy](https://chromeenterprise.google/policies/print-preview-use-system-default-printer/)
- [node-thermal-printer](https://github.com/Klemen1337/node-thermal-printer)
- [WebUSB receipt printer](https://github.com/NielsLeenheer/WebUSBReceiptPrinter), [WebUSB](https://developer.chrome.com/docs/capabilities/usb)

**Secure Payment Confirmation (Dhruv):**
- [W3C SPC](https://www.w3.org/TR/secure-payment-confirmation/) and [editor's draft](https://w3c.github.io/secure-payment-confirmation/)
- Chrome docs: [SPC](https://developer.chrome.com/docs/payments/secure-payment-confirmation), [register](https://developer.chrome.com/docs/payments/register-secure-payment-confirmation), [authenticate](https://developer.chrome.com/docs/payments/authenticate-secure-payment-confirmation), [SPC on Android](https://developer.chrome.com/blog/spc-on-android)
- [SimpleWebAuthn SPC support](https://simplewebauthn.dev/docs/advanced/server/secure-payment-confirmation)
- [py_webauthn verify_authentication_response](https://raw.githubusercontent.com/duo-labs/py_webauthn/master/webauthn/authentication/verify_authentication_response.py)
- [securePaymentConfirmationAvailability](https://developer.mozilla.org/docs/Web/API/PaymentRequest/securePaymentConfirmationAvailability_static)
- [Visa SPC talk at W3C](https://www.w3.org/2025/Talks/visa-spc-20251110.pdf)

From the Phase 1 research, still current:
- xAI [speech-to-speech guide](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech) (`force_message`, resumption).
- SimpleWebAuthn [custom challenges](https://simplewebauthn.dev/docs/advanced/server/custom-challenges).
- [py_webauthn](https://pypi.org/project/webauthn/).
- [OWASP MFA cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) and [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html).
- [ngrok free plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits).
- Cybersource [webhook signature validation](https://developer.cybersource.com/docs/vas/en-us/webhooks/implementation/all/rest/webhooks/wh-fg-optional-intro/wh-fg-optional-validate-intro.html).
- Scam eval sources are in `PHASE1_PLAYBOOK.md` Section 10.
