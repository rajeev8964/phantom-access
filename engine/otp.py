"""OTP sweep engine. A 6-digit code is only 1,000,000 values."""
import hashlib

TOTAL = 1_000_000


def sweep(target, rate=200_000):
    h = int(hashlib.sha256(("otp|" + (target or "target")).encode()).hexdigest(), 16)
    code = h % TOTAL

    return {
        "target": target,
        "code": str(code).zfill(6),
        "index": code,
        "total": TOTAL,
        "rate": rate,
        "seconds": round(code / rate, 3),
        "coverage": round(code / 10_000, 2),
    }
