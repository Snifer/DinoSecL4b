#!/usr/bin/env bash
# 
#  DinosecLabs 
#  Usage: bash setup.sh [--secret <your-secret>] [--auto-stop-hours]
# 
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

FLAG_SECRET=""
AUTO_STOP_HOURS="4"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --secret)       FLAG_SECRET="$2";      shift 2 ;;
    --auto-stop)    AUTO_STOP_HOURS="$2";  shift 2 ;;
    *)              shift ;;
  esac
done

banner() {
  echo -e "${BOLD}${CYAN}"
  echo "╔══════════════════════════════════════════════════════╗"
  echo "║            🦕  DinosecLabs — Setup                  ║"
  echo "╚══════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
err()  { echo -e "${RED}✗ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}→${NC} $1"; }

# ─── OS Detection ─────────────────────────────────────────────────────────────
detect_os() {
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if grep -qi "ubuntu\|debian" /etc/os-release 2>/dev/null; then
      echo "debian"
    elif grep -qi "fedora\|centos\|rhel" /etc/os-release 2>/dev/null; then
      echo "fedora"
    elif grep -qi "arch" /etc/os-release 2>/dev/null; then
      echo "arch"
    else
      echo "linux"
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  else
    echo "unknown"
  fi
}

# ─── Dependency checks ────────────────────────────────────────────────────────
check_deps() {
  info "Checking dependencies..."
  local missing=()

  command -v docker      &>/dev/null || missing+=("docker")
  command -v docker-compose &>/dev/null || missing+=("docker-compose")
  command -v python3     &>/dev/null || missing+=("python3")

  if [[ ${#missing[@]} -gt 0 ]]; then
    warn "Missing: ${missing[*]}"
    OS=$(detect_os)
    info "Detected OS: $OS"
    case "$OS" in
      debian)
        warn "Install with: sudo apt-get install -y docker.io docker-compose python3"
        ;;
      fedora)
        warn "Install with: sudo dnf install -y docker docker-compose python3"
        ;;
      macos)
        warn "Install Docker Desktop: https://www.docker.com/products/docker-desktop"
        warn "Install with: brew install docker-compose python3"
        ;;
    esac
    err "Please install missing dependencies and re-run setup.sh"
  fi

  ok "Docker:         $(docker --version | cut -d' ' -f3 | tr -d ',')"
  ok "docker-compose: $(docker-compose --version | cut -d' ' -f4)"
  ok "Python3:        $(python3 --version | cut -d' ' -f2)"
}

# ─── Docker service check ─────────────────────────────────────────────────────
check_docker_running() {
  info "Checking Docker daemon..."
  if ! docker info &>/dev/null; then
    err "Docker daemon is not running. Start it with: sudo systemctl start docker"
  fi
  ok "Docker daemon is running"
}

# ─── Port check ───────────────────────────────────────────────────────────────
check_ports() {
  info "Checking ports 8000-8010..."
  local busy=()
  for port in $(seq 8000 8010); do
    if ss -tuln 2>/dev/null | grep -q ":${port} " || \
       netstat -tuln 2>/dev/null | grep -q ":${port} "; then
      busy+=($port)
    fi
  done
  if [[ ${#busy[@]} -gt 0 ]]; then
    warn "Ports already in use: ${busy[*]}"
    warn "Some labs may fail to start. Free the ports or check docker ps."
  else
    ok "Ports 8000-8010 are available"
  fi
}

# PIP Offline packages
check_packages() {
  info "Checking offline pip packages..."
  local pkg_dir="$SCRIPT_DIR/packages"
  local min_count=10
  local needs_download=false

  if [[ ! -d "$pkg_dir" ]] || [[ $(ls "$pkg_dir"/*.whl 2>/dev/null | wc -l) -lt $min_count ]]; then
    needs_download=true
  elif ! docker run --rm \
      -v "$SCRIPT_DIR:/work" \
      -v "$pkg_dir:/packages" \
      python:3.12-slim \
      sh -c "pip install --no-index --find-links=/packages -r /work/dashboard/requirements.txt pyjwt --dry-run >/dev/null 2>&1"; then
    warn "Offline packages are not compatible with the dashboard image. Refreshing..."
    needs_download=true
  fi

  if [[ "$needs_download" == true ]]; then
    warn "Offline packages missing or incomplete. Downloading..."
    mkdir -p "$pkg_dir"
    rm -f "$pkg_dir"/*.whl
    if docker run --rm \
        -v "$SCRIPT_DIR:/work" \
        -v "$pkg_dir:/packages" \
        python:3.12-slim \
        sh -c "pip download --only-binary=:all: -r /work/dashboard/requirements.txt pyjwt -d /packages --quiet"; then
      ok "Packages downloaded to packages/"
    else
      warn "Package download failed. Build may require internet access."
    fi
  else
    ok "Offline packages present ($(ls "$pkg_dir"/*.whl | wc -l) wheels)"
  fi
}


generate_env() {
  info "Configuring environment..."

  if [[ -z "$FLAG_SECRET" ]]; then
    if [[ -f "$ENV_FILE" ]] && grep -q "FLAG_SECRET=" "$ENV_FILE" 2>/dev/null; then
      FLAG_SECRET=$(grep "FLAG_SECRET=" "$ENV_FILE" | cut -d= -f2)
      ok "Reusing existing FLAG_SECRET from .env"
    else
      FLAG_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
      ok "Generated new FLAG_SECRET"
    fi
  else
    ok "Using provided FLAG_SECRET"
  fi

  cat > "$ENV_FILE" <<EOF
# DinosecLabs environment — generated by setup.sh
# DO NOT share FLAG_SECRET publicly — flags are derived from it
FLAG_SECRET=${FLAG_SECRET}
AUTO_STOP_HOURS=${AUTO_STOP_HOURS}
EOF

  ok ".env written"
}

#  Build dashboard 
build_dashboard() {
  info "Building dashboard image..."
  cd "$SCRIPT_DIR"
  if docker-compose build dashboard; then
    ok "Dashboard image built"
  else
    err "Dashboard build failed. Check logs above."
  fi
}

#  Start dashboard 
start_dashboard() {
  info "Starting dashboard..."
  cd "$SCRIPT_DIR"
  docker-compose up -d dashboard
  sleep 2
  if curl -sf http://localhost:8000/ &>/dev/null; then
    ok "Dashboard is running at ${BOLD}http://localhost:8000${NC}"
  else
    warn "Dashboard may still be starting. Wait a few seconds and open http://localhost:8000"
  fi
}

# Summary 
print_summary() {
  echo ""
  echo -e "${BOLD}${GREEN}Setup complete!${NC}"
  echo ""
  echo -e "  Dashboard:    ${CYAN}http://localhost:8000${NC}"
  echo -e "  Labs:         Start from the dashboard or run ${CYAN}./manage.sh start a01${NC}"
  echo -e "  Flag secret:  ${YELLOW}${FLAG_SECRET:0:8}...${NC} (stored in .env)"
  echo -e "  Auto-stop:    Labs idle for more than ${AUTO_STOP_HOURS}h will stop automatically"
  echo ""
  echo -e "  Flags are HMAC-derived from your secret — they are unique to this deployment."
  echo -e "  To get the flag values: ${CYAN}curl http://localhost:8000/api/flag-values${NC}"
  echo ""
}

# Main
banner
check_deps
check_docker_running
check_ports
check_packages
generate_env
build_dashboard
start_dashboard
print_summary
