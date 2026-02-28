from app.auth.jwt import create_access_token, decode_access_token
from app.auth.security import hash_secret, verify_secret


def test_hash_and_verify_secret():
    raw = "p@ssword-1234"
    secret_hash = hash_secret(raw)

    assert secret_hash.startswith("pbkdf2_sha256$")
    assert verify_secret(raw, secret_hash) is True
    assert verify_secret("wrong-value", secret_hash) is False


def test_token_roundtrip_parent_claims():
    token = create_access_token(subject="parent_abc", role="parent")
    claims = decode_access_token(token)

    assert claims["sub"] == "parent_abc"
    assert claims["role"] == "parent"
    assert "exp" in claims


def test_token_roundtrip_student_claims():
    token = create_access_token(subject="student_xyz", role="student", parent_id="parent_abc")
    claims = decode_access_token(token)

    assert claims["sub"] == "student_xyz"
    assert claims["role"] == "student"
    assert claims["parent_id"] == "parent_abc"
