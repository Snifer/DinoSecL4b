<div align="center">

<img src="https://github.com/Snifer/DinoSecL4b/blob/main/Dino.png?raw=true" alt="DinosecLabs Logo" width="200"/>

> Para la versión en Español [Español](README.md)

# DinosecLabs

**Extensible ethical hacking labs platform**
*Realistic vulnerable applications · Gamified dashboard · HMAC flags · Progressive hints*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://choosealicense.com/licenses/mit/)
[![Docker](https://img.shields.io/badge/Docker-24%2B-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%202025-000000?logo=owasp&logoColor=white)](https://owasp.org/Top10/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

## What is DinosecLabs

DinosecLabs is an **extensible ethical hacking training platform** completely self-contained in Docker. Each lab is an application with hidden vulnerabilities: no tags, no UI hints, no help. You attack it like a real pentester.

The platform starts with the **OWASP Top 10 2025** track (10 labs, 21 flags) and is designed to grow: new tracks can be added independently without modifying the base infrastructure.

It features a **gamified dashboard** that centralizes everything: unique flags per deployment generated with HMAC, you can redeem DinoCoins for progressive hints by levels, and a public Hall of Fame powered by GitHub Actions.

<div align="center">

Developed by [@Snifer](https://github.com/Snifer) · [sniferl4bs.com](https://sniferl4bs.com)

If you find this project useful, consider supporting its development:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/sniferl4bs)

</div>

---

## Features

| Feature | Description |
|---------|-------------|
| Realistic labs | 10 applications with no UI hints |
| 21 hidden flags | Only accessible by correctly exploiting the vulnerability |
| Unique HMAC flags | `HMAC-SHA256(FLAG_SECRET, vuln_id)[:20]` — unique per deployment |
| Coin system | 100–200 coins per completed flag |
| Progressive hints | 3 levels per lab (50 / 75 / 100 coins, or free by progression) |
| Lab notes | Integrated notepad with auto-save, persisted in SQLite |
| Reset state | Resets the lab's internal state without rebuilding the image |
| Exportable progress | Detailed CSV export from the dashboard |
| Search and filter | Filter labs by state: All / Online / Offline / Completed |
| HTTP health checks | Distinguishes between running and crashed in real time |
| Uptime | HH:MM:SS chip per lab while running |
| Auto-stop | Automatically stops inactive labs (default: 4 hours) |
| Hall of Fame | Via GitHub Issue + automatic GitHub Action |
| Offline build | All pip packages included in `packages/` |
| Dynamic tracks | New tracks can be added from `tracks/my-track/track.json` |

---

## Dashboard

The dashboard runs on **http://localhost:8000** and has four tabs:

| Tab | Content |
|-----|---------|
| OWASP Top 10 2025 | Lab grid: start / stop / submit flag / hints / notes / reset |
| OWASP API Top 10 | API Security Top 10 reference (upcoming labs) |
| Container & K8s | Container and Kubernetes vulnerabilities reference (planned labs) |
| About | Project info, developer, and integrated roadmap |

---

## OWASP Top 10 2025 Labs

**10 labs · 21 flags · maximum 3000 coins**

| Lab | Category | Application | Port |
|-----|----------|-------------|------|
| A01 | Broken Access Control | CorpHR — HR Portal | 8001 |
| A02 | Security Misconfiguration | DevPortal — Internal DevOps Portal | 8002 |
| A03 | Software Supply Chain Failures | PkgManager — Dependency Manager | 8003 |
| A04 | Cryptographic Failures | SecureBank — Online Banking | 8004 |
| A05 | Injection | ShopCorp — Marketplace e-commerce | 8005 |
| A06 | Insecure Design | BizStore — B2B Marketplace | 8006 |
| A07 | Authentication Failures | EmpPortal — Employee Portal | 8007 |
| A08 | Software & Data Integrity Failures | UpdateHub — Update System | 8008 |
| A09 | Security Logging & Alerting Failures | AuditLog — Compliance Portal | 8009 |
| A10 | Mishandling of Exceptional Conditions | DataAPI — Data and Analytics API | 8010 |

---

## Requirements

| Requirement | Minimum Version |
|-------------|-----------------|
| Docker Engine | 24.x |
| docker-compose | 2.x |
| Free RAM | 2 GB |
| Free Disk | 3 GB |
| Free Ports | 8000 – 8010 |

---

## Quick Start

```bash
git clone https://github.com/Snifer/DinoSecL4b.git
cd DinoSecL4b/owasp-labs
bash setup.sh
```

Open the dashboard at: **http://localhost:8000**

`setup.sh` detects the operating system, checks dependencies, generates the `FLAG_SECRET`, downloads offline packages if missing, builds the images, and automatically starts the dashboard.

It currently works smoothly on Linux and MacOS. If you find any bug or error, feel free to open an issue and report it.

---

## How to Use

```
1. Start a lab             →  Start button on the dashboard (or ./manage.sh start aXX)
2. Open the lab            →  Open button
3. Explore the application    Act like a real pentester — no UI hints
4. Exploit the vuln           Find the hidden flag within the data
5. Submit the flag         →  Flag button → paste FLAG{...} → Submit
6. Earn coins              →  buy hints if you get stuck
7. Take notes              →  Notes button — auto-save per lab
8. Hall of Fame            →  Hall of Fame → enter your alias → GitHub Issue
```

---

## HMAC Flag System

Flags are **unique per deployment**: derived from `HMAC-SHA256(FLAG_SECRET, vuln_id)[:20]`. They cannot be shared between different installations.

`FLAG_SECRET` is automatically generated in `.env` during setup.

To check the active flag values in your installation:

```bash
curl http://localhost:8000/api/flag-values
```

---

## Gamification System

### Coins per flag

| Difficulty | Coins | Examples |
|------------|-------|----------|
| Easy | 100 | IDOR, exposed config, hidden panel |
| Medium | 150 | SQLi, JWT forgery, brute force |
| Hard | 200 | RCE (CMDi, pickle, SSTI) |

### Progressive hints

Three levels per lab:

| Level | Cost | Content |
|-------|------|---------|
| 1 | 50 coins or free* | General direction of the attack |
| 2 | 75 coins | Specific technique to use |
| 3 | 100 coins | Almost complete hint |

*Level 1 of lab N+1 is unlocked for free when submitting any flag from lab N.

### Hall of Fame

```
1. Dashboard → Hall of Fame → Submit my score
2. Enter your alias → Submit
3. A pre-filled GitHub Issue opens → click "Submit new issue"
4. GitHub Action parses your score, updates HALL_OF_FAME.md and closes the issue
```

---

## Terminal Management

```bash
./manage.sh status          # View status of all labs
./manage.sh start a01       # Start a specific lab
./manage.sh stop a01        # Stop a lab
./manage.sh start-all       # Start all labs
./manage.sh logs a05        # View real-time logs
./manage.sh build           # Rebuild all images
```

---

## Project Structure

```
owasp-labs/
├── setup.sh                          # Setup and start script
├── manage.sh                         # Labs management CLI
├── docker-compose.yml                # 11 services orchestration
├── .env.example
├── packages/                         # Pip wheels for offline installation
├── scores.json                       # Hall of Fame data
├── HALL_OF_FAME.md
├── .github/
│   └── workflows/
│       └── hall-of-fame.yml          # GitHub Action: processes score issues
├── tracks/
│   └── owasp-top10-2025/
│       └── track.json
├── dashboard/
│   ├── app.py                        # Flask + Docker SDK + SQLite
│   ├── Dockerfile
│   └── templates/
│       └── index.html                # Complete dashboard UI
└── labs/
    ├── a01-broken-access-control/
    ├── a02-security-misconfiguration/
    ├── a03-supply-chain/
    ├── a04-cryptographic-failures/
    ├── a05-injection/
    ├── a06-insecure-design/
    ├── a07-auth-failures/
    ├── a08-integrity-failures/
    ├── a09-logging-failures/
    └── a10-exceptional-conditions/
```

---

## Troubleshooting

### Dashboard does not start

```bash
# Check that Docker is running
docker info

# Check dashboard logs
docker compose logs dashboard

# Check that ports 8000-8010 are free
ss -tlnp | grep -E '800[0-9]|8010'
```

### A lab doesn't start or appears as crashed

```bash
# View logs for the specific lab (example: A01)
docker compose logs a01-broken-access-control

# Restart only that lab
docker compose restart a01-broken-access-control

# Or from the management terminal
./manage.sh start a01
```

### Flags are not validated

Flags are unique per deployment. If you reinstalled or regenerated the `.env`, the flags change. Check the current values:

```bash
curl http://localhost:8000/api/flag-values
```

If the `.env` file was deleted, run `bash setup.sh` again to regenerate `FLAG_SECRET`. Previous flags will be invalidated.

### Permission error on setup.sh

```bash
chmod +x setup.sh manage.sh
bash setup.sh
```

### DNS or package error during build

The pip packages are included in `packages/` — the build is completely offline. If you need to regenerate them:

```bash
pip3 download flask docker pyjwt \
  -d packages/ \
  --platform manylinux2014_x86_64 \
  --python-version 312 \
  --only-binary=:all:
```

### Out of disk space or RAM

```bash
docker system df
free -h
```

Use the dashboard to start only the required labs in each session. Auto-stop (default 4h) frees resources automatically.

### Reinstall from scratch

```bash
docker compose down -v --remove-orphans
docker system prune -f
bash setup.sh
```

### Reset progress

```bash
# From the dashboard → Reset progress button
# Or via API:
curl -X POST http://localhost:8000/api/reset
```

---

## Contributions

Contributions are welcome: new labs, new tracks, translations, and bug fixes.

### How to contribute a new track

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-track`
3. Create the structure in `tracks/my-track/` with the following format
4. Make sure each lab has its own `Dockerfile` and is self-contained
5. Open a Pull Request describing the track, covered vulnerabilities, and included flags

### track.json structure

```json
{
  "id": "my-track",
  "name": "Track Name",
  "description": "Track description",
  "labs": [
    {
      "id": "lab-id",
      "name": "Lab Name",
      "description": "Short description",
      "category": "OWASP Category",
      "port": 8011,
      "service": "docker-service-name",
      "flags": [
        {
          "id": "unique_vuln_id",
          "description": "Vulnerability description",
          "points": 150,
          "hints": [
            "Level 1 hint (general direction)",
            "Level 2 hint (specific technique)",
            "Level 3 hint (detailed hint)"
          ]
        }
      ]
    }
  ]
}
```

### Directory structure for a new track

```
tracks/
└── my-track/
    ├── track.json
    └── labs/
        └── lab-01/
            ├── Dockerfile
            └── app/
```

To report bugs or suggest improvements, open a [GitHub Issue](https://github.com/Snifer/DinoSecL4b/issues).

---

## Tracks Roadmap

| Track | Status |
|-------|--------|
| OWASP Top 10 2025 | Available |
| OWASP API Security Top 10 | Coming soon |
| Cloud Security Fundamentals | Planned |
| Container & Kubernetes Security | Planned |
| Active Directory Attacks | Under consideration |
| Mobile Security (Android) | Under consideration |
| Cert Prep: eJPT / OSCP / CEH | Under consideration |

---

## Disclaimer

This lab is provided **solely for educational and ethical hacking training purposes**. It is not intended for use in production environments. Use it ethically and responsibly, only on your own systems or with explicit authorization.

---

## License

[MIT](https://choosealicense.com/licenses/mit/) — see the `LICENSE` file for details.

---

<div align="center">

Developed by [@Snifer](https://github.com/Snifer) · [sniferl4bs.com](https://sniferl4bs.com)

If you find this project useful, consider supporting its development:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/sniferl4bs)

</div>
