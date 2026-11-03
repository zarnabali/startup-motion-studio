# Security policy

Please report vulnerabilities privately via GitHub: **Security → Report a vulnerability**. Don't open a public issue.

Scope worth reporting: anything that could leak a user's API keys, run untrusted code during a render (e.g. via a
reference video, a downloaded asset or a skill instruction), or make Claude publish or log in without the user's consent.

Users: keep API keys in your own environment or an uncommitted `.env` (already in `.gitignore`). Never paste keys
into skills, briefs or `film.json`.
