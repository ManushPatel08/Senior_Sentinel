# Chaperone: Judge Q&A

The questions judges will ask in the last minute of the slot, with the answers the whole team gives the same way.

---

## Technical and security questions

Answer in two sentences, then offer to show it on the wall; the ledger and the merchant panel are the evidence.

- *What stops the model from spending?* It cannot. The only thing the model can do is call `checkout`, which runs a deterministic policy engine, and only that engine's allow reaches the signer. The model never holds the key.
- *How is the mandate trusted?* The caregiver's passkey signs a hash of the mandate once. The engine verifies that assertion at load and refuses to run without it, so nobody can edit the limits without the caregiver's fingerprint.
- *What is the signature on the merchant request?* RFC 9421 HTTP message signatures: Ed25519 over the method, authority, path, content digest and content type, with created, an expiry eight minutes out, a key id, a fresh nonce and a Trusted-Agent-style tag. The merchant fetches our JWKS, checks the window, rejects a reused nonce, and checks that the decision id is a real allow on the ledger. Try replaying one; the panel shows the rejection.
- *Is that really Visa's protocol?* It follows the public Trusted Agent Protocol specification's header format and validity rules. Our keys are ours, not registered in Visa's directory, and we sign headers only, because the spec's body-object signing is under-specified. We say exactly that in the README.
- *Is the payment real?* The API calls are real: the Visa Acceptance Agent Toolkit's MCP creates a payment link in the Cybersource sandbox. No real money moves, and the merchant is ours.
- *How does the scam refusal work?* Two layers. Hard rules run before any model call: blocked categories, a third party dictating the purchase, purposes like fines or bail, secrecy, a relative in trouble. Soft signals go to grok-4.7 with a JSON schema that scores the conversation; above a threshold it refuses and alerts. The rule id is on the ledger every time.
- *False positives?* Measured on our eval set, [x] percent of benign scripts were refused. Blocked categories are the caregiver's choice; everything else can be approved by the caregiver in one tap.
- *Why passkeys and not a PIN?* A PIN is a cognitive-function test, which WCAG 2.2 now warns against for authentication; a passkey is a fingerprint. And an assertion over the approval id is evidence, a PIN is not.
- *Latency?* Button release to first audio about [x] seconds; checkout to signature verified about [x] milliseconds on the LAN; payment link in one to three seconds from the sandbox. Refusals are faster than purchases because the rules run first.
- *What breaks without internet?* Live voice, the judge model and the sandbox. Policy, signing, verification, the ledger, the receipt and the cached sessions run on our router.
- *Where do the prices come from?* A catalog seeded from the Kroger API for one Atlanta store and openFDA for the pharmacy items, cached locally. The model never invents a price; it can only read the catalog tool's answer.
- *What did Claude Code and Cursor write versus you?* The boilerplate: the apps' scaffolding, schema validation, the printer glue. We designed the trust chain, wrote the policy engine and its tests, the refusal scripts, the eval set and the demo, and we debugged the audio in the hall ourselves.

---

## Fraud, ethics and business questions

The fraud answers cite the FTC and FinCEN; the ethics answers put the shopper's dignity first; the business answer is that the people who eat scam losses today are the buyers.

**Fraud.**

- *Where do the scam rules come from?* The FTC's published rule that only scammers ask for gift cards, its family-emergency and impersonation guides, and FinCEN's elder financial exploitation red flags: a customer taking direction from someone on a phone, agitation about sending money immediately, unusual gift-card purchases. We encoded those, not our intuitions.
- *Could a scammer coach the shopper around it?* They can coach the words, not the mandate. Gift cards are blocked regardless of phrasing; a coached purchase in an allowed category above the threshold still goes to the caregiver, who sees the shopper's own words. The attack surface is the caregiver's phone, which is the point.
- *What about the caregiver being the exploiter?* FinCEN found a family member involved in nearly half of elder theft cases, so we do not pretend the caregiver is always safe. The shopper hears every rule that fires, the ledger is the shopper's too, mandate changes are signed and logged, and a real deployment would add a second trusted contact who sees changes.

**Ethics.**

- *Isn't refusing an adult's purchase paternalistic?* The limits are set by the person the shopper chose, not by us, and anything can be approved in one tap. What we refuse outright is a category the caregiver blocked. The refusal script never accuses and always offers the legitimate next step.
- *Privacy?* No real personal data in the prototype; audio is not stored; the ledger is local. In a deployment the ledger belongs to the shopper and the caregiver, not to the merchant.
- *Consent?* The shopper consents to the mandate when it is set up, in their language, and can hear it read back at any time. That conversation is the first thing a real product would build.

**Business.**

- *Who pays?* The institutions that eat the losses: issuers and banks (reimbursements, disputes, regulatory pressure that is already mandatory in the UK), retailers (gift-card fraud interventions like Walmart's, which returned $4 million), and insurers and care programs that already sell caregiver cards at $12 a month. Chaperone is the layer those cards lack: voice, language, refusal and approval.
- *Market?* 63 million family caregivers, a quarter of them at a distance; 58 million Americans over 65; $7.75 billion reported lost by people over 60 in one year, with the true figure estimated far higher.
- *Why now?* Visa and Mastercard are standardizing signed agent payments with mandates this year; realtime speech in the shopper's language runs under a second; and the guardrails they describe are written for the cardholder who sets them, not for the people who need someone else to.
- *What exists?* Static caregiver cards, after-the-fact alert services, Alexa's voice purchasing with a spoken code, a human phone line at Instacart. None talk, none refuse, none ask the family.

---

## Visa, xAI and Social Good track questions

The Visa judge wants to know the payment and the trust are real; the xAI judge wants Grok on the critical path; the track judge wants to know who is no longer left behind.

**Visa.**

- *Which Visa products did you use?* The Visa Acceptance Agent Toolkit's MCP server to create and check payment links in the Cybersource sandbox, and the public Trusted Agent Protocol specification for the signature format on every merchant request.
- *Why not Visa Intelligent Commerce?* Its MCP is in pilot and needs VDP credentials, X-Pay tokens and message-level encryption; that is the next step once we have access, and the mandate maps directly onto its payment controls.
- *How does this fit Visa's agentic commerce direction?* Visa's June announcement describes spending limits, merchant categories and approval requirements as the guardrails for agent-led payments. Chaperone is those guardrails, signed by a caregiver, enforced in code, with the refusal path Visa's model does not have yet.
- *Which stages did you transform?* Discovery and decision by voice and profile, checkout by policy, payments by signature and sandbox settlement, post-purchase by spoken and printed receipts and a family ledger.
- *What would a merchant need to accept this?* A verifier: fetch our JWKS, check the signature, window and nonce, and trust the decision id. Ours is about 200 lines.

**xAI.**

- *Where is Grok?* Everywhere the shopper hears or is understood: Grok Voice is the interface, Grok models structure the cart and judge the conversation, and the refusal audio comes from the xAI TTS endpoint. Remove Grok and there is no product, only a policy engine with nobody to talk to.
- *Why not let Grok make the decision?* Because a model can be persuaded and a mandate should not be. Grok proposes and explains; code decides.
- *Cursor?* The whole repo; the rules file and a recording are in the README.

**Social Good track.**

- *Who is left behind today?* The person who cannot use an app: least likely to own a smartphone, one in seven with a vision impairment over 65, three in five Spanish-speaking elders who do not speak English well, and the family two hundred miles away who gets the call after the money is gone.
- *What is the impact?* A scam refused at the moment of coercion instead of a loss reported later; a purchase that was impossible without a smartphone now made by speaking; a family that sees what happened. The ledger counts all three.
- *Real-world potential?* The buyers already exist: caregiver cards, bank fraud teams, retailers fighting gift-card scams at the register. We plug into the sandbox those institutions already use.
- *Why this track and not ML?* Because the point is the person at the station, not the model; the mechanism is policy, signatures and a voice that says no kindly.

---

## Weak points and how to answer them honestly

Judges reward a team that names its own limits first. Each weak point has the honest answer and the one thing done about it.

| Weak point | Honest answer | What we did about it |
|---|---|---|
| "It is Alexa with parental controls" | Alexa cannot sign a mandate, refuse a scam, ask your son, or prove to a merchant that it was allowed to buy. The guardrails live in code below the model and every request is signed; that is the product | The trust chain is on the wall, not in the pitch |
| The model could be talked into anything | It can be talked into proposing anything; it cannot spend anything. Checkout is a deterministic function of the cart and the mandate, and the merchant verifies a signature the model never holds | Policy engine unit tests and a live "try to jailbreak it" invitation |
| Scam refusals will insult the shopper or block real purchases | Blocked categories are the caregiver's choice, not ours; soft patterns go to a judge, not straight to a refusal; the refusal script is written to protect dignity; the caregiver can approve anything the shopper genuinely wants | Refusal wording in three languages, an eval set of benign scripts with the false-refusal rate |
| No real money moves | Correct: the Visa Acceptance sandbox and test cards. The API calls, the signatures and the settlement flow are the real ones; the card is not | Sandbox responses shown live on the wall |
| Passkeys and mandates are heavy for a caregiver | Setup is once, five fields and one fingerprint; approvals are one tap. Compare with what caregivers do today: sharing a card number | The caregiver page is shown in the video at real speed |
| Voice assistants have not worked for older adults | Ours does not ask them to learn commands: press a button, speak as you would to a person, in your language, and everything is read back before anything happens | Read-back is mandatory in the persona |
| Who is liable when it refuses wrongly or approves wrongly | The mandate is the caregiver's instruction and the ledger records exactly what was heard, decided and signed; a real deployment sits inside a bank's or retailer's existing dispute process | Ledger with rule ids and signature ids |
| Only one merchant | One merchant with a verifier is enough to prove the protocol; a second key is a P1 | Second merchant if time allows |
| We are not fraud experts | The rules come from the FTC's and FinCEN's published red flags and retailers' own gift-card interventions; the judge model is a second opinion, not the law | Sources cited on the table card and in the README |
| Built in 36 hours | It was. The two-outcome loop works end to end; the rest is in the plan | Nothing half-working is shown |

**Phrases to avoid.** "Detects scams" (say "refuses these patterns and flags the rest"), "secure" without saying what is signed, "AI-powered card", "users" for the shopper (say "Ruth" or "the shopper"), "it always works".
