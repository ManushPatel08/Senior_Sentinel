# Devpost submission (paste-ready)

## Project name (60 max)

Chaperone: The Scam-Proof Shopping Agent for Grandparents

## Elevator pitch (200 max)

A voice shopping agent for older adults that only spends inside rules their family signed, stops scams at the phone call and at the card, and works in their language on any phone.

---

## About the project

## Inspiration

Last year, Americans over 60 reported **$7.7 billion** in losses to fraud ([FBI IC3, 2025](https://www.housingwire.com/articles/fbi-seniors-cybercrime-2025/)). The pattern is painfully familiar: a call from a "grandson" in jail, a "lawyer" who needs the bail within the hour, and a trip to a Bitcoin machine or the gift-card rack. The same people are often the ones today's shopping apps leave behind: older adults, people who don't read English comfortably, people without a smartphone. Their families already help with the money, just informally, from other cities, by phone.

Agentic commerce is arriving with spending limits, merchant restrictions and approvals, but those controls assume the cardholder sets them for themselves. We asked: what if a family could set them together, and the agent could say **no to the scam, out loud, in Grandpa's own language**?

## What it does

Chaperone is a shopping agent for an older adult (in our demo, Grandpa Ruthvik, "Ruth") and his caregiver (his grandson Priyank). It covers the whole journey, **discover, decide, transact, continue**, behind four guards:

- **Ask: a scam check on the call.** Grandpa describes a call ("my grandson is in jail and needs bail, don't tell Mom") to the kiosk or on the phone. Chaperone recognizes the scam in English, Spanish or Hindi, checks it against his own accounts ("your Peachtree Power bill is paid, so this call is a scam"; "call Alex at the number you have saved") and recent scam reports, speaks a calm two-sentence answer, and puts his card on a 24-hour cool-down. Priyank gets the alert with the sources and a plain-English **Why?**.
- **Card: every swipe checked.** Grandpa's card is authorized in real time by our rules. The card never pays gift-card kiosks, crypto machines or money transfers. During a cool-down, a $480 charge at a drugstore is declined, and Chaperone tells Grandpa why. Priyank can **Allow once** or **Keep blocked**. The rules are mirrored to Visa Transaction Controls.
- **Agent: errands inside signed rules.** "My blood pressure medicine, denture adhesive, and pay my power bill." Chaperone finds products (his usual items first, anything else live from Kroger), reads the cart back **store by store**, and on a clear "yes" places one signed order per store. Each store verifies the signature before taking the order. Payment runs through Visa Acceptance, and every order gets a Visa Decision Manager risk score. Anything over the approval line waits for Priyank's passkey.
- **Family: rules signed together.** Priyank signs the rules (stores, categories, limits, card rules) with a passkey. Chaperone reads them to Grandpa, and his spoken "yes" is recorded beside them.

After checkout: pickup codes, order status, cancellations, returns and refunds only to the card that paid, bills, rewards points, and a receipt with a QR code to a public page of the session's story. **The Trust Ledger** wall shows every decision live, in four lanes, with a **dollars protected** counter.

No smartphone? Grandpa can **call a phone number** and do all of this by voice, entering his PIN by voice or on the keypad.

*Everything runs in sandboxes with test cards; no real money moves.*

## How we built it

- **Voice.** The kiosk talks through Grok Voice in real time. The phone line is an agent in xAI's Voice Agent Builder calling our own MCP server, with a PIN spoken or typed on the keypad.
- **Guardrails outside the model.** The model never decides a payment. A policy service (FastAPI) re-prices every cart from the catalog and applies the signed rules deterministically: stores, categories, caps, approval threshold, monthly budget. A multilingual rule lexicon (English, Spanish, Hindi and Hinglish) screens every request. A Grok judge only weighs the ambiguous ones.
- **Scam radar.** Grok's Responses API with X search and web search, under one time budget. A known scam gets its answer in under a second, and the sources for the caregiver's alert are fetched in the background.
- **Signed intent.** The caregiver's passkey (WebAuthn) signs a canonical (JCS) hash of the rules. Each agent request to a store is signed with RFC 9421 HTTP Message Signatures in the Trusted Agent Protocol header format, and each store verifies it against our JWKS. The rules are also expressed in Visa Intelligent Commerce's `mandates[]` shape.
- **Payments.** Visa Acceptance (Cybersource) sandbox Pay by Link, on four separate sandbox merchant accounts (grocery, pharmacy, home goods, power company), with Decision Manager scoring each order. Webhooks are signature-verified per account.
- **Card.** A sandbox card on Lithic with Auth Stream Access: our service approves or declines each swipe in under a millisecond, about a second end to end. The rules are mirrored to the Visa Transaction Controls sandbox over two-way SSL.
- **Catalog.** The Kroger Products API, live for anything our curated list doesn't carry, with real store prices; openFDA for over-the-counter medicines.
- **Caregiver app.** Next.js on the caregiver's phone: passkey approvals, a Safety feed, card holds, rules, weekly activity, and live alerts over server-sent events.
- **Trust Ledger.** Every service posts events validated against a JSON Schema contract to a relay, which drives the wall, the caregiver's alerts and the public session page.
- **Tests and evaluation.** More than 900 automated tests. The scam evaluation covers 102 scripts in four languages. On the held-out half, rules plus Grok caught 25 of 25 scams and wrongly refused 1 of 24 honest requests. The scripts were written alongside the rules, so treat that as in-sample.

We built it in 36 hours with AI coding assistants (Claude Code and Cursor).

## Challenges we ran into

- **Keeping the agent from being talked into things.** Voice models are agreeable. We moved every money decision out of the model: a read-back gate, a fresh "yes" required after the read-back, deterministic pricing, and rules the model can't edit.
- **False positives versus real scams.** "Buy a gift card for someone at church" is a request to refuse kindly; "my grandson called from jail, don't tell Mom" is a scam; "don't tell Mom, it's a surprise party" is fine. Getting that right in Hindi, in Devanagari and Hinglish, took a lot of care.
- **Sandbox reality.** Card authorizations on our Cybersource sandbox account failed with a processor configuration error, so we paid through Pay by Link and a card-network sandbox instead. Visa Intelligent Commerce's API needs pilot credentials, so we modeled its mandate shape rather than calling it.
- **Latency.** A scam check has to answer while Grandpa is still on the phone with the scammer: one time budget, fast answers from the rules, a late model answer kept for next time.
- **Multi-store checkout.** One "yes" can place orders at a pharmacy and a power company, each separately signed, verified, paid and refundable.

## Accomplishments that we're proud of

- The whole journey works end to end on real sandbox calls: Visa Acceptance, Decision Manager, Visa Transaction Controls, a card network's real-time authorization and Kroger's live catalog.
- A phone number anyone can call, with no app needed, in three languages.
- The refusal is kind: it never blames Grandpa, and it always tells him the one thing to do next.
- Trust is visible: every decision has a plain-English reason for the family and a public record.

## What we learned

- In agentic commerce, trust comes from **who sets the rules** and from making every "no" understandable, not from a smarter model.
- Deterministic guardrails around a language model are what make it safe to hand it a wallet.
- Evaluate honestly: our numbers are strong but in-sample, and we say so.

## What's next for Chaperone

- Run on a real issuer's card controls (Visa Transaction Controls in production) and join the Visa Intelligent Commerce pilot, so the mandate travels with the payment.
- Pilot with a senior center and families, test with older adults, and add more languages.
- Let several family members share caregiving, and bring in pharmacies and utilities directly.

---

## Built with (25 max)

python, fastapi, typescript, vite, next.js, react, node.js, grok, xai-grok-voice, xai-voice-agent-builder, model-context-protocol, visa-acceptance, cybersource, visa-decision-manager, visa-transaction-controls, lithic, kroger-api, openfda, webauthn, simplewebauthn, rfc-9421, json-schema, ngrok, cursor, claude-code

---

## Technology feedback

- **xAI Grok Voice and the Voice Agent Builder.** Great voice quality and fast turn-taking, and multilingual out of the box. Connecting our own MCP server was easy. Pain points:
  - A server that answers 401 is treated as OAuth-only, so we had to put the token in the URL.
  - Tools marked as "write" are off by default, which silently broke our PIN tool until we noticed.
  - Keypad (DTMF) input arriving as text worked well once we tested it; it would help to document it for Builder phone numbers.
- **Grok Responses API with X search and web search.** Excellent for current scam reports with real citations. Latency varies from about 1 to 6 s, so we needed a time budget and caching.
- **Visa Acceptance / Cybersource sandbox.** Pay by Link and Decision Manager worked well across several sandbox accounts. Direct card authorizations failed with reason 150 (a processor outlet and terminal configuration error) on a fresh sandbox account; clearer sandbox processor setup would save teams hours.
- **Visa Developer (VTC).** Two-way SSL setup is well documented, but it takes time at a hackathon.
- **Lithic sandbox.** Auth Stream Access is a great fit for real-time card rules. A transaction isn't retrievable for about a second after a simulated authorization.
- **Kroger API.** Real store prices and stock are great. Price needs a location id, and search is loose ("bananas" returns banana peppers), so we filter results.
- **ngrok (free).** The browser interstitial page confused testers on phones until we sent the skip header.

---

## Did you implement a generative AI model or API in your hack this weekend?

Yes. We used xAI's Grok throughout, always inside deterministic guardrails:

- **Grok Voice (real-time)** is the kiosk's voice, so an older adult can shop by speaking in English, Spanish or Hindi.
- **xAI's Voice Agent Builder** answers a real phone number and calls our MCP server's tools, so people without smartphones can use Chaperone.
- **The Grok Responses API with X search and web search** is our scam radar: it checks a caller's story against recent reports and returns a short answer with citations for the caregiver.
- **A Grok judge** weighs ambiguous requests that our multilingual rules can't settle.
- **Grok explanations** turn every decision into a plain-English "Why?" for the caregiver.

We used it because the people we're building for need a natural voice in their own language, and scams change weekly. Grok never authorizes a payment: prices, rules, signatures and payments are deterministic, and model outputs are schema-validated and screened before anyone sees them. We also used Claude Code and Cursor as coding assistants.
