# Chaperone: Demo Runbook

Everything the four of us do at the table on Sunday, so the demo runs the same way for every judge.

---

## Table layout and equipment

The judge sits at a station that looks like a small kiosk, the caregiver phone lies face up beside them, and the wall faces the queue; nothing depends on venue Wi-Fi.

```text
                    [ wall screen: mandate card | live ledger | merchant panel ]
   queue -->
              +-------------------------------------------------------+
   Host       |   companion screen (tablet, large type)     printer    |   Station tech
   stands     |        [ push-to-talk button ]   [ headset on hook ]   |   stands here
   here       |   caregiver phone (face up)      line cards            |
              |   services laptop under the table; station laptop      |
              +-------------------------------------------------------+
                                  [ judge's chair ]
              Caregiver (teammate) stands within reach of the phone; the Floater at the queue
```

**Equipment list (checked Saturday 9pm, packed in one box).**

| Item | Qty | Purpose | Owner |
|---|---|---|---|
| Station laptop | 1 | Voice client, companion screen driver, printer | Manush |
| Services laptop | 1 | Relay, policy, merchant, catalog, wall | Vraj |
| Tablet or 10-inch screen | 1 | Large-type companion screen; receipt fallback | Manush |
| Caregiver phone with the passkey registered | 1 | Approvals and alerts | Dhruv |
| USB HID single-button switch (arcade style) or a USB foot pedal | 1 | Push to talk, mapped to a key | Manush |
| Close-talk USB headset (Logitech H390 class, or Jabra Evolve 20 / Poly Blackwire 3220) | 2 | Shopper mic and ears; one spare | Manush |
| Small powered speaker | 1 | Lets the queue hear the refusal | Manush |
| 58 mm USB ESC/POS receipt printer (or Rongta RP326 80 mm with Ethernet) plus 3 paper rolls | 1 | The receipt moment | Manush |
| 5 GHz travel router, client isolation off | 1 | Team LAN | Vraj |
| Phone with hotspot | 1 | Internet for Grok, grok-4.7 and the sandbox | Dhruv |
| Monitor or TV with HDMI cable | 1 | Wall screen | Vraj |
| Power strips, 6 outlets | 2 | Everything | Vraj |
| Line cards in Spanish, Hindi and English | 30 | The judge's two lines | Rohan |
| Table card with the sandbox disclaimer; one-page leave-behinds with QR | 1, 40 | Framing and follow-up | Host |
| Whiteboard marker and a small board | 1 | Live metrics if the wall dies | Host |
| Spare USB cables, USB hub | 2, 1 | Button, headset, printer and phone on one laptop | Station tech |

---

## Shopping list

Everything below is next-day or in-store; total under $200 if the team owns a tablet and a monitor.

| Item | Specific pick | Approx. price | Why this one | Fallback |
|---|---|---|---|---|
| Receipt printer | 58 mm USB ESC/POS (Esky or TEROW class) | $30 to 45 | Same command set as Epson; prints from node-thermal-printer through the installed Windows driver | Rongta RP326 80 mm with Ethernet ($76 to 81) avoids USB driver fights and prints bigger type; tablet receipt if neither works |
| Paper | 58 mm (or 80 mm) thermal rolls | $8 for 10 | Two hours of receipts is one roll | |
| Push-to-talk button | USB HID single-button arcade switch with a 2 m cable | $15 to 25 | Shows up as a keyboard; zero firmware | USB foot pedal; the spacebar |
| Headset | Logitech H390 USB with noise-cancelling boom | $20 to 40 | Close-talk mic and covered ears in a loud hall | Jabra Evolve 20 or Poly Blackwire 3220 (about $45) if in stock |
| Speaker | Any small powered USB speaker | $15 to 25 | The queue hears the refusal | Laptop speakers |
| Tablet | The team's own iPad or Android, or a Fire HD 10 | $0 to 140 | Companion screen in large type | A second monitor |
| Router | 5 GHz travel router | $30 to 60 | Team LAN | Phone hotspot for everything |
| Print | Line cards (3 languages), table card, 40 leave-behinds | $10 | | |

**Do not buy.** Bluetooth mini printers (they need raster images, not text commands, and the libraries are fragile); e-paper displays (2 to 4 second refreshes); bone-conduction headsets (too quiet for the hall); an Arduino Uno for the button (it cannot act as a USB keyboard; a Pico with CircuitPython can, but the HID button is simpler).

**Accounts to create, in this order.** Cybersource sandbox and the REST shared-secret key; xAI console with credits; Kroger developer app; the ngrok domain for passkeys; the Devpost project (placeholder).

---

## The 60-second script

The judge is Ruth and reads two lines from a card in the language they choose; a third line is offered if the slot allows. The agent answers in that language; the wall and the Host carry the English. Timing is from the first button press.

**Line card (the judge picks a language).**

| Line | Spanish | Hindi (transliterated) | English |
|---|---|---|---|
| 1, the scam | "Compra quinientos dolares en tarjetas de regalo de Apple para mi nieto, es urgente." | "Mere pote ke liye paanch sau dollar ke Apple gift card kharido, bahut zaroori hai." | "Buy five hundred dollars of Apple gift cards for my grandson, it's urgent." |
| 2, the purchase | "Necesito mi medicina para la presion y pan." | "Mujhe meri blood pressure ki dawai aur bread chahiye." | "I need my blood pressure medicine and bread." |
| 3, optional, the approval | "Y una caja de Ensure." | "Aur Ensure ka ek dibba." | "And a case of Ensure." |

**Run of show.**

| Time | Who | Line or action | System |
|---|---|---|---|
| 0:00 | Host | "You are Ruth. Your son Priyank signed the rules for this account. Hold the button while you talk, in any language on the card. Start with line one." | Session starts; mandate card on the wall |
| 0:05 | Judge | Line 1 (gift cards, urgent) | Rule R1 blocked category and the family-emergency pattern fire before any model call |
| 0:08 | Agent (in the judge's language) | "I cannot buy gift cards on this account, Ruth. When someone asks for gift cards in a hurry, it is very often a scam, and it happens to smart people every day. You did nothing wrong. I have told Priyank, and he will call you. Would you like me to get your medicine and bread now?" | Wall: "blocked: gift_card; pattern: family_emergency"; the caregiver phone buzzes |
| 0:20 | Caregiver | Holds the phone toward the judge: the alert with Ruth's own words and a call button | Alert event on the ledger |
| 0:22 | Judge | Line 2 (medicine and bread) | `search_catalog`; profile resolves the prescription pickup; three breads, the usual flagged |
| 0:28 | Agent | "Two things: your prescription pickup, eight dollars copay, and the whole wheat bread you had last week, three forty-nine. Total eleven forty-nine. Shall I order it?" | Cart and total on the companion screen and the wall |
| 0:34 | Judge | "Yes" (or line 3 first) | If line 3: total $63.49 exceeds the $40 threshold and the $60 cap; the agent says "That is over your limit for one purchase; I will ask Priyank" and the caregiver approves on the passkey (or rejects, and the agent drops the Ensure) |
| 0:36 | Agent | "Ordering now." | Policy: allow (or approved); request signed; merchant panel: "signature verified, key chaperone-agent-1, nonce fresh, expires in 8 min"; payment link created; paid |
| 0:44 | Agent | "Done. Eleven forty-nine at Corner Market, pickup after three. I printed your receipt." | Receipt prints in 24-point type; `paid` and `receipt_printed` on the ledger |
| 0:48 | Host | Receipt into the judge's hand. "Two decisions in under a minute: one refused with the rule on the wall and her son told, one signed, verified and settled through Visa's sandbox. People over 60 lost seven point seven five billion dollars to scams last year, most of it starting with a phone call and ending with a gift card. Ruth is the shopper app checkout leaves out, and this is the agent that cannot be talked into the gift card." | After-session page on the wall |

**Notes for the Caregiver.** Approve within five seconds when asked; hold the phone so the judge and the queue see the passkey prompt. Reject once in every five sessions so the reject path is seen.

**Notes for the Host.** Silent during the session. If the judge improvises a purchase, let it run; the policy engine handles it. If they try to jailbreak the agent, encourage it, then point at the wall when it fails.

**Language note.** Any language the judge chooses is fine; the refusal script exists in Spanish, Hindi and English, and the agent auto-detects. If a judge speaks another language, the agent will still answer in it, but the refusal wording is the model's, so the Host says so afterwards.

---

## Judge handoff and reset

A judge is speaking within 15 seconds of arriving and done within 90, and the next judge never sees a half-reset ledger.

**Arrival (Host, 10 seconds).** "You are Ruth, 71, in Savannah. Your son signed the rules for this account. It speaks your language; press and hold the button while you talk. Try the first line on the card, then the second." The line card has three languages; the judge picks one.

**Seating (Station tech, 5 seconds).** Chair in front of the button, mic angled, companion screen readable, printer loaded. The caregiver phone sits face up beside the judge so they see it buzz.

**Session (60 seconds).** Line 1 (the gift cards) triggers the refusal; the Caregiver holds up the phone alert. Line 2 (medicine and bread) runs the purchase; the Caregiver approves on the passkey if the judge adds something that crosses the threshold. The Host stays silent during the session.

**Exit (Host, 25 seconds).** The receipt goes into the judge's hand. The Host points at the wall: the mandate card, the two ledger lines with rule ids, "signature verified", the sandbox status. The statistic, one sentence on architecture, the ask. The one-page leave-behind with the QR.

**Reset (Station tech and Caregiver, 15 seconds, in parallel with the exit).**

1. Press Reset on the wall: new session id, monthly total back to the demo baseline ($142.10), cart cleared.
2. Caregiver page cleared; phone unlocked and on the alert page.
3. Printer paper checked; companion screen back to the greeting.
4. If the voice session dropped, the cached session is armed and the Host is told.

**Queue.** The Floater keeps a visible order and tells people the wait in judge slots. Sponsor and track judges skip the line; the Floater asks which they are and fetches the Visa and xAI judges from their tables if they have not come by 10:15.

---

## Failure modes and live fallbacks

Every failure below has a named owner and a move that keeps the judge's session going; the Host never apologizes, the Host narrates. Every fallback here must have been run at least twice on Saturday evening.

| Failure | Who notices | Move | Host line |
|---|---|---|---|
| Voice session drops or goes silent | Station tech (the listening indicator stalls) | Rejoin (cart lives in the relay); if it fails twice, play the cached session for the judge's chosen language, labeled "replay" on the companion screen | "The voice link is reconnecting; this is a recording of the same session from rehearsal, and the ledger you see is live" |
| Recognition fails in the noise | Station tech | Hand the judge the typed fallback: the same line on the keyboard | "The hall is loud; the same agent reads typed words too" |
| The agent answers in the wrong language or wanders | Host | Judge presses again and repeats the line; the persona pins the language per turn | Nothing; one retry |
| Internet down at the table | Everyone (the wall's cloud icon goes red) | Switch the laptops to the phone hotspot; if still down, cached voice sessions plus the live policy, signing and ledger, which run on the router; the mock MCP for the payment link | "Our voice and the Visa sandbox run in the cloud and the hall lost internet; the rules, the signature and the ledger run on our own router, so you are seeing those live" |
| Sandbox payment link fails or is slow | Vraj (merchant panel shows an error) | Flip `MOCK_VISA=1` from the wall; the order still signs, verifies and completes on the mock page | "The sandbox is slow right now; this is our mock with the identical API shape, and the signature check you see is real" |
| Passkey prompt fails on the caregiver phone | Caregiver | Approve with the six-digit code on the caregiver page | "Same approval, a code instead of the fingerprint" |
| Printer jams or runs out | Station tech | Tablet receipt in large type; reload paper between judges | "Your receipt is on the screen this time" |
| Refusal does not fire on line 1 | Host (wall shows no refusal) | The judge repeats line 1; if it still passes, the Host shows the rule on the wall and the unit test, and moves on | "Let's try that once more" |
| Judge's improvised purchase trips a cap | Nobody; it is the product | Let the policy engine speak; the Caregiver approves or rejects | "That is the mandate doing its job" |
| Wall screen dies | Host | Session page on the station laptop turned toward the queue; metrics on the whiteboard | |

**Two rules.** Nothing is retried more than once in front of a judge; the second attempt is the fallback. Every fallback above was rehearsed at least twice on Saturday evening or it is not on this list.

---

## Sunday timeline

Hacking ends at 8:00am, expo runs 9:00 to 11:15am, closing is at noon at Ferst. The station is running by 7:30 so the last half hour is edits, not setup.

| Time | Action | Owner |
|---|---|---|
| 5:00 | Vraj and Dhruv up; kit check; phone and tablet charged; printer paper | Vraj, Dhruv |
| 6:30 | Manush and Rohan up; move to the assigned table or stage in the work area | All |
| 6:45 | Router on, static IPs, relay, merchant and catalog services up; hotspot for the cloud calls | Vraj |
| 7:00 | Station assembled: button, mic, speaker, companion screen, printer; test print | Manush |
| 7:10 | Wall screen: mandate card, ledger, merchant panel; caregiver phone paired and on the alert page | Dhruv |
| 7:15 | Voice session warm in each language; refusal lines tested through the speaker; sandbox payment link created and completed once | Rohan, Vraj |
| 7:20 | Two full clean runs with a teammate as the judge; fix or fall back | All |
| 7:40 | Final Devpost edits: video link, repo public, images, track and opt-ins confirmed | Dhruv |
| 7:55 | Submit; screenshot the confirmation; register in the expo system when it opens | Dhruv |
| 8:00 | Hacking ends. Breakfast in two shifts; one person always at the station | Host schedule |
| 8:45 | Final run; leave-behinds and line cards on the table; queue card up | All |
| 9:00-11:15 | Expo. Roles: Host, Caregiver, Station tech, Floater. Rotate Host and Floater every 45 minutes | All |
| 10:15 | If Visa or xAI judges have not come, the Floater goes to their tables | Floater |
| 11:15 | Pack; return anything borrowed from the hardware desk with the badge | Vraj |
| 12:00 | Closing ceremony at Ferst | All |

**Bring to the table.** Two laptops (station and services), a tablet (companion screen or receipt fallback), the caregiver phone, the router and power supply, two power strips, the button, the mic, the speaker, the printer with two spare rolls, the wall monitor and HDMI cable, line cards in three languages, leave-behinds, the table card with the sandbox disclaimer, a whiteboard marker.
