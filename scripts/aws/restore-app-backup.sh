#!/usr/bin/env bash
set -Eeuo pipefail

# Run as root on the EC2. The argument is the backup path printed by update-app.
if [ "$#" -ne 1 ] || ! [[ "$1" =~ ^/etc/m7/backups/update-[A-Za-z0-9]{8}$ ]]; then
  echo 'Expected one reviewed update backup path.' >&2
  exit 64
fi
backup=$1
compose=/opt/m7/compose.prod.yml
deploy=/etc/m7/deploy.env
runtime=/etc/m7/runtime.env
agent=/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
wrapper=/usr/local/bin/m7-compose-up
for name in compose.prod.yml deploy.env runtime.env cloudwatch-agent.json m7-compose-up.sh; do
  test -f "$backup/$name" || { echo "Backup is incomplete: $name" >&2; exit 64; }
done
test "$(stat -c '%U:%G:%a' "$backup")" = root:root:700 || {
  echo 'Backup permissions are unsafe.' >&2
  exit 64
}

current=$(mktemp -d /etc/m7/backups/pre-restore-XXXXXXXX)
chmod 0700 "$current"
install -o root -g root -m 0644 "$compose" "$current/compose.prod.yml"
install -o root -g root -m 0600 "$deploy" "$current/deploy.env"
install -o root -g root -m 0600 "$runtime" "$current/runtime.env"
install -o root -g root -m 0644 "$agent" "$current/cloudwatch-agent.json"
install -o root -g root -m 0750 "$wrapper" "$current/m7-compose-up.sh"

restore_files() {
  local source=$1
  install -o root -g root -m 0644 "$source/compose.prod.yml" "$compose"
  install -o root -g root -m 0600 "$source/deploy.env" "$deploy"
  install -o root -g root -m 0600 "$source/runtime.env" "$runtime"
  install -o root -g root -m 0644 "$source/cloudwatch-agent.json" "$agent"
  install -o root -g root -m 0750 "$source/m7-compose-up.sh" "$wrapper"
}

on_error() {
  local status=$?
  trap - ERR
  echo 'Restore failed; recovering the configuration from before this attempt.' >&2
  restore_files "$current"
  /usr/local/bin/m7-compose up -d --no-build --remove-orphans --wait --wait-timeout 240 >/dev/null 2>&1 || true
  echo "Pre-restore files preserved at $current; verify container health." >&2
  exit "$status"
}
trap on_error ERR

restore_files "$backup"
/usr/local/bin/m7-compose pull backend frontend rabbitmq >/dev/null
/usr/local/bin/m7-compose up -d --no-build --remove-orphans --wait --wait-timeout 240 >/dev/null
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c "file:$agent" -s >/dev/null
curl --fail --silent --show-error --output /dev/null http://127.0.0.1:80/health
echo "Backup restored and frontend healthy. Pre-restore configuration: $current"
