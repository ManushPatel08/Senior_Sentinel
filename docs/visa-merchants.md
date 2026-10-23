# Visa sandbox merchants (Phase 5, X5-1)

Registry: `contracts/merchants.json`. Each storefront makes its Pay by Link on its own Cybersource sandbox account
when `<prefix>MERCHANT_ID`, `<prefix>API_KEY_ID` and `<prefix>SECRET_KEY` are in `.env`; otherwise on the main
account (`VISA_ACCEPTANCE_*`), tagged by the purchase number prefix and the store's name on the line
("Parkside Pharmacy - Lisinopril ..."). `GET :8002/panel` → `storefronts` shows which, live.

Re-run: `python -m merchant.spike_link --stores --no-open` (one real $1.00 link per storefront).

## Sat Sep 26, ~5:50pm: one real link per storefront (pass condition 6)

| Store | Account | Mode | Purchase number / link id |
|---|---|---|---|
| Corner Market | `hackgt_13_1790386462` | own account | `CM6AB833BC6B464F` |
| Parkside Pharmacy | `hackgt_13_1790386462` | main account, tagged `PHARM` | `PHARM6AB833C044D5C7` |
| Main Street Home | `hackgt_13_1790386462` | main account, tagged `HOME` | `HOME6AB833C0135D30` |
| Peachtree Power | `hackgt_13_1790386462` | main account, tagged `POWER` | `POWER6AB833C1F6FB12` |

All four on `ebc2test.cybersource.com/ebc2/payByLink/pay/...`.

## Sat Sep 26, ~5:51pm: Parkside and Main Street on their own accounts

Keys from Dhruv (Parkside) and Rohan (Main Street) are in `.env`. Pay by Link check on both: signed
`GET /ipl/v2/payment-links?offset=0&limit=1` → 404 "No payment links found" (authenticated, service on, empty);
creating a link then worked on each.

| Store | Account | Mode | Purchase number / link id |
|---|---|---|---|
| Corner Market | `hackgt_13_1790386462` | own account | `CM6AB83E35AC19F2` |
| Parkside Pharmacy | `chaperone_1790457937` (Dhruv) | **own account** | `PHARM6AB83E386B696E` |
| Main Street Home | `chap_mainst26_1790458309` (Rohan) | **own account** | `HOME6AB83E3A23581D` |
| Peachtree Power | `hackgt_13_1790386462` | main account, tagged `POWER` (Manush's account pending) | `POWER6AB83E3CE87365` |
 When a teammate's account keys arrive, add them
under `CYBS_PARKSIDE_*`, `CYBS_MAINST_*` or `CYBS_PEACHTREE_*`, restart the merchant, re-run the spike, and
update this table (check Pay by Link first: signed `GET /ipl/v2/payment-links?offset=0&limit=1` → 200).

Dhruv's check (Sat ~5:55pm), once each account had a link: signed `GET /ipl/v2/payment-links?offset=0&limit=1` on
`apitest.cybersource.com` → **HTTP 200** on both. Five Ensure at $49.95 (one line, quantity 1, unit price 49.95),
read back from Visa as 49.95 ACTIVE:

| Store | Account | Link | Hosted page shows $49.95 |
|---|---|---|---|
| Parkside Pharmacy | `chaperone_1790457937` | `PHARM6AB83E9BF072C3` | ✅ $49.95, 1 × $49.95, max qty 1 (header "Chaperone, Stony Brook NY": the account's company name) |
| Main Street Home | `chap_mainst26_1790458309` | `HOME6AB83E9E2E5221` | ✅ $49.95, 1 × $49.95, max qty 1 (header "Main Street") |


## Sat Sep 26, ~6:45pm: Peachtree Power on its own account; every store has its own

Keys from Manush (`chaperone_pp_1790462505`) are in `.env` as `CYBS_PEACHTREE_*`. Dhruv's check: signed
`GET /ipl/v2/payment-links?offset=0&limit=1` → 404 "No payment links found" on the empty account, **200** once it had
a link. Five Ensure at $49.95 read back from Visa as 49.95 ACTIVE (`POWER6AB84AEDC74188`), and the real bill link
"Peachtree Power bill PP-...0098" at $86.40 (`POWER6AB84AF0D296B9`). Hosted page to confirm by eye.

| Store | Account | Mode |
|---|---|---|
| Corner Market | `hackgt_13_1790386462` | own account |
| Parkside Pharmacy | `chaperone_1790457937` (Dhruv) | own account |
| Main Street Home | `chap_mainst26_1790458309` (Rohan) | own account |
| Peachtree Power | `chaperone_pp_1790462505` (Manush) | own account |
