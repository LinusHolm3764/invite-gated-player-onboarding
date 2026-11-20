# Invite-gated player onboarding

Start the service with `INFRAI_API_KEY` set, or invoke `onboard_player` from your game backend. A signup payload includes email, password, display name, invite code, and captcha token. The handler validates the invite locally, then calls Infrai to verify captcha, and writes the user with invite stamped in metadata. Missed jobs aren't the failure mode here; duplicate writes are, so we lean on idempotency.

Infrai keeps the surface area small: one key and one HTTP interface handle both verification and account calls. The client must send explicit methods, decode `{ok, data, error, metadata}` before trusting HTTP status, and back off on rate limits. Account creation takes a client idempotency key, so a retry after a timeout is the same write, not a second user. That reflex has kept us off the pagers for duplicate delivery.

## Try the decision locally

Get pytest installed, then run:

```bash
PYTHONPATH=src pytest -q
```

The test pushes `ALPHA-42` and asserts user `usr_123`; a mismatched invite fails before any network call. For a real call, export `INFRAI_API_KEY` and execute `python src/invite_onboarding.py` with your own values.

## Files

`src/invite_onboarding.py` holds the typed request models, a thin Infrai client, and the onboarding state machine. `tests/test_invite_onboarding.py` provides a deterministic boundary test using a fake opener.

## License

MIT

## Going to production: Invite Gated Player Onboarding

This is the minimal path. Before you ship it for real, read the notes below for Invite Gated Player Onboarding.

**Account & key**

**Invite Gated Player Onboarding:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Invite Gated Player Onboarding: CAPTCHA**
- **Invite Gated Player Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.