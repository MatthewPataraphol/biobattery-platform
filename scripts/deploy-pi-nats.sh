#!/bin/bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
    echo "Run this script with sudo." >&2
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

install -d -m 0755 /etc/oats/nats
install -d -m 0755 /var/lib/oats/nats/jetstream
install -d -m 0755 /etc/containers/systemd

install -m 0644 \
    "${REPO_ROOT}/config/pi/nats/nats-server.conf" \
    /etc/oats/nats/nats-server.conf

install -m 0644 \
    "${REPO_ROOT}/quadlet/pi/oats.network" \
    /etc/containers/systemd/oats.network

install -m 0644 \
    "${REPO_ROOT}/quadlet/pi/oats-nats.container" \
    /etc/containers/systemd/oats-nats.container

systemctl daemon-reload
systemctl restart oats-nats.service

echo
systemctl --no-pager --full status oats-nats.service
