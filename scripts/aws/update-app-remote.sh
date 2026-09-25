#!/usr/bin/env bash
set -Eeuo pipefail

# Invoked as root over a verified SSH connection. Arguments contain no secrets.
if [ "$#" -ne 3 ] || ! [[ "$1" =~ ^/home/ubuntu/\.m7-update-[A-Za-z0-9]+$ ]] \
  || ! [[ "$2" =~ ^[a-f0-9]{40}$ && "$3" =~ ^[a-f0-9]{40}$ ]]; then
  echo 'Invalid update arguments.' >&2
  exit 64
fi
stage=$1
backend_tag=$2
frontend_tag=$3
backup=
compose=/opt/m7/compose.prod.yml
deploy=/etc/m7/deploy.env
runtime=/etc/m7/runtime.env
agent=/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
active_agent=/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/file_amazon-cloudwatch-agent.json
services=(rabbitmq backend frontend scheduler publisher evaluator notifier)

cleanup_stage() {
  rm -f -- "$stage/compose.prod.yml" "$stage/runtime.env" "$stage/cloudwatch-agent.json" "$stage/update-app-remote.sh"
  rmdir -- "$stage" 2>/dev/null || true
}
rollback() {
  status=$?
  trap - ERR
  echo 'Update failed; restoring prior Compose, deploy.env and runtime.env.' >&2
  install -o root -g root -m 0644 "$backup/compose.prod.yml" "$compose"
  install -o root -g root -m 0600 "$backup/deploy.env" "$deploy"
  install -o root -g root -m 0600 "$backup/runtime.env" "$runtime"
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

for file in compose.prod.yml runtime.env cloudwatch-agent.json update-app-remote.sh; do
  test -f "$stage/$file" || { echo 'Update stage is incomplete.' >&2; exit 64; }
done
grep -Eq '^BACKEND_IMAGE_TAG=[a-f0-9]{40}$' "$deploy" || { echo 'Existing backend tag is invalid.' >&2; exit 64; }
grep -Eq '^FRONTEND_IMAGE_TAG=[a-f0-9]{40}$' "$deploy" || { echo 'Existing frontend tag is invalid.' >&2; exit 64; }
if grep -Eq '^[[:space:]]*(export[[:space:]]+)?AWS_[A-Za-z0-9_]*[[:space:]]*=' "$stage/runtime.env"; then
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
install -o root -g root -m 0600 "$stage/runtime.env" "$runtime"
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
    api = services["backend"]["environment"]
    broker = services["rabbitmq"]["environment"]
    url = urlsplit(api["RABBITMQ_URL"])
    valid = (api["ALERT_REPOSITORY_MODE"] == "database"
             and api["ALERT_SCHEDULE_SOURCE"] == "database"
             and bool(api["DATABASE_URL"] or api["SUPABASE_DATABASE_URL"])
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
echo "Update healthy. Root-only backup: $backup"
