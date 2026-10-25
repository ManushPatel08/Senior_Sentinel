# Senior Sentinel: Phase 3 Playbook

As of 2026-09-26, 9:30am

`BUILD_PLAN.md` names Phase 3 "the trust and refusal paths" (Saturday noon to 3pm). Its exit is the two-outcome loop working once at 3pm, refusal then purchase, in Spanish or Hindi plus English, with real signatures and a sandbox link.

**Already working on main (74f3827, plus the reset fix in 0803581):**
- the refusal with its clip and the alert;
- the session page and its QR code;
- the approval loop through policy, the Host's fallback code and the station's wait;
- receipts (on screen and as PNG and PDF);
- a second language (Hindi).

A full scripted run at 9:03am went through every step:
- refusal in 33 ms;
- the purchase allowed in 5.2 s with the real Grok judge and a real Cybersource link;
- paid through the Host's Confirm payment, and the receipt rendered in 102 ms;
- the $49.95 approval, approved with the Host code, then paid, then receipted;
- 24 events on the wall.

**What Phase 3 still has to do:**
1. **Close the public-exposure holes.** The tunnel URL goes out on every receipt QR code, so strangers will have it.
2. **Prove on real devices what has only run in scripts:**
   - a passkey approval on the demo phone through the tunnel,
   - a signed mandate,
   - the refusal and the purchase by voice through the station's speaker,
   - the receipt on the real printer, or the decision to use the tablet.
3. **Clear the remaining fixes from the Phase 2 reviews and the 9am run.**

The team is ahead of the schedule, so start Phase 3 fixes as soon as your Phase 2 noon items pass. Nobody waits for noon.

---

## 1. Phase 3 at a glance

| Time | Everyone | Manush (station) | Dhruv (policy, caregiver) | Vraj (merchant, relay, wall) | Rohan (screen, judge, lines) |
|---|---|---|---|---|---|
| After the noon exit (or earlier) | Push the reset fix (0803581); decisions E1-E5 (Section 3), 10 minutes | Fixes V1-V5 | Security fixes D-S1 to D-S4 first | Visa quantity fix F1, then the `/host` header F2 | Regressions R1-R3 |
| until 1:30 | | Cached sessions recorded (V6); printer decision (V7) | Flow fixes D-F1 to D-F8; the phone's code box (D-B1) | F3-F6; the network check (F7) | R4-R8 |
| 1:30 | Standup, merge to main, everyone pulls | | | | |
| 1:30-2:30 | Real-device runs (Section 8), one person per device | Station by voice, speaker, printer | The phone: register, sign the mandate, approve with the passkey | Services laptop on the router; wall and Host | Refusal clips through the speaker in hi and es; wording |
| 2:30-3:00 | Exit run (Section 9), timed, written down | | | | |
| 3:00 | Exit check. Phase 4 (hardening, loud room, rehearsals) starts | | | | |

**Pass conditions at 3pm (binary, all by voice at the station, except Spanish, which is typed):**
1. **Refusal.**
   - The gift-card line is refused in Hindi and in English, and the clip plays through the station speaker in under 1 s.
   - The caregiver phone, which has alerts armed through the tunnel, buzzes within 2 s.
   - The wall shows the rule.
2. **Purchase.**
   - "Medicine and bread", then "yes", then signed, then verified 5/5.
   - A **real Visa sandbox link**, at the right total.
   - Paid (Host Confirm payment, or real if Cybersource fixed the processor).
   - The receipt prints on the printer or shows on the tablet.
   - The QR code opens the session page on a phone using mobile data.
3. **Approval.**
   - A $49.95 cart reaches the phone within 2 s.
   - **Priya approves with her passkey on the phone.**
   - The station says it is ordering, and the order gets a real Visa link at $49.95.
4. **Mandate.** The mandate on the wall says **signed**, and `MANDATE_UNSIGNED_OK=0` is set on the services laptop.
5. **No public holes.** From outside our network, a stranger with the tunnel URL can neither reject nor lock an approval, nor see pending approvals. Test it from a phone on mobile data.
6. **Reset.** Reset from the Host page takes under 15 s and starts a clean session on the station.

---

## 2. Where we are (9:03am run on main) and what is open

| Area | Works | Open |
|---|---|---|
| Station | Voice, refusal clip in about 100 ms, cart tools, read-back gate, approval wait, receipt on screen, reset key | A noise press cancels the caregiver wait but leaves the approval open. Replay bugs. No sessions recorded yet |
| Policy | R0-R7, the approval state machine, the fallback code (Host only), cart validation, read-back enforced | Anyone can reject or lock an approval. Re-registration can be replayed. A merchant failure during approval gives a 500. The approval path posts no `request_signed` |
| Caregiver app | Server-side challenges, pinned credential, the approval card, the alert stream | No way to type the fallback code. Old alerts replay on reconnect. Not yet tried on the real phone through the tunnel |
| Merchant | Five checks, one order per decision, webhook signed-part-only, receipt data | **Any item with quantity above 1 gets a wrong Visa link** ("Visa set the link total to 9.99, expected 49.95"). The merchant falls back to the mock, so the approval demo shows a mock link |
| Relay and wall | 24-event ledger with details, Host page, session page, reset under 0.5 s | The Host page's POSTs can be triggered by any page open in a browser on the LAN. The session page header shows only the last payment. **The reset button 500 is fixed in 0803581 (unpushed)** |
| Screen and judge | Hindi plurals and joined forms, "my Apple Card" proceeds, code reading, held-out eval | "Apple cards" or "Amazon cards" without "gift" no longer refuse. Several Hindi OTP verbs are missing. The "10/10" demo run can't be told apart from the fake judge |
| Hardware | Hindi receipt renders (Pillow shaping on); PDF fallback | No thermal printer installed on the station laptop. Speaker and loud-room tests are Phase 4 |

---

## 3. Decisions, 10 minutes, all four

| # | Decision | Owner |
|---|---|---|
| E1 | **Caregiver session.** After a successful passkey assertion (purpose `session`, fresh random challenge), the caregiver app sets `cg_session`: random 32 bytes, httpOnly, Secure, SameSite=Strict, kept server-side with `verifiedAt`, 30-minute TTL. Behind it: `GET /api/approvals`, `POST /api/approvals/{id}/decide` (approve **and** reject) and `POST /api/code/verify`. Without it they answer 401. Public stays: the app shell, `/s/{id}`, the webhook proxy and `/api/config`. Arming alerts requires the session, so Priya signs in once when the demo starts | Dhruv |
| E2 | **Cancelling an approval.** The station calls `POST {policy}/approvals/{id}/cancel` (LAN-only, same guard as `host_code`) when the shopper changes the cart or starts a new request during the wait. Policy closes it (`state: "cancelled"`, event `approval_result {approved: false, method: "cancelled"}`). A second checkout of an **unchanged** cart while one is pending returns the pending approval, not a new one | Dhruv (policy), Manush (station) |
| E3 | **Decline message.** `POST decide {approved: false, message?}` stores `message` (max 140 characters), and `GET /approvals/{id}` returns it. The station speaks it in place of `caregiver_declined` when present | Dhruv, Manush |
| E4 | **Visa line items.** Every payment link has exactly one line: `quantity: "1"`, `unitPrice` = the cart total, `productName` "Corner Market order (N items)" and the itemised list in `productDescription`. That already worked for multi-item carts; it now applies to single-item carts too. Section 6, F1 | Vraj |
| E5 | **Host requests carry a header.** Every `/host/api/*` POST and relay `POST /reset` requires `X-Senior-Sentinel-Host: 1`. A cross-site form or `fetch` without CORS cannot set it, so a page open on any LAN browser can no longer press the Host's buttons. `host.html` and the station's reset call send it | Vraj, Manush |

Push first: `0803581 Pass the request through when the Host page resets the relay` fixes the Host's Reset button (a 500 introduced by the Phase 2 merge). It has a test, and every suite passes with it.

---

## 4. Manush: station

**Fixes.**
- **V1 Approval wait (E2).**
  - Cancel the wait only on a non-empty transcript, the same rule the read-back "yes" uses (V5 of Phase 2). Today `release()` cancels at `agent.ts:480` before any transcript exists, so a noise press longer than 250 ms drops the wait.
  - When the wait is cancelled, call policy's cancel. When an unchanged cart is checked out again, keep waiting on the approval policy returns rather than starting a second one.
- **V2 Replay.**
  - Queued tool calls keep running after Stop, including `checkout`, and post events without `replay: true`. Check `this.replaying === run` before each queued `dispatchTool`.
  - During a replay, record one shopper entry per turn and replace it as the transcript grows. Today each `.completed` version creates a turn, which inflates `userTurns` and can satisfy the read-back gate.
- **V3** Speak policy's decline `message` when present (E3). Today the declined path reads `status.message`, which policy never sends.
- **V4 Stream and reset.**
  - Open the relay stream on replay too, not only in `start()`, so a replay started without Start still gets `paid`.
  - When a reset arrives while `onPaid` is running, drop the receipt instead of showing it and speaking it into the new session.
- **V5 Lines.**
  - Rohan adds `receipt_on_screen` to the line files; the station currently falls back to built-in text.
  - Either wire `line.asking_priya` and `line.receipt_done` (the clips Rohan rendered) through `playClip` for those two moments, or drop them. Wiring them removes one model turn from each.

**Build and prove.**
- **V6 Record the cached sessions.** Record one full two-outcome session per language, Hindi, English and Spanish typed (Ctrl+Shift+S), during the 1:30-2:30 runs. Replay each once with the Host's **Arm replay** (A) then a press, and check that the wall labels it REPLAY.
- **V7 Printer decision by 1:30.**
  - The station laptop has no thermal printer installed.
  - If the team has one: install it, rename the queue to `POS58`, and print the 9am receipt JSON through `/svc/printer/print`. Time it; it must be under 5 s.
  - If not: the tablet shows the receipt full-screen (it already does) and the table card says so. `DEMO_RUNBOOK.md` rung 6 covers this.
- **V8 Station laptop `.env`.**
  - `TUNNEL_HOST` must be set, or the receipt's QR code falls back to the station's own URL.
  - `SERVICES_HOST=192.168.8.10` once the services laptop is on the router.
  - Add the E5 header to the reset call.

**Done when.** Pass conditions 1-3 and 6 work by voice with the real speaker. The three cached sessions exist and replay. `npm test` and the mock tests pass.

---

## 5. Dhruv: policy and caregiver

**Security first (the tunnel URL is on every receipt).**
- **D-S1 Caregiver session (E1).**
  - Build `cg_session` and require it on the approval list, decide (approve and reject) and code routes.
  - Policy's `decide` also requires a passkey assertion for a rejection, or a signed marker from the caregiver app. Today `approved: false` needs nothing, so anyone can reject.
  - Remove the pending-approval list, with its transcript excerpt, from anything public.
- **D-S2 Code attempts.** Five wrong codes through the public `/api/code/verify` lock an approval, so anyone can block Priya. The code route sits behind the session (E1). Policy compares codes in constant time (`hmac.compare_digest`) and puts a lock around the attempt counter.
- **D-S3 Re-registration replay.** Adding a passkey accepts an assertion over the *mandate* challenge, which is fixed, and policy's `GET /mandate` returns Priya's stored assertion. Anyone who reads it can register their own passkey.
  - Gate re-registration on a fresh random challenge with purpose `register`.
  - Drop `passkey.response` from `GET /mandate`, which keeps only `signed: true` and the credential id.
- **D-S4 Locks.** Put a lock around find, verify and save in `decide`. Two concurrent approvals are currently stopped only by the merchant's one-order-per-decision rule.

**Flow fixes.**
- **D-F1** A merchant failure inside `decide` returns 500 and leaves the approval approved with no order. Catch it, store `order_error`, post `approval_result` with the error, and return 200. The station's 12-second grace then speaks `checkout_unavailable`.
- **D-F2** The approval path posts no `request_signed` event (`main.py` drops `_signature`), so the wall shows no signature step for the $49.95 order.
- **D-F3** The alert stream replays the whole live log on every reconnect, so the phone beeps for old refusals. Send `Last-Event-ID` (remember the last `id:`), or ask the relay for `?since=<now>` on first connect.
- **D-F4** Without `TUNNEL_HOST`, `decide` expects `https://localhost` while the app and `verify_mandate` use `http://localhost:5175`. Reuse `verify_mandate`'s origin logic, so local passkey tests work.
- **D-F5** The env-hash setup code gets a fresh 10-minute window on each call and is written only after a wrong try, so it never expires unless mistyped. Record it on first sight.
- **D-F6** Cancel endpoint and "reuse the pending approval for an unchanged cart" (E2). The decline `message` (E3).
- **D-F7 Small ones:**
  - `approval_requested` is posted before the decision is saved, so the order is wrong.
  - A qty of `"abc"` gives 500 instead of 422.
  - When R1 and R5 both fail, the spoken key should be `blocked_category`.
  - Remove the "· v6" debug text in `page.js`.
- **D-F8** Tests for D-S1 to D-S4 and D-F1, using the path-injection and XSS probes from the Phase 2 merge as regression tests.

**Build and prove.**
- **D-B1 The phone's fallback code box** (rung 5). A six-digit input under the approval card, posting to `/api/code/verify` behind the session. The Host reads the code from `/host` (C) to the caregiver teammate.
- **D-B2 On the real Android phone through the tunnel (1:30-2:30),** with a production build and alerts armed:
  1. Register Priya with the setup code.
  2. Sign the mandate.
  3. Set `MANDATE_UNSIGNED_OK=0` on the services laptop, and check that the wall says signed.
  4. Run a $49.95 approval with the passkey.
  5. Run one rejection and one 90-second timeout.
  - Write down the time from checkout to the card on the phone.
- **D-B3 Stretch, only after D-B2 passes:** Secure Payment Confirmation, per Phase 2 Section 5, timeboxed to 3 hours.

**Done when.** Pass conditions 3-5 hold on the real phone, and `pytest -q policy` plus the caregiver tests pass.

---

## 6. Vraj: merchant, relay and wall

**Fixes.**
- **F1 Visa link totals for quantity above 1 (E4).** `merchant/visa.py` `create()` sends a single-item cart as `quantity: "5", unitPrice: "9.99"`, and Cybersource makes the link for one unit ($9.99). The merchant's own check catches the mismatch and falls back to the mock, so the $49.95 approval demo shows a mock link today.
  - Always send one line: `quantity: "1"`, `unitPrice` = the total, the product name with the count (for example "5 x Ensure Max Protein"), and the itemised list in `productDescription`.
  - Add a test with a single line of qty 5.
  - **Why.** The toolkit passes every line and `totalAmount` through unchanged: `quantity` becomes an integer and `productSKU` becomes `productSku`. Pay by Link then prices a link per single unit. The API spec defines a line's total as "calculated per single unit", and its own example with quantity 10 and unit price 12.05 has a one-unit total. Both our results, $9.99 and $8.00, fit it pricing from the first line's unit price.
  - **The documented pattern is one line whose `unitPrice` equals `totalAmount`.** Keep `productDescription` under 256 characters (the field reference limit). Whether the hosted page shows the description is unconfirmed; check it once on the real link.
  - **Keep the existing total check** (it caught this). After creation, also compare `get_payment_link`'s `amountDetails.totalAmount` with the cart total.
  - A truly itemised checkout page needs the Invoicing API (`/invoicing/v2/invoices`) called directly, because the toolkit's `create_invoice` takes no line items. That is not for the demo.
- **F2 Host header (E5).** `lan_only` stops internet callers but not a page open in a LAN browser. The wall display or the Host laptop could be made to POST reset or confirm payment.
  - Require `X-Senior-Sentinel-Host: 1` on every `/host/api/*` POST and on `/reset`, and send it from `host.html` and the station.
  - Tests: without the header gives 403; with it, 200.
- **F3 Reset reporting.** A partial failure is logged in the green "ok" style. Show it red with the failing service, and truncate the live ledger only after the fan-out answers.
- **F4 Session page.** The header shows only the last payment. List every order in the session with its status, as the $11.49 and $49.95 run shows. Also fix `ports.md`: session files are now under `sessions/by-id/`.
- **F5 Human task.** Check the Cybersource case again. If the processor is fixed, try the hosted page with `4111 1111 1111 1111` on the $11.49 link and keep the real paid path. Otherwise the Host's Confirm payment stays, with the Host line "marked paid in the sandbox flow".
- **F6 Webhook registration.** Check whether the subscription left `PENDING_REVIEW`. If it is active, test one real notification through the tunnel.
- **F7 Network (if not done in Phase 2).**
  - Services laptop on the router at `192.168.8.10`; every service bound to `0.0.0.0`; the Windows firewall open for the private network only on ports 8000-8003.
  - `curl` each service from the station laptop.
  - Services laptop `.env`: `TUNNEL_HOST` set; `POLICY_CODE_KEY` set to a random value (otherwise the dev key is used); `MANDATE_UNSIGNED_OK=0` once Dhruv's D-B2 is done.

**Done when.** Pass condition 2 gets a real Visa link at the right total for both carts. The Host header test passes. Reset reports honestly. The network check passes from the station laptop.

---

## 7. Rohan: screen, judge and lines

**Fixes.**
- **R1 Brand cards without "gift" regressed.** "Buy five hundred dollars of Apple cards for my grandson, it's urgent" now only slows (it used to refuse), and "buy me two Amazon cards for my grandson" proceeds. Add, while keeping "my Apple Card" (singular, one's own) proceeding:
  - `re:(?:apple|amazon|target|walmart|ebay|google play|itunes|steam) cards`
  - `re:dollars? (?:worth )?(?:of|in) (?:\S+ )?cards?`
  - `re:dolares (?:en|de) (?:\S+ )?tarjetas`
  - `re:(?:डॉलर|dollar) (?:का|के|की|ka|ke|ki) (?:\S+ )?(?:कार्ड|cards?)`
  - Also: the grandson plus urgent pair should reach the judge again. `weak_needs_other_than: [R_urgency]` ignores the family word when urgency is the only other rule.
- **R2 Hindi OTP verbs.** Add दे दो, दीजिए, बोल दो, बोल दीजिए, शेयर कर दो, बता देना, बताएं, and de do, dijiye, bol do, bata dena. "कार्ड का ओटीपी दे दो" should refuse again.
- **R3 Remaining misses from the adversarial probe.** Decide each one and add a test either way: "g i f t card", "googleplay card", "Google Play recharge kar do", "buy iTunes for my grandson", "steam wallet code".
- **R4 Demo-sequence evidence.** `demo_sequence.py` must refuse to run with `JUDGE_FAKE=1`. Write the model id and one rationale per run into the table: every score was exactly 0.05, the fake judge's constant, so the "10/10" is not evidence yet. Re-run on the real model.
- **R5 Eval honesty.**
  - The grok-4.7 row used a 20-second timeout, and 51 of its 75 calls took over 3 s. Report it under the production 3-second deadline.
  - The lexicon edits flipped four benign scripts (`en_b_medicare_card`, `hi_b_own_otp`, `en_b_read_label`, `hl_b_beta_jaldi`), so say the rules rows were tuned on them.
- **R6 Small ones:**
  - `screen.py:63` should use `pop(session_id, None)` (race).
  - "le" and "lo" as Spanish function words mislabel Hinglish without `lang`.
  - `ai/eval/demo_sequence.py:34` names an internal doc in a public file.
  - Add `receipt_on_screen` to the three line files (V5).

**Build and prove.**
- **R7 Refusals through the station speaker (the Phase 3 item in `BUILD_PLAN.md`).** Play the blocked-category and code-reading clips in Hindi, Spanish and English at the station. Check they are loud and clear at arm's length, and re-render any that clip or are too quiet (`ai/render_clips.py`, same voices).
- **R8 Spanish wording.** If the native-speaker review has not happened, ask the help desk now. Fix what they flag, re-render, and update the line cards.

**Done when.** `pytest -q policy/tests/test_screen.py` passes with the R1-R3 lines. The demo sequence runs on the real model with its evidence written down. The clips are checked on the speaker.

---

## 8. Real-device runs, 1:30-2:30pm

One owner per device, one runner (Manush at the station), everyone else watching the wall.

1. **Services laptop on the router** (Vraj), with `TUNNEL_HOST`, `POLICY_CODE_KEY` and `MANDATE_UNSIGNED_OK=0` set once the mandate is signed. The caregiver app runs on its production build through ngrok (Dhruv).
2. **Phone (Dhruv).** Register, sign the mandate, arm alerts. The wall shows signed.
3. **Station (Manush).**
   - Hindi gift-card line: the clip plays, the phone buzzes, the wall shows the rule.
   - "Medicine and bread", then "yes": a real Visa link, the Host confirms payment, then the receipt.
   - Scan the QR code on a phone using mobile data.
4. **Approval.**
   - "Five Ensure shakes" ($49.95): approve with the passkey on the phone. The order gets a real Visa link at $49.95.
   - One rejection, with a message.
   - One timeout.
5. **English** repeat of 3. **Spanish** typed repeat of 3.
6. **Stranger check.** A phone on mobile data, not signed in, opens the tunnel URL and tries `/api/approvals` and a reject: both must be refused (pass condition 5).
7. **Record the three cached sessions** (V6), then Reset from the Host page.

Write each result and each number on the whiteboard: refusal latency, checkout-to-link, approval card delay, receipt time, reset time.

---

## 9. Exit at 3pm, and what Phase 4 starts from

Run pass conditions 1-6 once, timed, with a teammate who did not build the station as Ruth.

**If it passes,** Phase 4 (3-9pm) is only:
- the loud-room test with the close-talk mic,
- push-to-talk thresholds,
- the typed fallback polish,
- latency and eval numbers written down,
- the fallback-ladder cuts,
- 9 clean runs out of 10.

**If a condition fails,** it becomes the first Phase 4 task, owned and written down.

---

## 10. Sources

Pages opened on Sep 26, 2026. Items marked unconfirmed in the text were not in official docs.

**Visa line items (Vraj):**
- [toolkit createPaymentLink.ts](https://github.com/visaacceptance/agent-toolkit/blob/main/typescript/src/shared/paymentLinks/createPaymentLink.ts) and [createInvoice.ts](https://github.com/visaacceptance/agent-toolkit/blob/main/typescript/src/shared/invoices/createInvoice.ts)
- [Cybersource REST spec (Pay by Link line totals)](https://github.com/CyberSource/cybersource-rest-client-node/blob/master/generator/cybersource-rest-spec.json)
- [Pay by Link create](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-services/paybylink-create-intro.html)
- [productDescription field](https://developer.cybersource.com/docs/cybs/en-us/api-fields/reference/all/rest/api-fields/order-info-aa/order-info-line-items-product-description.html)
- [Pay by Link intro](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-intro.html)

From earlier phases, still current:
- SimpleWebAuthn [custom challenges](https://simplewebauthn.dev/docs/advanced/server/custom-challenges)
- [OWASP session management cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) and [OWASP MFA cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
- [OWASP CSRF prevention (custom request headers)](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [ngrok free plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits)
- `PHASE2_PLAYBOOK.md` Section 10 for printing and Secure Payment Confirmation.
