from base64 import urlsafe_b64decode, urlsafe_b64encode
from hashlib import pbkdf2_hmac
from hmac import compare_digest
import os


def hash_secret(value: str) -> str:
    salt = os.urandom(16)
    digest = pbkdf2_hmac("sha256", value.encode("utf-8"), salt, 120_000)
    salt_b64 = urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${salt_b64}${digest_b64}"


def verify_secret(value: str, stored_hash: str) -> bool:
    try:
        algorithm, salt_b64, digest_b64 = stored_hash.split("$", 2)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = urlsafe_b64decode(salt_b64.encode("ascii"))
        digest = urlsafe_b64decode(digest_b64.encode("ascii"))
    except Exception:
        return False

    candidate = pbkdf2_hmac("sha256", value.encode("utf-8"), salt, 120_000)
    return compare_digest(candidate, digest)
