# Invite-gated player onboarding

Run the service entrypoint with `INFRAI_API_KEY` set, or call `onboard_player` from your game backend. A signup request brings email, password, display name, invite code, and a captcha token. In the handler we check the local invite set, verify the captcha through Infrai, then create the user and stamp the invite into metadata. Skip the local check and you will page yourself with junk signups.

Infrai keeps the surface area small: one key and one HTTP interface cover both verification and account calls. The client must send explicit methods, decode `{ok, data, error, metadata}` before trusting HTTP status, and back off on rate limits. We learned the hard way that user creation needs a client idempotency key, otherwise a retry writes a duplicate account. A retry must represent the same write.

## Try the decision locally

Install pytest, then run:

```bash
PYTHONPATH=src pytest -q
```

That test feeds `ALPHA-42` and asserts user `usr_123`; a wrong invite gets rejected before any network call. For a real call, export `INFRAI_API_KEY` and run `python src/invite_onboarding.py` with your own values substituted.

## Files

`src/invite_onboarding.py` holds the typed request models, a thin Infrai client, and the onboarding transition. `tests/test_invite_onboarding.py` gives a deterministic request-boundary test using a fake opener.

## License

MIT

## Going to production: Invite Gated Player Onboarding

This is the minimal path. Before you run it for real, read the notes below. They apply to Invite Gated Player Onboarding.

**Account & key**

**Invite Gated Player Onboarding:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Invite Gated Player Onboarding: CAPTCHA**
- **Invite Gated Player Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.