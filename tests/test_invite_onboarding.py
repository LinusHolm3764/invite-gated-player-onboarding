from invite_onboarding import InfraiClient, PlayerSignup, onboard_player


class Response:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        import json
        return json.dumps(self.payload).encode()


def test_valid_invite_verifies_captcha_and_creates_user():
    calls = []

    def opener(request, timeout):
        calls.append((request.method, request.full_url, request.data))
        if request.full_url.endswith("/v1/captcha/verify"):
            return Response({"ok": True, "data": {"verified": True}})
        return Response({"ok": True, "data": {"user_id": "usr_123"}})

    signup = PlayerSignup("p@example.com", "pw", "P", "ALPHA-42", "token")
    result = onboard_player(signup, {"ALPHA-42"}, InfraiClient("test-key", opener))
    assert result.user_id == "usr_123"
    assert [call[0] for call in calls] == ["POST", "POST"]
    assert calls[0][1].endswith("/v1/captcha/verify")


def test_invalid_invite_stops_before_api_call():
    def opener(*args, **kwargs):
        raise AssertionError("API should not be called")

    signup = PlayerSignup("p@example.com", "pw", "P", "NOPE", "token")
    try:
        onboard_player(signup, {"ALPHA-42"}, InfraiClient("test-key", opener))
    except ValueError as exc:
        assert "invite code" in str(exc)
    else:
        raise AssertionError("expected rejection")
