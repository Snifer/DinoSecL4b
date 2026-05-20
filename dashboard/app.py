import docker
import subprocess
import os
import sqlite3
import json
import hmac
import hashlib
import secrets
import threading
import time
import urllib.request
from datetime import datetime
from flask import Flask, jsonify, render_template, request, g

app = Flask(__name__)
DB_PATH      = os.environ.get("DB_PATH",      "/data/progress.db")
COMPOSE_DIR  = os.environ.get("COMPOSE_DIR",  "/project")
TRACKS_DIR   = os.environ.get("TRACKS_DIR",   "/project/tracks")
FLAG_SECRET_ENV = os.environ.get("FLAG_SECRET", "")
AUTO_STOP_HOURS = int(os.environ.get("AUTO_STOP_HOURS", "4"))

# ──────────────────────────────────────────────────────────────────────────────
# HMAC Flag system
# ──────────────────────────────────────────────────────────────────────────────
_flag_secret_cache = None

def get_flag_secret():
    global _flag_secret_cache
    if _flag_secret_cache:
        return _flag_secret_cache
    if FLAG_SECRET_ENV:
        _flag_secret_cache = FLAG_SECRET_ENV
        return _flag_secret_cache
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT value FROM state WHERE key='flag_secret'").fetchone()
        if row:
            _flag_secret_cache = row["value"]
            conn.close()
            return _flag_secret_cache
        secret = secrets.token_hex(32)
        conn.execute("INSERT OR IGNORE INTO state VALUES ('flag_secret',?)", (secret,))
        conn.commit()
        conn.close()
        _flag_secret_cache = secret
    except Exception:
        _flag_secret_cache = "dinoseclabs-default"
    return _flag_secret_cache

def compute_flag(vuln_id):
    secret = get_flag_secret()
    h = hmac.new(secret.encode(), vuln_id.encode(), hashlib.sha256).hexdigest()[:20]
    return f"FLAG{{{h}}}"

def find_vuln_by_flag(submitted):
    for vuln_id, info in VULN_REGISTRY.items():
        if compute_flag(vuln_id) == submitted:
            return vuln_id, info
    return None, None

# ──────────────────────────────────────────────────────────────────────────────
# Dynamic track loader — reads from tracks/ directory
# ──────────────────────────────────────────────────────────────────────────────
def load_tracks():
    tracks = {}
    if not os.path.isdir(TRACKS_DIR):
        return tracks
    for entry in sorted(os.listdir(TRACKS_DIR)):
        track_file = os.path.join(TRACKS_DIR, entry, "track.json")
        if os.path.isfile(track_file):
            try:
                with open(track_file) as f:
                    data = json.load(f)
                tracks[data["id"]] = data
            except Exception:
                pass
    return tracks

_TRACKS = load_tracks()

# Active track (first loaded, or owasp-top10-2025)
_ACTIVE_TRACK = _TRACKS.get("owasp-top10-2025") or (next(iter(_TRACKS.values())) if _TRACKS else None)

LABS = _ACTIVE_TRACK["labs"] if _ACTIVE_TRACK else []
LAB_ORDER = [l["id"] for l in LABS]
LAB_HINTS = _ACTIVE_TRACK.get("hints", {}) if _ACTIVE_TRACK else {}
VULN_REGISTRY = _ACTIVE_TRACK.get("flag_registry", {}) if _ACTIVE_TRACK else {}

FLAGS_PER_LAB = {}
for vid, vd in VULN_REGISTRY.items():
    FLAGS_PER_LAB.setdefault(vd["lab"], []).append(vid)

# ──────────────────────────────────────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS submitted_flags (
            flag_id   TEXT PRIMARY KEY,
            flag_code TEXT NOT NULL,
            lab_id    TEXT NOT NULL,
            coins     INTEGER NOT NULL,
            name      TEXT NOT NULL,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS unlocked_hints (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            lab_id     TEXT NOT NULL,
            level      INTEGER NOT NULL,
            method     TEXT NOT NULL,
            coins_spent INTEGER DEFAULT 0,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(lab_id, level)
        );
        CREATE TABLE IF NOT EXISTS notes (
            lab_id     TEXT PRIMARY KEY,
            content    TEXT NOT NULL DEFAULT '',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lab_sessions (
            lab_id      TEXT PRIMARY KEY,
            started_at  DATETIME,
            last_active DATETIME
        );
        INSERT OR IGNORE INTO state VALUES ('coins', '0');
        INSERT OR IGNORE INTO state VALUES ('started_at', datetime('now'));
    """)
    conn.commit()
    conn.close()

def get_coins():
    db = get_db()
    row = db.execute("SELECT value FROM state WHERE key='coins'").fetchone()
    return int(row["value"]) if row else 0

def add_coins(amount):
    db = get_db()
    db.execute("UPDATE state SET value = CAST(CAST(value AS INTEGER) + ? AS TEXT) WHERE key='coins'", (amount,))
    db.commit()

def spend_coins(amount):
    current = get_coins()
    if current < amount:
        return False
    db = get_db()
    db.execute("UPDATE state SET value = CAST(CAST(value AS INTEGER) - ? AS TEXT) WHERE key='coins'", (amount,))
    db.commit()
    return True

def get_submitted_flags():
    db = get_db()
    rows = db.execute("SELECT flag_id FROM submitted_flags").fetchall()
    return {r["flag_id"] for r in rows}

def get_completed_labs():
    """Labs with at least 1 flag submitted."""
    db = get_db()
    rows = db.execute("SELECT DISTINCT lab_id FROM submitted_flags").fetchall()
    return {r["lab_id"] for r in rows}

def get_unlocked_hints():
    db = get_db()
    rows = db.execute("SELECT lab_id, level FROM unlocked_hints").fetchall()
    result = {}
    for r in rows:
        result.setdefault(r["lab_id"], set()).add(r["level"])
    return result

def is_hint_unlocked(lab_id, level):
    hints = get_unlocked_hints()
    return level in hints.get(lab_id, set())

def unlock_hint_free(lab_id, level, method="progression"):
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO unlocked_hints (lab_id, level, method, coins_spent) VALUES (?,?,?,0)",
        (lab_id, level, method)
    )
    db.commit()

# Time tracking helpers
def record_lab_start(lab_id):
    db = get_db()
    db.execute(
        "INSERT INTO lab_sessions (lab_id, started_at, last_active) VALUES (?,datetime('now'),datetime('now')) "
        "ON CONFLICT(lab_id) DO UPDATE SET started_at=datetime('now'), last_active=datetime('now')",
        (lab_id,)
    )
    db.commit()

def record_lab_stop(lab_id):
    db = get_db()
    db.execute("DELETE FROM lab_sessions WHERE lab_id=?", (lab_id,))
    db.commit()

def get_lab_uptime(lab_id):
    db = get_db()
    row = db.execute("SELECT started_at FROM lab_sessions WHERE lab_id=?", (lab_id,)).fetchone()
    if not row or not row["started_at"]:
        return None
    try:
        started = datetime.fromisoformat(row["started_at"])
        elapsed = int((datetime.utcnow() - started).total_seconds())
        h, rem = divmod(elapsed, 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return None

# ──────────────────────────────────────────────────────────────────────────────
# Docker helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_docker_client():
    try:
        return docker.from_env()
    except Exception:
        return None

def get_container_status(client, container_name):
    if not client:
        return "unknown"
    try:
        return client.containers.get(container_name).status
    except docker.errors.NotFound:
        return "stopped"
    except Exception:
        return "unknown"

def http_health_check(port, timeout=2):
    """Returns True if the lab HTTP endpoint responds with any 2xx/3xx."""
    try:
        req = urllib.request.Request(f"http://localhost:{port}/", method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status < 500
    except Exception:
        return False

# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    client = get_docker_client()
    submitted = get_submitted_flags()
    completed = get_completed_labs()
    unlocked_hints = get_unlocked_hints()
    coins = get_coins()

    labs_data = []
    for lab in LABS:
        status  = get_container_status(client, lab["container"])
        healthy = http_health_check(lab["port"]) if status == "running" else False
        uptime  = get_lab_uptime(lab["id"]) if status == "running" else None
        lab_flags = FLAGS_PER_LAB.get(lab["id"], [])
        found = sum(1 for fid in lab_flags if fid in submitted)
        total = len(lab_flags)
        hints_info = []
        for h in LAB_HINTS.get(lab["id"], []):
            unlocked = h["level"] in unlocked_hints.get(lab["id"], set())
            hints_info.append({**h, "unlocked": unlocked})
        labs_data.append({
            **lab,
            "status":       status,
            "healthy":      healthy,
            "uptime":       uptime,
            "difficulty":   lab.get("difficulty", "medium"),
            "flags_found":  found,
            "flags_total":  total,
            "completed":    found > 0,
            "hints":        hints_info,
        })

    total_flags = sum(l["flags_total"] for l in labs_data)
    found_flags = sum(l["flags_found"] for l in labs_data)

    return render_template(
        "index.html",
        labs=labs_data,
        coins=coins,
        total_flags=total_flags,
        found_flags=found_flags,
    )


@app.route("/api/status")
def api_status():
    client = get_docker_client()
    return jsonify({lab["id"]: get_container_status(client, lab["container"]) for lab in LABS})


@app.route("/api/start/<lab_id>", methods=["POST"])
def start_lab(lab_id):
    lab = next((l for l in LABS if l["id"] == lab_id), None)
    if not lab:
        return jsonify({"error": "Lab not found"}), 404
    # Remove any stopped/created container so docker-compose can recreate it cleanly
    client = get_docker_client()
    if client:
        try:
            old = client.containers.get(lab["container"])
            if old.status != "running":
                old.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception:
            pass

    try:
        result = subprocess.run(
            ["docker-compose", "-p", "owasp-labs", "up", "-d", "--build", "--no-deps", lab["service"]],
            cwd=COMPOSE_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            record_lab_start(lab_id)
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": (result.stdout + result.stderr).strip()[-2000:]}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "Timeout — image is building, wait and refresh status"}), 500
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "docker-compose not found — check the /usr/bin/docker-compose volume mount"}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/stop/<lab_id>", methods=["POST"])
def stop_lab(lab_id):
    lab = next((l for l in LABS if l["id"] == lab_id), None)
    if not lab:
        return jsonify({"error": "Lab not found"}), 404
    client = get_docker_client()
    if not client:
        return jsonify({"ok": False, "error": "Docker not available"}), 500
    try:
        c = client.containers.get(lab["container"])
        c.stop(timeout=10)
        c.remove(force=True)
        record_lab_stop(lab_id)
        return jsonify({"ok": True})
    except docker.errors.NotFound:
        record_lab_stop(lab_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/logs/<lab_id>")
def lab_logs(lab_id):
    lab = next((l for l in LABS if l["id"] == lab_id), None)
    if not lab:
        return jsonify({"error": "Lab not found"}), 404
    client = get_docker_client()
    if not client:
        return jsonify({"logs": "Docker not available"})
    try:
        c = client.containers.get(lab["container"])
        logs = c.logs(tail=60, timestamps=True).decode("utf-8", errors="replace")
        return jsonify({"logs": logs or "(no output)"})
    except docker.errors.NotFound:
        return jsonify({"logs": "Container stopped / not started"})
    except Exception as e:
        return jsonify({"logs": str(e)})


@app.route("/api/submit-flag", methods=["POST"])
def submit_flag():
    data = request.get_json(silent=True) or {}
    code = (data.get("flag") or "").strip()
    if not code:
        return jsonify({"ok": False, "error": "Empty flag"}), 400

    vuln_id, flag_info = find_vuln_by_flag(code)
    if not flag_info:
        return jsonify({"ok": False, "error": "Invalid flag"}), 400

    submitted = get_submitted_flags()
    if vuln_id in submitted:
        return jsonify({"ok": False, "error": "This flag has already been submitted", "already": True}), 200

    db = get_db()
    db.execute(
        "INSERT INTO submitted_flags (flag_id, flag_code, lab_id, coins, name) VALUES (?,?,?,?,?)",
        (vuln_id, code, flag_info["lab"], flag_info["coins"], flag_info["name"])
    )
    db.commit()
    add_coins(flag_info["coins"])

    # Unlock progression: completar lab N → desbloquear hint nivel 1 del lab N+1 gratis
    lab_id = flag_info["lab"]
    if lab_id in LAB_ORDER:
        idx = LAB_ORDER.index(lab_id)
        if idx + 1 < len(LAB_ORDER):
            next_lab = LAB_ORDER[idx + 1]
            unlock_hint_free(next_lab, 1, method="progression")

    return jsonify({
        "ok": True,
        "coins_earned": flag_info["coins"],
        "total_coins": get_coins(),
        "flag_name": flag_info["name"],
        "lab": flag_info["lab"],
    })


@app.route("/api/buy-hint/<lab_id>/<int:level>", methods=["POST"])
def buy_hint(lab_id, level):
    hints = LAB_HINTS.get(lab_id, [])
    hint = next((h for h in hints if h["level"] == level), None)
    if not hint:
        return jsonify({"ok": False, "error": "Hint no encontrado"}), 404

    if is_hint_unlocked(lab_id, level):
        return jsonify({"ok": True, "already": True, "text": hint["text"]})

    cost = hint["cost"]
    if not spend_coins(cost):
        return jsonify({"ok": False, "error": f"Not enough Dinocoins. You need {cost}, you have {get_coins()} Dinocoins"}), 400

    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO unlocked_hints (lab_id, level, method, coins_spent) VALUES (?,?,?,?)",
        (lab_id, level, "coins", cost)
    )
    db.commit()

    return jsonify({
        "ok": True,
        "text": hint["text"],
        "coins_spent": cost,
        "total_coins": get_coins(),
    })


@app.route("/api/progress")
def api_progress():
    submitted = get_submitted_flags()
    completed = get_completed_labs()
    unlocked = get_unlocked_hints()
    db = get_db()
    flags_list = db.execute(
        "SELECT flag_id, flag_code, lab_id, coins, name, submitted_at FROM submitted_flags ORDER BY submitted_at"
    ).fetchall()
    return jsonify({
        "coins": get_coins(),
        "flags_submitted": [dict(r) for r in flags_list],
        "completed_labs": list(completed),
        "unlocked_hints": {k: list(v) for k, v in unlocked.items()},
    })


@app.route("/api/reset", methods=["POST"])
def reset_progress():
    db = get_db()
    db.execute("DELETE FROM submitted_flags")
    db.execute("DELETE FROM unlocked_hints")
    db.execute("UPDATE state SET value='0' WHERE key='coins'")
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/health/<lab_id>")
def lab_health(lab_id):
    lab = next((l for l in LABS if l["id"] == lab_id), None)
    if not lab:
        return jsonify({"healthy": False}), 404
    client = get_docker_client()
    status = get_container_status(client, lab["container"])
    healthy = http_health_check(lab["port"]) if status == "running" else False
    return jsonify({"status": status, "healthy": healthy, "uptime": get_lab_uptime(lab_id)})


@app.route("/api/reset-lab/<lab_id>", methods=["POST"])
def reset_lab(lab_id):
    """Stop the container, remove it and start fresh — resets lab internal state."""
    lab = next((l for l in LABS if l["id"] == lab_id), None)
    if not lab:
        return jsonify({"error": "Lab not found"}), 404
    client = get_docker_client()
    if not client:
        return jsonify({"ok": False, "error": "Docker not available"}), 500
    try:
        try:
            c = client.containers.get(lab["container"])
            c.stop(timeout=5)
            c.remove(force=True)
        except docker.errors.NotFound:
            pass
        record_lab_stop(lab_id)
        result = subprocess.run(
            ["docker-compose", "-p", "owasp-labs", "up", "-d", "--no-build", "--no-deps", lab["service"]],
            cwd=COMPOSE_DIR, capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            record_lab_start(lab_id)
            return jsonify({"ok": True})
        # Fallback: rebuild if image not available
        result2 = subprocess.run(
            ["docker-compose", "-p", "owasp-labs", "up", "-d", "--build", "--no-deps", lab["service"]],
            cwd=COMPOSE_DIR, capture_output=True, text=True, timeout=300,
        )
        if result2.returncode == 0:
            record_lab_start(lab_id)
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": (result2.stdout + result2.stderr).strip()[-1000:]}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/uptime")
def api_uptime():
    client = get_docker_client()
    result = {}
    for lab in LABS:
        status = get_container_status(client, lab["container"])
        result[lab["id"]] = {
            "uptime": get_lab_uptime(lab["id"]) if status == "running" else None,
            "healthy": http_health_check(lab["port"]) if status == "running" else False,
        }
    return jsonify(result)


@app.route("/api/progress/detail")
def progress_detail():
    db = get_db()
    flags = db.execute(
        "SELECT flag_id, lab_id, coins, name, submitted_at FROM submitted_flags ORDER BY submitted_at"
    ).fetchall()
    sessions = db.execute("SELECT lab_id, started_at FROM lab_sessions").fetchall()
    started_map = {r["lab_id"]: r["started_at"] for r in sessions}

    rows = []
    for f in flags:
        rows.append({
            "flag_id":      f["flag_id"],
            "lab_id":       f["lab_id"],
            "coins":        f["coins"],
            "name":         f["name"],
            "submitted_at": f["submitted_at"],
        })
    return jsonify({
        "coins":       get_coins(),
        "total_flags": len(VULN_REGISTRY),
        "found_flags": len(rows),
        "rows":        rows,
        "flag_secret_hint": get_flag_secret()[:8] + "...",
    })


@app.route("/api/notes/<lab_id>", methods=["GET"])
def get_notes(lab_id):
    db = get_db()
    row = db.execute("SELECT content, updated_at FROM notes WHERE lab_id=?", (lab_id,)).fetchone()
    if row:
        return jsonify({"ok": True, "content": row["content"], "updated_at": row["updated_at"]})
    return jsonify({"ok": True, "content": "", "updated_at": None})


@app.route("/api/notes/<lab_id>", methods=["POST"])
def save_notes(lab_id):
    data = request.get_json(silent=True) or {}
    content = data.get("content", "")
    db = get_db()
    db.execute(
        "INSERT INTO notes (lab_id, content, updated_at) VALUES (?,?,datetime('now')) "
        "ON CONFLICT(lab_id) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at",
        (lab_id, content)
    )
    db.commit()
    return jsonify({"ok": True})


GITHUB_REPO  = "Snifer/DinoSecL4b"
GITHUB_ISSUE_URL = f"https://github.com/{GITHUB_REPO}/issues/new"
SCORES_RAW_URL   = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/owasp-labs/scores.json"


@app.route("/api/score-payload", methods=["POST"])
def score_payload():
    """Build the issue title + body and return the prefilled GitHub URL."""
    data = request.get_json(silent=True) or {}
    alias = (data.get("alias") or "Anonymous").strip()[:40]
    if not alias:
        return jsonify({"ok": False, "error": "Alias required"}), 400

    coins = get_coins()
    submitted = get_submitted_flags()
    completed = get_completed_labs()

    flags_found = len(submitted)
    labs_done   = len(completed)

    from datetime import date
    today = date.today().isoformat()

    title = f"🏆 DinosecLabs Score | {alias}"

    body = (
        f"<!-- DINOSEC_SCORE\n"
        f"alias: {alias}\n"
        f"coins: {coins}\n"
        f"flags: {flags_found}\n"
        f"total_flags: 21\n"
        f"labs: {labs_done}\n"
        f"date: {today}\n"
        f"/DINOSEC_SCORE -->\n\n"
        f"## 🦕 DinosecLabs — Score Submission\n\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| **Player** | {alias} |\n"
        f"| **Coins** | {coins} / 3000 🪙 |\n"
        f"| **Flags** | {flags_found} / 21 🚩 |\n"
        f"| **Labs** | {labs_done} / 10 🧪 |\n"
        f"| **Date** | {today} |\n\n"
        f"*Submitted from the DinosecLabs dashboard.*"
    )

    import urllib.parse
    params = urllib.parse.urlencode({
        "title": title,
        "body":  body,
        "labels": "hall-of-fame",
    })

    return jsonify({
        "ok": True,
        "url": f"{GITHUB_ISSUE_URL}?{params}",
        "summary": {
            "alias": alias,
            "coins": coins,
            "flags": flags_found,
            "labs": labs_done,
            "date": today,
        }
    })


@app.route("/api/hall-of-fame")
def hall_of_fame():
    """Fetch leaderboard from the GitHub repo's scores.json."""
    import urllib.request
    try:
        with urllib.request.urlopen(SCORES_RAW_URL, timeout=5) as r:
            scores = json.loads(r.read().decode())
        return jsonify({"ok": True, "scores": scores})
    except Exception as e:
        return jsonify({"ok": False, "scores": [], "error": str(e)})


@app.route("/api/flag-values")
def flag_values():
    """Return computed flag values for the current secret — used by lab reset and debugging."""
    result = {vid: compute_flag(vid) for vid in VULN_REGISTRY}
    return jsonify({"ok": True, "flags": result, "secret_prefix": get_flag_secret()[:8] + "..."})


# ──────────────────────────────────────────────────────────────────────────────
# Auto-stop background thread
# ──────────────────────────────────────────────────────────────────────────────
def _auto_stop_worker():
    while True:
        time.sleep(1800)  # check every 30 min
        try:
            client = get_docker_client()
            if not client:
                continue
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            sessions = conn.execute("SELECT lab_id, last_active FROM lab_sessions").fetchall()
            conn.close()
            for row in sessions:
                lab_id = row["lab_id"]
                last   = row["last_active"]
                if not last:
                    continue
                try:
                    elapsed_h = (datetime.utcnow() - datetime.fromisoformat(last)).total_seconds() / 3600
                except Exception:
                    continue
                if elapsed_h >= AUTO_STOP_HOURS:
                    lab = next((l for l in LABS if l["id"] == lab_id), None)
                    if not lab:
                        continue
                    try:
                        c = client.containers.get(lab["container"])
                        if c.status == "running":
                            c.stop(timeout=10)
                            c.remove(force=True)
                            conn2 = sqlite3.connect(DB_PATH)
                            conn2.execute("DELETE FROM lab_sessions WHERE lab_id=?", (lab_id,))
                            conn2.commit()
                            conn2.close()
                            app.logger.info(f"[auto-stop] Stopped idle lab {lab_id} after {elapsed_h:.1f}h")
                    except Exception:
                        pass
        except Exception:
            pass

_auto_stop_thread = threading.Thread(target=_auto_stop_worker, daemon=True)
_auto_stop_thread.start()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=False)
