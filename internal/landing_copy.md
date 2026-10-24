# Landing page copy (for Dhruv to build)

The signed-out root of the caregiver app. Plain words, calm tone, no alarm red. Every number has its source link below it on the page.

---

## Hero

**The helper your mom can call before she pays anyone.**

Chaperone runs your parent's errands and bills by voice, in her language, and guards three ways her money can leave: a caller's story, her card and her agent. You set the rules, and she hears every change in her own language.

Buttons: **Set it up with Mom** · **For banks**

---

## One scam, before and after

**The call:** "This is Peachtree Power. Your power goes off at 7 tonight unless you pay $480. Stay on the line, and don't tell anyone."

1. **She asks first.** Instead of driving to the drugstore, Ruth asks Chaperone, on the kitchen station or by phone. Chaperone looks up her real Peachtree Power account, sees the bill is paid, and says in her language: "Ruth, your Peachtree Power bill is paid, so this call is a scam. Please hang up and don't pay anyone; I've told Priyank." Priyank's app shows what happened, with links to recent reports of the same scam once the search comes back.
2. **Her card takes extra care.** For the next 24 hours, any card charge over $25 and any cash withdrawal is declined. If the caller talks her into the drugstore anyway, the $480 charge is declined at the register; Priyank sees the decline in his app, and the kitchen station says why out loud.
3. **Nothing lost, nothing hidden.** Priyank sees the scam check and the declined charge, each with a plain reason, and can let a real charge through once with one tap. Ruth keeps her card and her independence.

*Without Chaperone:* she buys the gift cards, reads the numbers over the phone, and the money is gone in minutes.

---

## Four guards, one set of rules

| Guard | What it does |
|---|---|
| **Ask** (the conversation) | Ruth describes a call, text or pop-up. Chaperone checks her own accounts (her bill, recent orders, family numbers) and, when its rules don't already know the scam, recent scam reports. It answers in two short, calm sentences and logs every check for Priyank, with an alert when it's a scam. |
| **Card** (her Visa card) | Every swipe is checked against her rules before it's approved. Gift-card, money-transfer, crypto and betting merchants are blocked by store type; after a scam call, charges over $25 and cash withdrawals are declined for a day. |
| **Agent** (errands and bills) | Groceries, medicine and the power bill, only from the stores and billers on her list and only within the limits. Every order is signed, so the store can check it came from Chaperone. It never buys gift cards, wires or crypto, and a refund only goes back to the card that paid. |
| **Family** (shared rules) | Priyank sets the rules and signs them with his passkey, and can change them on his own. Chaperone reads every new set to Ruth in her language and keeps her spoken yes on record. |

---

## For families

**$14.99 a month.** Voice help in English, Spanish and Hindi; the scam check on a call or at the kitchen station; card protection with one-tap "allow once"; a Home tab that counts the week's errands, bills paid and attempts stopped; a plain-words "Why?" behind scam checks and refusals.

## For banks and credit unions

Offer caregiver protection on the Visa debit cards your members already have. The same rules decide each card authorization in real time, so a scam-call cool-down or a blocked store type is enforced before a charge goes through, and a charge declined during a scam-call cool-down comes with a record of the call behind it, ready for a dispute. In the prototype this runs on a sandbox card's real-time authorization; part of the rules (a spending threshold, ATM and online caps, a gambling block) is also mirrored into **Visa Transaction Controls**. Priced per protected account.

*70% of caregivers say they would move deposits to a bank with good caregiver support; about 20% of banks offer delegated access today.*

---

## The numbers

- **$7.75 billion** lost to reported scams by people over 60 in 2025, up 59%, an average of $38,500 per complaint. [FBI IC3 2025](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)
- **$1.04 billion** of that went to tech-support scams. [FBI IC3 2025](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)
- **41%** of older adults' $10k+ impersonation losses started with a phone call. [FTC, Aug 2025](https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/08/false-alarm-real-scam-how-scammers-are-stealing-older-adults-life-savings)
- **Gift cards** are the most-reported way older adults pay tech-support, government and family impostors. [FTC, Dec 2025](https://www.ftc.gov/system/files/ftc_gov/pdf/P144400-OlderAdultsReportDec2025.pdf)
- **63 million** US family caregivers; **81%** help with shopping and **58%** manage finances. [Caregiving in the US 2025](https://www.caregivingintheus.org/wp-content/uploads/2026/03/caregiving-in-us-2025.doi_.10.26419-2fppi.00373.001.pdf)
- **72%** of elder financial exploitation is by someone the victim knows, which is why every change to the rules is read to Ruth and her answer is kept on record. [AARP](https://www.aarp.org/pri/topics/work-finances-retirement/fraud-consumer-protection/scope-elder-financial-exploitation/)
- Bank figures: [True Link caregiver survey](https://aijourn.com/102-million-caregivers-find-banks-fail-to-deliver/), [Keynova bank review](https://www.prnewswire.com/news-releases/banks-increase-digital-debit-card-safeguards-address-rising-elder-fraud-prevention-and-caregiver-oversight-with-online-banking-account-access-privileges-302619531.html)

**Measured in our prototype** (sandbox, no real money): a scam story the rules don't already recognize is answered in a median 3.9 s (p90 5.3 s) with sources, at about $0.05 per check; one the rules recognize is answered without waiting for the search. On our own test scripts, the safety rules plus the Grok judge caught all 25 scams in the held-out half, across English, Spanish, Hindi and Hinglish, and refused 1 of 24 honest requests. We wrote those scripts alongside the rules, so this shows the checks do what we built them to do, not how they fare against scams we haven't seen. Details: `ai/eval/RESULTS.md`, `ai/eval/RADAR_LATENCY.md`.

---

## What Chaperone can't do

- **It can't hear a scammer's call unless she asks.** The habit comes from daily errands and a card on the fridge: "Before you pay anyone, ask Chaperone."
- **Her card can't see what she's buying,** only the store and the amount. A drugstore charge is a drugstore charge, so Chaperone judges by store type, amount, her usual spending and the day's cool-down.
- **Priyank can't approve inside the card network's few seconds.** A held charge is declined first; after Priyank's "allow once", Ruth simply tries again within 10 minutes.
- **It adds friction and family, not a guarantee.** A determined, willing victim can still find a way. Chaperone makes that way slower, visible and shared.
- **This is a prototype.** Store payments run in the Visa sandbox and card swipes on a sandbox card; no real money moves and no real personal data is used.
