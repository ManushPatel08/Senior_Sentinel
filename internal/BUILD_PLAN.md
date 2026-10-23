# Chaperone: Build Plan

The 36-hour plan for four people ending Sunday 8am with a working two-outcome demo, a video and a Devpost page. Tonight's detailed steps are in `PHASE0_PLAYBOOK.md`.

---

## Phases

Seven phases, done in order; within each phase all four lanes work in parallel against the contracts frozen at 8:30pm Friday, and a phase ends only when its exit criterion is met together.

| Phase | Window | Goal | Exit criterion (whole team) |
|---|---|---|---|
| 0. Setup and de-risk | Fri 8:00-10:00pm | Accounts, keys, router, repo scaffold with the frozen schemas; four spike tests, one per lane | Go/no-go at 10pm: voice round trip with a tool call, passkey assertion plus a verified signature, a sandbox payment link (real or mock), rules refusing the scam line |
| 1. Foundations against fakes | Fri 10pm-Sat 2am | Each lane builds its service against a fake of its neighbor, with unit tests | Every seam has a fake; policy tests pass for all seven rules; the station talks to a fake catalog; the merchant verifies a fake signed request |
| 2. The purchase path | Sat 6am-12pm | Replace fakes with real components along the happy path: voice, catalog, policy, signer, merchant, payment link, ledger, wall, receipt | One real purchase end to end at noon, with "signature verified" on the wall and a printed receipt |
| 3. The trust and refusal paths | Sat 12-3pm | The caregiver approval loop with a passkey, the scam refusal with an alert, the session page, a second language | The two-outcome loop (refusal, then purchase) works once at 3pm, in Spanish or Hindi and English |
| 4. Hardening and rehearsal | Sat 3-9pm | Station hardware in the loud room, cached sessions, typed fallback, reset, latency and eval numbers written down, cuts per the fallback ladder | 9 of 10 clean runs by 9pm; anything else moves to the video |
| 5. Freeze, video, submission | Sat 9pm-Sun 3am | Polish only, README, Devpost write-up, footage, edit | Devpost submitted with the video link by 3am; repo public and clean |
| 6. Expo | Sun 6:30-11:15am | Set up at the table, two clean runs, final edits, run the runbook | Submitted by 7:55am; every judge gets the same 60-second experience |

Rules: a phase's exit criterion is binary and demoed to the other three at a two-minute standup; missing a criterion by more than two hours triggers the next rung of the fallback ladder, decided together; sleep is scheduled in two shifts so no phase loses all four people at once.

---

## Team assignments and workstreams

Four workstreams with one owner each; the seams are the event schemas and the mandate and order formats in `PRD.md` Section 9, so nobody waits on anybody before Saturday noon.

| Owner | Workstream | Deliverables | Why this person |
|---|---|---|---|
| Manush | Shopper station | The Grok Voice browser client with push-to-talk and tool calling, the persona and read-back logic, the large-type companion screen (WCAG AA, captions, cart), the receipt printer integration and its tablet fallback, cached-session replay, the station's physical build | React and .NET UI work, audio-video plumbing, owns the table experience |
| Dhruv | Trust layer and caregiver app | Mandate schema and signing with WebAuthn passkeys, the deterministic policy engine, the Ed25519 RFC 9421 signer and merchant verifier with JWKS and nonce store, the caregiver phone page (alerts, approve and reject with passkey), the ledger schema, the Cursor evidence trail | JWT, OAuth2 and RBAC background; production infra; eval mindset for the policy tests |
| Vraj | Merchant, catalog and Visa | The catalog service and shopper profile (Kroger API or synthetic), the Corner Market merchant service, the Visa Acceptance Agent Toolkit MCP integration and sandbox payment links, the wall ledger and merchant verification panel, network and router | Real-time services, MCP servers, dashboards |
| Rohan | Scam refusal and AI quality | The rule layer, the LLM judge with a labeled eval set of scam and benign scripts, refusal scripts in three languages, the cart-structuring prompts and schemas, the Devpost write-up's evidence, the video's scam-caller scene | NLP classifiers, eval discipline |

**Shared rules.**

- The mandate token, the order request format, the signature headers and the event schemas are frozen Friday 8:30pm.
- Every seam has a fake by Friday midnight: a fake catalog for the voice client, a fake policy engine for the merchant, a fake merchant for the signer, a fake alert feed for the caregiver page.
- Hourly two-minute standups, blockers only.
- Claude Code and Cursor write boilerplate; humans own the policy engine tests, the refusal wording, the audio at the table and the demo.
- Nothing merges to main after Saturday 11pm except rehearsal fixes.
- Commit messages describe the code change only; no phase names, no strategy.

---

## Friday 8-10pm

See `PHASE0_PLAYBOOK.md` for the shared setup, the four spikes with exact commands and pass conditions, the integration smoke and the go/no-go table.

---

## Hour-by-hour schedule

Four hard milestones: voice to cart to policy to ledger with fakes by Saturday 9am, the full two-outcome loop with real signatures and a sandbox link by Saturday 3pm, feature freeze at Saturday 11pm, and the video by Sunday 3am.

| Window | Manush (station) | Dhruv (trust and caregiver) | Vraj (merchant, catalog, Visa) | Rohan (refusal and AI) | Milestone |
|---|---|---|---|---|---|
| Fri 8:00-8:30pm | Button, mic, speaker, printer plugged in and recognized | xAI and sandbox keys into the vault; repo scaffold | Router, static IPs, services skeleton | Eval set of scam and benign scripts started | Hardware and keys in hand |
| Fri 8:30-10pm | De-risk: Grok Voice round trip with one tool call from the browser, push-to-talk | De-risk: passkey registered and asserted on a phone through the tunnel; Ed25519 signature verified by a stub | De-risk: Acceptance MCP creates a sandbox payment link, or the mock does with the same schema | De-risk: rule layer refuses the gift-card line; judge schema returns valid JSON | **Go/no-go 10pm** |
| Fri 10pm-2am | Persona, read-back, tool schemas, companion screen skeleton | Mandate form and signing; policy engine with unit tests | Catalog and profile service; merchant service with the verifier | Refusal scripts in three languages; judge prompt tuned on the eval set | Fakes on every seam |
| Sat 2-9am | Sleep 2-6 (Manush, Rohan) | Sleep 5-9 (Dhruv, Vraj) | Sleep 5-9 | Sleep 2-6 | |
| Sat 6-9am | Voice to real catalog to real policy engine | Signer wired to the merchant verifier; ledger persisted | Payment link from a real decision id; merchant panel | Judge wired into checkout | **9am: full loop with fakes replaced** |
| Sat 9am-12pm | Receipt printing from a real order; cached sessions recorded | Caregiver phone page: alert, approve, reject, timeout | Wall ledger and merchant panel polished; sandbox paid status | False-refusal rate measured; wording fixes | First end-to-end two-outcome run at noon |
| Sat 12-3pm | Fixes; typed fallback; reset button | Fixes; approval path with passkey on the phone | Sandbox completion with a test card, or the callback fallback | Hindi and Spanish refusals through the speaker | **3pm: two outcomes, real signatures, sandbox link** |
| Sat 3-6pm | Loud-room test with the close-talk mic; push-to-talk thresholds | Second merchant key if ahead; ledger export | Budget-left and history queries (P1) if ahead | Cursor evidence recording; Devpost evidence | Run the loop 5 times |
| Sat 6-9pm | Rehearsals with a non-team speaker of the second language; fix list | Fix list | Fix list; latency numbers written down | Fix list; eval numbers written down | 9 of 10 clean runs or cut per the ladder |
| Sat 9-11pm | Polish only | Devpost draft from `DEVPOST.md`; README | Sunday kit packed | Video script | **11pm freeze** |
| Sat 11pm-Sun 1am | Station footage | Caregiver phone footage | Wall capture | Scam-caller scene; voiceover | Footage done |
| Sun 1-3am | Video edit | Devpost submitted with placeholder video by 2am, final by 3am | Sleep 1-5 | Sleep 1-5 | **3am: video uploaded** |
| Sun 3-6am | Sleep 3-6:30 | Sleep 3-6:30 | Wake 5; kit check | Wake 5; line cards printed | |
| Sun 6:30-8am | Station set up, test print, two clean runs | Wall, phone, Devpost final edits | Services up, sandbox link tested | Voice warm in three languages | **7:45am final edits; 8am hacking ends** |
| Sun 8-9am | Breakfast in shifts; one more clean run | | | | Expo 9:00 |

**Rules of the schedule.** A milestone missed by more than two hours triggers the next rung of the fallback ladder, decided at the standup, not alone. Nobody works more than 20 hours without a 3-hour sleep. Whoever is on the station takes a 10-minute break every hour.

---

## Repo structure, stack and setup

One monorepo, four services and three web apps, all on two laptops; the caregiver app is reached through the ngrok domain, everything else on the LAN.

```text
chaperone/
  README.md                 what it is, run it, measured numbers, built with Cursor and Grok
  .cursor/rules             conventions: policy is pure, no secrets in browsers, read-back before checkout
  .env.example              XAI_API_KEY, MERCHANT_ID, API_KEY_ID, SECRET_KEY, KROGER_CLIENT_ID/SECRET, TUNNEL_HOST, ROOM_CODE
  contracts/                JSON Schemas for mandate, decision, order_request, approval, events, judge, cart; signing.md; ports.md
  relay/                    FastAPI
    main.py                 rooms, ledger, session pages, wall data, reset
    tokens.py               ephemeral client secrets for the station
    jwks.json               agent public keys
  policy/                   FastAPI
    mandate.py              canonicalize, hash, verify the passkey assertion
    engine.py               rules R1-R7, monthly total, decisions
    judge.py                grok-4.7 scam judge with the JSON schema
    tests/                  one test per rule, both directions; eval set of scripts
  signer/                   Python http-message-signatures
    sign.py                 RFC 9421, ed25519, created/expires/keyid/nonce/tag
  merchant/                 FastAPI "Corner Market"
    verify.py               JWKS, window, nonce store, digest, decision id check
    orders.py               order intake, receipt data
    visa.py                 PaymentLinks interface: real MCP client and mock with the same schema
    panel.tsx               the verification and payment panel for the wall
  catalog/                  FastAPI
    seed_kroger.py          one-time seed from the Kroger API into catalog.json
    seed_openfda.py         OTC names
    catalog.json  profile.json
    search.py
  station/                  Next.js
    voice.ts                Grok Voice session, push-to-talk, tools, transcripts
    persona.ts              instructions, refusal scripts per language
    screen.tsx              large-type companion screen
    receipt.ts              node-thermal-printer via the installed driver; tablet fallback
    replay.ts               cached sessions
  caregiver/                Next.js, served through the ngrok domain
    mandate.tsx             form and passkey signing (SimpleWebAuthn)
    approvals.tsx           alerts, approve, reject
    ledger.tsx
  wall/                     Next.js: mandate card, ledger, merchant panel, metrics
  ai/
    prompts/                persona, cart-structuring schema, judge schema, judge prompt
    rules/                  rules and lexicons
    warnings/               pre-rendered refusal audio per language
  spikes/                   throwaway spike code, one folder per lane
  docs/                     video link, Cursor recording, screenshots (public)
  internal/                 planning docs (to be ignored before the repo goes public)
  sessions/                 sample.jsonl from rehearsal
```

**Stack.** Next.js and React for the station, caregiver and wall apps; FastAPI and uvicorn for the relay, policy engine, merchant and catalog; Python `http-message-signatures` (Ed25519) for signing and verification, or Cloudflare's `http-message-sig` in Node; SimpleWebAuthn v14 for passkeys; `@visaacceptance/mcp` for the sandbox; node-thermal-printer for the receipt; Grok Voice realtime; grok-4.7 and grok-4.20 non-reasoning with structured outputs; the xAI TTS endpoint for pre-rendered refusal audio.

**Setup commands (the README's Run it section).**

```bash
# services laptop
cd relay && uv run uvicorn main:app --host 0.0.0.0 --port 8000
cd policy && uv run uvicorn main:app --host 0.0.0.0 --port 8001
cd merchant && uv run uvicorn main:app --host 0.0.0.0 --port 8002   # MOCK_VISA=1 for the mock
cd catalog && uv run uvicorn main:app --host 0.0.0.0 --port 8003
cd wall && npm run dev -- --host 0.0.0.0 --port 5176
# station laptop
cd station && npm run dev -- --host 0.0.0.0 --port 5173
# caregiver app, through the ngrok domain (same domain every time)
cd caregiver && npm run dev -- --port 5175
ngrok http 5175 --url https://<your-free-dev-domain>
```

**Conventions.** The policy engine is a pure function with no network calls in the allow path; every event carries `t` from the sender and `rt` from the relay; nonces are single-use and stored for 8 minutes; refusal scripts are files, not prompts; feature flags for the fallbacks live in one file the wall can toggle.

---

## Fallback ladder: what to cut and when

Cut from the bottom up; never cut the top rung. Each rung names the trigger, the cut and what the demo still shows.

| Rung | If by this time | Cut | The demo still shows |
|---|---|---|---|
| 1 (never cut) | Always | Nothing | Voice in the shopper's language, a cart read back, the mandate evaluated in code, one refusal with the rule on the wall, one purchase signed and verified, a receipt |
| 2 | Sat 9pm: third language unstable | Hindi (or Spanish); keep two languages | The language claim with two languages |
| 3 | Sat 6pm: sandbox payment cannot be completed with a test card | The "paid" step through the hosted page; the merchant marks the order paid on callback and the Host says so | Payment link created through Visa's sandbox, shown live |
| 4 | Sat 3pm: sandbox credentials have not arrived or Pay by Link is not enabled | The real Acceptance MCP; a mock with the identical tool schema, swapped when credentials land | The full flow with a clearly labeled mock settlement |
| 5 | Sat noon: passkeys fail on the phone (RP ID or HTTPS) | WebAuthn; approve with a six-digit code on the caregiver page, passkey shown in the video | The caregiver approval loop |
| 6 | Sat noon: the printer will not print | Thermal receipt; a large-type receipt on the tablet | The receipt moment |
| 7 | Fri midnight: Grok Voice unreliable | Realtime voice; browser speech recognition, grok-4.7, browser speech synthesis; keep Grok Voice for the refusal line if it works | A talking agent with a second more latency |
| 8 | Fri midnight: the push-to-talk button does not register | The button; the spacebar on a hidden keyboard, or the tablet's tap | Push to talk |

**Rehearsal gate.** A feature stays in the live demo only if it worked in at least 9 of the last 10 rehearsal runs on Saturday evening. Anything else is shown in the video, not at the table.
