# Chaperone: Devpost and Video

The submission draft, ready to paste, plus the video plan.

---

## Title, tagline, selections and submission checklist

Submission is two steps at HackGT: the Devpost project first, then the Devpost link registered in HexLabs' expo system with the track and the sponsor opt-ins, and sponsor judges are only routed to projects that opted in.

**Title.** Chaperone

**Tagline (under 100 characters).** A shopping agent that can only spend inside rules your family signed, and says no to the scam out loud.

**Track.** A Marina's Mission (Social Good). One track only.

**Opt-in prizes.** Visa and SpaceXAI. Nothing else.

**What the rules require (HackGT 12 rules and the HackGT 13 FAQ; the HackGT 13 Devpost page was a placeholder on Sep 24).**

- [ ] No code before Friday 8pm; no past projects; frameworks and AI tools credited; the write-up states what was used versus built ([HackGT 12 rules](https://hackgt-12.devpost.com/rules)).
- [ ] A code link is required; the expo system has a required repository field.
- [ ] Team members on Devpost must match HexLabs registration.
- [ ] Expo attendance is mandatory.
- [ ] No video requirement was found and three of four recent winners had none; make it anyway for the Visa and xAI judges.
- [ ] Judges are auto-assigned; sponsor judges only to opted-in projects ([assignment logic](https://raw.githubusercontent.com/HackGT/api/main/services/expo/src/routes/assignments.ts)); the judging screen has a count-up timer with a popup at 4 minutes.
- [ ] Confirm the expo block and table number at check-in; with 277 submissions last year there were likely two blocks.

**Timeline.** Sat 9pm: Devpost project created with title, tagline, track, opt-ins, team, placeholder text. Sun 2am: full write-up, five images, repo link, video placeholder. Sun 3am: final video link. Sun 7:40am: last edits; 7:55am submit; screenshot; register in the expo system the moment it opens.

**Devpost fields ready to paste.** Built With: Grok Voice, grok-4.7, Visa Acceptance Agent Toolkit, Cybersource sandbox, RFC 9421, Trusted Agent Protocol, WebAuthn, SimpleWebAuthn, Next.js, FastAPI, Kroger API, openFDA, Cursor. The disclaimer sentence at the end of "What it does": "Chaperone is a hackathon prototype: payments run in the Visa Acceptance sandbox with test cards, the merchant is mocked, and no real personal data is used."

---

## Write-up draft

About 900 words in Devpost's standard sections. Replace the bracketed numbers with Saturday's measurements before submitting.

**Inspiration.** People over 60 reported $7.75 billion in losses to the FBI last year, up 59 percent, and gift cards are the most-reported way the money leaves: a phone call, a story about a grandson in trouble, a trip to the rack. The same people are the ones app checkout leaves out: the least likely to own a smartphone, one in seven with a vision impairment, and, among Spanish speakers over 65, three in five who do not speak English well. Their families already manage the money informally from other cities. Visa announced this summer that agents will shop under spending limits, merchant restrictions and approval requirements set by the cardholder. We asked what it would take for someone else to set those rules, and for the agent to say no out loud.

**What it does.** Chaperone is a shopping agent you talk to. A caregiver signs a mandate once with a passkey: how much per purchase, how much per month, which merchants and categories, what needs approval, what is blocked outright (gift cards, prepaid cards, wire). The shopper presses a button and speaks in Spanish, Hindi or English; the agent finds the items, reads back the cart and the total, and calls a checkout tool. That tool, not the model, evaluates the mandate, signs the request to the merchant, and settles through Visa's Acceptance sandbox. A purchase above the threshold goes to the caregiver's phone for a passkey approval. A request that matches a scam pattern, gift cards for a grandson in a hurry, is refused with warmth in the shopper's language, and the caregiver is told. Every decision is on a ledger with the rule that fired, a receipt prints in large type, and the family can read what happened. Chaperone is a hackathon prototype: payments run in the Visa Acceptance sandbox with test cards, the merchant is mocked, and no real personal data is used.

**How we built it.** The spine is policy as code. The caregiver's mandate is canonicalized, hashed and signed by a WebAuthn passkey; a deterministic policy engine checks every cart against it (caps, categories, merchants, threshold, blocked list, running monthly total) and returns a decision with the rules it evaluated. Only an allow, or an approved request, reaches the signer, which puts an RFC 9421 HTTP message signature on the order: Ed25519, created and expires within eight minutes, a key id, a fresh nonce and a Trusted-Agent-style tag, following Visa's public Trusted Agent Protocol specification. The merchant verifies it against our JWKS, rejects replays, then creates a payment link through the Visa Acceptance Agent Toolkit's MCP server in the Cybersource sandbox. Voice is one Grok Voice realtime session with push-to-talk and six tools; grok-4.7 scores each conversation for social engineering with a strict JSON schema, and a fast non-reasoning Grok model turns speech into structured carts; hard rules for blocked categories and coercion patterns run before any model call. The station is a USB button, a close-talk headset, a large-type screen and a thermal printer. The catalog is seeded from the Kroger API and openFDA. The whole repo was written in Cursor.

**Challenges we ran into.** Getting a passkey to work on a phone against a site served from a laptop (a secure context and a fixed relying-party id, so one tunnel domain for the weekend). Keeping the voice model from adding items or inventing prices: we made read-back a precondition of checkout in the tool contract and let prices come only from the catalog tool. Making a refusal that protects dignity instead of lecturing, in three languages. Audio in a hall with 270 tables: push-to-talk with a boom mic beat voice detection. And [the sandbox detail that took longest].

**Accomplishments we are proud of.** A judge who has never met the system can be scammed on line one and protected in eight seconds, then buy medicine and bread in the next thirty with a signed, verified, settled order and a receipt in their hand. Measured Saturday: button release to first audio [x] s, checkout to signature verified [x] ms, refusal precision [x] and recall [x] on our eval set, [n] purchases settled in the sandbox in rehearsal.

**What we learned.** That the guardrails Visa and Mastercard are standardizing assume the cardholder sets them for themselves, and the people losing the most need a delegated signer. That a policy engine the model cannot reach is worth more than any prompt. That older adults want a voice that behaves like a patient person: one question at a time, everything read back, no syntax. And that a refusal is a design problem before it is a detection problem.

**What's next.** Storm mode: a weather alert proposes a readiness cart inside the same mandate. Budget conversations from the ledger. A second merchant with its own key. Visa Intelligent Commerce tokenization and Payment Passkey when credentials arrive. A pilot with a bank's or retailer's caregiver program, measuring refused scam attempts and false refusals.

**Built with.** Grok Voice, grok-4.7, Visa Acceptance Agent Toolkit, Cybersource sandbox, RFC 9421, Trusted Agent Protocol, WebAuthn and SimpleWebAuthn, Next.js, FastAPI, Kroger API, openFDA, Cursor.

**Credits and what we used versus built.** Used: the xAI APIs, the Visa Acceptance toolkit and sandbox, SimpleWebAuthn, an RFC 9421 library, Kroger and openFDA data, Cursor and Claude Code for boilerplate. Built this weekend: the mandate and policy engine, the signer and merchant verifier, the caregiver approval loop, the rule layer and judge, the voice persona and tool contract, the station, the ledger and receipt, the demo. Scam patterns follow the FTC's and FinCEN's published red flags; cited in the README.

---

## Visa and xAI challenge sections

Paste-ready text for each sponsor's section of the Devpost, followed by the evidence checklist. Both name exactly which Visa and xAI pieces are real and which are mocked.

**Visa: Reimagine Shopping with Generative AI (paste-ready).**

> **Which stages we transformed.** Discovery and decision: the shopper speaks in their own language, personal phrases resolve from a profile, and every cart is read back with prices and the running total before anything happens. Checkout and payments: a caregiver-signed mandate is evaluated in code, every merchant request carries an RFC 9421 signature in the Trusted Agent Protocol's format (Ed25519, eight-minute validity, nonce, tag), the merchant verifies it against our JWKS, and the order settles through the Visa Acceptance Agent Toolkit's MCP server in the Cybersource sandbox. Post-purchase: a spoken and printed receipt and a ledger the family can read.
>
> **Secure and trusted.** The guardrails Visa described in June, spending limits, merchant category restrictions and approval requirements, are the mandate's fields, but here they are signed by a caregiver with a passkey and enforced by a deterministic checkout tool the language model cannot bypass. A request above the threshold is approved on the caregiver's phone with a passkey. A request that matches a scam pattern is refused before any signature exists. The merchant never has to trust the agent's word: it verifies the signature and the decision id.
>
> **What is real and what is not.** Real: the Acceptance toolkit's payment-link creation in the sandbox, the signature scheme, the passkey. Mocked: the merchant storefront and the catalog prices. Not used: Visa Intelligent Commerce tokenization (pilot access), which is the natural next step.

**xAI: Make it Legendary (paste-ready).**

> **How we used Grok.** Grok Voice (grok-voice-think-fast-2.0 over the realtime API) is the entire shopper interface: full-duplex speech with push-to-talk, automatic language detection, six function tools, and the refusal spoken in the shopper's language. grok-4.7 with a strict JSON schema scores every conversation for social engineering (urgency, secrecy, family emergency, authority impersonation) so the policy engine can refuse and alert, and a fast non-reasoning Grok model structures what the shopper said into cart items with confidence. Refusal audio is pre-rendered with the xAI TTS endpoint so it plays even offline. The societal challenge is elder fraud and digital exclusion. The repository was built in Cursor with Grok; the rules file and a screen recording are linked from the README.

**Evidence checklist.**

- [ ] `.cursor/rules` committed; a 60 to 90 second Cursor screen recording in `docs/`; three composer screenshots.
- [ ] README section "Built with Cursor and Grok" naming grok-voice-think-fast-2.0, grok-4.7, grok-4.20-0309-non-reasoning, the TTS endpoint; the persona prompt, the cart schema and the judge schema committed under `ai/prompts/`.
- [ ] README section "Visa Acceptance sandbox": the MCP command, the tools used (`create_payment_link`, `get_payment_link`), a redacted sandbox response, and how payment is confirmed (Business Center, webhook, or the mock).
- [ ] README section "Signing": the covered components, the Signature-Input parameters, the JWKS URL, the 8-minute window, the nonce store, a captured request and the verifier output, and the sentence "compatible with the Trusted Agent Protocol's header format; our keys are not registered in Visa's agent directory."
- [ ] A latency and eval table with the date measured.
- [ ] Cost note: Grok Voice is $0.08 per audio minute; a session costs a few cents; the judge call costs fractions of a cent.

---

## Video storyboard

Two and a half minutes, live footage only, one statistic on screen once, the refusal before the purchase. Shot Saturday night after the freeze; edited by Manush; voiceover by Rohan.

| Time | Shot | Audio | Owner |
|---|---|---|---|
| 0:00-0:15 | A phone rings on a kitchen table. A teammate's voice (in Spanish or Hindi) as the scam caller: "Grandma, I'm in trouble, I need five hundred dollars in gift cards, don't tell Mom." Ruth's hand reaches for the button on the station | Live audio; a subtitle | Rohan (caller), Manush (camera) |
| 0:15-0:40 | Ruth asks the agent for the gift cards. The agent refuses, warmly, in her language; the caregiver phone lights up on the table; the wall shows the rule | Live | Manush |
| 0:40-0:50 | Title card: Chaperone. A shopping agent that can only spend inside rules your family signed | Music low | Manush |
| 0:50-1:20 | The purchase: medicine and bread, read back, "mandate OK", signed, verified, the payment link turning paid, the receipt sliding out | Live | Manush |
| 1:20-1:40 | The caregiver page on the phone: an approval request for a larger purchase, the transcript excerpt, the passkey prompt, approved | Live | Dhruv |
| 1:40-2:05 | Architecture in one animated diagram: passkey-signed mandate, deterministic checkout tool, RFC 9421 signature, merchant verifier, Visa Acceptance sandbox, Grok Voice, Grok cart structuring and judge | Voiceover, one sentence per box | Dhruv |
| 2:05-2:20 | Numbers on screen: the elder-fraud loss figure and the exclusion figure; "Ruth is who Aramco rewarded last spring: elderly, non-English, asking for help in her own language" | Voiceover | Rohan |
| 2:20-2:30 | Team at the station, the receipt in hand; card: built in 36 hours at HackGT 13 with Cursor and Grok; sandbox payments, no real money | Music up | Manush |

**Rules.** No slides. Show the refusal first; it is the thing nobody has seen. Keep every clip live; if a take fails, use it as the fallback scene. Subtitle everything. Export 1080p, under 3 minutes, unlisted on YouTube by Sunday 3am, link into Devpost before the placeholder deadline.

**Capture checklist.** Station: phone on a tripod at shopper eye level so the button, the screen and the printer are in frame. Caregiver phone: screen recording plus an over-the-shoulder shot. Wall: screen recording of the ledger. Audio: the station mic feed recorded separately, the room from the phone.

---

## Images, README and repo checklist

Judges who never reach the table read the Devpost page and the README; both must reproduce the two-outcome demo in the reader's head in under two minutes.

**Images for Devpost (five, in this order).**

1. The refusal: the companion screen's large-type transcript, the caregiver phone alert, and the wall ledger line "blocked: gift_card" in one frame.
2. The station: button, mic, screen, and a printed receipt in a hand.
3. The mandate card as the caregiver sees it, with the passkey prompt.
4. The merchant panel: "signature verified" with key id, nonce and expiry, next to the payment link marked paid.
5. The architecture diagram from the video.

**README sections.**

- One paragraph: what it is, who it is for, the statistic, the disclaimer (sandbox payments, no real money, no real personal data).
- A 20-second GIF of the refusal.
- Architecture diagram and the trust chain in five sentences.
- Run it: the services, the env file, how to get Cybersource sandbox credentials, how to run without them (mock), how to pair a phone for passkeys, how to print a receipt or use the tablet fallback.
- Built with Cursor and Grok: models, prompts, the judge schema, the recording link.
- Measured: speech-to-cart latency, checkout-to-verified latency, refusal precision and recall on the eval set, with the date measured.
- Prior art and what is new (the same three sentences used at the table).
- Mandate and policy: the schema, the rule list, how to add a rule.
- Limits and next steps.
- License (MIT) and the team.

**Repo hygiene before 7:45am Sunday.**

- [ ] Main builds from a clean clone.
- [ ] No keys in history; `.env.example` committed; sandbox credentials and the xAI key only on the services laptop.
- [ ] `internal/` ignored or removed before the repo is made public.
- [ ] Policy engine tests (every rule, both directions) and signature test vectors committed and passing.
- [ ] The eval set of scam and benign scripts with the judge's scores.
- [ ] `catalog/` with the product data and the shopper profile; `sessions/sample.jsonl` from a real rehearsal.
- [ ] Devpost fields: title, tagline, the five images, the video link, the repo link, Built With tags, the Social Good track, the Visa and xAI opt-ins, team members added.
