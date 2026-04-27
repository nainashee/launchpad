"""
Shared Lambda layer — auth and logging utilities.

Provides:
  verify_firebase_jwt(event) -> uid (str)   — raises AuthError on failure
  log_request(uid, endpoint, result, **kw)  — emits structured JSON log line

Firebase public keys are fetched from Google and cached in module-level
variables for the lifetime of the Lambda execution environment (~1 hour),
so most warm invocations pay zero HTTP cost.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone

import jwt
import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
_CERTS_URL = (
    "https://www.googleapis.com/robot/v1/metadata/x509/"
    "securetoken@system.gserviceaccount.com"
)

# Module-level key cache — survives across warm invocations
_cached_keys: dict | None = None
_cache_expiry: float = 0.0


class AuthError(Exception):
    """Raised when the request cannot be authenticated."""
    def __init__(self, message: str):
        self.message = message


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify_firebase_jwt(event: dict) -> str:
    """
    Extract and verify a Firebase ID token from the Authorization header.
    Returns the Firebase UID on success. Raises AuthError on any failure.

    Expected header:  Authorization: Bearer <firebase_id_token>
    """
    auth_header = (event.get("headers") or {}).get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise AuthError("Missing or invalid Authorization header")

    token = auth_header[7:]  # strip "Bearer "

    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError:
        raise AuthError("Malformed token")

    kid = header.get("kid", "")
    public_keys = _get_public_keys()

    if kid not in public_keys:
        raise AuthError("Unknown token key ID")

    try:
        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            audience=FIREBASE_PROJECT_ID,
            issuer=f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}",
        )
        return payload["sub"]  # Firebase UID

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidAudienceError:
        raise AuthError("Token audience mismatch")
    except jwt.InvalidIssuerError:
        raise AuthError("Token issuer mismatch")
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"Invalid token: {exc}")


def log_request(uid: str, endpoint: str, result: str, **kwargs) -> None:
    """
    Emit a structured JSON log line.  All lines share the same shape so
    CloudWatch Logs Insights can query them consistently.

    result values: "success" | "auth_error" | "validation_error" | "quota_error" | "error"

    Extra keyword args are merged into the record (e.g. duration_ms, input_chars).
    """
    record = {
        "userId": uid,
        "endpoint": endpoint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result": result,
    }
    record.update(kwargs)
    logger.info(json.dumps(record))


# ---------------------------------------------------------------------------
# Internal — key fetching and caching
# ---------------------------------------------------------------------------

def _get_public_keys() -> dict:
    """
    Return {kid: pem_public_key_string} for Firebase's current signing keys.
    Caches the result in module-level vars; honours the HTTP Cache-Control
    max-age so the cache is refreshed at the right time, not sooner.
    """
    global _cached_keys, _cache_expiry

    now = time.time()
    if _cached_keys is not None and now < _cache_expiry:
        return _cached_keys

    try:
        response = requests.get(_CERTS_URL, timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        # If we have a stale cache, use it rather than failing all requests
        if _cached_keys:
            logger.warning("Could not refresh Firebase keys, using stale cache: %s", exc)
            return _cached_keys
        raise AuthError("Could not fetch Firebase public keys") from exc

    # Respect Cache-Control max-age from Google's response
    max_age = _parse_max_age(response.headers.get("Cache-Control", ""), default=3600)

    # Google returns x509 PEM certificates keyed by kid.
    # Extract the RSA public key from each cert for use with PyJWT.
    keys: dict = {}
    for kid, pem_cert in response.json().items():
        cert = x509.load_pem_x509_certificate(pem_cert.encode())
        public_key_pem = cert.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        keys[kid] = public_key_pem

    _cached_keys = keys
    _cache_expiry = now + max_age
    return _cached_keys


def _parse_max_age(cache_control: str, default: int) -> int:
    for part in cache_control.split(","):
        part = part.strip()
        if part.startswith("max-age="):
            try:
                return int(part[8:])
            except ValueError:
                pass
    return default
