#!/bin/bash
set -e

PIDS=()

cleanup() {
    echo "Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait
    exit 0
}
trap cleanup SIGTERM SIGINT

# 1. Start MagiC server
magic serve &
PIDS+=($!)

# 2. Wait for server to be ready (max 30s)
echo "Waiting for MagiC server..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:${MAGIC_PORT:-8080}/health > /dev/null 2>&1; then
        echo "MagiC server ready"
        break
    fi
    [ "$i" -eq 30 ] && { echo "Server failed to start"; exit 1; }
    sleep 1
done

# 3. Start all workers
for w in workers/*.py; do
    python "$w" &
    PIDS+=($!)
done

# 4. Wait for workers to register
sleep 2
echo "All workers started"

# 5. Start Streamlit (foreground)
exec streamlit run app.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0
