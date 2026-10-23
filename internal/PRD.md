# Chaperone: build-critical PRD extract

Full PRD with evidence, winning strategy, demo runbook, Devpost draft and judge Q&A: https://claude.ai/code/artifact/a094142f-fea1-4531-89a9-22ec99c0a3d4 (tabs: PRD, Build Plan, Demo Runbook, Devpost and Video, Judge Q&A). The Ghost Hands PRD (the alternative build) is at https://claude.ai/code/artifact/60d931c2-fd85-4385-ba9a-fb5f92d7b61f; PRD section 13 compares the two for the Friday 8pm decision.

This file is the subset a coding agent needs: decisions, P0 scope, journey, trust chain, interfaces, repo layout, Friday tests, fallback ladder.

## One line

A voice-first shopping agent for older, low-vision and non-English shoppers that can only spend inside a caregiver-signed mandate, signs every merchant request, refuses scams out loud, escalates large purchases to a passkey approval on the caregiver's phone, and logs every decision.

## Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Spine | Policy as code below the model: the mandate is evaluated deterministically in the checkout tool; the model can only propose |
| D2 | Track | A Marina's Mission (Social Good) |
| D3 | Sponsor claims | Visa (primary) and xAI. No Meta |
| D4 | Voice | One Grok Voice session per shopper, auto language (Spanish, Hindi, English), push-to-talk, no interpreter layer |
| D5 | Trust chain | Caregiver passkey signs the mandate -> checkout tool evaluates -> Ed25519 RFC 9421 signature (TAP-style: created, expires 8 min, keyid, alg, nonce, tag=agent-payer-auth) -> merchant verifier (JWKS, nonce store, decision id) -> Visa Acceptance Agent Toolkit MCP payment link in the Cybersource sandbox -> test card completes (or callback fallback) |
| D6 | Scam refusal | Rule layer first (blocked categories, coached purchase, purpose flags, secrecy, family emergency), then a grok-4.7 judge with a strict JSON schema; refusal spoken with dignity; caregiver alerted |
| D7 | Station | USB HID push-to-talk button, close-talk USB headset, small speaker, large-type companion screen (tablet), 58 mm USB ESC/POS receipt printer (tablet fallback) |
| D8 | Catalog | ~300 items seeded from the Kroger API (one Atlanta locationId) and openFDA OTC labels, cached locally; synthetic fallback |
| D9 | Demo | Judge is the shopper; refusal first, then purchase; two outcomes in 60 s; caregiver phone and ledger on the table |
| D10 | Framing | Sandbox payments, mock merchant, no real money, no real PII |

## P0 scope (freeze Saturday 11pm)

1. Caregiver app (Next.js, served via one fixed tunnel domain for WebAuthn): mandate form (per-purchase cap, monthly cap, approval threshold, allowed merchants/categories, blocked categories, languages, validity), passkey signing of the mandate hash (SimpleWebAuthn v14), alerts, approve/reject with passkey assertion, 90 s timeout.
2. Voice client (Next.js on the station laptop): Grok Voice session with `turn_detection` off, button drives `input_audio_buffer.commit` + `response.create`; tools `search_catalog`, `add_to_cart`, `remove_from_cart`, `read_cart`, `budget_left`, `checkout`; read-back mandatory before checkout (tool contract); transcripts to the relay; companion screen in 24-pt type; typed fallback; cached-session replay.
3. Catalog + profile service (FastAPI): local JSON catalog with names, prices, categories, tags; profile resolves "my blood pressure medicine" -> saved pharmacy pickup item ($8 copay), "bread" -> usual brand flagged; search < 100 ms.
4. Policy engine (FastAPI, pure function): verify passkey assertion on load; rules R1 blocked category, R2 merchant allowed, R3 category allowed, R4 per-purchase cap, R5 monthly cap (running total persisted), R6 approval threshold, R7 scam judge; returns allow | approve | deny with every rule result; unit tests per rule both directions.
5. Signer: Ed25519 key; RFC 9421 over `@method @authority @path content-digest content-type`; params created, expires (<= 8 min), keyid, alg=ed25519, nonce, tag="agent-payer-auth"; JWKS served by the relay. Library: Python `http-message-signatures` 2.0.1 or Cloudflare `http-message-sig` (Node). Header-only signing; skip TAP body-object signing.
6. Merchant "Corner Market" (FastAPI): verify signature vs JWKS, window, nonce store, decision id on ledger; create payment link via `npx -y @visaacceptance/mcp --tools=all --merchant-id=... --api-key-id=... --secret-key=...` (tools: invoices.*, paymentLinks.*); sandbox default; test card 4111 1111 1111 1111 on the hosted page; callback fallback marks paid; mock MCP with identical schema when credentials absent; verification panel for the wall.
7. Scam layer: rule list (hard-block gift cards, prepaid, wire, crypto, money orders; third party instructing; purposes fine/taxes/bail/refund/unlock; relative in trouble; secrecy; urgency slows down; non-whitelisted merchant -> approval; quantity anomaly; address/payee change -> escalate; pop-up/caller trigger -> refuse; cap-dodging splits) + grok-4.7 judge `{scam_score, patterns[], rationale, action}` at every checkout and on two soft signals; refusal scripts in es/hi/en as files; pre-rendered refusal audio via xAI TTS.
8. Relay (FastAPI): rooms, ledger (JSONL per session), ephemeral client secrets (`POST https://api.x.ai/v1/realtime/client_secrets`), JWKS, session pages, wall data, reset (monthly total back to $142.10 baseline).
9. Wall (Next.js): mandate card, live ledger with rule ids and signature ids, merchant panel, monthly total.
10. Receipt: node-thermal-printer via the installed Windows driver (`interface: 'printer:<name>'`), 24-pt text + QR to session; tablet HTML fallback.
11. Hardening: cached sessions per language, typed input, one-button reset.

P1: budget/history voice queries, preference memory, storm mode, loyalty line, second merchant key. P2: Visa Intelligent Commerce tokenization/passkey, SMS/push, recurring orders, "why did it refuse" page.

## Journey (60 s demo)

Line 1 (gift cards, urgent) -> R1 + family-emergency pattern fire before any model call -> refusal spoken -> caregiver alert -> ledger "blocked: gift_card; pattern: family_emergency". Line 2 (medicine and bread) -> catalog + profile -> read-back with total ($11.49) -> checkout -> allow -> signed -> verified -> payment link -> paid -> receipt printed. Optional line 3 (a case of Ensure, $52) -> exceeds $40 threshold and $60 cap -> approval on the caregiver phone (passkey) or reject.

Refusal script (en): "I cannot buy gift cards on this account, Ruth. When someone asks for gift cards in a hurry, it is very often a scam, and it happens to smart people every day. You did nothing wrong. I have told Priya, and she will call you. Would you like me to get your medicine and bread now?"

## Interfaces

Mandate JSON: mandate_id, shopper, caregiver, currency, per_purchase_cap, monthly_cap, approval_threshold, allowed_merchants[], allowed_categories[], blocked_categories[], languages[], valid_from, valid_to, passkey{credential_id, assertion{authenticatorData, clientDataJSON, signature}}.

Policy decision: `{decision: "allow"|"approve"|"deny", rules:[{id, passed, detail}], monthly_total_after}`.

Signed order request headers:
```
Content-Digest: sha-256=:...:
Signature-Input: sig1=("@method" "@authority" "@path" "content-digest" "content-type");created=...;expires=...;keyid="chaperone-agent-1";alg="ed25519";nonce="...";tag="agent-payer-auth"
Signature: sig1=:...:
```
Body: `{mandate_id, decision_id, cart, approval_id|null}`. Verifier checks signature, expires <= created + 8 min, unseen nonce, known keyid, decision id is allow/approved on the ledger.

Approval: `{approval_id, session_id, amount, excerpt, rule, expires_at}` -> phone -> `{approval_id, approved, assertion}`.

Ledger events: session_started, heard, items_found, cart_updated, checkout_requested, policy_decision, approval_requested, approval_result, refusal, request_signed, signature_verified, payment_link_created, paid, receipt_printed, caregiver_alerted (each with session_id, mandate_id, t, rt).

Judge schema: `{scam_score: 0-1, patterns: [family_emergency|urgency|secrecy|authority_impersonation|code_reading|amount_anomaly], rationale, action: proceed|ask_clarifying|refuse_and_alert}`. Cart schema: `{items:[{sku, qty, confidence}], needs_clarification, question}`; ask below 0.7.

## Repo layout

```
chaperone/
  README.md  .cursor/rules  .env.example
  relay/     main.py tokens.py jwks.py
  policy/    mandate.py engine.py judge.py tests/
  signer/    sign.py
  merchant/  verify.py orders.py visa.py panel.tsx
  catalog/   seed_kroger.py seed_openfda.py catalog.json profile.json search.py
  station/   voice.ts persona.ts screen.tsx receipt.ts replay.ts
  caregiver/ mandate.tsx approvals.tsx ledger.tsx
  wall/
  ai/prompts/  persona, cart schema, judge schema, refusal scripts
  docs/  sessions/
```

Ports: relay 8000, policy 8001, merchant 8002, catalog 8003, station 5173, caregiver 5175 (through the tunnel), wall 5176.

## Owners

Manush: station (voice client, persona, companion screen, printer, cached sessions). Dhruv: trust layer and caregiver app (mandate, passkeys, policy engine, signer, verifier, ledger, Cursor evidence). Vraj: merchant, catalog, Visa MCP, wall, network. Rohan: rule layer, judge, eval set, refusal scripts, cart prompts, Devpost evidence, video scam-caller scene.

## Thursday and Friday tests

Thursday: Cybersource sandbox account + REST shared-secret key; run the MCP and create a $1 payment link; Kroger app registration (else synthetic catalog); xAI console + credits; fix the tunnel domain and register the caregiver passkey; order the station parts; print line cards.

Friday 8:30-9:15pm: (1) Manush: Grok Voice round trip with a tool call via push-to-talk, Spanish reply < 1.5 s. (2) Dhruv: passkey assertion on the phone against the tunnel domain; RFC 9421 request verified by a stub, tampered body and reused nonce rejected. (3) Vraj: sandbox payment link created with a decision id; test card completes it (else callback fallback). (4) Rohan: rules refuse the three scam lines in each language before any model call; judge returns valid JSON separating scam and benign scripts. 9:30 integration smoke; 10:00 go/no-go.

## Fallback ladder (cut bottom-up, never rung 1)

1. Never cut: voice in the shopper's language, cart read back, mandate evaluated in code, one refusal with the rule on the wall, one purchase signed and verified, a receipt.
2. Sat 9pm: third language.
3. Sat 6pm: sandbox completion -> callback marks paid, Host says so.
4. Sat 3pm: sandbox credentials -> mock MCP with the same schema.
5. Sat noon: passkeys -> six-digit approval code.
6. Sat noon: printer -> tablet receipt.
7. Fri midnight: Grok Voice -> browser STT + grok-4.7 + browser TTS.
8. Fri midnight: button -> spacebar.

Rehearsal gate: 9 of 10 clean runs Saturday evening or the feature moves to the video.

## Key evidence lines (sources in the full PRD)

- IC3 2025: 201,266 complaints from people 60+, $7.75B lost (+59%), average $38,500; tech-support scams $1.04B; 3,100+ AI-referenced complaints.
- FTC: 60+ reported losses $600M (2020) -> $2.4B (2024), true figure up to $82B; gift cards in 16% of 60+ loss reports, top payment for impersonation scams; $10k+ impersonation losses 1,790 -> 8,269 reports; phone first contact 41%.
- FinCEN: 155,415 elder exploitation reports, ~$27B in one year; 80% scams; family involved in 46% of theft cases.
- Exclusion: 65+ smartphone ownership 78% (lowest); 13.6% of 65+ vision-impaired; 58.4% of Spanish-speaking 65+ speak English less than very well; 63M caregivers, a quarter > 20 min away.
- Existing: True Link ($12/mo, static categories), Carefull/EverSafe (after the fact), Alexa voice purchasing (code, one store), Instacart Senior Support (human line), Visa TAP / Mastercard Agent Pay (cardholder-set mandates, no delegated signer, no refusal).
- Visa June 2026: "spending limits, merchant category restrictions, and approval requirements"; past Visa university tracks did not require sandbox use -> real sandbox + signing is a differentiator.
- Prototype, sandbox, no real money, no PII.
