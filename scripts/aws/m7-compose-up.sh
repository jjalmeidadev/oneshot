#!/usr/bin/env bash
set -Eeuo pipefail

runtime=/etc/m7/runtime.env
services=(rabbitmq backend frontend scheduler publisher evaluator notifier delivery sharepoint-publisher sharepoint-consumer)

if grep -Eq '^[[:space:]]*(export[[:space:]]+)?AWS_[A-Za-z0-9_]*[[:space:]]*=' "$runtime"; then
  echo 'Runtime configuration must not contain AWS_* assignments.' >&2
  exit 64
fi
for name in GEMINI_API_KEY AZURE_SPEECH_KEY AZURE_SPEECH_TIMEOUT_SECONDS AZURE_SPEECH_MAX_ATTEMPTS AUDIO_SIMULATED_IDENTITIES REPORT_SIMULATED_IDENTITIES ALERT_CONFIRMATION_SECRET RABBITMQ_USER RABBITMQ_PASSWORD RABBITMQ_URL DATABASE_POOL_MAX_SIZE DATABASE_STATEMENT_TIMEOUT_MS SUPABASE_URL NOTIFICATION_CALLBACK_SECRET SHAREPOINT_WEBHOOK_CLIENT_STATE; do
  if ! grep -Eq "^$name=.+" "$runtime"; then
    echo "Runtime configuration is missing a required variable: $name" >&2
    exit 64
  fi
done
if ! grep -Eq '^(SUPABASE_PUBLISHABLE_KEY|SUPABASE_ANON_KEY)=.+' "$runtime"; then
  echo 'Runtime configuration needs a public Supabase API key.' >&2
  exit 64
fi
if ! grep -Eq '^AZURE_SPEECH_RESOURCE=.+|^AZURE_SPEECH_ENDPOINT=.+' "$runtime"; then
  echo 'Runtime configuration needs AZURE_SPEECH_RESOURCE or AZURE_SPEECH_ENDPOINT.' >&2
  exit 64
fi
if ! grep -Eq '^(DATABASE_URL|SUPABASE_DATABASE_URL)=.+' "$runtime"; then
  echo 'Runtime configuration needs DATABASE_URL or SUPABASE_DATABASE_URL.' >&2
  exit 64
fi

# The rendered Compose contains secrets. Validate it through a pipe only.
if ! /usr/local/bin/m7-compose config --format json | python3 -c '
import json, sys
from urllib.parse import unquote, urlsplit
try:
    services = json.load(sys.stdin)["services"]
    expected = {"rabbitmq", "backend", "frontend", "scheduler", "publisher", "evaluator", "notifier", "delivery", "sharepoint-publisher", "sharepoint-consumer"}
    api = services["backend"]["environment"]
    broker = services["rabbitmq"]["environment"]
    url = urlsplit(api["RABBITMQ_URL"])
    valid = (expected.issubset(services)
             and bool(api["SUPABASE_URL"])
             and bool(api["SUPABASE_PUBLISHABLE_KEY"] or api["SUPABASE_ANON_KEY"])
             and bool(api["NOTIFICATION_CALLBACK_SECRET"])
             and bool(api["SHAREPOINT_WEBHOOK_CLIENT_STATE"])
             and url.scheme == "amqp" and url.hostname == "rabbitmq"
             and url.port == 5672
             and broker["RABBITMQ_DEFAULT_USER"] != "guest"
             and unquote(url.username or "") == broker["RABBITMQ_DEFAULT_USER"]
             and unquote(url.password or "") == broker["RABBITMQ_DEFAULT_PASS"])
except (KeyError, ValueError, TypeError, json.JSONDecodeError):
    valid = False
sys.exit(0 if valid else 1)
'; then
  echo 'Compose runtime validation failed.' >&2
  exit 64
fi

/usr/local/bin/m7-compose up -d --no-build --wait --wait-timeout 240 "${services[@]}"
for service in "${services[@]}"; do
  systemctl enable "m7-container-logs@$service.service"
  systemctl restart "m7-container-logs@$service.service"
done
