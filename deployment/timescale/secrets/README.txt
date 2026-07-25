Create these Podman secrets before deployment:

- timescale_biobatt_password
  Used by TimescaleDB as POSTGRES_PASSWORD.

- rpc_tsdb_biobatt
  Used by Redpanda as POSTGRES_DSN.

Do not commit real passwords or secret files.
