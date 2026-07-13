# OATS Biobattery RF Readout Platform

Containerized RF readout platform for the Purdue OATS / IoT4Ag
biobattery project.

## Current architecture

Raspberry Pi:

1. SDR acquisition service using a USRP B200mini and GNU Radio
2. NATS server with JetStream
3. Redpanda Connect transformer

Future deployment targets include the Polaris field computer and
the campus server.

## Current NATS deployment

- Container runtime: Podman
- Service management: systemd through Quadlet
- NATS image: official NATS image
- Subjects:
  - `sdr.peaks`
  - `sdr.fft`
- JetStream stream: `BIOBATTERY`
- Stream storage limit: 200 GiB
- Server-wide JetStream file limit: 210 GiB
- Persistent JetStream path:
  `/var/lib/oats/nats/jetstream`

## Repository layout

- `containers/`: source files for custom container images
- `config/`: machine-specific service configuration
- `quadlet/`: systemd/Podman Quadlet definitions
- `scripts/`: deployment and validation scripts
- `docs/`: architecture and operating documentation
- `.github/workflows/`: GitHub Actions CI workflows

## Security

Do not commit database credentials, NATS credentials, private keys,
runtime data, FFT captures, or JetStream storage.
