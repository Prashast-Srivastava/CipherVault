import hashlib
import pytest
from project import generate_password, hash_password, search_vault


# ── test_generate_password ────────────────────────────────────────────────────

def test_generate_password_default_length():
    assert len(generate_password()) == 16


def test_generate_password_custom_length():
    for length in [8, 20, 32, 64]:
        assert len(generate_password(length=length)) == length


def test_generate_password_too_short_raises():
    with pytest.raises(ValueError):
        generate_password(length=3)


def test_generate_password_no_charset_raises():
    with pytest.raises(ValueError):
        generate_password(use_upper=False, use_lower=False,
                          use_digits=False, use_symbols=False)


def test_generate_password_contains_upper():
    pwd = generate_password(length=20, use_upper=True,
                            use_lower=False, use_digits=False, use_symbols=False)
    assert any(c.isupper() for c in pwd)


def test_generate_password_no_upper_when_disabled():
    pwd = generate_password(length=20, use_upper=False,
                            use_lower=True, use_digits=True, use_symbols=False)
    assert not any(c.isupper() for c in pwd)


def test_generate_password_uniqueness():
    passwords = {generate_password(length=16) for _ in range(20)}
    assert len(passwords) > 15


def test_generate_password_only_digits():
    pwd = generate_password(length=12, use_upper=False, use_lower=False,
                            use_digits=True, use_symbols=False)
    assert pwd.isdigit()


# ── test_hash_password ────────────────────────────────────────────────────────

def test_hash_password_returns_string():
    assert isinstance(hash_password("hello"), str)


def test_hash_password_length_is_64():
    assert len(hash_password("anything")) == 64


def test_hash_password_deterministic():
    assert hash_password("pyvault") == hash_password("pyvault")


def test_hash_password_different_inputs():
    assert hash_password("password1") != hash_password("password2")


def test_hash_password_matches_hashlib():
    pwd = "TestPassword!99"
    expected = hashlib.sha256(pwd.encode()).hexdigest()
    assert hash_password(pwd) == expected


def test_hash_password_non_string_raises():
    with pytest.raises(TypeError):
        hash_password(12345)


def test_hash_password_empty_string():
    assert len(hash_password("")) == 64


def test_hash_password_unicode():
    assert len(hash_password("pásswörd")) == 64


# ── test_search_vault ─────────────────────────────────────────────────────────

SAMPLE_VAULT = [
    {"site": "github.com", "username": "prashast@dev.com", "hash": "abc"},
    {"site": "gmail.com", "username": "prashast@gmail.com", "hash": "def"},
    {"site": "netflix.com", "username": "user123@mail.com", "hash": "ghi"},
    {"site": "linkedin.com", "username": "prashast_dev", "hash": "jkl"},
]


def test_search_vault_by_site():
    results = search_vault(SAMPLE_VAULT, "github")
    assert len(results) == 1
    assert results[0]["site"] == "github.com"


def test_search_vault_by_username():
    results = search_vault(SAMPLE_VAULT, "prashast@gmail")
    assert len(results) == 1


def test_search_vault_case_insensitive():
    assert search_vault(SAMPLE_VAULT, "GITHUB") == search_vault(SAMPLE_VAULT, "github")


def test_search_vault_no_match():
    assert search_vault(SAMPLE_VAULT, "twitter") == []


def test_search_vault_empty_query():
    assert search_vault(SAMPLE_VAULT, "") == []


def test_search_vault_empty_vault():
    assert search_vault([], "github") == []


def test_search_vault_multiple_matches():
    results = search_vault(SAMPLE_VAULT, "prashast")
    assert len(results) == 3


def test_search_vault_whitespace_stripped():
    assert search_vault(SAMPLE_VAULT, "  github  ") == search_vault(SAMPLE_VAULT, "github")
