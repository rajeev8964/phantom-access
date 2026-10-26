"""Credential attack engine. Deterministic per target so runs are repeatable."""
import hashlib

from .wordlist import build_wordlist

CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
_DICT = build_wordlist()


def dict_size():
    return len(_DICT)


def space(length):
    return len(CHARSET) ** length


def _hash(key):
    return int(hashlib.sha256(key.encode()).hexdigest(), 16)


def index_to_password(i, length):
    """Map an integer to a fixed-length charset string (base-N encoding)."""
    s = ""
    for _ in range(length):
        s = CHARSET[i % len(CHARSET)] + s
        i //= len(CHARSET)
    return s


def password_to_index(p):
    n = 0
    for ch in p:
        n = n * len(CHARSET) + CHARSET.index(ch)
    return n


def crack(target, salt="ig", mode="dict", length=5):
    key = (target or "target").strip().lower()
    h = _hash(salt + "|" + key)

    if mode == "brute":
        total = space(length)
        idx = h % total
        password = index_to_password(idx, length)
    else:
        total = len(_DICT)
        idx = h % total
        password = _DICT[idx]

    return {
        "target": key,
        "password": password,
        "attempts": idx + 1,
        "index": idx,
        "total": total,
        "mode": mode,
        "length": length if mode == "brute" else None,
        "twofa": (_hash(password) % 2 == 0),
        "eta_at_1k": round((idx + 1) / 1000, 2),
    }
