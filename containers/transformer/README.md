# Transformer Container

This container consumes SDR data from NATS JetStream and transforms it into
other formats.

Current backend:
- Redpanda Connect

Outputs:
- JSONL (development)
- TimescaleDB (future)

Consumes:
- sdr.peaks
- sdr.fft
