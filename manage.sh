#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# Lab Manager
# ─────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

LABS=(a01 a02 a03 a04 a05 a06 a07 a08 a09 a10)
LAB_NAMES=(
  "Broken Access Control"
  "Security Misconfiguration"
  "Software Supply Chain Failures"
  "Cryptographic Failures"
  "Injection"
  "Insecure Design"
  "Authentication Failures"
  "Software or Data Integrity Failures"
  "Security Logging & Alerting Failures"
  "Mishandling of Exceptional Conditions"
)
PORTS=(8001 8002 8003 8004 8005 8006 8007 8008 8009 8010)

banner() {
  echo -e "${BOLD}${CYAN}"
  echo "╔══════════════════════════════════════════════════════╗"
  echo "║                      Lab Manager                     ║"
  echo "╚══════════════════════════════════════════════════════╝"
  echo -e "${NC}"
}

status_all() {
  echo -e "${BOLD}Estado de los Labs:${NC}"
  echo "────────────────────────────────────────────────────────"
  for i in "${!LABS[@]}"; do
    lab="${LABS[$i]}"
    name="${LAB_NAMES[$i]}"
    port="${PORTS[$i]}"
    container="owasp-${lab}"
    status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "stopped")
    if [ "$status" = "running" ]; then
      icon="${GREEN}● ONLINE ${NC}"
    else
      icon="${RED}○ OFFLINE${NC}"
    fi
    printf " ${BOLD}%s${NC} %b  %s (:%s)\n" "${lab^^}" "$icon" "$name" "$port"
  done
  echo "────────────────────────────────────────────────────────"
  echo -e " ${BLUE}Dashboard:${NC} http://localhost:8000"
}

start_lab() {
  local lab="$1"
  echo -e "${YELLOW}Iniciando lab ${lab}...${NC}"
  docker-compose --profile "$lab" up -d --build
  echo -e "${GREEN}✓ Lab ${lab} iniciado${NC}"
}

stop_lab() {
  local lab="$1"
  local container="owasp-${lab}"
  echo -e "${YELLOW}Deteniendo lab ${lab}...${NC}"
  docker stop "$container" 2>/dev/null && echo -e "${GREEN}✓ Lab ${lab} detenido${NC}" || echo -e "${RED}El lab no estaba corriendo${NC}"
}

start_all() {
  echo -e "${YELLOW}Iniciando todos los labs...${NC}"
  for lab in "${LABS[@]}"; do
    docker-compose --profile "$lab" up -d --build &
  done
  wait
  echo -e "${GREEN}✓ Todos los labs iniciados${NC}"
}

stop_all() {
  echo -e "${YELLOW}Deteniendo todos los labs...${NC}"
  for lab in "${LABS[@]}"; do
    docker stop "owasp-${lab}" 2>/dev/null || true
  done
  echo -e "${GREEN}✓ Todos los labs detenidos${NC}"
}

start_dashboard() {
  echo -e "${YELLOW}Iniciando dashboard...${NC}"
  docker-compose up -d --build dashboard
  echo -e "${GREEN}✓ Dashboard disponible en http://localhost:8000${NC}"
}

usage() {
  echo -e "Uso: ${BOLD}./manage.sh${NC} <comando> [lab_id]"
  echo ""
  echo "Comandos:"
  echo "  status              — Ver estado de todos los labs"
  echo "  start <lab_id>      — Iniciar un lab (ej: start a01)"
  echo "  stop <lab_id>       — Detener un lab"
  echo "  start-all           — Iniciar todos los labs"
  echo "  stop-all            — Detener todos los labs"
  echo "  dashboard           — Iniciar solo el dashboard"
  echo "  logs <lab_id>       — Ver logs de un lab"
  echo "  build               — Construir todas las imágenes"
  echo ""
  echo "Lab IDs: a01 a02 a03 a04 a05 a06 a07 a08 a09 a10"
}

banner

case "${1:-status}" in
  status)       status_all ;;
  start)        [ -n "${2:-}" ] && start_lab "$2" || echo "Especifica lab_id" ;;
  stop)         [ -n "${2:-}" ] && stop_lab "$2"  || echo "Especifica lab_id" ;;
  start-all)    start_all ;;
  stop-all)     stop_all  ;;
  dashboard)    start_dashboard ;;
  logs)         [ -n "${2:-}" ] && docker logs -f "owasp-${2}" || echo "Especifica lab_id" ;;
  build)        docker-compose build ;;
  help|--help)  usage ;;
  *)            echo -e "${RED}Comando desconocido: $1${NC}"; usage ;;
esac
