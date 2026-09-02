#!/data/data/com.termux/files/usr/bin/env bash
# agent_cli.sh — Unified Agent Contextual Workflow CLI Client
set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AGENT_URL="${SAAS_AGENT_URL:-http://127.0.0.1:8000}"
CARD_ID="${SAAS_AGENT_CARD:-}"
TASK=""
MODE="execute"

# Colors & Formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

die() { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }
info() { echo -e "${CYAN}[agent]${RESET} $*"; }

require_cmd() { command -v "$1" &>/dev/null || die "Required command not found: $1"; }
require_cmd curl
require_cmd jq

# Argument parsing
while [[ $# -gt 0 ]]; do
  case "$1" in
    --card|-c) CARD_ID="${2:-}"; shift 2 ;;
    --list-cards|-l) MODE="list-cards"; shift ;;
    --history|-H) MODE="history"; shift ;;
    --health) MODE="health"; shift ;;
    --state|-s) MODE="state"; shift ;;
    --url|-u) AGENT_URL="${2:-}"; shift 2 ;;
    --help|-h)
      echo -e "${BOLD}Unified Agent Contextual Workflow CLI Client${RESET}"
      echo "Usage: $0 [options] \"<task>\""
      echo ""
      echo "Options:"
      echo "  -c, --card <uuid>     Run task using specific AgentCard UUID"
      echo "  -l, --list-cards      List all saved AgentCards"
      echo "  -H, --history         Show recent contextual workflow execution history"
      echo "  -s, --state           Show system & engine status state"
      echo "  --health              Check server health endpoint"
      echo "  -u, --url <url>       Target agent backend URL (default: http://127.0.0.1:8000)"
      exit 0
      ;;
    *) TASK="$*"; break ;;
  esac
done

if [[ "$MODE" == "health" ]]; then
  info "Checking backend health at ${AGENT_URL}…"
  curl -sf "${AGENT_URL}/health" | jq .
  exit 0
fi

if [[ "$MODE" == "state" ]]; then
  info "Fetching system state from ${AGENT_URL}…"
  curl -sf "${AGENT_URL}/state" | jq .
  exit 0
fi

if [[ "$MODE" == "list-cards" ]]; then
  info "Fetching AgentCards…"
  curl -sf "${AGENT_URL}/cards" | jq -r '.cards[] | "• [\(.id)] \(.name) — \(.description)"'
  exit 0
fi

if [[ "$MODE" == "history" ]]; then
  info "Fetching recent workflow execution history…"
  curl -sf "${AGENT_URL}/tasks/history?limit=10" | jq -r '
    .history[] |
    "[\(.created_at[0:19])] \(.card_name) | Status: \(.status) (\(.duration_ms)ms)\n  Task: \(.task)\n  Reply: \(.reply[0:120])\n"
  '
  exit 0
fi

[[ -z "$TASK" ]] && die "No task provided. Usage: $0 \"<task>\""

# ---------------------------------------------------------------------------
# Gather device context
# ---------------------------------------------------------------------------
info "Gathering device context…"

# Clipboard
CLIPBOARD=""
if command -v termux-clipboard-get &>/dev/null; then
  CLIPBOARD="$(termux-clipboard-get 2>/dev/null || true)"
elif command -v xclip &>/dev/null; then
  CLIPBOARD="$(xclip -o 2>/dev/null || true)"
fi

# Battery (Termux)
BATTERY_LEVEL=""
if command -v termux-battery-status &>/dev/null; then
  BATTERY_LEVEL="$(termux-battery-status 2>/dev/null | jq -r '.percentage // empty' 2>/dev/null || true)"
fi

# System Info
KERNEL="$(uname -r 2>/dev/null || true)"
HOSTNAME="$(hostname 2>/dev/null || true)"
UPTIME="$(uptime -p 2>/dev/null || true)"
WHOAMI="$(whoami 2>/dev/null || true)"
CWD="$(pwd)"

# Network
LOCAL_IP=""
if command -v ip &>/dev/null; then
  LOCAL_IP="$(ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if ($i=="src") print $(i+1)}' | head -1 || true)"
fi

# Active Android Notifications
NOTIFICATIONS="[]"
if command -v termux-notification-list &>/dev/null; then
  NOTIFICATIONS="$(termux-notification-list 2>/dev/null | jq '[.[] | {packageName, title, content}]' 2>/dev/null || echo "[]")"
fi

# Music / Media state
CURRENT_MUSIC="Stopped"
if command -v playerctl &>/dev/null; then
  CURRENT_MUSIC="$(playerctl metadata --format "{{ artist }} - {{ title }}" 2>/dev/null || echo "Stopped")"
fi

# ---------------------------------------------------------------------------
# Build JSON payload
# ---------------------------------------------------------------------------
PAYLOAD="$(jq -n \
  --arg task          "$TASK" \
  --arg card_id       "$CARD_ID" \
  --arg clipboard     "$CLIPBOARD" \
  --arg kernel        "$KERNEL" \
  --arg hostname      "$HOSTNAME" \
  --arg uptime        "$UPTIME" \
  --arg whoami        "$WHOAMI" \
  --arg cwd           "$CWD" \
  --arg battery       "$BATTERY_LEVEL" \
  --arg local_ip      "$LOCAL_IP" \
  --arg music         "$CURRENT_MUSIC" \
  --argjson alerts    "$NOTIFICATIONS" \
  '{
    task: $task,
    card_id: (if $card_id == "" then null else $card_id end),
    local_context: {
      clipboard:     $clipboard,
      kernel:        $kernel,
      hostname:      $hostname,
      uptime:        $uptime,
      user:          $whoami,
      cwd:           $cwd,
      battery_pct:   $battery,
      local_ip:      $local_ip,
      current_music: $music,
      notifications: $alerts
    }
  }'
)"

# ---------------------------------------------------------------------------
# POST to /execute
# ---------------------------------------------------------------------------
info "Compiling and executing contextual workflow at ${AGENT_URL}/execute…"
echo -e "${YELLOW}${BOLD}Task:${RESET} $TASK"
echo ""

RESPONSE="$(
  curl -sf \
    --max-time 60 \
    -X POST \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    "${AGENT_URL}/execute" \
  || die "Failed to execute workflow at ${AGENT_URL}. Is the server running?"
)"

# ---------------------------------------------------------------------------
# Render Workflow Telemetry & Execution Progress
# ---------------------------------------------------------------------------
CARD_NAME="$(echo "$RESPONSE" | jq -r '.card_name // "System Agent"')"
REPLY="$(echo "$RESPONSE" | jq -r '.reply // "(no reply)"')"
STATUS="$(echo "$RESPONSE" | jq -r '.status // "completed"')"
DURATION="$(echo "$RESPONSE" | jq -r '.duration_ms // 0')"
NEW_CARD_NAME="$(echo "$RESPONSE" | jq -r '.new_card.name // ""')"
NEW_CARD_ID="$(echo "$RESPONSE" | jq -r '.new_card.id // ""')"

# Status banner color
STATUS_COLOR="$GREEN"
[[ "$STATUS" == "failed" ]] && STATUS_COLOR="$RED"
[[ "$STATUS" == "partial" ]] && STATUS_COLOR="$YELLOW"

echo -e "${BOLD}${STATUS_COLOR}[${CARD_NAME}] (${STATUS}, ${DURATION}ms)${RESET}"
echo -e "${REPLY}"
echo ""

# Render Workflow Steps Progress
STEP_COUNT="$(echo "$RESPONSE" | jq '.step_results | length')"

if [[ "$STEP_COUNT" -gt 0 ]]; then
  echo -e "${BOLD}${CYAN}Contextual Workflow Execution (${STEP_COUNT} steps):${RESET}"
  
  echo "$RESPONSE" | jq -c '.step_results[]' | while read -r step_json; do
    S_ID="$(echo "$step_json" | jq -r '.step_id')"
    S_TITLE="$(echo "$step_json" | jq -r '.title // .target')"
    S_STATUS="$(echo "$step_json" | jq -r '.status')"
    S_TARGET="$(echo "$step_json" | jq -r '.target')"
    S_OUTPUT="$(echo "$step_json" | jq -r '.output // ""' | head -n 25)"

    S_DUR="$(echo "$step_json" | jq -r '.duration_ms')"
    S_VAR="$(echo "$step_json" | jq -r '.captured_var // ""')"

    ICON="${GREEN}✔${RESET}"
    if [[ "$S_STATUS" == "failed" ]]; then
      ICON="${RED}✖${RESET}"
    elif [[ "$S_STATUS" == "healed" ]]; then
      ICON="${PURPLE}↺ (healed)${RESET}"
    elif [[ "$S_STATUS" == "skipped" ]]; then
      ICON="${YELLOW}↷ (skipped)${RESET}"
    fi

    echo -e "  ${ICON} ${BOLD}Step ${S_ID}:${RESET} ${S_TITLE} (${S_DUR}ms)"
    echo -e "     ${BLUE}Command/Target:${RESET} ${S_TARGET}"
    if [[ -n "$S_OUTPUT" ]]; then
      echo -e "     ${CYAN}Output:${RESET}"
      echo "$S_OUTPUT" | sed 's/^/       /'
    fi

    if [[ -n "$S_VAR" ]]; then
      echo -e "     ${YELLOW}Captured Context Variable:${RESET} \${${S_VAR}}"
    fi
    echo ""
  done
fi

# Render created AgentCard notification
if [[ -n "$NEW_CARD_NAME" && "$NEW_CARD_NAME" != "null" ]]; then
  echo -e "${YELLOW}✦ New AgentCard Created: \"${NEW_CARD_NAME}\" (id: ${NEW_CARD_ID})${RESET}"
  echo -e "  Use it for future specialized tasks: ${BOLD}$0 --card ${NEW_CARD_ID} \"<task>\"${RESET}"
  echo ""
fi
