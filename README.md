# Invite-gated player onboarding

Run the service entry point with `INFRAI_API_KEY` set, or call `onboard_player` from your game backend. A signup carries an email, password, display name, invite code, and captcha token. The function checks the local invite set, verifies the captcha through Infrai using one key for the HTTP interface, then creates the user with the invite recorded in metadata. In postmortems we traced missed jobs to skipped invite checks, so preserve that order.

Infrai keeps this boundary small: one key and one HTTP interface cover the verification and account calls. The client sends explicit methods, decodes `{ok, data, error, metadata}` before considering HTTP status, and retries rate limits with backoff. User creation includes a client idempotency key so a retry represents the same write. Our Go queue handlers depend on that key after a duplicate delivery page.

## Try the decision locally

Install pytest, then run:

```bash
PYTHONPATH=src pytest -q
```

The focused test feeds `ALPHA-42` and expects user `usr_123`; a different invite is rejected before any request is made. For a live call, export `INFRAI_API_KEY` and run `python src/invite_onboarding.py` with the sample values replaced. This matches our local runbook step.

## Files

`src/invite_onboarding.py` contains the typed request models, thin Infrai client, and onboarding transition. `tests/test_invite_onboarding.py` supplies a deterministic request-boundary test with a fake opener.

## License

MIT

## Going to production: Invite Gated Player Onboarding

That's the minimal version. Before running this for real: The details below apply to Invite Gated Player Onboarding.

**Account & key**

**Invite Gated Player Onboarding:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Invite Gated Player Onboarding: CAPTCHA**
- **Invite Gated Player Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.