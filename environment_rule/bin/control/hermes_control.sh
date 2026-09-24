#!/usr/bin/env sh
set -u

CONTROL_DIR="${REMOTE_RUNNER_CONTROL_DIR:-/workspace/work/behavior/control}"
RUNNING_DIR="${CONTROL_DIR}/running"
LOG_FILE="${CONTROL_DIR}/control_events.log"

ACTION="${1:-status}"
TASK_ID="${2:-}"
REASON="${3:-manual}"

mkdir -p "$CONTROL_DIR" "$RUNNING_DIR"
chmod 700 "$CONTROL_DIR" "$RUNNING_DIR" 2>/dev/null || true
touch "$LOG_FILE"
chmod 600 "$LOG_FILE" 2>/dev/null || true

now_ts() {
  date "+%Y-%m-%d %H:%M:%S"
}

log_event() {
  echo "[$(now_ts)] action=$ACTION task_id=${TASK_ID:-<all>} reason=$REASON" >> "$LOG_FILE"
}

kill_from_pid_files() {
  pattern="$1"
  for file in $pattern; do
    [ -f "$file" ] || continue
    pid="$(sed -n 's/^pid=//p' "$file" | head -1)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}

case "$ACTION" in
  pause-all)
    date > "$CONTROL_DIR/PAUSE_ALL"
    log_event
    echo "PAUSE_ALL set"
    ;;

  stop-all)
    date > "$CONTROL_DIR/STOP_ALL"
    kill_from_pid_files "$RUNNING_DIR/*.pid"
    log_event
    echo "STOP_ALL set; running remote_runner processes were signaled"
    ;;

  resume-all)
    rm -f "$CONTROL_DIR/PAUSE_ALL" "$CONTROL_DIR/STOP_ALL"
    log_event
    echo "Global pause and stop signals cleared"
    ;;

  pause)
    [ -n "$TASK_ID" ] || { echo "Usage: hermes_control.sh pause TASK_ID"; exit 2; }
    date > "$CONTROL_DIR/PAUSE_${TASK_ID}"
    log_event
    echo "PAUSE_${TASK_ID} set"
    ;;

  stop)
    [ -n "$TASK_ID" ] || { echo "Usage: hermes_control.sh stop TASK_ID"; exit 2; }
    date > "$CONTROL_DIR/STOP_${TASK_ID}"
    kill_from_pid_files "$RUNNING_DIR/${TASK_ID}_*.pid"
    log_event
    echo "STOP_${TASK_ID} set; matching remote_runner processes were signaled"
    ;;

  resume)
    [ -n "$TASK_ID" ] || { echo "Usage: hermes_control.sh resume TASK_ID"; exit 2; }
    rm -f "$CONTROL_DIR/PAUSE_${TASK_ID}" "$CONTROL_DIR/STOP_${TASK_ID}"
    log_event
    echo "Task pause and stop signals cleared: $TASK_ID"
    ;;

  status)
    echo "=== control files ==="
    ls -la "$CONTROL_DIR" 2>/dev/null || true
    echo
    echo "=== running tasks ==="
    ls -la "$RUNNING_DIR" 2>/dev/null || true
    echo
    echo "=== recent events ==="
    tail -20 "$LOG_FILE" 2>/dev/null || true
    ;;

  *)
    echo "Usage:"
    echo "  hermes_control.sh pause-all"
    echo "  hermes_control.sh stop-all"
    echo "  hermes_control.sh resume-all"
    echo "  hermes_control.sh pause TASK_ID"
    echo "  hermes_control.sh stop TASK_ID"
    echo "  hermes_control.sh resume TASK_ID"
    echo "  hermes_control.sh status"
    exit 2
    ;;
esac
