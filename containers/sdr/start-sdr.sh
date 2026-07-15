#!/bin/bash
set -euo pipefail

export UHD_IMAGES_DIR="${UHD_IMAGES_DIR:-/usr/share/uhd/4.8.0/images}"
export NATS_URL="${NATS_URL:-nats://oats-nats:4222}"
export OATS_DATA_DIR="${OATS_DATA_DIR:-/data}"
export QT_X11_NO_MITSHM=1
export PYTHONUNBUFFERED=1

mkdir -p "${OATS_DATA_DIR}"

echo "[OATS SDR] DISPLAY=${DISPLAY:-not-set}"
echo "[OATS SDR] UHD_IMAGES_DIR=${UHD_IMAGES_DIR}"
echo "[OATS SDR] NATS_URL=${NATS_URL}"
echo "[OATS SDR] OATS_DATA_DIR=${OATS_DATA_DIR}"
echo "[OATS SDR] Waiting for B200mini..."

until uhd_find_devices 2>&1 | grep -Eq 'B200|B200mini|B2'; do
    echo "[OATS SDR] B200mini not detected; retrying in 5 seconds."
    sleep 5
done

echo "[OATS SDR] B200mini detected."
echo "[OATS SDR] Starting GNU Radio GUI flowgraph."

cd /opt/oats
exec python3 /opt/oats/SDR_Implementation.py
