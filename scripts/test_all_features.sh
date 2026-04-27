#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pass() { echo "[PASS] $1"; }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; exit 1; }

run_cmd() {
  local name="$1"
  shift
  echo "\n>>> $name"
  if "$@"; then
    pass "$name"
  else
    fail "$name"
  fi
}

# 1) Unit tests
run_cmd "unittest suite" python -m unittest discover -s tests -v

# 2) CLI mock prompt mode should succeed
run_cmd "cli mock prompt mode" bash -lc 'python -m src.seogeo_reporter.cli --month 2026-03 --mode mock --prompt-mode mock > /tmp/seogeo_mock.json'
python - <<'PY'
import json
from pathlib import Path
p = Path('/tmp/seogeo_mock.json')
data = json.loads(p.read_text(encoding='utf-8'))
assert 'overview' in data
assert 'prompt_rows' in data
print('[PASS] mock output JSON schema check')
PY

# 3) OAuth URL print should succeed
run_cmd "cli oauth url" bash -lc 'python -m src.seogeo_reporter.cli --month 2026-03 --print-oauth-url > /tmp/seogeo_oauth.json'
python - <<'PY'
import json
from pathlib import Path
p = Path('/tmp/seogeo_oauth.json')
data = json.loads(p.read_text(encoding='utf-8'))
assert 'auth_url' in data and 'state' in data
print('[PASS] oauth output JSON schema check')
PY


# 3.5) Runner smoke mode should succeed
run_cmd "runner smoke mode" bash -lc 'RUN_MODE=mock PROMPT_MODE=mock python -m src.seogeo_reporter.runner > /tmp/seogeo_runner.json'
python - <<'PY'
import json
from pathlib import Path
p = Path('/tmp/seogeo_runner.json')
data = json.loads(p.read_text(encoding='utf-8'))
assert data.get('status') == 'ok'
assert 'month' in data
print('[PASS] runner output JSON schema check')
PY
# 4) Browser mode is expected to fail when playwright is missing
set +e
python -m src.seogeo_reporter.cli --month 2026-03 --mode mock --prompt-mode browser > /tmp/seogeo_browser.json 2>&1
browser_exit=$?
set -e
if [[ "$browser_exit" -eq 2 ]]; then
  if grep -q 'Playwright is not installed' /tmp/seogeo_browser.json; then
    pass "cli browser mode expected dependency error"
  else
    fail "cli browser mode returned exit 2 but missing expected message"
  fi
else
  warn "cli browser mode exit code=$browser_exit (playwright may be installed or behavior changed)"
fi

# 5) Optional Excel writer integration check (requires openpyxl)
set +e
python - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec('openpyxl') else 1)
PY
has_openpyxl=$?
set -e

if [[ "$has_openpyxl" -eq 0 ]]; then
  run_cmd "cli excel export" python -m src.seogeo_reporter.cli --month 2026-03 --mode mock --prompt-mode mock --excel-out /tmp/seogeo_report.xlsx
  [[ -f /tmp/seogeo_report.xlsx ]] && pass "excel output file exists" || fail "excel output file missing"
else
  warn "openpyxl not installed, skipping excel export runtime check"
fi

echo "\nAll feature checks completed."
