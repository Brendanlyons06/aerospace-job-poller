#!/bin/bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_ROOT="${HOME}/Library/Application Support/AerospaceJobPoller"
RUNTIME_REPO="${RUNTIME_ROOT}/job-poller"
LAUNCH_AGENTS="${HOME}/Library/LaunchAgents"
LABEL="com.brendanlyons.aerospace-job-poller"
PLIST_SOURCE="${SOURCE_DIR}/launchd/${LABEL}.plist"
PLIST_INSTALLED="${LAUNCH_AGENTS}/${LABEL}.plist"
USER_ID="$(id -u)"

if [[ ! -f "${SOURCE_DIR}/.env" ]]; then
    echo "Missing ${SOURCE_DIR}/.env; configure notifications before deploying." >&2
    exit 1
fi

plutil -lint "${PLIST_SOURCE}"
install -d -m 700 "${RUNTIME_ROOT}" "${RUNTIME_REPO}" "${RUNTIME_ROOT}/logs" "${LAUNCH_AGENTS}"

# Code is replaced as one reviewed snapshot. Runtime state and secrets are
# preserved separately so a deploy cannot reset notification history.
rsync -a --delete \
    --exclude=.git \
    --exclude=.venv \
    --exclude=.env \
    --exclude=jobs.db \
    --exclude=logs \
    --exclude=__pycache__ \
    "${SOURCE_DIR}/" "${RUNTIME_REPO}/"

install -m 600 "${SOURCE_DIR}/.env" "${RUNTIME_REPO}/.env"
if [[ ! -f "${RUNTIME_REPO}/jobs.db" && -f "${SOURCE_DIR}/jobs.db" ]]; then
    install -m 600 "${SOURCE_DIR}/jobs.db" "${RUNTIME_REPO}/jobs.db"
fi

if [[ ! -x "${RUNTIME_ROOT}/.venv/bin/python" ]]; then
    /usr/bin/python3 -m venv "${RUNTIME_ROOT}/.venv"
fi
"${RUNTIME_ROOT}/.venv/bin/python" -m pip install -r "${RUNTIME_REPO}/requirements.txt"

install -m 600 "${PLIST_SOURCE}" "${PLIST_INSTALLED}"
launchctl bootout "gui/${USER_ID}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${USER_ID}" "${PLIST_INSTALLED}"

echo "Deployed ${LABEL}; scheduled every 30 minutes."
echo "Logs: ${RUNTIME_ROOT}/logs"
