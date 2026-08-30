"""Password hashing utilities (bcrypt, used directly).

``bcrypt`` is used directly instead of ``passlib``: passlib 1.7.4 reads
``bcrypt.__about__.__version__`` during backend detection, an attribute removed
in bcrypt 4.1. That failure makes passlib skip its 72-byte truncation path,
and bcrypt 4.1+ then raises ``ValueError`` for the long probe secret passlib
uses in its self-test — so *every* hash/verify call fails, regardless of the
actual password length.
"""

import bcrypt

# bcrypt only considers the first 72 bytes of a password.
MAX_PASSWORD_LENGTH = 72

_ROUNDS = 12


def _truncate(plain: str) -> bytes:
    """Encode and truncate to bcrypt's 72-byte input limit.

    Truncation is done by *byte* length because multi-byte characters (e.g.
    Chinese) can be split mid-character; invalid trailing bytes are dropped.
    """
    raw = plain.encode("utf-8")
    if len(raw) <= MAX_PASSWORD_LENGTH:
        return raw
    return raw[:MAX_PASSWORD_LENGTH]


def hash_password(plain: str) -> str:
    """Hash a plaintext password, returning the stored-form string."""
    return bcrypt.hashpw(_truncate(plain), bcrypt.gensalt(rounds=_ROUNDS)).decode("ascii")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash.

    Returns False for malformed hashes instead of raising, so a corrupted
    record denies login rather than returning a 500.
    """
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("ascii"))
    except (ValueError, TypeError, UnicodeEncodeError):
        return False
