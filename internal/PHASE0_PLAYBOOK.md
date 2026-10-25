# Senior Sentinel: Phase 0 Playbook

As of 2026-09-25

Phase 0 runs tonight from 8:00 to 10:00pm and ends with a go/no-go at 10:00: four spikes, one per lane, that prove the voice, the trust chain, the sandbox and the refusal each work in isolation before anyone builds on them. Each of us works from our own section without asking the others until 9:30. Exact field names and commands are quoted from the docs linked in Section 10.

---

## 1. Phase 0 at a glance

Two hours, four spikes, one decision. Each spike proves one unknown in isolation with throwaway code; the go/no-go at 10:00 decides whether Phase 1 builds on Senior Sentinel as designed or on a rung of the fallback ladder.

| Time | Everyone | Manush (station) | Dhruv (trust) | Vraj (merchant, catalog, Visa) | Rohan (rules, judge, audio) |
|---|---|---|---|---|---|
| 8:00-8:30 | Shared setup: router, repo scaffold, vault, contracts frozen, standup rhythm (Section 3) | | | | |
| 8:30-9:15 | Spikes, heads down | Grok Voice round trip from a browser with push-to-talk and one tool call | A passkey asserted on the phone through the tunnel; an RFC 9421 request verified by a stub, tampered body and reused nonce rejected | A sandbox payment link created through the Visa MCP and opened; the Kroger seed started; the mock MCP shell | The rule layer refusing the three scam lines; a judge call returning schema-valid JSON on 10 scripts; one refusal clip rendered by TTS |
| 9:15-9:30 | Each lane demos its pass condition to the other three in two minutes | | | | |
| 9:30-10:00 | Integration smoke (Section 8): connect the four spikes end to end, ugly is fine | | | | |
| 10:00 | Go/no-go (Section 9) | | | | |

**Pass conditions, binary.**

- Manush: a Spanish sentence spoken while the button is held gets a Spanish reply within 1.5 s of release, the model calls `search_catalog`, and both transcripts print in the console.
- Dhruv: the caregiver phone completes a passkey assertion against the tunnel domain and the server verifies it; separately, a signed POST verifies in the stub, and a one-byte change to the body or a replayed nonce is rejected.
- Vraj: `create_payment_link` returns a hosted URL from the sandbox (real, or the mock with the identical schema if credentials are missing), and the URL opens; a test card completes it if the sandbox allows.
- Rohan: the three scam lines are refused before any model call in each language; the judge returns valid JSON for 10 of 10 scripts and separates the scam and benign halves; a Spanish refusal clip plays from a file.

**Exit criteria for the phase.** Go if Manush, Dhruv (passkeys or the six-digit fallback) and Rohan pass, and Vraj has a link from the real sandbox or the mock. Any other combination means the 10:00 standup picks a rung of the fallback ladder in `BUILD_PLAN.md` and writes it on the whiteboard.

**What Phase 0 is not.** Not the product, not clean code, not the final schemas. Spike code lives in `spikes/<lane>/` and is allowed to be thrown away; what survives into Phase 1 is the knowledge, the credentials, and the contracts.

---

## 2. Before 8pm today

HackGT's rule is no project code before 8pm; accounts, purchases, installs, reading and printing are fine, and they are the difference between a two-hour Phase 0 and a four-hour one.

**Accounts and keys (owner in brackets; all values go into the shared vault, never into chat or git).**

- [ ] Cybersource sandbox account created, email confirmed, Test Business Center login working, one REST shared-secret key generated; merchant id, key id and shared secret in the vault. (Vraj)
- [ ] xAI console: team created, all four invited, hackathon credits redeemed once the sponsor booth gives the code or link, one API key per person, spend limits visible. (Rohan)
- [ ] Kroger developer app registered (production, not certification); client id and secret in the vault; if registration is not instant, Vraj seeds the catalog synthetically instead. (Vraj)
- [ ] Tunnel domain fixed: an ngrok account with its free stable dev domain; write the exact hostname on the whiteboard because the passkey relying-party id is bound to it for the whole weekend. (Dhruv)
- [ ] Caregiver phone prepared: browser updated, screen lock with fingerprint or face enabled (passkeys need it), charged, able to join the team router. (Dhruv)
- [ ] Devpost account for each member, and the HexLabs registration names match. (Everyone)

**Hardware in hand, tested for power only.**

- [ ] USB HID push-to-talk button or foot pedal; a USB close-talk headset; a small USB speaker; a 58 mm USB ESC/POS receipt printer with three paper rolls; a tablet or second screen; the 5 GHz travel router with its power supply; two power strips; a USB hub; spare cables. (Manush collects, Vraj carries the router)
- [ ] Receipt printer driver installed on the station laptop and a test page printed from the OS (this is not project code). (Manush)

**Installs on every laptop.**

- [ ] Node 22, npm or pnpm, Python 3.11 with uv, git, Cursor with the team's Grok model selected, Claude Code.
- [ ] ngrok on Dhruv's laptop; the `mcp` Python SDK and Node 18+ for the Visa toolkit on Vraj's laptop.

**Reading (20 minutes each).**

- [ ] Everyone: `PRD.md` Sections 6 (the journey) and 9 (the contracts), and your own section of this playbook.

**Printing.**

- [ ] Line cards in Spanish, Hindi and English (`DEMO_RUNBOOK.md`), the table card with the sandbox disclaimer, and the fallback ladder for the whiteboard. (Rohan)

**Sponsor fair, 5:30-7:00pm.** Ask Visa whether their judges come to tables or judge from Devpost, and whether they have a sandbox contact for the weekend. Ask xAI how credits are issued. Ask the help desk whether personal routers are allowed in Klaus and whether tables have power.

---

## 3. Shared setup, 8:00-8:30pm

Thirty minutes, all four at the table, in this order; nobody starts a spike until the contracts are committed, because the spikes are only useful if they speak the same shapes.

**8:00-8:10, network (Vraj drives, others join).** Router on with a 5 GHz SSID `chaperone`, client isolation off, DHCP reservations by MAC: services laptop `192.168.8.10`, station laptop `.11`, Dhruv `.12`, Rohan `.13`, caregiver phone `.20`. Phone hotspot shared to the services and station laptops as a second interface for the cloud calls. Test: every laptop pings every other; each laptop reaches `https://api.x.ai` through the hotspot. Router settings: on GL.iNet, NETWORK, LAN, AP Isolation off and Address Reservation for the static IPs; on TP-Link, Wireless Advanced, uncheck Client Isolation, and DHCP Address Reservation.

**8:10-8:20, repo and vault (Dhruv drives).** In the `Senior_Sentinel` repository, add the layout from `BUILD_PLAN.md` with empty service folders, `.env.example`, and a `spikes/` folder with one subfolder per lane. Add `.cursor/rules` with four lines: policy is a pure function with no network calls; no secret ever reaches a browser; every event carries `session_id` and `t`; read-back before checkout. Everyone pulls. Planning docs stay in `internal/`; commit messages describe the code change only (no phase names, no strategy). The vault is a shared password-manager vault (or an encrypted note on one phone) holding: xAI keys, Cybersource merchant id, key id and secret, Kroger id and secret, the tunnel hostname, the agent Ed25519 private key once Dhruv generates it.

**8:20-8:30, contracts frozen (Dhruv writes, all four read).** Commit `contracts/` with one JSON Schema file each, copied from `PRD.md` Section 9: `mandate.schema.json`, `decision.schema.json`, `order_request.schema.json` (body plus the required signature headers), `approval.schema.json`, `events.schema.json` (the event union), `judge.schema.json`, `cart.schema.json`. Also `contracts/ports.md`: relay 8000, policy 8001, merchant 8002, catalog 8003, station 5173, caregiver 5175 (tunnel), wall 5176. A change to any of these after 8:30 needs all four at the table.

**The fakes, named now, built in Phase 1.** Each lane owes its neighbor a fake by Friday midnight: Vraj a fake catalog (`GET /search?q=` returning three items) for Manush; Dhruv a fake policy engine (`POST /checkout` returning allow) for Manush and Vraj; Vraj a fake merchant (`POST /orders` returning a fake link) for Dhruv; Rohan a fake judge (returns score 0.05) for Dhruv. Tonight they are just the URLs written on the whiteboard.

**Standup rhythm.** Every hour on the hour, two minutes, blockers only, standing. At 9:15 each lane demos its pass condition. The whiteboard has three columns: the fallback ladder, blockers, and the vault checklist.

**Cursor and Claude Code.** Both are allowed from 8:00. Use them for boilerplate inside the spikes; keep the spike pass conditions human-verified. Start the Cursor screen recording for the xAI evidence during the first real component in Phase 1, not tonight.

---

## 4. Manush: station spike, 8:30-9:15pm

One thing to prove: a browser page opens a Grok Voice session with an ephemeral token, streams the mic only while the button is held, gets a spoken reply in the language spoken within 1.5 s of release, calls a `search_catalog` tool, and prints both transcripts. Work in `spikes/manush/` as a single Vite or Next.js page plus a 20-line token endpoint. The xAI cookbook's web example is the closest starting point but uses server VAD and OpenAI-style subprotocols, so follow the steps below rather than copying it.

**8:30-8:40, token endpoint and socket (10 min).** Backend (FastAPI or a Next.js route): `POST https://api.x.ai/v1/realtime/client_secrets` with `Authorization: Bearer <XAI_API_KEY>` and body `{"expires_after": {"seconds": 300}}`; the response is `{"value": "xai-realtime-client-secret-...", "expires_at": ...}`. Browser: `new WebSocket("wss://api.x.ai/v1/realtime?model=grok-voice-think-fast-2.0", ["xai-client-secret." + token])`. Open the socket and the microphone in parallel to save latency. Pass: `session.updated` arrives after the next step.

**8:40-8:50, session configuration (10 min).** Send this once the socket opens; `turn_detection: null` is manual mode and means nothing happens until you commit:

```json
{"type":"session.update","session":{
  "instructions":"You are Senior Sentinel, a patient shopping helper for older adults. Speak slowly, one question at a time, plain words. Always reply in the language the user spoke in their most recent turn. Before any purchase, read back every item, its price and the total, and ask for a yes.",
  "voice":"ara",
  "reasoning":{"effort":"none"},
  "turn_detection":null,
  "audio":{
    "input":{"format":{"type":"audio/pcm","rate":48000},"transport":"json","transcription":{"keyterms":["Ensure","lisinopril"]}},
    "output":{"format":{"type":"audio/pcm","rate":48000},"transport":"json","speed":0.95}},
  "tools":[{"type":"function","name":"search_catalog","description":"Search the grocery and pharmacy catalog by a short query. Call this whenever the user names a product.",
    "parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}]}}
```

Notes from the docs: `reasoning.effort` is `"high"` or `"none"` (none for speed); codecs are `audio/pcm`, `audio/pcmu`, `audio/pcma`, `audio/opus`; PCM rates 8000 to 48000 with 24000 the default; set `rate` to your AudioContext's real sample rate (typically 48000) or the audio pitch-shifts; `transport: "json"` means base64 chunks; `keyterms` up to 100 items; `speed` 0.7 to 1.5. Transcription is built in; there is no `model` field, and `language_hint` only biases it (use `es-MX` or `hi` if set; omit it for a mixed-language demo). The model "automatically detects the input language and responds naturally in the same language"; the instruction line above pins it per turn. Voices: `ara` is warm and friendly, `naksh` is a warm Indian-accented voice that suits Hindi, `eve` and `leo` are British; every voice speaks every language.

**8:50-9:05, push to talk and audio (15 min).** The USB button arrives as a keyboard key (map it to Space). On keydown: start capture and send `{"type":"input_audio_buffer.append","audio":"<base64 pcm16>"}` every ~100 ms. On keyup: `{"type":"input_audio_buffer.commit"}` then `{"type":"response.create"}`. Cancel a reply with `{"type":"response.cancel"}`; discard a turn with `{"type":"input_audio_buffer.clear"}`. Capture as in the cookbook: `getUserMedia({audio:{channelCount:1, echoCancellation:true, noiseSuppression:true, autoGainControl:true}})`, `new AudioContext()`, a `createScriptProcessor(4096,1,1)` accumulating about 100 ms of samples, float32 to PCM16 to base64. Playback: decode each `response.output_audio.delta` (field `delta`, base64 PCM16) into an `AudioBuffer` at the context rate and schedule gaplessly: `startAt = Math.max(ctx.currentTime, nextPlayTime); source.start(startAt); nextPlayTime = startAt + buffer.duration`. In manual mode there are no `speech_started` events, so drive the UI from the key state and `input_audio_buffer.committed`.

**9:05-9:15, the tool round trip and transcripts (10 min).** Handle `response.function_call_arguments.done` (`call_id`, `name`, `arguments` as a JSON string): run the fake `search_catalog` (three hard-coded items tonight; Vraj's spike catalog during the smoke), reply with `{"type":"conversation.item.create","item":{"type":"function_call_output","call_id":"...","output":"{...}"}}` then `{"type":"response.create"}`; wait for playback to finish before that `response.create` so audio does not overlap. Transcripts: the user's from `conversation.item.input_audio_transcription.completed` (`transcript`; `.updated` gives the cumulative live text), the agent's from `response.output_audio_transcript.delta` and `.done`; `response.done` unlocks the button; `error` logs `error.type` and `error.message`. Pass: say "necesito pan" in Spanish while holding the button; within 1.5 s of release the agent answers in Spanish, the console shows a `search_catalog` call with a query, the tool result comes back spoken, and both transcripts print. Measure release-to-first-audio with `performance.now()` and write it on the whiteboard.

**Fail actions.** No reply at all: check the subprotocol string and that `session.update` was acknowledged. Reply but no tool call: sharpen the tool description and add one sentence to the instructions. Pitch-shifted audio: the `rate` fields do not match the AudioContext. Overlapping audio after a tool call: you sent `response.create` before playback ended. If nothing reliable by 9:30, rung 7 of the ladder: browser speech recognition, a Grok text model, browser speech synthesis, with Grok Voice retried Saturday morning.

**Costs and limits.** $0.08 per audio minute plus $0.004 per text input item (each `conversation.item.create`, including tool outputs, counts); tier 0 allows 10 concurrent sessions; a session lasts up to 120 minutes.

**Hand-off at 10:00.** `station/config/voice.json` with the exact session payload that worked (voice, rates, instructions, tool schema), the release-to-first-audio number, and the token endpoint moved into `relay/tokens.py`. Phase 1 builds the persona, the read-back rule in the tool contract, and the companion screen on top of this page.

---

## 5. Dhruv: trust spike, 8:30-9:15pm

Two things to prove: a passkey on the caregiver phone can sign a challenge that is the mandate's hash and the server verifies it through the tunnel domain; and a request signed with Ed25519 per RFC 9421 verifies in a separate process that also rejects a tampered body and a reused nonce. Work in `spikes/dhruv/`, Python for signing, a minimal Next.js app for the passkey.

**8:30-8:35, keys (5 min).** Generate the agent key pair and its JWK, and pick the canonicalization library; these lines are the basis of everything Vraj's merchant will verify.

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jwcrypto.jwk import JWK
import jcs, hashlib
priv = Ed25519PrivateKey.generate(); pub = priv.public_key()
jwk = JWK.from_pyca(pub).export_public(as_dict=True); jwk["kid"] = "senior-sentinel-agent-1"   # {"kty":"OKP","crv":"Ed25519","x":...}
mandate_hash = hashlib.sha256(jcs.canonicalize(mandate_dict)).digest()               # RFC 8785, 32 bytes
```

Use `jcs` in Python and `canonicalize` in JavaScript (not `canonicaljson`, which follows different rules). Save the private key to the vault; the JWK goes into `relay/jwks.json` as `{"keys":[jwk]}`.

**8:35-8:55, passkey through the tunnel (20 min).** Start the tunnel once and never change the hostname again this weekend: `ngrok http 5175 --url https://<your-free-dev-domain>` (the `--domain` flag is deprecated in favor of `--url`; every free account gets one stable dev domain). The free tier shows an interstitial page once per device; tap Visit on the phone, and add the header `ngrok-skip-browser-warning: 1` to the app's `fetch` calls so API requests skip it. A Cloudflare quick tunnel gets a new random host on every run, which would orphan the passkey, so only use Cloudflare if you own a domain for a named tunnel.

In a bare Next.js App Router app with SimpleWebAuthn v14 (Node 22+), four route handlers under `app/api/passkeys/`: generate-registration-options, verify-registration, generate-authentication-options, verify-authentication; keep the pending challenge in an httpOnly cookie. Exact calls:

```ts
// registration options
generateRegistrationOptions({ rpName: 'Senior Sentinel', rpID: '<tunnel-host>', userName: 'priya',
  attestationType: 'none', authenticatorSelection: { residentKey: 'preferred', userVerification: 'preferred' } })
// verify registration -> store registrationInfo.credential.{id, publicKey, counter, transports}
verifyRegistrationResponse({ response, expectedChallenge, expectedOrigin: 'https://<tunnel-host>', expectedRPID: '<tunnel-host>' })
// authentication over OUR challenge: the mandate hash
import { isoBase64URL } from '@simplewebauthn/server/helpers'
generateAuthenticationOptions({ rpID: '<tunnel-host>', challenge: mandateHashBytes /* Uint8Array */, allowCredentials: [{ id, transports }] })
verifyAuthenticationResponse({ response, expectedChallenge: isoBase64URL.fromBuffer(mandateHashBytes),
  expectedOrigin: 'https://<tunnel-host>', expectedRPID: '<tunnel-host>', credential: { id, publicKey, counter, transports } })
// browser (v11+ shape, object argument)
const attResp = await startRegistration({ optionsJSON }); const asseResp = await startAuthentication({ optionsJSON })
```

A custom challenge is supported: pass the 32-byte hash as `challenge` and verify against its base64url form. `expectedOrigin` is scheme plus host with no path or trailing slash, and the origin check is exact. Save `authenticationInfo.newCounter` after each assertion. Pass: register on the phone, then assert over a real mandate hash and see `verified: true` on the server. Fail: if the phone's authenticator rejects user verification, set `requireUserVerification: false` and note it; if the browser throws "Cannot read properties of undefined (reading 'challenge')", the client call is using the old positional form; if nothing works by 8:55, switch to the six-digit code page and keep passkeys for Saturday morning.

**8:55-9:15, RFC 9421 sign and verify (20 min).** Two Python processes, signer and verifier, using `http-message-signatures` 2.0.1 (Python 3.10 or later; it imports `http_sf`, not `http_sfv`):

```python
import hashlib, datetime, secrets, requests
from http_sf.compat import Dictionary
from http_message_signatures import HTTPMessageSigner, HTTPMessageVerifier, HTTPSignatureKeyResolver, algorithms
class KR(HTTPSignatureKeyResolver):
    def resolve_private_key(self, key_id): return PRIV               # Ed25519PrivateKey
    def resolve_public_key(self, key_id):  return jwks_lookup(key_id) # Ed25519PublicKey from the JWKS
req = requests.Request('POST', 'http://192.168.8.10:8002/orders', json=body, headers={'Content-Type': 'application/json'}).prepare()
req.headers['Content-Digest'] = str(Dictionary({'sha-256': hashlib.sha256(req.body).digest()}))   # RFC 9530
now = datetime.datetime.now(datetime.timezone.utc)
HTTPMessageSigner(signature_algorithm=algorithms.ED25519, key_resolver=KR()).sign(
    req, key_id='senior-sentinel-agent-1', created=now, expires=now + datetime.timedelta(minutes=8),
    nonce=secrets.token_urlsafe(32), tag='agent-payer-auth', label='sig1',
    covered_component_ids=('@method', '@authority', '@path', 'content-digest', 'content-type'))
# verifier side (FastAPI): rebuild a requests.Request from the incoming request, then
res = HTTPMessageVerifier(signature_algorithm=algorithms.ED25519, key_resolver=KR()).verify(
    req, max_age=datetime.timedelta(minutes=8), expect_tag='agent-payer-auth')
# then, in your code: recompute sha-256 of the raw body and compare to Content-Digest; reject res[0].nonce if seen in the last 8 minutes
```

The library emits `Signature-Input` and `Signature`, rejects a `created` in the future, an `expires` in the past, an age over `max_age`, and any `alg` other than `ed25519`; it returns the nonce but does not check replay, and body-digest verification is out of its scope, so those two checks are yours. In FastAPI, rebuild the message as `requests.Request(request.method, str(request.url), headers=dict(request.headers), data=await request.body()).prepare()` because the resolver reads only `method`, `url` and `headers`. Convention to state in `contracts/signing.md`: `alg="ed25519"` in lower case (the RFC-registered value the library accepts; Visa's example writes it capitalized), covered components as above, the 8-minute window, tag `agent-payer-auth` for orders, nonce kept for 8 minutes. Pass: a signed POST verifies; flipping one byte of the body fails the digest check; sending the same request twice fails on the nonce; an `expires` set to one minute ago fails. Fail: if the Python library fights past 9:10, the Node alternative is Cloudflare's `http-message-sig` 0.3.0 (`createSignature` and `verifySignature` with `parameters: { created, expires, nonce, alg, keyid, tag }`); if both fight, an HMAC placeholder tonight with the panel wording kept honest, Ed25519 by Saturday 9am.

**Hand-off at 10:00.** `contracts/signing.md` (the convention above), `relay/jwks.json`, the signer as `signer/sign.py` and the verifier as `merchant/verify.py` (Vraj runs it inside the merchant), the passkey route handlers moved into `caregiver/`, the tunnel hostname on the whiteboard and in the vault, and the stored credential (id, public key, counter, transports) for Priya's passkey in `caregiver/data/credentials.json` (gitignore it if it holds anything sensitive).

**Pitfalls.** `startRegistration` needs `{ optionsJSON }`; `credential.publicKey` is a `Uint8Array`, store it base64url; `rpID` is the bare hostname and is baked into the passkey, so the tunnel host must not change; `expectedOrigin` must equal `https://<tunnel-host>` exactly; the Python verifier surfaces the nonce and nothing more, so the nonce store and the digest comparison are two functions you write tonight and Vraj imports.

---

## 6. Vraj: merchant, catalog and Visa spike, 8:30-9:15pm

Three things to prove: the Visa Acceptance MCP creates a sandbox payment link from a script, a mock with the identical tool schema stands in when it cannot, and a local catalog can be seeded from Kroger and openFDA. The router is already up from the shared setup. Work in `spikes/vraj/`, Python.

**Before 8:30: the sandbox account.** Sign up at the Cybersource sandbox page (`https://developer.cybersource.com/hello-world/sandbox.html`); the Organization ID you choose is your merchant id. Confirm the email, sign in to the Test Business Center (`https://businesscentertest.cybersource.com`), then Payment Configuration, Key Management, Generate key, REST Shared Secret, Generate key: the Key value is the key id and the Shared Secret is the secret. All three into the vault. Two caveats from the docs: Pay by Link requires the merchant account to be enabled for Unified Checkout, which may need a support request, and a link's status only reads `ACTIVE` or `INACTIVE`; a payment is confirmed in Transaction Management or by the `payByLink.merchant.payment` webhook, not on the link. So the merchant marks an order paid on a callback either way; the difference is whether the link is real.

**8:30-8:50, a real link through the MCP (20 min).** The shipped CLI (v0.0.96) accepts only `merchant-id`, `api-key-id`, `secret-key`, `environment` (default `SANDBOX`) and `tools`; the README's `--use-test-env` is rejected, and the valid tool selectors are `invoices.create`, `invoices.read`, `invoices.update`, `paymentLinks.create`, `paymentLinks.read`, `paymentLinks.update`, `all`. Registered tool names are snake case: `create_payment_link`, `get_payment_link`, `list_payment_links`, `update_payment_link`. Call it from Python with the MCP SDK (`pip install "mcp[cli]"`; pass credentials as arguments because the subprocess environment is allow-listed):

```python
import asyncio, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
p = StdioServerParameters(command="npx", args=["-y", "@visaacceptance/mcp", "--tools=paymentLinks.create,paymentLinks.read",
    f"--merchant-id={os.environ['MID']}", f"--api-key-id={os.environ['KID']}", f"--secret-key={os.environ['SEC']}"], env=dict(os.environ))
async def main():
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize(); print([t.name for t in (await s.list_tools()).tools])
            res = await s.call_tool("create_payment_link", {"linkType": "PURCHASE", "purchaseNumber": "HG13A001", "currency": "USD",
                "totalAmount": "11.49", "lineItems": [{"productName": "Prescription pickup", "quantity": 1, "unitPrice": "8.00"},
                                                     {"productName": "Whole wheat bread", "quantity": 1, "unitPrice": "3.49"}]})
            print(res.content[0].text)
asyncio.run(main())
```

Rules from the tool schema and the REST API behind it: `purchaseNumber` unique, alphanumeric, under 20 characters; `totalAmount` as a string, always passed even though the tool marks it optional; the response carries `id`, `status`, and `purchaseInformation.paymentLink`, the hosted page URL. Open the link; pay with `4111 1111 1111 1111`, any future expiry, any CVV; 3-D Secure is off unless support enabled it. Then check Transaction Management in the Test Business Center for the authorization. Pass: a link URL printed and opened; bonus: an authorization visible in the Business Center. Fail on "not enabled" errors: capture the exact message, open a support request, and move to the mock; fail on credentials: same.

**8:50-9:05, the mock and the merchant stub (15 min).** `spikes/vraj/mock_mcp.py`: a class with `create_payment_link(args) -> dict` and `get_payment_link(id) -> dict` that returns the same JSON shape as the real tool (`id`, `status: "ACTIVE"`, `purchaseInformation.paymentLink` pointing at a local page `http://192.168.8.10:8002/pay/<id>` that shows a fake card form and a Pay button). Behind one interface `PaymentLinks` with `real` and `mock` implementations chosen by `MOCK_VISA=1`. Then the merchant stub: FastAPI `POST /orders` that (tonight) skips verification, calls `PaymentLinks.create`, stores the order, returns the link; `POST /pay/<id>/complete` (the mock's Pay button, or a real webhook later) marks the order paid and prints `paid`. Pass: a curl to `/orders` returns a link; visiting the mock page and clicking Pay prints `paid`.

**9:05-9:15, the catalog seed (10 min).** Kroger, if the app registered this afternoon (production credentials, not certification; they are not interchangeable): token with `POST https://api.kroger.com/v1/connect/oauth2/token`, header `Authorization: Basic base64(client_id:client_secret)`, form body `grant_type=client_credentials&scope=product.compact`; a store with `GET https://api.kroger.com/v1/locations?filter.zipCode.near=30308&filter.limit=5` (take `data[0].locationId`); products with `GET https://api.kroger.com/v1/products?filter.term=bread&filter.locationId=<id>&filter.limit=20`, keeping `productId`, `brand`, `description`, `categories`, `items[0].price.regular`, `items[0].price.promo`, `items[0].size`, and the medium image URL. Ten terms tonight (bread, milk, eggs, rice, beans, bananas, ibuprofen, acetaminophen, loratadine, Ensure), the rest in Phase 1; limits are 10,000 product calls a day. OTC names from openFDA: `https://api.fda.gov/drug/label.json?search=openfda.product_type:"HUMAN+OTC+DRUG"+AND+openfda.brand_name:"ibuprofen"&limit=100`, keeping `openfda.brand_name`, `openfda.generic_name`, `openfda.route`, `purpose`; 240 requests a minute without a key. Write everything to `catalog/catalog.json` as `{sku, name, brand, category, price, size, image, tags}` plus the two profile items (prescription pickup at $8.00, the usual whole wheat bread). Fail: if Kroger is not registered, write 30 items by hand from real product names with plausible prices and mark the file `source: synthetic`.

**Hand-off at 10:00.** `merchant/visa.py` (the `PaymentLinks` interface with real and mock), `merchant/config/visa.json` (environment, tool names, field mapping), `catalog/catalog.json` v0 and `catalog/profile.json`, the exact error text from the sandbox if any, and a note on the whiteboard: real link yes or no, paid confirmation path (Business Center, webhook through Dhruv's tunnel, or mock).

**Pitfalls.** `--use-test-env` is rejected; use `--environment` or the default. Docs list `paymentLinks.get` and `list` but the CLI accepts only `paymentLinks.read`. The MCP package was last published in July 2025. Kroger's docs are JavaScript-only, so the community client (`github.com/CupOfOwls/kroger-api`) is the readable reference.

---

## 7. Rohan: rules, judge and refusal audio, 8:30-9:15pm

Three things to prove: the hard rules refuse the three demo scam lines in three languages with no model in the loop, a Grok model returns schema-valid judge JSON that separates scam from benign scripts, and one refusal sentence renders to an audio file per language. Work in `spikes/rohan/` with Python and the OpenAI SDK pointed at xAI.

**8:30-8:40, keys and models (10 min).** Confirm the team's API key from the vault works: `client = OpenAI(api_key=..., base_url="https://api.x.ai/v1")` and one plain completion. Model choice, from the docs: `grok-4.7` supports structured outputs but reasoning cannot be disabled (minimum `reasoning_effort="low"`, and reasoning tokens bill as output); `grok-4.3` accepts `reasoning_effort="none"` for a non-reasoning mode at $1.25 in and $2.50 out per million; `grok-4.20-0309-non-reasoning` is the fastest with structured outputs and no reasoning. Plan: judge on `grok-4.7` with `low`, cart structurer on `grok-4.20-0309-non-reasoning`; measure both tonight and swap if the judge is too slow. `grok-4.7-fast` exists only in Cursor, not on the API.

**8:40-8:55, the rule layer (15 min).** A pure Python module `rules.py` with `evaluate(transcript_text: str, lang: str, cart: dict, mandate: dict) -> list[RuleHit]`. Version 0 needs only the rules the demo touches, each with an id, a lexicon per language (Spanish, Hindi in Devanagari and in Latin transliteration because the transcript may arrive either way, English), and a spoken-reason key:

- `R1_blocked_category`: gift card, prepaid card, wire, crypto, money order (es: tarjeta de regalo, tarjetas de regalo, giro; hi: गिफ्ट कार्ड, gift card, upahaar card, wire; en: gift card, prepaid card, wire).
- `R_family_emergency`: grandson, granddaughter, son, daughter plus trouble, jail, hospital, stranded, accident (es: nieto, nieta, hijo, hija, problemas, carcel, hospital; hi: पोता, pota, poti, beta, beti, museebat, jail, hospital).
- `R_urgency`: now, today, immediately, right away, urgent (es: ahora, hoy, inmediatamente, urgente; hi: abhi, aaj, turant, zaroori).
- `R_secrecy`: don't tell, keep this between us, secret (es: no le digas, secreto; hi: mat batana, kisi ko na batana).
- `R_authority`: IRS, police, Medicare, bank security, Microsoft, tech support (es: policia, impuestos, banco; hi: police, tax, bank).
- `R_third_party_instruction`: they said, he told me to, the man on the phone said (es: me dijo, me dijeron; hi: unhone kaha, phone pe bola).

Rule: any `R1` hit refuses outright; two soft hits send the transcript to the judge; one soft hit only slows the agent down (mandatory read-back). Test file: the three demo lines in each language (the gift-card scam, the medicine and bread purchase, the Ensure add-on) plus three benign sentences that contain a soft word without being a scam ("I need it today because my daughter is visiting"). Pass: the scam line hits `R1` and `R_family_emergency` in all three languages; the benign lines produce at most one soft hit. Normalize case and accents (`unicodedata.normalize('NFKD')`, strip combining marks) before matching.

**8:55-9:10, the judge call (15 min).** Every field in `required`, `additionalProperties` left at its default of false, non-empty enums (the API returns 400 on an empty enum and loses strictness if `additionalProperties` is set true):

```python
JUDGE_SCHEMA = {
  "type": "object",
  "properties": {
    "scam_score": {"type": "number", "minimum": 0, "maximum": 1},
    "patterns": {"type": "array", "items": {"type": "string",
      "enum": ["family_emergency", "urgency", "secrecy", "authority_impersonation", "code_reading", "amount_anomaly", "none"]}},
    "rationale": {"type": "string", "maxLength": 600},
    "action": {"type": "string", "enum": ["proceed", "ask_clarifying", "refuse_and_alert"]}
  },
  "required": ["scam_score", "patterns", "rationale", "action"]
}
r = client.chat.completions.create(
    model="grok-4.7", reasoning_effort="low", temperature=0,
    messages=[{"role": "system", "content": JUDGE_PROMPT},
              {"role": "user", "content": f"TRANSCRIPT:\n{t}\nCART:\n{cart}\nMANDATE:\n{mandate}"}],
    response_format={"type": "json_schema", "json_schema": {"name": "scam_judgment", "schema": JUDGE_SCHEMA, "strict": True}},
)
out = json.loads(r.choices[0].message.content)
```

The judge prompt in one paragraph: you are reviewing a shopping conversation for an older adult under a family-set mandate; score the probability the shopper is being coerced or deceived, using only the transcript; name the patterns; recommend proceed, ask a clarifying question, or refuse and alert; never invent facts. Run it on 10 scripts (5 scam, 5 benign, written now in English; the 40-script set is a Phase 1 task) and print `scam_score` and `action` for each. Then time the same 10 calls on `grok-4.20-0309-non-reasoning`. Pass: 10 of 10 schema-valid, every scam script scores above 0.6 and every benign below 0.4 on at least one of the two models, and the median latency is under 3 s. Fail: tighten the prompt with two few-shot examples front-loaded in the system message (it also helps prompt caching); if separation still fails, raise the refusal threshold to 0.8 and let the rules carry the demo. Do the cart structurer the same way with the cart schema from `PRD.md` on the non-reasoning model; one call on "necesito mi medicina para la presion y pan" against three fake catalog results is enough tonight.

**9:10-9:15, the refusal clip (5 min).** Render the refusal sentence per language with the TTS endpoint and play one:

```bash
for L in en es-MX hi; do
curl -X POST https://api.x.ai/v1/tts \
  -H "Authorization: Bearer $XAI_API_KEY" -H "Content-Type: application/json" \
  -d "{\"text\": \"$TEXT\", \"voice_id\": \"eve\", \"language\": \"$L\", \"speed\": 0.95, \"output_format\": {\"codec\": \"mp3\", \"sample_rate\": 44100, \"bit_rate\": 128000}}" \
  --output refusal_$L.mp3; done
```

Use `es-MX` or `es-ES`, not `es`; `hi` for Hindi; every voice is multilingual, and `GET /v1/tts/voices` lists them. Leave `with_timestamps` false or the response becomes JSON with base64 audio. Price is $15 per million characters, so the whole weekend's clips cost cents. Pass: three files exist and the Spanish one sounds right.

**Fallback to know about.** If the voice lane needs speech-to-text later, `POST https://api.x.ai/v1/stt` (multipart `file`, `model=grok-voice-transcribe-2.0`, `language`) returns `text` and `words[]` at $0.10 per hour.

**Console housekeeping (2 min, whenever).** Team at console.x.ai, members at `/team/default/users`, one API key per member at `/team/default/api-keys` so usage is attributable, promo code redeemed on `/team/default/billing`, spend visible at `/team/default/usage`; rate limits are team-level by spend tier. No documented hackathon-credit process exists; the xAI booth is the source.

**Hand-off at 10:00.** `ai/prompts/judge_schema.json`, `ai/prompts/judge_prompt.txt`, `ai/prompts/cart_schema.json`, `ai/rules/rules_v0.yaml` with the six rules and lexicons, `ai/warnings/refusal_{en,es-MX,hi}.mp3`, and the ten scripts with their scores and latencies in `spikes/rohan/eval_v0.md`.

**Eval snippet for Phase 1.**

```python
def score(rows):  # rows: [(is_scam: bool, predicted_block: bool)]
    tp = sum(a and b for a, b in rows); fp = sum((not a) and b for a, b in rows)
    fn = sum(a and (not b) for a, b in rows); tn = len(rows) - tp - fp - fn
    p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    print(f"TP={tp} FP={fp} FN={fn} TN={tn}\nprecision={p:.2f} recall={r:.2f} f1={f1:.2f}")
```

**Pitfalls.** `presence_penalty`, `frequency_penalty` and `stop` are incompatible with reasoning models. Reasoning tokens are not capped by `max_completion_tokens`. Keep the system prompt and few-shot examples first for cache hits. Expect roughly 1 to 3 s for a 1,500-token prompt with a 200-token JSON answer on the non-reasoning model, longer on grok-4.7.

---

## 8. Integration smoke, 9:30-10:00pm

Connect the four spikes in the order below, one link at a time, each proven by a printout before the next; the goal is one refusal and one purchase flowing through all four laptops, ugly, with console logs as the ledger.

1. **Voice to catalog (Manush and Vraj, 5 min).** Manush points the `search_catalog` tool handler at Vraj's spike catalog on `http://192.168.8.10:8003/search?q=`. Say "pan" in Spanish; the agent reads back a real item and price from Vraj's seed. Pass: the item name spoken matches the catalog line.
2. **Voice to policy (Manush and Dhruv, 5 min).** Manush's `checkout` tool posts the cart to Dhruv's stub policy on `:8001/checkout`, which returns `allow` with rule results. Pass: the decision JSON prints on Manush's console and the agent says "ordering now."
3. **Policy to signer to merchant (Dhruv and Vraj, 8 min).** Dhruv's signer signs an order request with the decision id; Vraj's merchant stub runs Dhruv's verifier code, then calls `create_payment_link` through the MCP (or the mock). Pass: the merchant prints "verified" and a payment link URL; a second send with the same nonce prints "rejected: replay."
4. **Rules in front of the tools (Rohan and Manush, 5 min).** Rohan's rule module is imported into Manush's tool handler; the gift-card line in Spanish returns a refusal before `search_catalog` runs; the agent speaks the refusal (the model reads Rohan's script text, or the pre-rendered clip plays). Pass: no catalog call, refusal heard, rule id printed.
5. **Judge in the loop (Rohan and Dhruv, 5 min).** Dhruv's stub policy calls Rohan's judge on the transcript for the benign purchase; score under threshold; decision still `allow`. Pass: the score prints in the decision JSON.
6. **Two runs end to end (all, 2 min).** Line 1 refused, line 2 purchased, both with printouts on all four screens.

**If a link fails.** Do not debug past 10 minutes on any one link; note it on the whiteboard and move to the next. A missing link is a Phase 1 task, not a Phase 0 failure, unless it is the pass condition of a spike.

**What to write down before 10:00.** Measured numbers from tonight: button release to first audio, checkout to verified, link creation time. The exact model ids, voice id, tool schema and session fields that worked. The exact tunnel hostname. Every credential's location in the vault.

---

## 9. Go/no-go at 10:00pm and hand-offs into Phase 1

The decision is a table lookup, not a debate: read each spike's result against the rows below, pick the rung, write it on the whiteboard, and start Phase 1 at 10:05.

| Spike | Result | Decision |
|---|---|---|
| Manush, voice | Reply within 1.5 s with a tool call | Go as designed |
| | Reply but no tool call | Go; Phase 1 starts with the tool schema, not the persona |
| | No reliable reply by 9:30 | Rung 7: fallback pipeline first (browser speech recognition, a Grok text model, browser TTS); Grok Voice retried Saturday morning |
| Dhruv, passkey | Assertion verified on the phone | Go |
| | Passkey fails, code fallback works | Go on rung 5; passkey retried Saturday 9am for the video |
| Dhruv, signature | Verified, tamper and replay rejected | Go |
| | Library fights | Swap library (Python to Node or back); if still failing at 10:00, HMAC placeholder tonight, Ed25519 by Saturday 9am; the merchant panel wording stays honest |
| Vraj, sandbox | Real link created and opened | Go |
| | Real link created, test card cannot complete | Go on rung 3: callback marks paid, Host line written now |
| | No credentials yet, or Pay by Link not enabled | Go on rung 4: mock MCP; inbox polled hourly |
| Rohan, rules and judge | Rules refuse; judge valid JSON separating the sets | Go |
| | Judge noisy | Go; threshold raised; rules carry the demo; judge tuned Saturday |
| | TTS clip fails | Go; the voice model reads the refusal script tonight; clips retried Saturday |

**Hand-offs into Phase 1 (each lane, by 10:15).**

- Move the surviving spike code into its service folder as the starting point; leave the rest in `spikes/`.
- Commit the exact working configuration as a file: Manush `station/config/voice.json` (model, voice, session fields, tool schema); Dhruv `contracts/signing.md` (covered components, parameters, JWKS path, window, nonce rule) and the tunnel hostname; Vraj `merchant/config/visa.json` (environment, tool names, field mapping) and `catalog/catalog.json` v0; Rohan `ai/prompts/` (judge schema, cart schema, refusal scripts, rule list v0).
- Write your Phase 1 fake for your neighbor first (Section 3), then your own service.

**Phase 1 first tasks, 10:15pm to midnight.** Manush: persona, read-back rule in the tool contract, companion screen skeleton. Dhruv: mandate form and passkey signing, policy engine with unit tests. Vraj: catalog and profile service, merchant service with the verifier, mock and real MCP behind one interface. Rohan: refusal scripts in three languages as files, judge prompt tuned on the 40-script eval set, pre-rendered clips.

**Sleep.** Manush and Rohan sleep 2 to 6am, Dhruv and Vraj 5 to 9am; whoever is awake at 6 runs the Phase 2 integration on the real catalog and policy engine.

---

## 10. Sources

Pages opened on Sep 25, 2026; the field names and commands above are quoted from them.

**Grok Voice (Manush):** [Voice Agent API guide](https://docs.x.ai/developers/model-capabilities/audio/voice-agent), [ephemeral tokens](https://docs.x.ai/developers/model-capabilities/audio/ephemeral-tokens), [voice REST and WebSocket reference](https://docs.x.ai/developers/rest-api-reference/inference/voice), [prompting guide](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech/prompting-guide), [xai-cookbook web voice example](https://github.com/xai-org/xai-cookbook/blob/main/voice-examples/agent/web), [community browser client](https://github.com/arthurkatcher/xai-voice-agent/blob/main/static/app.js), [flagship voices](https://x.ai/news/new-flagship-voices), [pricing](https://docs.x.ai/developers/pricing), [rate limits](https://docs.x.ai/developers/rate-limits).

**Passkeys and signing (Dhruv):** [SimpleWebAuthn server](https://simplewebauthn.dev/docs/packages/server), [browser](https://simplewebauthn.dev/docs/packages/browser), [custom challenges](https://simplewebauthn.dev/docs/advanced/server/custom-challenges), [Next.js App Router guide](https://rebeccamdeprey.com/blog/passkeys-webauthn-nextjs-practical-guide), [ngrok CLI](https://ngrok.com/docs/agent/cli), [ngrok free static domains](https://ngrok.com/blog/free-static-domains-ngrok-users), [ngrok interstitial](https://ngrok.com/docs/errors/err_ngrok_6024/), [http-message-signatures](https://pypi.org/project/http-message-signatures/) and its [README](https://github.com/pyauth/http-message-signatures/blob/main/README.rst), [Cloudflare http-message-sig](https://github.com/cloudflare/web-bot-auth/tree/main/packages/http-message-sig), [cryptography Ed25519](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/), [jwcrypto JWK](https://jwcrypto.readthedocs.io/en/latest/jwk.html), [jcs](https://pypi.org/project/jcs/), [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html), [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html), [Trusted Agent Protocol specification](https://developer.visa.com/capabilities/trusted-agent-protocol/trusted-agent-protocol-specifications).

**Visa sandbox, MCP and catalog (Vraj):** [Cybersource sandbox sign-up](https://developer.cybersource.com/hello-world/sandbox.html), [REST key generation](https://developer.cybersource.com/docs/cybs/en-us/platform/developer/all/rest/rest-getting-started/restgs-http-message-intro/restgs-security-key-pair-intro/restgs-security-key-pair-task.html), [key id article](https://support.visaacceptance.com/knowledgebase/knowledgearticle/?code=000002926), [testing guide](https://developer.cybersource.com/hello-world/testing-guide.html), [Agent Toolkit MCP quick start](https://developer.visaacceptance.com/docs/vas/en-us/agent-toolkit/quick-start/all/na/agent-toolkit/agent-toolkit-options/agent-toolkit-mcp.html), [CLI source](https://raw.githubusercontent.com/visaacceptance/agent-toolkit/main/modelcontextprotocol/src/index.ts), [createPaymentLink.ts](https://raw.githubusercontent.com/visaacceptance/agent-toolkit/main/typescript/src/shared/paymentLinks/createPaymentLink.ts), [Pay by Link intro](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-intro.html), [Pay by Link webhooks](https://developer.cybersource.com/docs/cybs/en-us/paybylink/developer/all/rest/paybylink/paybylink-webhooks-intro.html), [MCP Python SDK](https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/v1.12.0/README.md), [Kroger community client](https://github.com/CupOfOwls/kroger-api), [openFDA authentication](https://open.fda.gov/apis/authentication/), [GL.iNet LAN settings](https://docs.gl-inet.com/router/en/4/interface_guide/lan/), [TP-Link device isolation](https://www.tp-link.com/us/support/faq/3968/).

**Grok text, TTS and console (Rohan):** [structured outputs](https://docs.x.ai/developers/model-capabilities/text/structured-outputs), [reasoning](https://docs.x.ai/developers/model-capabilities/text/reasoning), [grok-4.7](https://docs.x.ai/developers/models/grok-4.7), [grok-4.3](https://docs.x.ai/developers/models/grok-4.3), [grok-4.20 non-reasoning](https://docs.x.ai/developers/models/grok-4.20-0309-non-reasoning), [text to speech](https://docs.x.ai/developers/model-capabilities/audio/text-to-speech), [speech to text](https://docs.x.ai/developers/model-capabilities/audio/speech-to-text), [team management](https://docs.x.ai/developers/faq/team-management), [billing](https://docs.x.ai/console/billing), [prompt caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/best-practices).
