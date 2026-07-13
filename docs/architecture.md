# Architecture

## Raspberry Pi

B200mini
  -> SDR container
  -> NATS subjects `sdr.peaks` and `sdr.fft`
  -> NATS JetStream stream `BIOBATTERY`
  -> Redpanda Connect transformer
  -> central TimescaleDB

## Future routing

Raspberry Pi NATS
  -> NATS leafnode
  -> Polaris NATS
  -> NATS leafnode
  -> campus NATS

Machine-specific behavior is controlled by mounted configuration files.
Container images should remain reusable across deployment targets.
