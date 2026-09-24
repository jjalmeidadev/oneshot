#!/usr/bin/env bash
set -Eeuo pipefail

# CloudFormation substitutes only these non-secret stack values.
STACK_NAME="${AWS::StackName}"
AWS_REGION="${AWS::Region}"
ECR_REGISTRY_URI="${EcrRegistryUri}"
BACKEND_IMAGE_TAG="${BackendImageTag}"
FRONTEND_IMAGE_TAG="${FrontendImageTag}"

export DEBIAN_FRONTEND=noninteractive
export AWS_DEFAULT_REGION="$AWS_REGION"

install -d -m 0755 /etc/apt/keyrings
apt-get update
apt-get install -y ca-certificates curl gnupg logrotate rsyslog snapd
systemctl enable --now rsyslog

curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
ARCH="$(dpkg --print-architecture)"
. /etc/os-release
printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu %s stable\n' "$ARCH" "$VERSION_CODENAME" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin amazon-ecr-credential-helper
systemctl enable --now docker

# Ubuntu cloud images normally ship SSM Agent. Keep this idempotent fallback for images where it is absent.
if ! systemctl list-unit-files | grep -q '^snap.amazon-ssm-agent.amazon-ssm-agent.service'; then
  snap install amazon-ssm-agent --classic
fi
systemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service

CWA_DEB="/var/tmp/amazon-cloudwatch-agent.deb"
curl -fsSL "https://amazoncloudwatch-agent-$AWS_REGION.s3.$AWS_REGION.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb" -o "$CWA_DEB"
dpkg -i "$CWA_DEB"
rm -f "$CWA_DEB"

install -d -m 0750 /opt/m7 /etc/m7 /var/log/m7 /var/lib/m7/reports /var/lib/m7/notebooks /root/.docker
if [ ! -e /etc/m7/runtime.env ]; then
  install -m 0600 /dev/null /etc/m7/runtime.env
fi
chmod 0600 /etc/m7/runtime.env

# These base64 payloads contain only version-controlled, non-secret configuration.
printf '%s' '__COMPOSE_PROD_BASE64__' | base64 --decode > /opt/m7/compose.prod.yml
printf '%s' '__CLOUDWATCH_AGENT_BASE64__' | base64 --decode > /var/tmp/cloudwatch-agent.json
sed "s/__STACK_NAME__/$STACK_NAME/g" /var/tmp/cloudwatch-agent.json > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
chmod 0644 /opt/m7/compose.prod.yml /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
rm -f /var/tmp/cloudwatch-agent.json

cat > /etc/m7/deploy.env <<EOF
APP_BIND_ADDRESS=127.0.0.1
APP_PORT=80
BACKEND_IMAGE=$ECR_REGISTRY_URI/m7-g05-backend
BACKEND_IMAGE_TAG=$BACKEND_IMAGE_TAG
FRONTEND_IMAGE=$ECR_REGISTRY_URI/m7-g05-frontend
FRONTEND_IMAGE_TAG=$FRONTEND_IMAGE_TAG
NOTEBOOK_BIND_ADDRESS=127.0.0.1
NOTEBOOK_HOST_PORT=8888
EOF
chmod 0600 /etc/m7/deploy.env

printf '{"credHelpers":{"%s":"ecr-login"}}\n' "$ECR_REGISTRY_URI" > /root/.docker/config.json
chmod 0600 /root/.docker/config.json

cat > /usr/local/bin/m7-compose <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
export AWS_ECR_DISABLE_CACHE=true
exec docker compose --project-name m7 --project-directory /opt/m7 \
  --env-file /etc/m7/deploy.env --env-file /etc/m7/runtime.env \
  -f /opt/m7/compose.prod.yml "$@"
EOF
chmod 0750 /usr/local/bin/m7-compose

cat > /usr/local/bin/m7-compose-up <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
RUNTIME_FILE=/etc/m7/runtime.env
for name in GEMINI_API_KEY AZURE_SPEECH_KEY AZURE_SPEECH_TIMEOUT_SECONDS AZURE_SPEECH_MAX_ATTEMPTS AUDIO_SIMULATED_IDENTITIES REPORT_SIMULATED_IDENTITIES; do
  if ! grep -Eq "^$name=.+" "$RUNTIME_FILE"; then
    echo "Runtime configuration is missing a required variable: $name" >&2
    exit 64
  fi
done
if ! grep -Eq '^AZURE_SPEECH_RESOURCE=.+|^AZURE_SPEECH_ENDPOINT=.+' "$RUNTIME_FILE"; then
  echo 'Runtime configuration needs AZURE_SPEECH_RESOURCE or AZURE_SPEECH_ENDPOINT.' >&2
  exit 64
fi
/usr/local/bin/m7-compose up -d --no-build
systemctl enable m7-container-logs@backend.service m7-container-logs@frontend.service
systemctl restart m7-container-logs@backend.service m7-container-logs@frontend.service
EOF
chmod 0750 /usr/local/bin/m7-compose-up

cat > /usr/local/bin/m7-rollback <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
if [ "$#" -ne 2 ]; then
  echo 'Rollback needs backend and frontend full 40-character commit SHA tags.' >&2
  exit 64
fi
BACKEND_TAG="$1"
FRONTEND_TAG="$2"
if ! [[ "$BACKEND_TAG" =~ ^[a-fA-F0-9]{40}$ && "$FRONTEND_TAG" =~ ^[a-fA-F0-9]{40}$ ]]; then
  echo 'Rollback needs backend and frontend full 40-character commit SHA tags.' >&2
  exit 64
fi
for name in GEMINI_API_KEY AZURE_SPEECH_KEY AUDIO_SIMULATED_IDENTITIES REPORT_SIMULATED_IDENTITIES; do
  if ! grep -Eq "^$name=.+" /etc/m7/runtime.env; then
    echo 'Runtime configuration is not available.' >&2
    exit 64
  fi
done
BACKEND_IMAGE_TAG="$BACKEND_TAG" FRONTEND_IMAGE_TAG="$FRONTEND_TAG" /usr/local/bin/m7-compose pull backend frontend
sed -i "s/^BACKEND_IMAGE_TAG=.*/BACKEND_IMAGE_TAG=$BACKEND_TAG/" /etc/m7/deploy.env
sed -i "s/^FRONTEND_IMAGE_TAG=.*/FRONTEND_IMAGE_TAG=$FRONTEND_TAG/" /etc/m7/deploy.env
/usr/local/bin/m7-compose-up
EOF
chmod 0750 /usr/local/bin/m7-rollback

cat > /etc/systemd/system/m7-container-logs@.service <<'EOF'
[Unit]
Description=Forward M7/g05 %i container output to a bounded host log file
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker compose --project-name m7 --project-directory /opt/m7 --env-file /etc/m7/deploy.env --env-file /etc/m7/runtime.env -f /opt/m7/compose.prod.yml logs --no-color --follow %i
Restart=always
RestartSec=5
StandardOutput=append:/var/log/m7/%i.log
StandardError=append:/var/log/m7/%i.stderr.log
EOF

cat > /etc/logrotate.d/m7-containers <<'EOF'
/var/log/m7/*.log /var/log/m7/*.stderr.log {
  size 10M
  rotate 3
  compress
  missingok
  notifempty
  copytruncate
}
EOF

systemctl daemon-reload

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

docker volume create m7_report-artifacts >/dev/null
docker volume create m7_notebook-workspace >/dev/null

# The helper uses the EC2 instance profile and does not persist a docker login token.
export AWS_ECR_DISABLE_CACHE=true
/usr/local/bin/m7-compose pull backend frontend

echo 'Bootstrap completed. The notebook image was intentionally not pulled. Inject runtime configuration through SSM, then run m7-compose-up.'
