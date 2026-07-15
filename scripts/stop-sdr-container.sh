#!/bin/bash
set -e

sudo podman rm -f oats-sdr 2>/dev/null || true
echo "OATS SDR container stopped."
