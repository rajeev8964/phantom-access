"""Base dictionary + the mutations people actually apply to passwords."""

BASE_WORDS = [
    "password", "123456", "123456789", "qwerty", "12345", "12345678",
    "111111", "1234567", "sunshine", "qwerty123", "iloveyou", "princess",
    "admin", "welcome", "666666", "abc123", "football", "123123", "monkey",
    "654321", "charlie", "donald", "password1", "qwerty1", "1234", "letmein",
    "dragon", "baseball", "master", "shadow", "superman", "michael", "jordan",
    "harley", "hunter", "trustno1", "ranger", "buster", "thomas", "tigger",
    "robert", "soccer", "batman", "killer", "hockey", "george", "andrew",
    "michelle", "love", "jessica", "pepper", "daniel", "access", "joshua",
    "maggie", "starwars", "silver", "william", "dallas", "yankees", "mustang",
    "banana", "liverpool", "chelsea", "arsenal", "freedom", "whatever", "ninja",
    "azerty", "samsung", "google", "london", "taylor", "matrix", "summer",
    "winter", "flower", "angel", "jasmine", "orange", "purple", "butterfly",
]

SUFFIXES = [
    "", "1", "12", "123", "1234", "12345", "!", "@", "2024", "2025",
    "01", "99", "007", "_", ".", "$",
]


def _capitalize(w):
    return w[0].upper() + w[1:] if w else w


def build_wordlist():
    """Cross every base word with every suffix and case variant."""
    out, seen = [], set()
    for base in BASE_WORDS:
        for suf in SUFFIXES:
            stem = base + suf
            for variant in (stem, _capitalize(stem), stem.upper()):
                if variant not in seen:
                    seen.add(variant)
                    out.append(variant)
    return out
