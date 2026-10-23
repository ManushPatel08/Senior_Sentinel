# Chaperone Phase 0: commands and pass conditions (Fri Sep 25, 8:00-10:00pm)

Full playbook with the reasoning, fail actions and sources: https://claude.ai/code/artifact/4a9d5c03-fbb6-4f0f-a5df-0da76eacb5a3

## Timeline
- 8:00-8:30 shared setup: router (SSID `chaperone`, client isolation off, static IPs .10 services, .11 station, .12 Dhruv, .13 Rohan, .20 caregiver phone; hotspot as second interface), repo scaffold, vault, `contracts/*.schema.json` from PRD section 9, ports (relay 8000, policy 8001, merchant 8002, catalog 8003, station 5173, caregiver 5175 via tunnel, wall 5176).
- 8:30-9:15 spikes in `spikes/<lane>/`. 9:15 two-minute demos. 9:30-10:00 integration smoke. 10:00 go/no-go.

## Manush: Grok Voice round trip with push-to-talk and one tool
- Token: `POST https://api.x.ai/v1/realtime/client_secrets` body `{"expires_after":{"seconds":300}}` -> `{"value":"xai-realtime-client-secret-...","expires_at":...}`.
- Socket: `new WebSocket("wss://api.x.ai/v1/realtime?model=grok-voice-think-fast-2.0", ["xai-client-secret." + token])`.
- `session.update`: `instructions`, `voice: "ara"` (`naksh` for Hindi), `reasoning: {effort: "none"}`, `turn_detection: null`, `audio.input/output.format: {type: "audio/pcm", rate: <AudioContext rate>}`, `transport: "json"`, `tools: [{type: "function", name: "search_catalog", parameters: {...}}]`.
- Key down: `input_audio_buffer.append` (base64 PCM16, ~100 ms chunks). Key up: `input_audio_buffer.commit` then `response.create`.
- Handle: `response.output_audio.delta` (`delta`), `response.output_audio_transcript.delta/.done`, `conversation.item.input_audio_transcription.completed` (`transcript`), `response.function_call_arguments.done` (`call_id`, `name`, `arguments`) -> `conversation.item.create {type: "function_call_output", call_id, output}` then `response.create` after playback ends; `response.done`; `error`.
- Pass: Spanish in, Spanish reply < 1.5 s after release, tool call logged, both transcripts printed.

## Dhruv: passkey through the tunnel and RFC 9421 sign/verify
- Tunnel (never change the host): `ngrok http 5175 --url https://<free-dev-domain>`; tap Visit once on the phone; add header `ngrok-skip-browser-warning: 1` on fetches.
- Keys: `Ed25519PrivateKey.generate()`; JWK via `JWK.from_pyca(pub).export_public(as_dict=True)` + `kid`; mandate hash = `sha256(jcs.canonicalize(mandate))`.
- Passkey (SimpleWebAuthn v14, Node 22+): `generateRegistrationOptions({rpName, rpID: '<tunnel-host>', userName, attestationType: 'none', authenticatorSelection: {residentKey: 'preferred', userVerification: 'preferred'}})`; `verifyRegistrationResponse({response, expectedChallenge, expectedOrigin: 'https://<tunnel-host>', expectedRPID})`; `generateAuthenticationOptions({rpID, challenge: mandateHashBytes, allowCredentials})`; `verifyAuthenticationResponse({response, expectedChallenge: isoBase64URL.fromBuffer(mandateHashBytes), expectedOrigin, expectedRPID, credential})`. Browser: `startRegistration({optionsJSON})`, `startAuthentication({optionsJSON})`.
- Signing (`http-message-signatures` 2.0.1): `HTTPMessageSigner(signature_algorithm=algorithms.ED25519, key_resolver=KR()).sign(req, key_id='chaperone-agent-1', created=now, expires=now+8min, nonce=secrets.token_urlsafe(32), tag='agent-payer-auth', label='sig1', covered_component_ids=('@method','@authority','@path','content-digest','content-type'))`; `Content-Digest: sha-256=:<base64 raw digest>:` set by you; verify with `HTTPMessageVerifier(...).verify(req, max_age=8min, expect_tag='agent-payer-auth')` plus your own digest comparison and 8-minute nonce store.
- Pass: assertion verified on the phone; signed POST verifies; tampered body, reused nonce and expired window rejected.

## Vraj: sandbox payment link, mock, catalog seed
- Sandbox: sign up at developer.cybersource.com/hello-world/sandbox.html (Organization ID = merchant id) -> Test Business Center -> Payment Configuration > Key Management > Generate key > REST Shared Secret (Key = key id). Pay by Link may need Unified Checkout enabled; link status is only ACTIVE/INACTIVE, payment confirmed in Transaction Management or by webhook -> merchant marks paid on callback either way.
- MCP: `npx -y @visaacceptance/mcp --tools=paymentLinks.create,paymentLinks.read --merchant-id=... --api-key-id=... --secret-key=...` (sandbox default; `--use-test-env` is rejected). Tools: `create_payment_link`, `get_payment_link`, `list_payment_links`, `update_payment_link`. Create args: `linkType: "PURCHASE"`, `purchaseNumber` (< 20 alnum, unique), `currency`, `totalAmount` (string, always), `lineItems[{productName, quantity, unitPrice}]` -> `id`, `status`, `purchaseInformation.paymentLink`.
- Python client: `mcp` SDK, `StdioServerParameters(command="npx", args=[...])`, `stdio_client`, `ClientSession.initialize()`, `call_tool("create_payment_link", {...})`.
- Test card 4111 1111 1111 1111, any future expiry, any CVV; 3DS off unless support enabled it.
- Mock: `PaymentLinks` interface with `real`/`mock`, `MOCK_VISA=1`; mock link -> `http://192.168.8.10:8002/pay/<id>` with a Pay button -> `paid`.
- Kroger: token `POST https://api.kroger.com/v1/connect/oauth2/token` (Basic client_id:secret; `grant_type=client_credentials&scope=product.compact`); `GET /v1/locations?filter.zipCode.near=30308&filter.limit=5`; `GET /v1/products?filter.term=bread&filter.locationId=<id>&filter.limit=20`. openFDA: `https://api.fda.gov/drug/label.json?search=openfda.product_type:"HUMAN+OTC+DRUG"+AND+openfda.brand_name:"ibuprofen"&limit=100`.
- Pass: a link URL printed and opened (real or mock); `catalog/catalog.json` v0 with ten terms plus the two profile items.

## Rohan: rules, judge, refusal audio
- Rules v0 (`rules.py`, lexicons in es/hi/en incl. Latin-transliterated Hindi, NFKD-normalized): R1_blocked_category (refuse), R_family_emergency, R_urgency, R_secrecy, R_authority, R_third_party_instruction (two soft hits -> judge).
- Judge: `client = OpenAI(base_url="https://api.x.ai/v1")`, model `grok-4.7` with `reasoning_effort="low"`, `temperature=0`, `response_format={"type":"json_schema","json_schema":{"name":"scam_judgment","schema":JUDGE_SCHEMA,"strict":True}}`; all fields required, `additionalProperties` left false, non-empty enums. Time the same on `grok-4.20-0309-non-reasoning` (cart structurer uses it).
- TTS: `POST https://api.x.ai/v1/tts` `{"text","voice_id":"eve","language":"es-MX"|"hi"|"en","speed":0.95,"output_format":{"codec":"mp3","sample_rate":44100,"bit_rate":128000}}` -> mp3 files.
- Pass: scam lines refused pre-model in three languages; 10/10 valid JSON with scam > 0.6 and benign < 0.4 on one model; three refusal clips exist.

## Integration smoke 9:30-10:00
1. Voice -> Vraj's catalog. 2. Voice -> Dhruv's stub policy (allow). 3. Policy -> signer -> merchant verify -> payment link; replay rejected. 4. Rules in front of the tools: gift-card line refused. 5. Judge score in the decision. 6. Two runs: refusal, purchase.

## Go/no-go 10:00
Go if Manush, Dhruv (passkey or code fallback) and Rohan pass and Vraj has a link (real or mock). Otherwise pick the ladder rung (Build Plan tab) and write it on the whiteboard. Hand-offs: `station/config/voice.json`, `contracts/signing.md` + `relay/jwks.json`, `merchant/visa.py` + `catalog/catalog.json`, `ai/prompts/*` + `ai/rules/rules_v0.yaml` + `ai/warnings/*.mp3`.
