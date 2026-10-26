"""Lightweight user-agent parsing for captured fingerprints."""
import re

_OS = [
    (r"iPhone", "iOS"), (r"iPad", "iPadOS"), (r"Android", "Android"),
    (r"Windows", "Windows"), (r"Mac OS X", "macOS"), (r"Linux", "Linux"),
]

_BROWSERS = [
    (r"SamsungBrowser", "Samsung Internet"), (r"EdgA?/", "Edge"),
    (r"FxiOS|Firefox", "Firefox"), (r"CriOS|Chrome", "Chrome"),
    (r"Safari", "Safari"),
]


def parse_ua(ua):
    ua = ua or ""
    device, os_name, browser = "Unknown device", "Unknown OS", "Unknown browser"

    m = re.search(r"\(([^)]+)\)", ua)
    if m:
        parts = m.group(1).split(";")
        if parts and parts[0].strip():
            device = parts[0].strip()

    for pat, name in _OS:
        if re.search(pat, ua, re.I):
            os_name = name
            break

    for pat, name in _BROWSERS:
        if re.search(pat, ua, re.I):
            browser = name
            break

    return {"device": device, "os": os_name, "browser": browser}
