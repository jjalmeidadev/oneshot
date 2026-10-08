#!/usr/bin/env bash
set -Eeuo pipefail

# Invoked as root over a verified SSH connection. Arguments contain no secrets.
if [ "$#" -ne 4 ] || ! [[ "$1" =~ ^/home/ubuntu/\.m7-update-[A-Za-z0-9]+$ ]] \
  || ! [[ "$2" =~ ^[a-f0-9]{40}$ && "$3" =~ ^[a-f0-9]{40}$ ]] \
  || ! [[ "$4" =~ ^(full|overlay)$ ]]; then
  echo 'Invalid update arguments.' >&2
  exit 64
fi
stage=$1
backend_tag=$2
frontend_tag=$3
runtime_mode=$4
backup=
compose=/opt/m7/compose.prod.yml
deploy=/etc/m7/deploy.env
runtime=/etc/m7/runtime.env
agent=/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
active_agent=/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/file_amazon-cloudwatch-agent.json
wrapper=/usr/local/bin/m7-compose-up
restore_helper=/usr/local/bin/m7-restore-backup
services=(rabbitmq backend frontend scheduler publisher evaluator notifier delivery sharepoint-publisher sharepoint-consumer)

cleanup_stage() {
  rm -f -- "$stage/compose.prod.yml" "$stage/runtime.env" "$stage/runtime.overlay" "$stage/cloudwatch-agent.json" "$stage/update-app-remote.sh" "$stage/m7-compose-up.sh" "$stage/restore-app-backup.sh"
  rmdir -- "$stage" 2>/dev/null || true
}
rollback() {
  status=$?
  trap - ERR
  echo 'Update failed; restoring prior Compose, deploy.env and runtime.env.' >&2
  install -o root -g root -m 0644 "$backup/compose.prod.yml" "$compose"
  install -o root -g root -m 0600 "$backup/deploy.env" "$deploy"
  install -o root -g root -m 0600 "$backup/runtime.env" "$runtime"
  install -o root -g root -m 0750 "$backup/m7-compose-up.sh" "$wrapper"
  install -o root -g root -m 0644 "$backup/cloudwatch-agent.json" "$agent"
  restored_health=1
  /usr/local/bin/m7-compose up -d --no-build --remove-orphans --wait --wait-timeout 240 >/dev/null 2>&1 || restored_health=0
  /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c "file:$agent" -s >/dev/null 2>&1 || true
  curl --fail --silent --output /dev/null http://127.0.0.1:80/health || restored_health=0
  cleanup_stage
  if [ "$restored_health" -eq 1 ]; then
    echo "Prior configuration and health restored from $backup." >&2
  else
    echo "Prior files restored from $backup, but health is not confirmed; investigate before retrying." >&2
  fi
  exit "$status"
}

runtime_stage_file=runtime.env
if [ "$runtime_mode" = overlay ]; then runtime_stage_file=runtime.overlay; fi
for file in compose.prod.yml "$runtime_stage_file" cloudwatch-agent.json update-app-remote.sh m7-compose-up.sh restore-app-backup.sh; do
  test -f "$stage/$file" || { echo 'Update stage is incomplete.' >&2; exit 64; }
done
grep -Eq '^BACKEND_IMAGE_TAG=[a-f0-9]{40}$' "$deploy" || { echo 'Existing backend tag is invalid.' >&2; exit 64; }
grep -Eq '^FRONTEND_IMAGE_TAG=[a-f0-9]{40}$' "$deploy" || { echo 'Existing frontend tag is invalid.' >&2; exit 64; }
if grep -Eq '^[[:space:]]*(export[[:space:]]+)?AWS_[A-Za-z0-9_]*[[:space:]]*=' "$stage/$runtime_stage_file"; then
  echo 'Runtime must not contain AWS_* assignments.' >&2
  exit 64
fi
test "$(stat -c %a "$stage")" = 700 || { echo 'Update stage permissions are unsafe.' >&2; exit 64; }
install -d -o root -g root -m 0700 /etc/m7/backups
backup=$(mktemp -d /etc/m7/backups/update-XXXXXXXX)
chmod 0700 "$backup"
install -o root -g root -m 0644 "$compose" "$backup/compose.prod.yml"
install -o root -g root -m 0600 "$deploy" "$backup/deploy.env"
install -o root -g root -m 0600 "$runtime" "$backup/runtime.env"
install -o root -g root -m 0750 "$wrapper" "$backup/m7-compose-up.sh"
if test -f "$agent"; then
  install -o root -g root -m 0644 "$agent" "$backup/cloudwatch-agent.json"
elif test -f "$active_agent"; then
  install -o root -g root -m 0644 "$active_agent" "$backup/cloudwatch-agent.json"
else
  echo 'Existing CloudWatch Agent configuration is unavailable.' >&2
  exit 64
fi
trap rollback ERR
trap cleanup_stage EXIT

install -o root -g root -m 0644 "$stage/compose.prod.yml" "$compose"
if [ "$runtime_mode" = full ]; then
  install -o root -g root -m 0600 "$stage/runtime.env" "$runtime"
else
  python3 - "$runtime" "$stage/runtime.overlay" <<'PY'
import os
import sys
import tempfile
from pathlib import Path

runtime = Path(sys.argv[1])
overlay = Path(sys.argv[2])
allowed = {
    "SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY",
    "NOTIFICATION_CALLBACK_SECRET", "SHAREPOINT_WEBHOOK_CLIENT_STATE",
    "REPORT_CALLBACK_TOKEN", "GEMINI_API_KEY",
}
updates = {}
for line in overlay.read_text(encoding="utf-8").splitlines():
    if not line or line.startswith("#"):
        continue
    if "=" not in line:
        raise SystemExit("Invalid runtime overlay")
    key, value = line.split("=", 1)
    if key not in allowed or key in updates or not value.strip():
        raise SystemExit("Invalid runtime overlay")
    updates[key] = value
if not {"SUPABASE_URL", "NOTIFICATION_CALLBACK_SECRET", "SHAREPOINT_WEBHOOK_CLIENT_STATE", "GEMINI_API_KEY"}.issubset(updates):
    raise SystemExit("Incomplete runtime overlay")
if not (updates.get("SUPABASE_PUBLISHABLE_KEY") or updates.get("SUPABASE_ANON_KEY")):
    raise SystemExit("Public Supabase key missing")
original = runtime.read_text(encoding="utf-8").splitlines()
preserved = [line for line in original if line.split("=", 1)[0] not in updates]
fd, temp = tempfile.mkstemp(prefix="runtime-", dir=str(runtime.parent))
try:
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("\n".join(preserved + [f"{key}={value}" for key, value in updates.items()]) + "\n")
    os.chmod(temp, 0o600)
    os.replace(temp, runtime)
finally:
    if os.path.exists(temp):
        os.unlink(temp)
PY
fi
install -o root -g root -m 0750 "$stage/m7-compose-up.sh" "$wrapper"
install -o root -g root -m 0750 "$stage/restore-app-backup.sh" "$restore_helper"
sed -i "s/^BACKEND_IMAGE_TAG=.*/BACKEND_IMAGE_TAG=$backend_tag/" "$deploy"
sed -i "s/^FRONTEND_IMAGE_TAG=.*/FRONTEND_IMAGE_TAG=$frontend_tag/" "$deploy"
chown root:root "$deploy"
chmod 0600 "$deploy"
test "$(stat -c '%U:%G:%a' "$runtime")" = root:root:600

# Parse the rendered Compose in memory; neither its output nor secrets are logged.
/usr/local/bin/m7-compose config --format json 2>/dev/null | python3 -c '
import json, sys
from urllib.parse import unquote, urlsplit
try:
    services = json.load(sys.stdin)["services"]
    expected = {"rabbitmq", "backend", "frontend", "scheduler", "publisher", "evaluator", "notifier", "delivery", "sharepoint-publisher", "sharepoint-consumer"}
    api = services["backend"]["environment"]
    broker = services["rabbitmq"]["environment"]
    url = urlsplit(api["RABBITMQ_URL"])
    valid = (expected.issubset(services)
             and api["ALERT_REPOSITORY_MODE"] == "database"
             and api["ALERT_SCHEDULE_SOURCE"] == "database"
             and bool(api["DATABASE_URL"] or api["SUPABASE_DATABASE_URL"])
             and bool(api["SUPABASE_URL"])
             and bool(api["SUPABASE_PUBLISHABLE_KEY"] or api["SUPABASE_ANON_KEY"])
             and bool(api["NOTIFICATION_CALLBACK_SECRET"])
             and bool(api["SHAREPOINT_WEBHOOK_CLIENT_STATE"])
             and bool(api["ALERT_CONFIRMATION_SECRET"])
             and bool(broker["RABBITMQ_DEFAULT_USER"] and broker["RABBITMQ_DEFAULT_PASS"])
             and url.scheme == "amqp" and url.hostname == "rabbitmq"
             and url.port == 5672
             and broker["RABBITMQ_DEFAULT_USER"] != "guest"
             and unquote(url.username or "") == broker["RABBITMQ_DEFAULT_USER"]
             and unquote(url.password or "") == broker["RABBITMQ_DEFAULT_PASS"])
except (KeyError, ValueError, TypeError, json.JSONDecodeError):
    valid = False
sys.exit(0 if valid else 1)
'

sed 's/__STACK_NAME__/m7-g05-mvp/g' "$stage/cloudwatch-agent.json" > "$agent"
chmod 0644 "$agent"
export AWS_ECR_DISABLE_CACHE=true
/usr/local/bin/m7-compose pull backend frontend rabbitmq >/dev/null
/usr/local/bin/m7-compose up -d --no-build --wait --wait-timeout 240 "${services[@]}" >/dev/null
for service in "${services[@]}"; do
  systemctl enable "m7-container-logs@$service.service" >/dev/null
  systemctl restart "m7-container-logs@$service.service" >/dev/null
done
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c "file:$agent" -s >/dev/null
curl --fail --silent --show-error --output /dev/null http://127.0.0.1:80/health
for service in "${services[@]}"; do
  id=$(/usr/local/bin/m7-compose ps -q "$service")
  test -n "$id"
  test "$(docker inspect -f '{{.State.Running}}' "$id")" = true
done
backend_id=$(/usr/local/bin/m7-compose ps -q backend)
python3 - "$runtime" "$backend_id" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

runtime = dict(line.split("=", 1) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines() if "=" in line and not line.startswith("#"))
expected = runtime.get("GEMINI_API_KEY", "").strip().strip('"').strip("'")
actual = subprocess.run(
    ["docker", "inspect", "--format", "{{json .Config.Env}}", sys.argv[2]],
    check=True, capture_output=True, text=True,
)
container = dict(line.split("=", 1) for line in json.loads(actual.stdout) if "=" in line)
if not expected or container.get("GEMINI_API_KEY") != expected:
    raise SystemExit("Backend Gemini key does not match protected runtime")
PY
echo "Update healthy. Root-only backup: $backup"
