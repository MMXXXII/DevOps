#!/usr/bin/env bash

set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_ROOT="${DEPLOY_ROOT:-$HOME/my-fastapi-deploy}"
VENV_DIR="$DEPLOY_ROOT/venv"
PID_FILE="$DEPLOY_ROOT/app.pid"
LOG_FILE="$DEPLOY_ROOT/app.log"
APP_PORT="${APP_PORT:-8000}"

mkdir -p "$DEPLOY_ROOT"

if [[ -f "$PID_FILE" ]]; then
    OLD_PID="$(tr -cd '0-9' < "$PID_FILE")"

    if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
        kill "$OLD_PID"

        for _attempt in {1..10}; do
            if ! kill -0 "$OLD_PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done

        if kill -0 "$OLD_PID" 2>/dev/null; then
            exit 1
        fi
    fi
fi

rsync -a \
    --exclude ".git/" \
    --exclude ".venv/" \
    --exclude "__pycache__/" \
    --exclude "*.db" \
    "$SOURCE_DIR/" "$DEPLOY_ROOT/"

cd "$DEPLOY_ROOT"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

JENKINS_NODE_COOKIE="fastapi-app-service" \
nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app \
    --host 127.0.0.1 \
    --port "$APP_PORT" \
    >> "$LOG_FILE" 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"