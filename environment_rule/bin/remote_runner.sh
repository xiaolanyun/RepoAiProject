#!/usr/bin/env bash
set -uo pipefail

CONFIG_ROOT="${GITEEREPO_CONFIG_ROOT:-/workspace/envs/giteerepo}"
INVENTORY_FILE="${CONFIG_ROOT}/config/inventory.yaml"
POLICY_FILE="${CONFIG_ROOT}/config/remote-runner-policy.yaml"
QUERY_BIN="${CONFIG_ROOT}/bin/config_query.py"
POLICY_CHECK_BIN="${CONFIG_ROOT}/bin/policy_check.py"

PYTHON_BIN="${HERMES_PYTHON_BIN:-/opt/hermes/.venv/bin/python3}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
  echo "ERROR: python3 is required."
  exit 2
fi

for required_file in "$INVENTORY_FILE" "$POLICY_FILE" "$QUERY_BIN" "$POLICY_CHECK_BIN"; do
  if [ ! -f "$required_file" ]; then
    echo "ERROR: missing configuration file: $required_file"
    exit 2
  fi
done

eval "$("$PYTHON_BIN" "$QUERY_BIN" resolve-policy "$POLICY_FILE")"

TASK_ID="${REMOTE_TASK_ID:-}"
CONTAINER_NAME=""
CLEANUP_SANDBOX=0
CLEANUP_TASK=0

usage() {
  cat <<'EOF'
Usage:
  remote_runner.sh [--task TASK_ID] [--container NAME] [--cleanup-sandbox] [--cleanup-task] HOST "COMMAND"

Rules:
  L0-L3 execute without interactive approval.
  L2-L3 are audited.
  L4 is blocked and logged.
EOF
}

now_ts() { date "+%Y-%m-%d %H:%M:%S"; }
now_id() { date "+%Y%m%d_%H%M%S"; }

sanitize_task_id() {
  local raw="$1"
  local cleaned
  cleaned="$(printf '%s' "$raw" | tr -cs 'A-Za-z0-9._-' '_' | sed 's/^_//;s/_$//')"
  if [ -z "$cleaned" ]; then
    cleaned="remote-task-$(now_id)"
  fi
  printf '%s' "$cleaned"
}

json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e ':a;N;$!ba;s/\n/\\n/g'
}

shell_single_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

contains_csv() {
  local csv="$1"
  local wanted="$2"
  local item
  IFS=',' read -r -a items <<< "$csv"
  for item in "${items[@]}"; do
    if [ "$item" = "$wanted" ]; then return 0; fi
  done
  return 1
}

init_control_dir() {
  RUNNING_DIR="${CONTROL_DIR}/running"
  CONTROL_LOG_FILE="${CONTROL_DIR}/control_events.log"
  mkdir -p "$CONTROL_DIR" "$RUNNING_DIR" 2>/dev/null || true
  chmod 700 "$CONTROL_DIR" "$RUNNING_DIR" 2>/dev/null || true
  touch "$CONTROL_LOG_FILE" 2>/dev/null || true
  chmod 600 "$CONTROL_LOG_FILE" 2>/dev/null || true
}

log_control_event() {
  local event="$1"
  local reason="$2"
  init_control_dir
  printf '[%s] event=%s task_id=%s host=%s container=%s reason=%s\n' "$(now_ts)" "$event" "$TASK_ID" "${TARGET_HOST:-}" "${CONTAINER_NAME:-<host>}" "$reason" >> "$CONTROL_LOG_FILE" 2>/dev/null || true
}

check_control_signal() {
  local stage="$1"
  init_control_dir
  if [ -f "$CONTROL_DIR/STOP_ALL" ] || [ -f "$CONTROL_DIR/STOP_${TASK_ID}" ]; then
    echo "STOP_REQUESTED at stage=${stage}"
    log_control_event "STOP" "stage=${stage}"
    exit 130
  fi
  if [ -f "$CONTROL_DIR/PAUSE_ALL" ] || [ -f "$CONTROL_DIR/PAUSE_${TASK_ID}" ]; then
    echo "PAUSE_REQUESTED at stage=${stage}"
    log_control_event "PAUSE" "stage=${stage}"
    exit 131
  fi
}

append_file() {
  local file="$1"
  shift
  printf '%s\n' "$@" >> "$file" 2>/dev/null || true
}

log_audit_json() {
  local event="$1"
  local exit_code="${2:-}"
  printf '{"time":"%s","event":"%s","task_id":"%s","host":"%s","container":"%s","scope":"%s","decision":"%s","risk_level":"%s","reason":"%s","exit_code":"%s","command":"%s","stdout_file":"%s","stderr_file":"%s"}\n' \
    "$(now_ts)" "$event" "$(json_escape "$TASK_ID")" "$(json_escape "$TARGET_HOST")" "$(json_escape "$CONTAINER_NAME")" \
    "$EXEC_SCOPE" "$DECISION" "$RISK_LEVEL" "$(json_escape "$REASON")" "$exit_code" "$(json_escape "$COMMAND")" \
    "$(json_escape "$STDOUT_FILE")" "$(json_escape "$STDERR_FILE")" >> "$AUDIT_FILE" 2>/dev/null || true
}

log_risk_markdown() {
  local target_file="$1"
  local title="$2"
  append_file "$target_file" "" "## $(now_ts) - ${title}" "" "- Task ID: ${TASK_ID}" "- Host: ${TARGET_ALIAS} (${TARGET_HOST})" "- Container: ${CONTAINER_NAME:-<host>}" "- Scope: ${EXEC_SCOPE}" "- Decision: ${DECISION}" "- Risk Level: ${RISK_LEVEL}" "- Reason: ${REASON}" "- Command:" "" '```bash' "$COMMAND" '```'
}

while [ "$#" -gt 0 ]; do
  case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    --task) [ "$#" -ge 2 ] || { echo "ERROR: --task requires TASK_ID"; exit 2; }; TASK_ID="$2"; shift 2 ;;
    --container) [ "$#" -ge 2 ] || { echo "ERROR: --container requires NAME"; exit 2; }; CONTAINER_NAME="$2"; shift 2 ;;
    --cleanup-sandbox) CLEANUP_SANDBOX=1; shift ;;
    --cleanup-task) CLEANUP_TASK=1; shift ;;
    --*) echo "ERROR: unknown option: $1"; usage; exit 2 ;;
    *) break ;;
  esac
done

if [ "$#" -lt 2 ]; then
  echo "ERROR: HOST and COMMAND are required."
  usage
  exit 2
fi

TARGET_REF="$1"
shift
COMMAND="$*"
TASK_ID="$(sanitize_task_id "${TASK_ID:-remote-task-$(now_id)}")"

eval "$("$PYTHON_BIN" "$QUERY_BIN" resolve-host "$INVENTORY_FILE" "$TARGET_REF")"

RUN_TIMEOUT="${RUN_TIMEOUT:-$POLICY_TIMEOUT}"
if ! [[ "$RUN_TIMEOUT" =~ ^[0-9]+$ ]]; then RUN_TIMEOUT="$POLICY_TIMEOUT"; fi

EXEC_SCOPE="host"
if [ -n "$CONTAINER_NAME" ]; then
  EXEC_SCOPE="sandbox-container"
  if [ "$TARGET_ALIAS" != "$SANDBOX_HOST_ALIAS" ]; then
    echo "ERROR: --container is only allowed on ${SANDBOX_HOST_ALIAS}."
    exit 100
  fi
  if ! contains_csv "$SANDBOX_CONTAINERS" "$CONTAINER_NAME"; then
    echo "ERROR: container is not in the sandbox allowlist: $CONTAINER_NAME"
    exit 100
  fi
fi

if [ "$CLEANUP_SANDBOX" -eq 1 ] && [ "$EXEC_SCOPE" != "sandbox-container" ]; then
  echo "ERROR: --cleanup-sandbox requires --container."
  exit 100
fi

if [ "$CLEANUP_TASK" -eq 1 ] && [ "$EXEC_SCOPE" != "host" ]; then
  echo "ERROR: --cleanup-task is only valid for host scope."
  exit 100
fi

init_control_dir
check_control_signal "after-validation"

AUDIT_DIR="${AUDIT_BASE_DIR}/${TASK_ID}"
STDOUT_DIR="${AUDIT_DIR}/stdout"
STDERR_DIR="${AUDIT_DIR}/stderr"
AUDIT_FILE="${AUDIT_DIR}/audit.jsonl"
HIGH_RISK_FILE="${AUDIT_DIR}/high_risk_operations.md"
CRITICAL_FILE="${AUDIT_DIR}/critical_blocks.md"

mkdir -p "$STDOUT_DIR" "$STDERR_DIR"
chmod 700 "$AUDIT_DIR" "$STDOUT_DIR" "$STDERR_DIR" 2>/dev/null || true
touch "$AUDIT_FILE" "$HIGH_RISK_FILE" "$CRITICAL_FILE"
chmod 600 "$AUDIT_FILE" "$HIGH_RISK_FILE" "$CRITICAL_FILE" 2>/dev/null || true

RUN_ID="$(now_id)_$$_${RANDOM:-0}"
STDOUT_FILE="${STDOUT_DIR}/${RUN_ID}.out"
STDERR_FILE="${STDERR_DIR}/${RUN_ID}.err"
RUN_PID_FILE="${RUNNING_DIR}/${TASK_ID}_${RUN_ID}.pid"

POLICY_ARGS=("$POLICY_CHECK_BIN" --policy "$POLICY_FILE" --scope "$EXEC_SCOPE" --container "$CONTAINER_NAME" --task-id "$TASK_ID" --target-workdir "$TARGET_WORKDIR" --command "$COMMAND")
if [ "$CLEANUP_SANDBOX" -eq 1 ]; then POLICY_ARGS+=(--cleanup-sandbox); fi
if [ "$CLEANUP_TASK" -eq 1 ]; then POLICY_ARGS+=(--cleanup-task); fi

eval "$("$PYTHON_BIN" "${POLICY_ARGS[@]}")"

if [ "$DECISION" = "BLOCK" ]; then
  log_audit_json "BLOCK" "$POLICY_EXIT_CODE"
  log_risk_markdown "$CRITICAL_FILE" "Blocked operation"
  echo "CRITICAL_SECURITY_BLOCK: $REASON"
  echo "Audit: $CRITICAL_FILE"
  exit "$POLICY_EXIT_CODE"
fi

if [ ! -f "$KEY_PATH" ]; then
  echo "ERROR: SSH private key not found: $KEY_PATH"
  exit 102
fi

SOURCE_KEY_PATH="$KEY_PATH"
RUNTIME_KEY_DIR="${REMOTE_RUNNER_KEY_DIR:-/tmp/hermes-remote-runner-$(id -u)/ssh}"
KEY_PATH="${RUNTIME_KEY_DIR}/hermes_ed25519"

umask 077
mkdir -p "$RUNTIME_KEY_DIR"
cp -f "$SOURCE_KEY_PATH" "$KEY_PATH"
chmod 600 "$KEY_PATH"

RUNTIME_KEY_MODE="$(stat -c '%a' "$KEY_PATH" 2>/dev/null || true)"
if [ "$RUNTIME_KEY_MODE" != "600" ]; then
  echo "ERROR: Runtime SSH private key mode is not 600: ${RUNTIME_KEY_MODE:-unknown}"
  exit 104
fi

if [ ! -s "$KNOWN_HOSTS" ]; then
  echo "ERROR: known_hosts is empty: $KNOWN_HOSTS"
  exit 103
fi

{
  echo "pid=$$"
  echo "task_id=${TASK_ID}"
  echo "host=${TARGET_HOST}"
  echo "container=${CONTAINER_NAME:-<host>}"
  echo "scope=${EXEC_SCOPE}"
  echo "start_time=$(now_ts)"
  echo "command=${COMMAND}"
} > "$RUN_PID_FILE"
chmod 600 "$RUN_PID_FILE" 2>/dev/null || true

cleanup() { rm -f "$RUN_PID_FILE" 2>/dev/null || true; }
trap cleanup EXIT

if [ "$DECISION" = "ALLOW_WITH_AUDIT" ]; then
  log_risk_markdown "$HIGH_RISK_FILE" "Audited operation"
fi

echo "remote_runner start"
echo "Task ID: $TASK_ID"
echo "Host: ${TARGET_ALIAS} (${TARGET_HOST}:${TARGET_PORT})"
echo "Container: ${CONTAINER_NAME:-<host>}"
echo "Scope: $EXEC_SCOPE"
echo "Timeout: ${RUN_TIMEOUT}s"
echo "Decision: $DECISION"
echo "Risk: $RISK_LEVEL"
echo "Reason: $REASON"
echo "Audit directory: $AUDIT_DIR"
echo "Command: $COMMAND"

log_audit_json "START" ""

if [ "$EXEC_SCOPE" = "sandbox-container" ]; then
  COMMAND_QUOTED="$(shell_single_quote "$COMMAND")"
  REMOTE_COMMAND="docker exec -i '$CONTAINER_NAME' sh -lc $COMMAND_QUOTED"
else
  REMOTE_COMMAND="mkdir -p '$TARGET_WORKDIR' && cd '$TARGET_WORKDIR' && $COMMAND"
fi

check_control_signal "before-ssh"

set +e
timeout "$RUN_TIMEOUT" ssh -F "$SSH_CONFIG" -i "$KEY_PATH" -p "$TARGET_PORT" -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$KNOWN_HOSTS" -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=2 "${TARGET_USER}@${TARGET_HOST}" "$REMOTE_COMMAND" > >(tee "$STDOUT_FILE") 2> >(tee "$STDERR_FILE" >&2)
EXIT_CODE=$?
set -e

chmod 600 "$STDOUT_FILE" "$STDERR_FILE" 2>/dev/null || true
log_audit_json "END" "$EXIT_CODE"

echo "remote_runner end"
echo "Exit code: $EXIT_CODE"
echo "STDOUT: $STDOUT_FILE"
echo "STDERR: $STDERR_FILE"
echo "Audit: $AUDIT_FILE"

exit "$EXIT_CODE"
