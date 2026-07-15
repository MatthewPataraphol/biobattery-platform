#!/bin/bash
set -euo pipefail

DISPLAY_VALUE="${1:-}"

if [[ ! "${DISPLAY_VALUE}" =~ ^:[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Invalid DISPLAY value: ${DISPLAY_VALUE}" >&2
    exit 1
fi

IMAGE="ghcr.io/matthewpataraphol/biobattery-sdr:main"
CONTAINER="oats-sdr"

# Remove an earlier container if it exists.
podman rm -f "${CONTAINER}" >/dev/null 2>&1 || true

exec podman run -d \
    --name "${CONTAINER}" \
    --network oats-net \
    --privileged \
    -e DISPLAY="${DISPLAY_VALUE}" \
    -e NATS_URL=nats://oats-nats:4222 \
    -e OATS_DATA_DIR=/data \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /usr/share/uhd/4.8.0/images:/usr/share/uhd/4.8.0/images:ro \
    -v /var/lib/oats/sdr/data:/data \
    "${IMAGE}"
