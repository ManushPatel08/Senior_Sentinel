# Landing page copy (for Dhruv to build in Phase 7)

The signed-out root of the caregiver app. Plain words, calm tone, no alarm red. Every number has its source link below it on the page.

---

## Hero

**The helper your mom can call before she pays anyone.**

Chaperone runs your parent's errands and bills by voice, in her language, and guards every place her money can leave: the call, her card and her agent. You set the rules together.

Buttons: **Set it up with Mom** · **For banks**

---

## One scam, before and after

**The call:** "This is Peachtree Power. Your power goes off at 7 tonight unless you pay $480. Stay on the line, and don't tell anyone."

1. **She asks first.** Instead of driving to the drugstore, Ruth asks Chaperone, on the kitchen station or by phone. Chaperone checks her real power bill (paid) and today's scam reports, then says in her language: "This is a scam. Your bill is paid. Please hang up." Her daughter's phone shows what happened, with sources.
2. **Her card takes extra care.** For the next day, risky charges on her card are held. If the caller talks her into the drugstore anyway, the $480 charge is declined at the register, and Chaperone tells her why.
3. **Nothing lost, nothing hidden.** Priya sees every stopped attempt with a plain reason, can allow a real purchase once with one tap, and Ruth keeps her card and her independence.

*Without Chaperone:* she buys the gift cards, reads the numbers over the phone, and the money is gone in minutes.

---

## Four guards, one set of rules

| Guard | What it does |
|---|---|
| **Ask** (the conversation) | Ruth describes a call, text or pop-up. Chaperone checks her own accounts and live scam reports, answers in two calm sentences with one action, and tells Priya. |
| **Card** (her Visa card) | Every swipe is checked against the signed rules in under a second. Gift-card kiosks and crypto ATMs never go through; after a scam call, risky spending waits a day. |
| **Agent** (errands and bills) | Groceries, medicine and the power bill, only from verified stores and billers, only within the limits, with signed requests. It can't be talked into gift cards, wires or fake refunds. |
| **Family** (co-signed rules) | Ruth and Priya agree the rules together, and Ruth can hear them any time. Neither can loosen them alone. |

---

## For families

**$14.99 a month.** Voice help in English, Spanish and Hindi; the scam check on a call or at the kitchen station; card protection with one-tap "allow once"; a weekly summary for the family; every decision explained in plain words.

## For banks and credit unions

Offer caregiver protection on the Visa debit cards your members already have. The same rules run through **Visa Transaction Controls**, so a scam-call cool-down or a blocked store type is enforced at authorization, and every stopped attempt comes with a dispute-ready record. Priced per protected account.

*70% of caregivers say they would move deposits to a bank with good caregiver support; about 20% of banks offer delegated access today.*

---

## The numbers

- **$7.75 billion** lost to reported scams by people over 60 in 2025, up 59%, an average of $38,500 per complaint. [FBI IC3 2025](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)
- **$1.04 billion** of that went to tech-support scams. [FBI IC3 2025](https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf)
- **41%** of older adults' $10k+ impersonation losses started with a phone call. [FTC, Aug 2025](https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/08/false-alarm-real-scam-how-scammers-are-stealing-older-adults-life-savings)
- **Gift cards** are the most-reported way older adults pay tech-support, government and family impostors. [FTC, Dec 2025](https://www.ftc.gov/system/files/ftc_gov/pdf/P144400-OlderAdultsReportDec2025.pdf)
- **63 million** US family caregivers; **81%** help with shopping and **58%** manage finances. [Caregiving in the US 2025](https://www.caregivingintheus.org/wp-content/uploads/2026/03/caregiving-in-us-2025.doi_.10.26419-2fppi.00373.001.pdf)
- **72%** of elder financial exploitation is by someone the victim knows, which is why the rules are co-signed. [AARP](https://www.aarp.org/pri/topics/work-finances-retirement/fraud-consumer-protection/scope-elder-financial-exploitation/)
- Bank figures: [True Link caregiver survey](https://aijourn.com/102-million-caregivers-find-banks-fail-to-deliver/), [Keynova bank review](https://www.prnewswire.com/news-releases/banks-increase-digital-debit-card-safeguards-address-rising-elder-fraud-prevention-and-caregiver-oversight-with-online-banking-account-access-privileges-302619531.html)

**Measured in our prototype** (sandbox, no real money): a scam story is answered in a median 3.9 s (p90 5.3 s) with sources, at about $0.05 per check; a rule match answers in milliseconds. The scam check caught all 20 scams in our held-out test set in English, Spanish and Hindi, with one false refusal out of 14 honest requests. Details: `ai/eval/RESULTS.md`, `ai/eval/RADAR_LATENCY.md`.

---

## What Chaperone can't do

- **It can't hear a scammer's call unless she asks.** The habit comes from daily errands and a card on the fridge: "Before you pay anyone, ask Chaperone."
- **Her card can't see what she's buying,** only the store and the amount. A drugstore charge is a drugstore charge, so Chaperone judges by store type, amount, her usual spending and the day's cool-down.
- **Priya can't approve inside the card network's few seconds.** A held charge is declined first; after Priya's "allow once", Ruth simply tries again.
- **It adds friction and family, not a guarantee.** A determined, willing victim can still find a way. Chaperone makes that way slower, visible and shared.
- **This is a prototype.** Payments run in the Visa sandbox; no real money moves and no real personal data is used.
