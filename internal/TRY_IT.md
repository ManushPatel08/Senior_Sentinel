# Try everything: a walkthrough of what's built

Everything runs on the services laptop (`bash .claude/run.sh all`, plus `bash .claude/run.sh tunnel` for ngrok). Go through the steps in order: each one sets up the next. Takes about 20 minutes with two people: one plays Ruth at the station, one holds Priyank's phone.

## What to open

| Who | Where | Notes |
|---|---|---|
| Ruth (station) | `http://localhost:5173` in Chrome on the laptop | Allow the mic, press **Start**. Hold the big button (or Space) to talk, or type in the box. `?operator` or Ctrl+Shift+O shows the operator panels. |
| Priyank (his phone) | `https://unmarked-subfloor-spiral.ngrok-free.dev` | Tap **Visit Site** on ngrok's page once, then sign in with the passkey. |
| Host | `http://127.0.0.1:8000/host` | **Confirm payment**, **Reset demo**, **Fallback code**. Ctrl+Shift+R on the station also resets. |
| Card terminal | `http://127.0.0.1:8000/terminal` | A store's card reader: pick a store, an amount, **Tap card**. Real swipes through the card network's sandbox (card ending 5018). |
| Trust Ledger (wall) | `http://127.0.0.1:8000/wall` | Four guard lanes, the protected-dollars counter, Ruth's rules in Visa's mandate shape. |
| Phone line | the xAI number from the Voice Agent Builder | The agent's MCP URL is `https://<tunnel>/line/k/<LINE_MCP_TOKEN>/mcp`; refresh its tool list (13 tools). PIN is `LINE_PIN` in `.env`. |

The relay listens on 127.0.0.1 only, so the terminal and the wall open on this laptop. To use a tablet or a second screen for them, the relay has to listen on the LAN (`--host 0.0.0.0` in run.sh).

## Before you start

1. Press **Reset demo** on the Host page. The wall empties and any cool-down is cleared.
2. On Priyank's phone, reopen the page and sign in again (his app restarted).

## 1. Family: Priyank signs the rules, Ruth agrees by voice

1. Priyank: **Rules** tab. Four stores listed (Corner Market, Parkside Pharmacy, Main Street Home, Peachtree Power), limits in dollars, the card sentence (drugstore cap, 24-hour care after a scam call). Change the per-purchase limit from $60 to $55 and **Sign** with the passkey.
2. Station: Chaperone reads the new rules to Ruth and asks if she agrees. Ruth: "Claro que no." Nothing is recorded; Priyank's Rules still waits for Ruth.
3. Priyank: set the limit back to $60 and **Sign** again. Chaperone reads the rules again.
4. Ruth: "Yes, I agree" (or "Sí, estoy de acuerdo").
   - Station: a thank-you and a "You agreed" note with her words.
   - Priyank: Rules shows **Ruth agreed by voice** with her words.
   - Wall: the Family lane shows the co-sign; the rules card says Ruth agreed.
   - A co-sign counts only for the rules Ruth actually heard: if Priyank signs again, Ruth is asked again.

## 2. Ask: the scam call

1. Ruth, at the station: "My grandson Alex just called. He's in jail, needs $2,000 bail, and said not to tell Mom."
   - Station: the full-screen green **Protected** card. Chaperone says it's a common scam, that a voice can be copied, and to call Alex at the number she has saved. Tap anywhere to close the card.
   - Priyank's phone beeps. **Safety** tab: the scam check, what it looked like in plain words, sources you can open, and **Why?**.
   - Wall: Ask lane row, **$2,000 protected**, and the Card lane shows the 24-hour cool-down.
2. Try it in Spanish or Hindi: "Mi nieto Alex acaba de llamar. Está en la cárcel, necesita 2000 dólares para la fianza y dijo que no le diga a mamá."
3. A plain refusal, not a scam check: "Buy a $100 gift card for someone at church." Chaperone refuses kindly; Priyank sees it under Refusals, no cool-down starts.

## 3. Card: the scammer's next move at a real store

1. Terminal: **Five Points Drug**, **$480**, **Tap card**.
   - Terminal: **DECLINED** with the plain reason (cool-down), "Chaperone decided in under 1 ms", and the whole swipe time.
   - Station: says why in Ruth's language, and shows the Protected card.
   - Wall: Card lane row with Visa's own card-controls answer beside it ("Visa VTC: …"). The protected counter does not add the $480 again: it's the same money the call asked for.
2. Priyank: **Approvals** tab shows the hold. Tap **Allow once** (10 minutes).
3. Terminal: same store, same amount, **Tap card**: **APPROVED** with the one-time pass. Tap again: declined (the pass is used up).
4. Terminal: **GiftCard Kiosk**, **$50**: **DECLINED**. Priyank sees "This kind of store stays blocked on Ruth's card" with only **Keep blocked**. Tap it: the hold leaves his list and the Approvals dot clears.
5. Priyank: **Home**, **Clear** next to the cool-down (or wait 24 hours).

## 4. Agent: errands across stores, and the bill

1. Ruth: "I need my blood pressure medicine and pay my power bill."
   - Station: the read-back names each store ("From Parkside Pharmacy: …. From Peachtree Power: your bill, $86.40.") and asks to place the order.
2. Ruth: "Yes."
   - Two signed orders, one per store, each verified by its store. The wall's Agent lane shows both, each with a Visa risk score (Decision Manager, on that store's own sandbox account).
3. Host: **Confirm payment** once. Both orders are paid.
   - Two receipts print (or show on screen), one per store. The bill's receipt has no pickup line.
   - Scan the receipt's QR code: the public session page with the story, the orders and the dispute record (JSON download).
4. An order that needs Priyank: "A case of Ensure shakes" ($52, over her $40 approval line).
   - Priyank's phone beeps; **Approvals** shows it with a countdown. **Approve with passkey** (or **Use a code instead** with the Host page's **Fallback code**).
   - Station: the order goes through; Host confirms payment.

## 4b. Anything Kroger sells

Ask for something the built-in catalog doesn't carry: "denture adhesive", "cat food", "reading glasses", "prune juice". Chaperone looks it up live at the Kroger store in Atlanta (about a second the first time, instant after that) with that store's real price, and it goes to the right store: denture adhesive to Parkside Pharmacy, cat food to Corner Market. "A bottle of wine" is found too, and Priyank's rules refuse it. The demo's own items (bread, the medicine, Ensure) never change.

## 5. The power-company call, after the bill is paid

Ruth: "Peachtree Power just called. They'll cut my power tonight unless I pay $480 in gift cards."
- Chaperone: "Ruth, your Peachtree Power bill is paid, so this call is a scam. Please hang up and don't pay anyone; I've told Priyank."
- This line uses her real account, so it only plays once the bill is paid (step 4). Before that, she hears the general scam line.

## 6. After the purchase: Priyank's view

- **Home**: this week's errands, bills paid and attempts stopped; protected dollars; spend by store (only money that actually left).
- **Activity**: every order by store, with **Cancel** for unpaid ones; refunds say which card the money goes back to.
- At the station, a return: "The Ensure shakes were damaged, I want my money back." Chaperone previews the amount and the card, then does it on "yes". Refunds only go back to the card that paid. (Medicine and bills can't be returned; Chaperone says so.)

## 7. The phone line

Call the xAI number:
1. "How much can I still spend this month?" answers without a PIN.
2. Ask for something to buy: Chaperone asks for the four-digit PIN first, and says she can speak it or type it on the keypad and press #. Try both. Typing two digits, pausing, then the other two also works ("I got part of it…"). It reads the cart back and places the order only on a clear "yes". A wrong PIN three times pauses PIN entry for 2 minutes, even if you hang up and call again.
3. Tell it the grandparent story: the same scam check as the station.
4. Wall: the call shows as started, then ended about 2 minutes after the last question.

## If something looks wrong

| Symptom | Check |
|---|---|
| A service shows DOWN on the station | `.claude/logs/<service>.log`; restart with `bash .claude/run.sh all` |
| Priyank's page is stale or signed out | Reopen it and sign in (his app restarts with the services) |
| No Visa VTC badge | Needs `keys/visa/cert.pem`, `key.pem` and `VISA_VDP_*`, `VISA_VTC_PAN` in `.env` |
| Terminal says card not enrolled | `sessions/card.json` is missing; enroll Ruth's card again |
| No "Call Ruth" button on Home | Set `RUTH_PHONE` in `.env`, restart |
| Everything is in a weird state | Host: **Reset demo** |
