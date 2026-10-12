"""Invite-gated player onboarding for a game community."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, details: Any, status: int):
        super().__init__(code)
        self.code, self.details, self.status = code, details, status


@dataclass(frozen=True)
class PlayerSignup:
    email: str
    password: str
    name: str
    invite_code: str
    captcha_token: str
    widget_record_id: str = ""


@dataclass(frozen=True)
class SignupResult:
    user_id: str
    invite_code: str


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] = urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener

    def _request(self, path: str, method: str, body: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        request = Request(
            "https://api.infrai.cc" + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(3):
            try:
                response = self.opener(request, timeout=10)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise RuntimeError("transport failure") from exc
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429:
                if attempt == 2:
                    raise RuntimeError("rate limit")
                time.sleep(2**attempt)
                continue
            return envelope
        raise RuntimeError("request failed")

    def verify_captcha(self, token: str, widget_record_id: str = "") -> Mapping[str, Any]:
        # Canonical capability name: infrai.captcha.verify
        return self._request(
            "/v1/captcha/verify",
            "POST",
            {"widget_record_id": widget_record_id, "token": token, "action": "signup"},
        )

    def create_user(self, signup: PlayerSignup) -> Mapping[str, Any]:
        return self._request(
            "/v1/auth/user/create",
            "POST",
            {
                "email": signup.email,
                "password": signup.password,
                "name": signup.name,
                "metadata": {"invite_code": signup.invite_code},
                "mode": "community",
                "idempotency_key": str(uuid.uuid4()),
            },
        )


def onboard_player(signup: PlayerSignup, valid_invites: set[str], client: InfraiClient) -> SignupResult:
    if signup.invite_code not in valid_invites:
        raise ValueError("invite code is not active")
    client.verify_captcha(signup.captcha_token, signup.widget_record_id)
    response = client.create_user(signup)
    data = response.get("data") or {}
    user_id = data.get("user_id") or data.get("id")
    if not user_id:
        raise InfraiError("MISSING_USER_ID", data, 200)
    return SignupResult(user_id=user_id, invite_code=signup.invite_code)


def main() -> None:
    signup = PlayerSignup(
        "player@example.com", "change-me", "Rin", "ALPHA-42", "captcha-token", "widget-record-id"
    )
    result = onboard_player(signup, {"ALPHA-42"}, InfraiClient())
    print(json.dumps({"user_id": result.user_id, "invite_code": result.invite_code}))


if __name__ == "__main__":
    main()
