"""
client.py — TypeSafe / Jev API Client Wrapper
=============================================
Manages connection to TypeSafe System One (Jev).
Handles authentication, timeouts, and error trapping so that network or API
failures never crash the AutoAds rendering engine.
"""

from __future__ import annotations
import os
import logging
from typing import Optional, Dict, Any

try:
    from typesafe_sdk import TypeSafeClient, SystemOneResponse
    from typesafe_sdk import TypeSafeError
    _HAS_SDK = True
except ImportError:
    TypeSafeClient = None
    SystemOneResponse = None
    TypeSafeError = Exception
    _HAS_SDK = False

logger = logging.getLogger("autoads.jev.client")


class JevClient:
    """
    Client wrapper for TypeSafe System One Jev model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "jev-latest",
        timeout: float = 10.0,
    ):
        self.api_key = api_key or os.environ.get("TYPESAFE_API_KEY", "").strip()
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        """
        Returns True only if typesafe-sdk is installed and a valid API key is present.
        """
        return _HAS_SDK and bool(self.api_key)

    def evaluate(
        self,
        state: Any,
        questions: Dict[str, Any],
    ) -> Optional[SystemOneResponse]:
        """
        Calls TypeSafe System One API to evaluate the given state with questions.
        Returns the SystemOneResponse on success, or None on any failure.
        """
        if not self.is_available():
            logger.info("TypeSafe client unavailable (missing API key or SDK).")
            return None

        try:
            with TypeSafeClient(api_key=self.api_key, timeout=self.timeout) as client:
                response = client.system_one(
                    state=state,
                    questions=questions,
                    model=self.model,
                )
                return response
        except Exception as e:
            logger.warning(f"TypeSafe API evaluation failed: {e}")
            return None
