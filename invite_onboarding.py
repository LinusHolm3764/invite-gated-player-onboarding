"""Compatibility entry point for the src-layout onboarding module.

This keeps the module importable when the repository is exercised directly
without an editable install or an explicit ``PYTHONPATH=src`` setting.
"""

from src.invite_onboarding import (  # noqa: F401
    InfraiClient,
    InfraiError,
    PlayerSignup,
    SignupResult,
    main,
    onboard_player,
)

__all__ = [
    "InfraiClient",
    "InfraiError",
    "PlayerSignup",
    "SignupResult",
    "main",
    "onboard_player",
]
