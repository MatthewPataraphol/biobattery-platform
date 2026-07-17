# OATS Biobattery Deployment

Each service directory contains its Quadlet container definition,
persistent volume definitions, configuration templates, and credential
placeholders.

- nats/: NATS server, JetStream volume, and NATS configuration
- redpanda/: Redpanda Connect pipeline template and transformer YAML files
- timescale/: local TimescaleDB container and persistent data volume

Real credentials, NATS .creds files, passwords, and runtime data must not
be committed to Git.
