#!/bin/zsh
set -euo pipefail

HOME_DIR="${HOME:-/Users/joey}"
NOTES_DIR="/Users/joey/Library/Mobile Documents/com~apple~CloudDocs/Notes"
PY_SCRIPT="${NOTES_DIR}/scripts/rename_untitled_notes.py"
DRY_RUN_FLAG=""
LOG_FILE="${NOTES_DIR}/scripts/rename_notes.log"
TARGET_LIST=""
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-600}"
IDLE_TIMEOUT_SECONDS="${IDLE_TIMEOUT_SECONDS:-60}"
PRECHECK_TIMEOUT_SECONDS="${PRECHECK_TIMEOUT_SECONDS:-20}"

run_cmd_timeout() {
  python3 - "$1" "${@:2}" <<'PY'
import subprocess
import sys

timeout = int(sys.argv[1])
cmd = sys.argv[2:]
try:
    result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, text=True, timeout=timeout)
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print(f"ERROR: command timed out after {timeout}s")
    sys.exit(124)
PY
}

LOG_DIR="$(dirname "$LOG_FILE")"
if ! mkdir -p "$LOG_DIR" 2>/dev/null || ! touch "$LOG_FILE" 2>/dev/null; then
  LOG_FILE="$HOME_DIR/Library/Logs/rename_notes.log"
  mkdir -p "$(dirname "$LOG_FILE")"
  touch "$LOG_FILE"
fi

run_cursor_agent() {
  # --trust: non-interactive launchd runs otherwise stall on "Workspace Trust Required"
  python3 - "$TIMEOUT_SECONDS" "$IDLE_TIMEOUT_SECONDS" cursor agent --print --trust --mode ask --workspace "${NOTES_DIR}" "${PROMPT}" <<'PY'
import selectors
import subprocess
import sys
import time

timeout = int(sys.argv[1])
idle_timeout = int(sys.argv[2])
cmd = sys.argv[3:]

start = time.time()
last_output = start
p = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

sel = selectors.DefaultSelector()
sel.register(p.stdout, selectors.EVENT_READ)

try:
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            p.kill()
            print(f"ERROR: Cursor CLI timed out after {timeout}s", flush=True)
            sys.exit(124)
        if time.time() - last_output > idle_timeout:
            p.kill()
            print(f"ERROR: Cursor CLI idle timeout after {idle_timeout}s", flush=True)
            sys.exit(124)

        events = sel.select(timeout=0.2)
        if not events:
            if p.poll() is not None:
                break
            continue

        for key, _ in events:
            line = key.fileobj.readline()
            if line:
                last_output = time.time()
                print(line, end="", flush=True)
            elif p.poll() is not None:
                break

    sys.exit(p.wait())
finally:
    try:
        sel.unregister(p.stdout)
    except Exception:
        pass
    try:
        if p.stdout:
            p.stdout.close()
    except Exception:
        pass
PY
}

for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    DRY_RUN_FLAG="--dry-run"
    break
  fi
done

# Set USE_CURSOR_CLI=1 after Cursor CLI is installed and configured.
USE_CURSOR_CLI="${USE_CURSOR_CLI:-0}"

if [[ "${USE_CURSOR_CLI}" == "1" ]]; then
  if ! command -v cursor >/dev/null 2>&1; then
    echo "Cursor CLI not found. Install it or set USE_CURSOR_CLI=0."
    exit 1
  fi

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Preflight: cursor --version" | tee -a "${LOG_FILE}"
  cursor --version 2>&1 | tee -a "${LOG_FILE}"

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Preflight: cursor whoami" | tee -a "${LOG_FILE}"
  if ! run_cmd_timeout "${PRECHECK_TIMEOUT_SECONDS}" cursor whoami 2>&1 | tee -a "${LOG_FILE}"; then
    message="[$(date '+%Y-%m-%d %H:%M:%S')] Preflight failed"
    echo "${message}" | tee -a "${LOG_FILE}"
    exit 1
  fi

  TARGET_LIST=$(python3 "${PY_SCRIPT}" --root "${NOTES_DIR}" --list-candidates)
  if [[ -z "${TARGET_LIST}" ]]; then
    echo "No files with non-meaningful titles found."
    exit 0
  fi
  CANDIDATE_COUNT=$(printf "%s\n" "${TARGET_LIST}" | wc -l | tr -d ' ')
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Candidates: ${CANDIDATE_COUNT}" | tee -a "${LOG_FILE}"

  PROMPT=$(cat <<'EOF'
Scan the Notes directory for .md or .txt files that do not have meaningful titles
like "Untitled", "New Note", "Note", or similar. For each one, read the content
and generate a short, topic-style title (3-6 words) that summarizes what the
note is about. Do NOT use the first line or first sentence verbatim; instead,
extract the underlying topic/subject and title it like a human would.
Sanitize the title to remove illegal filename characters, trim whitespace,
limit to ~60 characters, and ensure unique names by adding " (n)" if needed.
Rename the files in place.
EOF
)

  if [[ -n "${DRY_RUN_FLAG}" ]]; then
    PROMPT+=$'\n\nDry run only: do not rename files, only report what would change.'
  fi

  PROMPT+=$'\n\nIf a file is empty (no content), delete it instead of renaming.'
  PROMPT+=$'\nInclude a section listing deleted empty files.'
  PROMPT+=$'\n\nFirst output a JSON block between lines BEGIN_JSON and END_JSON.'
  PROMPT+=$'\nThe JSON must have keys: "renames" and "deletions".'
  PROMPT+=$'\nEach rename item: {"from": "<path>", "to": "<new filename>"}'
  PROMPT+=$'\nEach deletion item: {"path": "<path>"}'
  PROMPT+=$'\nPaths must be relative to the Notes root.'
  PROMPT+=$'\nDo NOT wrap the JSON in markdown fences.'
  PROMPT+=$'\nDo NOT attempt file operations or use tools; analysis only.'
  PROMPT+=$'\nDo NOT mention system restrictions; just output JSON + report.'
  PROMPT+=$'\nFor titles: avoid lead-in phrases like "Letter about", "Reflection on",'
  PROMPT+=$'\n"Quote about", "Thought on", "Commentary on". Use concise noun phrases'
  PROMPT+=$'\nthat capture the subject itself.'
  PROMPT+=$'\nAfter END_JSON, output the human-friendly report.'

  PROMPT+=$'\n\nOnly consider these files (paths are relative to the Notes root):\n'
  PROMPT+="${TARGET_LIST}"

  # Update the command below to match your Cursor CLI usage if needed.
  OUTPUT_FILE="$(mktemp)"
  EXIT_CODE=0
  if ! run_cursor_agent | tee "${OUTPUT_FILE}" >/dev/null; then
    EXIT_CODE=$?
  fi

  if [[ -n "${DRY_RUN_FLAG}" ]]; then
    cat "${OUTPUT_FILE}"
    if [[ "${EXIT_CODE}" -ne 0 ]]; then
      message="[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI dry-run failed (exit ${EXIT_CODE})"
      echo "${message}" | tee -a "${LOG_FILE}"
      rm -f "${OUTPUT_FILE}"
      exit "${EXIT_CODE}"
    fi
    rm -f "${OUTPUT_FILE}"
    exit 0
  fi

  if ! python3 - "${OUTPUT_FILE}" <<'PY'
import sys

text = open(sys.argv[1], "r", encoding="utf-8", errors="ignore").read()
start = text.find("BEGIN_JSON")
end = text.find("END_JSON")
if start == -1 or end == -1 or end <= start:
    sys.exit(1)
PY
  then
    message="[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI output missing JSON plan"
    echo "${message}" | tee -a "${LOG_FILE}"
    size=$(wc -c < "${OUTPUT_FILE}" | tr -d ' ')
    echo "Output bytes: ${size}" | tee -a "${LOG_FILE}"
    if [[ "${size}" -gt 0 ]]; then
      echo "--- Cursor CLI raw output ---" | tee -a "${LOG_FILE}"
      cat "${OUTPUT_FILE}" | tee -a "${LOG_FILE}"
      echo "--- End raw output ---" | tee -a "${LOG_FILE}"
    fi
    rm -f "${OUTPUT_FILE}"
    exit 1
  fi

  {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI run started"
    python3 - "${OUTPUT_FILE}" <<'PY'
import sys

in_json = False
with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as handle:
    for line in handle:
        if line.strip() == "BEGIN_JSON":
            in_json = True
            continue
        if line.strip() == "END_JSON":
            in_json = False
            continue
        if not in_json:
            sys.stdout.write(line)
PY
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI run finished"
    echo ""
    echo ""
  } | tee -a "${LOG_FILE}"

  if ! python3 "${PY_SCRIPT}" --root "${NOTES_DIR}" --apply-plan-file "${OUTPUT_FILE}"; then
    message="[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI plan apply failed"
    echo "${message}" | tee -a "${LOG_FILE}"
    rm -f "${OUTPUT_FILE}"
    exit 1
  fi

  rm -f "${OUTPUT_FILE}"
  if [[ "${EXIT_CODE}" -ne 0 ]]; then
    message="[$(date '+%Y-%m-%d %H:%M:%S')] Cursor CLI run failed (exit ${EXIT_CODE})"
    echo "${message}" | tee -a "${LOG_FILE}"
    exit "${EXIT_CODE}"
  fi
  exit 0
fi

python3 "${PY_SCRIPT}" --root "${NOTES_DIR}" ${DRY_RUN_FLAG}
