"""
client.py — TypeSafe / Jev API Client Wrapper
=============================================
Manages connection to TypeSafe System One (Jev).
Handles authentication, timeouts, and error trapping so that network or API
failures never crash the AutoAds rendering engine.

TypeSafe SDK v0.7.0 verified:
  - TypeSafeClient(api_key=str, timeout=float)  — NO context manager required
  - client.system_one(state=dict, questions=dict, model=str) -> SystemOneResponse
  - Error hierarchy:
      TypeSafeError (base)
        TypeSafeAPIConnectionError
        TypeSafeAPITimeoutError
        TypeSafeAuthenticationError
        TypeSafeRateLimitError  (529 = service overloaded)
        TypeSafeInternalServerError
        TypeSafeAPIResponseValidationError
"""

from __future__ import annotations
import os
import logging
from typing import Optional, Dict, Any

try:
    import typesafe_sdk as _ts
    from typesafe_sdk import (
        TypeSafeClient,
        SystemOneResponse,
        TypeSafeError,
        TypeSafeAPIConnectionError,
        TypeSafeAPITimeoutError,
        TypeSafeAuthenticationError,
        TypeSafeRateLimitError,
        TypeSafeInternalServerError,
        TypeSafeAPIResponseValidationError,
    )
    _HAS_SDK = True
except ImportError:
    TypeSafeClient = None
    SystemOneResponse = None
    TypeSafeError = Exception
    TypeSafeAPIConnectionError = Exception
    TypeSafeAPITimeoutError = Exception
    TypeSafeAuthenticationError = Exception
    TypeSafeRateLimitError = Exception
    TypeSafeInternalServerError = Exception
    TypeSafeAPIResponseValidationError = Exception
    _HAS_SDK = False

logger = logging.getLogger("autoads.jev.client")


class JevClient:
    """
    Client wrapper for TypeSafe System One Jev model.

    Never raises — all failures return None so callers can use fallback.
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
        self._client: Optional[Any] = None

    def is_available(self) -> bool:
        """
        Returns True only if typesafe-sdk is installed and a valid API key is present.
        """
        return _HAS_SDK and bool(self.api_key)

    def _get_client(self) -> Optional[Any]:
        """Lazily initialise TypeSafeClient (reused across calls)."""
        if not _HAS_SDK or not self.api_key:
            return None
        if self._client is None:
            self._client = TypeSafeClient(
                api_key=self.api_key,
                timeout=self.timeout,
            )
        return self._client

    def evaluate(
        self,
        state: Any,
        questions: Dict[str, Any],
    ) -> Optional[Any]:
        """
        Calls TypeSafe System One API.
        Returns SystemOneResponse on success, or None on any failure.

        SDK v0.7.0: client.system_one() is called directly (no context manager).
        """
        if not self.is_available():
            logger.info("TypeSafe client unavailable (missing API key or SDK).")
            return None

        client = self._get_client()
        if client is None:
            return None

        try:
            response = client.system_one(
                state=state,
                questions=questions,
                model=self.model,
            )
            return response

        except TypeSafeAuthenticationError as e:
            logger.error(f"TypeSafe auth error (check TYPESAFE_API_KEY): {e}")
            # Invalidate client so next call re-creates it if key changes
            self._client = None
            return None

        except TypeSafeRateLimitError as e:
            # 529 Service Overloaded — safe to log as warning, use fallback
            logger.warning(f"TypeSafe rate limit / service overloaded (529): {e}")
            return None

        except TypeSafeAPITimeoutError as e:
            logger.warning(f"TypeSafe API timeout ({self.timeout}s): {e}")
            return None

        except TypeSafeAPIConnectionError as e:
            logger.warning(f"TypeSafe connection error: {e}")
            return None

        except TypeSafeAPIResponseValidationError as e:
            logger.warning(f"TypeSafe response validation error: {e}")
            return None

        except TypeSafeInternalServerError as e:
            logger.warning(f"TypeSafe internal server error: {e}")
            return None

        except Exception as e:
            logger.warning(f"TypeSafe unexpected error ({type(e).__name__}): {e}")
            return None
