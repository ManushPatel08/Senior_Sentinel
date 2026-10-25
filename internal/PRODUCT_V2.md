# Senior Sentinel v2: a real product, and the plan to the expo

As of Sat Sep 26, 4:00pm. Written after the team's review ("bigger scope, a finished product, it must make sense, fit the tracks, better UI, too many 'One moment's, it sounds like a Kroger assistant, the safety angle isn't evident") and Manush's question: **how does this actually save anyone from a scam, what happened before, what happens after, and how does it fit into real life?**

Six research threads fed this: a code audit, the track and challenge text, Visa's current APIs, xAI's current APIs, the elder-fraud market, and how scams and card controls work in practice. Sources are in Section 11.

Nothing here has been built yet. Section 10 lists the decisions we need before anyone starts.

---

## 0. The short version

**The honest problem with v1.** Senior Sentinel only protects purchases made *through Senior Sentinel*. A real scammer never says "ask your shopping assistant to buy gift cards." They keep Ruth on the phone and send her to a drugstore with her own debit card, or have her read out card numbers, withdraw cash for a crypto ATM, or install remote-access software. In v1 our refusal happens on a road the scammer never takes. That is why it doesn't yet feel like it saves anyone.

**v2 in one sentence.** Senior Sentinel is an AI that runs an older adult's errands and payments by voice, in her language, and **guards every place her money can leave: the conversation, her card and her agent**. The rules are ones she and her family sign together.

**The four guards:**

| Guard | What Ruth sees | What stops the scam |
|---|---|---|
| **Ask** (the conversation) | She calls Senior Sentinel on any phone, or talks to it at home: "Peachtree Power says they'll cut my power tonight unless I pay $480 in gift cards." | Senior Sentinel checks her real bill (it's paid) and today's scam reports (Grok searching X and the web), then says plainly: "This is a scam. Please hang up. Shall I call Priya?" Priya's phone shows it, with sources. |
| **Card** (her Visa card) | She goes to the drugstore anyway, coached by the caller. The terminal declines $480. | Every swipe is checked against the signed rules in under a second. After a scam call the card is on a 24-hour cool-down for risky spending. Senior Sentinel tells Ruth why; Priya can allow it once with one tap. |
| **Agent** (errands) | "Order my blood pressure medicine and pay my power bill." | The agent buys only from verified stores and billers, only inside the rules, with signed requests. It can't be talked into gift cards, wires or fake "refunds". |
| **Family** (co-signed rules) | Ruth and Priya agree the rules together; Ruth can hear them any time. | Priya approves exceptions and sees every blocked attempt with a plain reason. 72% of elder financial exploitation is by someone the victim knows, so neither of them can change the rules alone. |

The link between the guards is what makes it work: **the conversation informs the card.** A scam story heard by Senior Sentinel puts Ruth's card into a cool-down before she reaches the store. The research says "active call plus payment attempt" is the strongest scam signal anyone can get (Section 2.4).

**What changes tonight:**
- A real phone number Ruth can call (Grok Voice over SIP).
- A real card round trip: Lithic's issuing sandbox calls our rules on every simulated swipe.
- A live scam radar (Grok with X and web search, with citations).
- Several stores and a biller instead of one Kroger-like shop.
- A caregiver app that looks like a product.
- A redesigned station and wall.
- A landing page with a business model.
- The "One moment" fix.

The details are in Section 5.

---

## 1. What we heard, what the audit found, and the fix

| Feedback | Root cause in the code | Fix |
|---|---|---|
| "Says 'One moment' a lot" | `station/config/voice.json:39` tells the model to say "One moment." / "Un momento." / "एक मिनट।" before searching. In practice it says it before every tool call, because each chained tool is a new model turn. It was added on purpose, to cover the ~1.5 s screen wait and the catalog call. The approval line also ends with "One moment, please." (`ai/prompts/lines.*.json:3`) | Remove the rule and tell the model to call tools silently. The station plays a soft earcon and shows "Checking…" while tools run. The one long wait, the scam radar, gets a single natural line ("Let me check that for you"). Rewrite `asking_priya`. |
| "It acts like a Kroger-only assistant" | One catalog of 323 items, all `merchant: corner_market`, with 119 Kroger-brand items. The prompt says "cheapest first", which is usually a Kroger store brand. There is no store parameter on any tool. The mandate allows only `["corner_market"]`. | Ruth's agent, not a store's. Several merchants (grocery, pharmacy, household, a utility biller), each with its own storefront, Visa sandbox account and signature check. Search across stores, name the store, prefer her usual and then the best price. The persona says it works for Ruth. |
| "The safety angle isn't evident" | Safety exists but is hidden or raw. The judge's score never reaches the ledger in the real flow. Soft "caution" signals are never shown or posted. Refusals from the screen don't alert Priya and have no "Why?". The station, wall and session page show raw ids like `R1_blocked_category`. Caregiver alerts say only "Ruth was refused." Pause isn't shown anywhere Ruth looks. | The four guards above. A "Protected" moment on every surface, in plain words. A Safety tab for Priya with reasons, sources and one-tap "Call Mom". A protected-dollars counter. Every blocked attempt alerts Priya with a "Why?". |
| "Should feel like a finished product / startup" | The station defaults to operator view with Hardware and Services panels. Status text like "Token received (valid 300 s)" shows. The caregiver app uses inline styles and native buttons, shows a debug `<pre>` log to Priya, prints "$142.1", and "Call Ruth" has no number. The wall reads like a debug log. There is no brand, landing page or business model. | One design system and a logo across every surface, plus a landing page with pricing and a "for banks" section. Operator panels move behind `?operator`. The caregiver app is rebuilt as a mobile app. The wall becomes a readable Trust Ledger. |
| "It must make sense, not features without logic" | Features were added stage by stage for Visa's rubric (pickup codes, points, timers) without one story tying them together. | Every feature has to answer "which guard, which scam, which person." Section 3.4 lists each feature with its reason; anything without one is demoted or cut. |
| "Focus on the tracks" | The story was "shopping agent with guardrails". | Section 4 maps each judge's words to a moment in the demo. |

---

## 2. How a scam works today, and where Senior Sentinel stops it

### 2.1 The numbers we'll use

- **Losses:** people 60+ lost **$7.75B** to reported scams in 2025, up 59%. That's 201,266 complaints, an average loss of $38,500, and 12,444 people losing over $100k. Of that, $1.04B was tech-support scams and $4.35B involved crypto (FBI IC3 2025).
- **Phone calls:** among older adults who lost $10k or more to impersonators, **41% of cases started with a phone call**. They paid by Bitcoin ATM (33%), bank transfer (20%), cash (16%) and gold (5%) (FTC, Aug 2025).
- **Gift cards:** gift cards are the most-reported payment method for tech-support, government-impersonation and family-impersonation scams against older adults, and appear in 16% of their loss reports (FTC, Dec 2025).
- **Hidden losses:** the FTC estimates the real cost to older adults at $10B–$81.5B a year, because most losses go unreported.
- **People they know:** **72%** of elder financial exploitation ($20.8B of an estimated $28.3B a year) is by people the victim knows (AARP; 2023, older).
- **Caregivers:** there are **63M** US family caregivers. **81% help with shopping and 58% manage finances** (AARP/NAC 2025).

### 2.2 One scam, minute by minute: before and after

**The scam:** "Peachtree Power" says Ruth's power is cut off tonight unless she pays. It's a real pattern: FTC and IC3 list utility impersonation and gift-card payment.

| Time | **Before (today)** | **After (with Senior Sentinel)** |
|---|---|---|
| 6:02pm | A caller says he's from Peachtree Power: $480 overdue, power cut at 7pm, "stay on the line, don't tell anyone". | Same call. Ruth has the fridge card: *"Before you pay anyone, ask Senior Sentinel."* She says, "Wait, I need to ask my helper." |
| 6:04 | He tells her to drive to the drugstore and buy Apple gift cards. | Ruth asks Senior Sentinel (station, or the Senior Sentinel Line from her landline). Senior Sentinel checks her Peachtree Power account: **paid through October**. The radar finds **this exact script reported in Atlanta this week**, and the rules know **utilities never take gift cards**. In Spanish: "This is a scam. Your bill is paid. Please hang up. Shall I call Priya?" |
| 6:05 | — | Priya's phone: **"Senior Sentinel stopped a scam call: fake Peachtree Power, $480 in gift cards"**, with sources and **Call Mom**. Ruth's card goes on a 24-hour cool-down for risky spending. |
| 6:25 | She buys $480 of gift cards with her debit card. The cashier doesn't ask; fewer than half of stores have limits, and store measures fully stop only about 9% of such purchases. | Suppose the scammer called back and she went anyway. At the register, **her card declines**: a pharmacy purchase far above her usual, during a cool-down. The station or her line: "I stopped a $480 charge at Five Points Drug. Is someone asking you to buy gift cards?" Priya gets **Keep blocked / Allow once**. |
| 6:30 | She reads the card numbers over the phone. The money is gone in minutes. | Nothing to read. Nothing lost. |
| Days later | Priya sees the statement. Recovery is near zero, the bank's dispute needs evidence nobody kept, and the family takes Ruth's card away. | Ruth keeps her card and her independence. The incident is in a **dispute-ready record** in case anything did get through. |

### 2.3 The big elder scams: where each guard acts, and what we can't do

| Scam (2025 losses, 60+) | How it works | Ask | Card | Agent | What we can't stop |
|---|---|---|---|---|---|
| **Tech support / "phantom hacker"** ($1.04B) | Pop-up or call → remote-access app → fake bank "fraud team" → "move money to a safe account" by wire, crypto ATM or gold | "A man from Microsoft wants me to install AnyDesk" → scam, don't install, Priya told | Transfers (MCC 4829), quasi-cash (6051) and large ATM withdrawals held; cool-down after the call | Agent never pays "tech support" or buys gift cards | Gold or cash handed to a courier; a wire at a branch (the bank partner's teller hold covers that, via FINRA 2165 or state hold laws) |
| **Government / utility impersonation** ($413M; complaints nearly doubled) | Call or text → pay now by gift card, crypto ATM or payment app, kept on the line | Checks the real bill or agency facts plus live reports → "hang up" | Gift-card-like pattern: a first large pharmacy or big-box purchase during a cool-down | Pays the real biller only | If Ruth never asks and pays cash at a kiosk |
| **Grandparent / voice clone** (a fast-growing "distress" pattern) | Cloned voice plus a "lawyer" → bail by cash courier, gift cards or wire; "don't tell your daughter" | Secrecy plus urgency → "Let me call Alex on the number Priya saved" | Cool-down on transfers and cash | — | A courier collecting cash at the door |
| **Refund / overpayment** ($8M reported; underreported) | Fake "we refunded too much" → send back the difference in gift cards or a wire | Refund-scam rules (built) plus radar | Same card pattern | Refunds only go back to the card that paid (built) | — |
| **Romance / crypto investment** ($3.5B+; long grooming) | Months of chat → a fake platform → growing transfers | "Is this investment real?" → radar plus a plain warning | First transfer to an exchange blocked (6051); Priya approves any exception | — | A determined, willing victim. We add friction and family, not a guarantee. |

**Honest limits, said out loud at the table:**
- **Gift cards are not visible at the card level.** A drugstore purchase is a drugstore purchase; True Link says so too. We infer from amount, merchant type, Ruth's history and the cool-down.
- **Priya can't approve inside the card network's 2–6 s window.** The industry pattern is decline → confirm → retry within a window. That's what we build.
- **Senior Sentinel can't hear the scammer's call** unless Ruth asks. The habit comes from daily use (errands, bills) and the fridge card. Future versions could add carrier call-screening (Grok SIP can answer calls) or Android's in-call signal.

### 2.4 Why these interventions work (evidence)

- **Talking to someone first:** targets who knew about the scam lost money 9% of the time, against 34% for those who didn't. Those who talked it over with anyone lost less (FINRA Foundation/Stanford, 2019, older). Senior Sentinel is the someone who always answers and knows this week's scams.
- **A specific action beats a warning:** a "cancel this payment" button cut fraudulent payments from 22% to 10%, and to 4% with a risk warning. Generic warnings alone didn't work, and showing one twice backfired (Behaviouralist/Open Banking, n=10,000, 2021). So Senior Sentinel gives one clear action ("hang up; shall I call Priya?"), not a lecture.
- **Friction at the moment of payment works in the real world:**
  - CommBank's scam losses are down 76% from the 2023 peak, with NameCheck and CallerCheck.
  - Android now pauses banking apps during calls from unknown numbers (UK and US pilots).
  - Singapore banks can apply 24-hour cooling holds.
  - The UK Banking Protocol prevented £59M in 2025.
- **Active call plus payment** is the strongest signal. It's why Osaka banned phone calls at ATMs for people 65+, and why our cool-down exists.

---

## 3. The product in real life

### 3.1 Who uses what

| Who | How they use Senior Sentinel | Built as |
|---|---|---|
| **Ruth**, 71, Spanish at home, landline, low vision | **Senior Sentinel Line:** a phone number she calls from any phone. **Senior Sentinel at home:** a speaker or tablet with one big button. Both are the same agent, in her language. | Grok Voice (realtime); SIP for the phone line; the station for home |
| **Ruth's card** | Her Visa debit card, enrolled in Senior Sentinel protection through her bank, or a Senior Sentinel Visa card | Demo: a Lithic sandbox card whose every swipe calls our rules. Production: an issuer partner using **Visa Transaction Controls**, or a card program on Visa |
| **Priya**, 44, Atlanta, 200 miles away | App on her phone: set rules *with* Ruth, approve exceptions, the Safety feed, a weekly digest. Alerts only when it matters. | Caregiver PWA, passkey signing |
| **Stores and billers** | Accept Senior Sentinel's purchases as a **recognized agent**: signed requests they can verify, paid through Visa | Our merchants: TAP-style RFC 9421 signatures; Cybersource sandbox Pay by Link per merchant |
| **The bank** (the customer who pays) | Offers Senior Sentinel to account holders and caregivers. Gets fewer scam losses, a dispute-ready record and deposit loyalty. | Trust Ledger and the record export; VTC rules |

### 3.2 A normal month

1. **Setup, 15 minutes.** Priya invites Ruth. They choose the rules together in plain words: "Up to $60 a trip at the grocery and pharmacy. Ask me above $40. Never gift cards, wires or crypto. Pay Peachtree Power up to $200." Priya signs with her passkey, and Ruth confirms by voice. They link Ruth's card, stores and power bill, and Priya adds trusted contacts (grandson Alex). Ruth gets the fridge card with the Senior Sentinel Line number.
2. **Every week.** Ruth calls or talks to Senior Sentinel for groceries, refills and household items, compared across her stores. It reads everything back before paying. Priya gets a quiet digest, not a buzz per purchase, because notification fatigue is real.
3. **Bills.** "Pay my power bill": Senior Sentinel reads the real balance and pays the real biller, inside the rules.
4. **After a purchase.** Order status, cancel, returns, and refunds only to the card that paid. All of this is built.
5. **The scam day.** Section 2.2.
6. **Changing the rules** needs both of them. Ruth hears every change. This protects Ruth from the helper too: the 72%.

### 3.3 Why each feature exists

| Feature | Guard | Why it's there |
|---|---|---|
| Voice in her language, landline number | Ask, Agent | Adults 65+ are the least likely to own smartphones; about 10M don't speak English "very well". The phone is where scams start, so it's where help should be. |
| Errands and bills by voice | Agent | Daily usefulness builds the habit and the trust that make "ask Senior Sentinel" natural on the scam day. It's independence, the Social Good core. |
| Several stores and a biller, compared | Agent | Senior Sentinel works for Ruth, not a store. The biller also answers the most common scam story: "your bill is overdue". |
| Scam radar with citations | Ask | Scams change weekly, and Grok reads X and the web in real time. Older adults trust concrete facts, not scores (Georgia Tech, CHI 2026). |
| Account truth checks (bill balance, trusted contacts) | Ask | The best counter to impersonation is the truth: "your bill is paid", "Alex's real number". |
| Card rules and 24-hour cool-down | Card | That's where the money actually leaves. |
| Decline → Priya "allow once" → retry | Card, Family | The only honest way to put a human in a card decision. |
| Co-signed rules; changes need both | Family | Supported decision-making (laws in 25 states plus DC), and protection from the helper. |
| Signed agent requests, verified stores only | Agent | Agents will be targeted with fake storefronts (Visa's own threat report); a signature proves the agent is inside the mandate. |
| Returns and refunds only to the paying card | Agent | Refund scams are the second path; built. |
| Dispute-ready record | All | When something does get through, the bank claim has evidence. |
| Pickup codes, points, savings | Agent | Kept, but minor. Not demo beats. |

### 3.4 The business

- **Who pays:**
  - **Banks and credit unions** (primary): offered as a caregiver feature on existing Visa debit cards, priced per protected account, and enforced through Visa Transaction Controls. Why they buy: **70% of caregivers would move deposits to a bank with good caregiver support** (True Link survey, Dec 2025); only about 20% of banks offer delegated access (Keynova Q4 2025); and scam-reimbursement pressure is rising (the UK now mandates it).
  - **Families directly:** $14.99 a month, in line with True Link's $12, EverSafe's $7.49–24.99 and Carefull's $29.99.
- **Precedents for this channel:**
  - Edward Jones gives Carefull free to about 9M clients and invested in it (Jun 2026).
  - Huntington white-labels True Link's controls.
  - State aging agencies pay for ElliQ.
- **Competitors and what they lack:**

  | Company | What it does | What it lacks |
  |---|---|---|
  | True Link | Card controls, $12/mo | No agent, no voice, can't see the conversation, "can't block gift cards" |
  | Carefull, EverSafe | Monitoring | Only after the fact |
  | ElliQ, Meela | Companions | They don't pay for anything; Meela's rides are booked by humans, with no limits |
  | Call screeners | Screen calls | Never touch the money |
  | Big tech | Apple Ask to Buy, Google Family Link | Built for minors |

  Alexa Together was shut down; direct-to-family monitoring alone is hard.
- **The whitespace:** nobody combines an agent that actually pays with co-signed limits and scam refusal inside the conversation.
- **Moat:** the link from conversation to card (the scam story sets the card's cool-down), a multilingual voice, and trust native to Visa (TAP-style signatures, the mandate in Visa's format, VTC).
- **Validation tonight:** interview 15 HackGT attendees and mentors ("Has an older relative been targeted? Would you set this up?") and put the numbers and one quote in the Devpost. The HackMIT Visa winner did this and cited it.

---

## 4. How it answers each judge

| Judge | Their words | Our answer at the table |
|---|---|---|
| **A Marina's Mission** (Social Good, presented by Aramco) | "Technology that makes a real difference … a problem that hits close to home" | Every team has a grandparent who got a scam call. We show a scam stopped at the call and at the register, and an older adult keeping her card. The metric is dollars protected, on the wall. |
| **Visa: Reimagine Shopping** ($5,000) | A GenAI commerce experience that is "intuitive, personalized and frictionless … while enabling secure and trusted payments"; discovering, comparing, managing budgets, completing purchases; stages from Discovery to Post-purchase. The HackGT briefing added "Make trust visible" and "beyond retail: accessibility". | **Discover/Decide:** compare across stores, her usual, her budget. **Transact:** mandate-bounded, a signed agent request per merchant, Visa sandbox Pay by Link per merchant, and the mandate in Visa Intelligent Commerce's exact `mandates[]` shape. The instruction API itself needs pilot credentials; we probe it and say so. **Continue:** bills, status, cancel, returns and refunds to the original card. **Trust visible:** the Trust Ledger and the card rules (VTC is Visa's issuer path). **Beyond retail:** bills, pharmacy, and a phone line for people without smartphones. |
| **SpaceXAI: Make it Legendary** (Cursor keyboards) | Must use Grok Voice or Grok Imagine; built with Cursor ("the more you use Cursor, the more likely you are to win"); related judging values usefulness ("would a real person want this tomorrow"), beauty and craft, and "the ambitious one" | Grok is the whole interface: at home and **on a real phone number judges can dial**. Grok is the **live scam radar** (X plus web search, with citations), the judge and the explainer. The build trail comes from Cursor. **Action: the team must actually build in Cursor tonight and screenshot it.** |
| **Best Overall** | Past winners: a real problem, something physical, a live dashboard, one clear metric | Phone, station, card terminal, Priya's phone, printed receipt, and "$480 protected" on the wall. |

Still to confirm on live.hexlabs.org (it needs a login): the submission deadline (8am Sunday vs Devpost's noon), whether there's a cap of two sponsor challenges, and whether we get one general track.

---

## 5. What we build tonight

Four workstreams, one per person. Each teammate uses their assistant to go wide. The shared contracts (Section 5.5) are agreed at the Phase 5 kickoff so the pieces meet.

### 5.1 Manush: Ruth's voice (station, persona, Senior Sentinel Line)

1. **Persona and prompt rewrite**, with Rohan (`station/config/voice.json`):
   - Senior Sentinel works for Ruth across her stores and bills, and names the store.
   - Her usual first, then the best price.
   - No preambles; call tools silently.
   - One short sentence at a time; one clear action in any safety moment.
   - Any mention of a caller, a text, or someone asking for money, gift cards, a transfer, a refund or remote access → call `scam_check` first.
2. **Filler fix:**
   - Remove the "One moment" rule.
   - Play a soft looping earcon while tools and the screen run, and show a "Checking…" state.
   - Rewrite `asking_priya` without "One moment, please".
   - Re-measure release-to-first-audio.
3. **New tools:**
   - `scam_check(story, caller_claims, phone_number?)`
   - `bill_status(biller)` and `pay_bill(biller)`
   - Store-aware `search_catalog` (returns the store and a price comparison)
   - Speaking card events: when the card guard declines, the station or line tells Ruth why.
4. **Station redesign (kiosk):**
   - Shopper view by default, with operator panels behind `?operator`.
   - Brand, big captions and one state at a time (Listening, Checking, Asking Priya, **Protected**).
   - A full-screen "Protected" card when a scam is stopped: shield, plain reason, what to do, "Priya knows".
   - A cart grouped by store and per-store receipts.
   - Remove debug text from shopper view: "Token received", raw rule ids, `order o_… · decision d_…`, the Spanish placeholder.
5. **Senior Sentinel Line** (spike 60 min in Phase 5; go/no-go at 7:30):
   - **Path A:** xAI Voice Agent Builder, which comes with a free US number, using our tools exposed through a remote MCP server (with Vraj).
   - **Path B:** the SIP webhook plus a server-side agent (the `?call_id=` WebSocket) reusing the station's tools.
   - The line and the station share the same policy, cart and scam checks. On the phone, safety is enforced in the tools (the scam check, and the judge at checkout).
   - Judges dial it from their own phones.

### 5.2 Rohan: the Ask guard (scam radar, rules, lines, evidence)

1. **Scam radar:** `POST /scam-check` in policy.
   - Screen the story with the rules first; hard rules answer instantly.
   - Add account facts: bill balance from the biller, trusted contacts, recent orders.
   - Grok Responses call:
     - Model: grok-4.20 non-reasoning, or grok-4.7 for flagged cases.
     - `x_search` over the last 30 days.
     - `web_search` limited to ftc.gov, consumer.ftc.gov, ic3.gov, aarp.org and bbb.org.
     - Structured output: `{verdict: scam|unsure|ok, pattern, say_for_ruth, facts_checked[], sources[{title,url,date}]}`.
   - A 12 s budget, a cached answer for the demo stories, and a rules-only fallback.
   - Post `scam_checked` and `caregiver_alerted` with sources.
   - Set Ruth's **risk state** (24-hour cool-down), which the card guard reads.
2. **New rule families:**
   - Utility shut-off
   - "Safe account" / move your money
   - Crypto ATM
   - Grandparent voice clone plus secrecy
   - Courier pickup
   - Remote access (extend)

   Add hard negatives for honest bill and pharmacy talk, then re-run the eval.
3. **Lines and clips:**
   - The Protected lines and the card-decline lines ("I stopped a charge at…").
   - `asking_priya` without filler.
   - en, es and hi.
4. **Make safety visible in data:**
   - Post soft "caution" results.
   - Screen-only refusals alert Priya with a `decision_id`, so "Why?" works.
   - The judge's score goes on the ledger.
5. **Validation:** interview 15 people at the venue with 5 questions; record the numbers and quotes for the Devpost.

### 5.3 Dhruv: the Card and Family guards (policy, card decisions, caregiver app)

1. **Card decision service** (in policy, or a new `card/` service):
   - A Lithic sandbox Auth Stream Access responder (public URL through the tunnel).
   - The decision reuses the mandate engine plus the risk state, as a precomputed lookup that must answer in under 300 ms. The rules:
     - Block MCCs 4829, 6051, 6540 and 7995.
     - Per-category caps.
     - "Unusual amount at a pharmacy or big-box" against Ruth's history.
     - Cool-down tightening.
     - ATM withdrawal cap.
   - Reply APPROVED, or decline with a code.
   - Post `card_authorization` with a plain reason.
   - `POST /card/holds/{id}/allow-once` (Priya's passkey or session) opens a 15-minute window for that merchant and amount.
   - **Backup:** Stripe Issuing test mode (2 s budget). **Visa path:** mirror the rules to Visa Transaction Controls sandbox and call `/decisions`, if Vraj's two-way SSL setup works.
2. **Co-signed rules:**
   - The mandate gets Ruth's co-sign: a spoken "yes" recorded at the station, plus a PIN (demo).
   - Changes need both signatures.
   - Add stores and billers and card rules to the mandate.
   - Shape it like Visa's `mandates[]` (`declineThreshold`, `effectiveUntilTime`, `preferredMerchantName`).
3. **Caregiver app as a product:**
   - Build:
     - A CSS design system
     - Bottom tabs: **Home** (status "Mom is protected", spend by store, protected this month), **Safety** (every blocked attempt: plain reason, sources, transcript excerpt, Call Mom), **Approvals** (agent approvals and card holds: Keep blocked / Allow once), **Activity** (orders, bills, refunds), **Rules** (plain words, stores, card, co-sign)
     - Onboarding
     - A weekly digest
   - Fix:
     - Money formatting
     - "Call Ruth" with a real number
     - Remove the debug log
     - Show the cart items on approvals
4. **Fixes carried over from the Phase 4 review:**
   - Put a caregiver marker on the refund, cancel, history and explain routes.
   - Handle a return with no item named when an order has several lines.

### 5.4 Vraj: the Agent guard and the trust layer (merchants, billers, Visa, wall)

1. **Several merchants:**
   - The stores:
     - **Corner Market** (grocery, from the Kroger data)
     - **Parkside Pharmacy** (Rx pickup and over-the-counter, from openFDA)
     - **Main Street Home** (household; seed from Kroger household categories)
     - **Peachtree Power** (utility biller: `GET /accounts/{id}/balance`, bill pay)
     - A **blocked gift-card shop** for the rules to refuse
   - Each has its own storefront name, its own verifier and nonce store, and its own **Cybersource sandbox account**. Signup is instant; if it isn't, use one account with a per-merchant descriptor.
   - The catalog gets a real `merchant` field and search across stores.
   - Fix Kroger-first ordering: usual first, then value.
2. **Visa:**
   - Probe Intelligent Commerce on Cybersource (`/icc/v1/instructions`, formerly `/acp`). It needs JWT, message-level encryption and pilot IDs, so it's a probe only; our mandate uses its exact `mandates[]` shape.
   - Probe Decision Manager `/risk/v1/decisions` on our own sandbox. Never use the public testrest credentials.
   - Two-way SSL for the **Visa Transaction Controls** sandbox. Timebox 90 minutes, then go/no-go at 7:30.
3. **Remote MCP server**, for the Senior Sentinel Line with Manush: expose the tools (`search`, `cart`, `read_cart`, `checkout`, `scam_check`, `bill_status`, `pay_bill`, `order_status`, `refund`), with the cart and read-back gate kept server-side per call.
4. **Trust Ledger** (the wall, redesigned):
   - Four guard lanes (Ask, Card, Agent, Family).
   - Plain-English rows, with raw ids on expand.
   - A **protected-dollars counter**, and sources on scam checks.
   - Per-merchant signature checks.
   - The mandate card in Visa's format.
   - The card-decision feed.
5. **Card terminal simulator:** a tablet page styled as a store card reader ("Five Points Drug · $480.00 · Tap card"). It calls Lithic `simulate/authorize` with MCC 5912, and Lithic calls Dhruv's responder. The terminal shows APPROVED or DECLINED. This is the physical prop at the table.

### 5.5 Contracts to agree at the Phase 5 kickoff (15 minutes)

- `POST /scam-check` request and response (Rohan → Manush, Dhruv, Vraj).
- `risk_state` read by the card guard: `{mandate_id, cooldown_until, reason, source_event}`.
- The card decision payload and events `card_authorization` and `card_hold_allowed` (Dhruv → Vraj wall, Manush station, Dhruv app).
- Merchant ids and names, and the biller API (Vraj → everyone).
- New event types in `contracts/events.schema.json`: `scam_checked`, `card_authorization`, `card_hold_allowed`, `caution`, `bill_paid`.
- Design tokens: colors, type scale, logo, the shield icon. One person makes them in the first hour; everyone uses them.

### 5.6 Everyone

- **Branding and landing page** (the caregiver app's signed-out root):
  - Hero, how it works (four guards), before and after.
  - "For families / for banks", pricing, the numbers, and the FAQ "What Senior Sentinel can't do".
- **Cursor:** build part of every workstream in Cursor with Grok and keep screenshots for the Devpost.
- **Demo topology:** one services laptop runs everything, including the caregiver app and a tunnel on an ngrok domain owned by that laptop's account. This also fixes today's "friend can't see the order". If two laptops are needed, use a hotspot, never eduroam.

---

## 6. The new demo (about 2 minutes; the judge plays Ruth)

The table below uses the power-company story. If the team picks the grandparent scam as the opener (the default in Section 7), the 0:15 line becomes: "My grandson Alex just called. He's in jail, needs $2,000 bail, and said not to tell Mom." Senior Sentinel answers: "That's a common scam, and the voice can be copied. Let me call Alex on the number Priya saved." The store and everyday beats stay the same.

| Time | Beat | Who |
|---|---|---|
| 0:00 | Host: "Last year people over 60 lost $7.7 billion to scams. Most started with a phone call and ended at a store or a crypto ATM. Senior Sentinel guards the call, the card and the agent. You're Ruth." | Host |
| 0:15 | **The call.** The judge reads the card: "Peachtree Power just called. They'll cut my power tonight unless I pay $480 in gift cards." Senior Sentinel: "Your Peachtree Power bill is paid. People reported this exact call in Atlanta this week. This is a scam. Please hang up. Shall I call Priya?" Priya's phone: the Safety card with sources. | Judge, Priya |
| 0:50 | **The store.** Host: "Scammers keep people on the line and send them to the store." The judge taps Ruth's card on the Five Points Drug terminal: $480 → **DECLINED**. The station: "I stopped a $480 charge at Five Points Drug. Is someone asking you to buy gift cards?" Priya's phone: Keep blocked / Allow once. | Judge, Priya |
| 1:15 | **Everyday.** "Order my blood pressure medicine and pay my power bill." Two merchants, read back, signed, Visa sandbox, receipt printed. | Judge |
| 1:45 | **Trust Ledger.** Four guards, "$480 protected", every decision in plain words, signatures, Visa responses. | Host |
| 2:00 | Close: "Call Senior Sentinel yourself: (404) …". Visa judges also get the return beat; xAI judges get the phone call in their own language. | Host |

We label what's simulated, as the HackMIT Visa winner did:
- **Real:** Visa sandbox payments, Lithic sandbox authorizations, Grok calls and search, the phone number.
- **Mocked:** the biller and refund settlement.
- **Stand-in:** the card terminal is a simulator.

---

## 7. Phases to implement v2

Phases 0 to 4 built v1. v2 is Phases 5 to 9. Each phase ends with a merge to main (I review, merge and test), and each exit is binary.

| Phase | Window (Sat → Sun) | Goal | Exit |
|---|---|---|---|
| **5. Kickoff and spikes** | 5:00–7:30pm | Every risky piece proven with one real round trip; contracts and the design system agreed | Go/no-go table at 7:30 |
| **6. Build the four guards** | 7:30–11:30pm (merge at 9:30) | Ask, Card, Agent and Family each work on their own, on main | The new demo runs once end to end |
| **7. Integrate, polish, rehearse** | 11:30pm–2:30am | One product: every surface on the design system, landing page, fallbacks, 10 rehearsals | 9 clean runs out of 10; freeze at 2:30 |
| **8. Ship** | 2:30–5:30am | Video, Devpost, README, public repo, submitted | Submitted on Devpost and expo.hexlabs.org |
| **9. Expo** | 7:00–11:15am | Table set up; every judge gets the same 2 minutes | — |

Defaults below, unless the team answers Section 10 differently:
- Card guard on Lithic, with Stripe as backup.
- Senior Sentinel Line gets a 60-minute spike.
- The four merchants plus the blocked shop.
- One services laptop.
- Everyone builds part of their work in Cursor.
- The demo opens with the grandparent scam (voice clone, "don't tell Mom"), and the power-company call becomes the second scam story on the line cards.

### Phase 5: Kickoff and spikes (5:00–7:30pm)

**5:00–5:25, all four:**
- Read this doc's Sections 0, 2 and 3.
- Agree the contracts in 5.5.
- Open accounts:
  - Lithic sandbox (Dhruv)
  - Extra Cybersource sandboxes and a Visa Developer project (Vraj)
  - xAI Voice Agent Builder number (Manush)
  - An ngrok domain on the services laptop's own account (Manush)
- Pull main.

| Person | Spike or foundation, each with one real round trip |
|---|---|
| Manush | Remove "One moment", add the earcon and the "Checking…" state, and re-measure release-to-first-audio. First draft of the new persona (with Rohan). **Senior Sentinel Line spike**: a call to the number reaches Grok and one of our tools runs (Path A: Builder plus MCP; Path B: SIP webhook plus server agent). |
| Rohan | **Radar spike**: one Grok call with `x_search` and `web_search` that returns a cited, structured verdict for the grandparent and power-company stories, with the time written down. Write down the new rule families and their hard negatives. |
| Dhruv | **Card spike**: Lithic `simulate/authorize` → our responder → APPROVED or declined, with the time written down. **Design system**: tokens, type scale, logo and shield icon, published as one CSS file every surface imports. The caregiver app shell with bottom tabs. |
| Vraj | Stand up **Parkside Pharmacy, Main Street Home and Peachtree Power** as merchants, each with its own sandbox account or descriptor, and one real Pay by Link each. Probe Intelligent Commerce (`/icc`) and Decision Manager on our own sandbox. VTC two-way SSL (about 45 min; stop at 7:15). Skeleton of the MCP server for the line. |

**Exit at 7:30 (go/no-go, anything red takes its fallback in Section 8):**
- Lithic round trip under 1 s.
- Radar verdict with sources under 12 s.
- Line: path chosen, or cut.
- Four merchants each with one real link.
- Intelligent Commerce probe result recorded; Decision Manager and VTC: each either works or is dropped.
- Design tokens pushed.
- Filler gone.

### Phase 6: Build the four guards (7:30–11:30pm; merge at 9:30)

| Person | Builds | Done when |
|---|---|---|
| Manush (Ask and Agent, the voice) | Final persona; tools `scam_check`, `bill_status`, `pay_bill` and store-aware search; the station speaks card declines; the station redesign (kiosk shopper view, Protected card, cart by store, receipts per store, no debug text); the Senior Sentinel Line full flow if it's a go | The grandparent story is answered at the station and on the line; card declines are spoken; shopper view has no raw ids |
| Rohan (Ask, the safety brain) | The radar in production (cache, rules-first, fallback, events with sources); it sets `risk_state` (cool-down); the new rule families plus the eval re-run; lines and clips in en, es and hi; safety made visible in the data (caution events, screen refusals alert Priya with a `decision_id`, judge score on the ledger); **15 validation interviews** at the venue | A scam story sets the cool-down; Priya gets a cited alert; the eval shows no new false refusals |
| Dhruv (Card and Family) | The card decision service (MCC blocks, category caps, unusual-amount rule, cool-down, ATM cap, "allow once" for 15 minutes, events); the co-signed mandate in Visa's `mandates[]` shape, with store, biller and card rules; caregiver app screens (Home, Safety, Approvals with card holds, Activity, Rules, onboarding, weekly digest) | The drugstore charge is declined in cool-down; Priya's "allow once" makes the retry pass; every screen uses real data |
| Vraj (Agent and trust layer) | The catalog across stores with a `merchant` field and value ordering; per-merchant verifiers and Pay by Link; biller balance and pay; a Decision Manager score per order and VTC mirroring if they're green; the **card terminal** tablet page; the **Trust Ledger** redesign (four lanes, plain rows, protected-dollars counter, sources, per-merchant checks); MCP tools for the line | "Medicine and power bill" pays two merchants for real; the terminal drives Lithic; the ledger shows all four guards |

**9:30 merge**: each person's first working slice goes to main, and I merge it and fix the seams.

**Exit at 11:30:** the new demo (Section 6) runs once end to end on main: the scam story, the store decline, the everyday purchase and the ledger.

### Phase 7: Integrate, polish, rehearse (11:30pm–2:30am)

- **Integration run** with times written down. Fix seams (me, on merge).
- **Polish pass**: every surface on the design system: station, caregiver app, Trust Ledger, session page, terminal, receipts.
- **Landing page** (Rohan, with Dhruv's design system): before and after, the four guards, for families and for banks, pricing, the numbers, validation quotes, "what we can't do".
- **Demo safety**:
  - Cached radar answers for the three stories.
  - Cached voice sessions.
  - One-key reset covering the card cool-down and holds.
  - Line cards: grandparent, power company, tech support, return.
- **Rehearse ten times.** Judges dial the line from their own phones; do a loud-room test.
- **Freeze at 2:30am.** 9 clean runs out of 10; anything else goes to the video only.

### Phase 8: Ship (2:30–5:30am)

- **Video**, 2–3 minutes: the before-and-after story from Section 2.2, the table demo, and the four guards.
- **Devpost** in each judge's words (Section 4). Include:
  - What's real, mocked or a stand-in (Section 6)
  - The Cursor screenshots
  - The validation numbers
  - The business model
- **README** with the four guards and an architecture diagram.
- Remove `internal/`, make the repo public, and submit on Devpost and expo.hexlabs.org. Confirm the deadline first (Section 10).
- Sleep in shifts from 5:30.

### Phase 9: Expo (7:00–11:15am)

- **Table**: station, phone for the line, terminal tablet, Priya's phone, printer and the wall.
- Two clean runs before judging opens.
- The Host script from Section 6; the demo runbook gets rewritten in Phase 7.

---

## 8. Risks and fallbacks

| Risk | Fallback |
|---|---|
| Voice Agent Builder can't use our MCP tools, or the SIP path is too slow to build | Path B, or cut the line and say it's the next step. The station stays the demo. |
| Lithic signup or the responder fails | Stripe Issuing test mode. Last resort: our own authorization simulator using the same decision code, labeled "simulated card network". |
| Scam radar is slow (x_search can take 5–15 s) | Earcon plus one line. Cached answers for the three demo stories. Rules-only verdict if over 12 s. |
| VTC two-way SSL or MLE eats the evening | Drop it and say "banks enforce the same rules with Visa Transaction Controls." Show the rules shaped for it. |
| Extra Cybersource sandboxes need approval | One account with per-merchant descriptors. |
| Hall noise, a dropped socket | Push-to-talk, cached sessions, typed input (all built). |

---

## 9. What we cut or demote

- The pickup countdown and points stop being demo beats; they remain on the receipt.
- The Kroger-heavy catalog ordering goes.
- Raw rule ids leave every Ruth- or Priya-facing surface.
- The Host page stays operator-only.

---

## 10. Decisions needed before we start

1. **Direction:** adopt v2 (four guards; Senior Sentinel is a safety layer plus errands)?
2. **Card guard:** Lithic sandbox as the real card round trip, with Stripe as backup? Try Visa Transaction Controls as well (90-minute timebox)?
3. **Senior Sentinel Line:** spend a 60-minute spike on a real phone number (Grok SIP)?
4. **Merchants:** Corner Market, Parkside Pharmacy, Main Street Home, Peachtree Power, plus the blocked gift-card shop? Fictional names on real product data.
5. **Demo topology:** one services laptop runs everything, including the caregiver app and tunnel?
6. **Cursor:** does everyone agree to build part of their workstream in Cursor tonight (a stated xAI requirement)?
7. **Deadlines:** someone logs in to live.hexlabs.org to confirm the submission time and the sponsor-challenge cap.

---

## 11. Sources

**Scams and caregivers**
- FBI IC3 2025 annual report (elder section): https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf
- FTC, Protecting Older Consumers (Dec 2025): https://www.ftc.gov/system/files/ftc_gov/pdf/P144400-OlderAdultsReportDec2025.pdf
- FTC impersonation spotlight (Aug 2025): https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/08/false-alarm-real-scam-how-scammers-are-stealing-older-adults-life-savings
- AARP, scope of elder financial exploitation (2023): https://www.aarp.org/pri/topics/work-finances-retirement/fraud-consumer-protection/scope-elder-financial-exploitation/
- FinCEN elder exploitation analysis (2024): https://www.fincen.gov/news/news-releases/fincen-issues-analysis-elder-financial-exploitation
- Caregiving in the US 2025: https://www.caregivingintheus.org/wp-content/uploads/2026/03/caregiving-in-us-2025.doi_.10.26419-2fppi.00373.001.pdf
- Gift-card store measures study (Bailey & DeLiema): https://pmc.ncbi.nlm.nih.gov/articles/PMC9771048/
- FTC gift-card best practices: https://consumer.ftc.gov/system/files/consumer_ftc_gov/pdf/ScamsAgainstOlderAdults_GiftCardBestPractices.pdf

**Interventions**
- FINRA Foundation, Exposed to Scams (2019): https://www.finrafoundation.org/sites/finrafoundation/files/exposed-to-scams-what-separates-victims-from-non-victims_0_0.pdf
- Behaviouralist / Open Banking payment-screen trial: https://thebehaviouralist.com/portfolio-item/open-banking/
- CommBank scam losses: https://www.commbank.com.au/articles/newsroom/2025/08/commbank-customer-scam-losses-fall-truyu.html
- UK Finance fraud report 2026: https://www.ukfinance.org.uk/news-and-insight/press-release/fraud-report-2026-press-release
- PSR, APP reimbursement one year on: https://www.psr.org.uk/news-and-updates/latest-news/news/one-year-on-impact-of-app-reimbursement-on-victims/
- Android in-call scam protection: https://blog.google/security/android-expands-pilot-in-call-scam-protection-financial-apps/
- Georgia Tech, older adults and AI explanations (CHI 2026): https://techxplore.com/news/2026-04-older-adults-ai.html

**Market**
- True Link for aging adults: https://www.truelinkfinancial.com/prepaid-card/aging-adults
- Huntington caregiver banking: https://www.huntington.com/Personal/online-banking/caregiver-banking
- Keynova bank safeguards review: https://www.prnewswire.com/news-releases/banks-increase-digital-debit-card-safeguards-address-rising-elder-fraud-prevention-and-caregiver-oversight-with-online-banking-account-access-privileges-302619531.html
- Edward Jones and Carefull: https://www.edwardjones.com/us-en/why-edward-jones/news-media/press-releases/edward-jones-introduces-carefull-financial-safety-platform
- True Link caregiver survey: https://aijourn.com/102-million-caregivers-find-banks-fail-to-deliver/
- Meela: https://www.meela.ai/
- AARP, ready for AI shopping: https://www.aarp.org/personal-technology/ready-for-ai-shopping/

**Card rails**
- Lithic Auth Stream Access: https://docs.lithic.com/docs/auth-stream-access-asa
- Lithic simulate authorization: https://docs.lithic.com/reference/postsimulateauthorize
- Lithic authorization challenges: https://docs.lithic.com/docs/authorization-challenges
- Stripe Issuing real-time authorizations: https://docs.stripe.com/issuing/controls/real-time-authorizations
- Stripe Issuing testing: https://docs.stripe.com/issuing/testing
- Visa Transaction Controls: https://developer.visa.com/capabilities/vctc
- Visa two-way SSL: https://developer.visa.com/pages/working-with-visa-apis/two-way-ssl
- VTC Postman collections: https://github.com/jcrosswh/vtc-postman-collections

**Visa agentic**
- Intelligent Commerce on Cybersource: https://developer.cybersource.com/docs/cybs/en-us/intelligent-commerce/developer/all/rest/intelligent-commerce/home.html
- Agentic sandbox signup: https://developer.cybersource.com/hello-world/agentic-sandbox.html
- Trusted Agent Protocol: https://developer.visa.com/capabilities/trusted-agent-protocol/overview
- Visa agentic threat landscape: https://corporate.visa.com/en/sites/visa-perspectives/security-trust/the-threats-landscape-of-agentic-commerce.html
- Visa scam disruption: https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21286.html

**xAI**
- Voice agent: https://docs.x.ai/developers/model-capabilities/audio/voice-agent
- Voice prompting guide: https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/prompting-guide
- SIP: https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/sip
- Voice Agent Builder: https://x.ai/news/grok-voice-agent-builder
- X search: https://docs.x.ai/developers/tools/x-search
- Web search: https://docs.x.ai/developers/tools/web-search
- Pricing: https://docs.x.ai/developers/pricing
- Telephony cookbook: https://github.com/xai-org/xai-cookbook/tree/main/voice-examples/agent/telephony

**Tracks**
- HackGT 13 Devpost: https://hackgt13.devpost.com/
- HackGT 13 rules: https://hackgt13.devpost.com/rules
- Visa and SpaceXAI challenge text (HackMIT 2026 edition): https://docs.google.com/document/d/1JxZA0eiX2iWj_-B5xtCo59FylUDlv3I35n5n8W0aIVs/preview
- SpaceXAI Grokathon criteria: https://spacexai-grokathon.devpost.com/
