#!/bin/bash
set -u

LOG_FILE="${HOME}/sdr-container-autostart.log"

{
    echo
    echo "===== $(date --iso-8601=seconds) ====="
    echo "[OATS SDR] XRDP startup wrapper"
    echo "[OATS SDR] DISPLAY=${DISPLAY:-not-set}"

    if [[ -z "${DISPLAY:-}" ]]; then
        echo "[OATS SDR] DISPLAY is not set; aborting."
        exit 1
    fi

    # Give the rootful GUI container permission to use this XRDP display.
    xhost +SI:localuser:root

    # Give the desktop and the B200mini a short time to settle.
    sleep 5

    sudo -n /usr/local/sbin/run-oats-sdr-container "${DISPLAY}"

    echo "[OATS SDR] Container launch requested."
} >> "${LOG_FILE}" 2>&1
