-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- SDR peak detections
CREATE TABLE IF NOT EXISTS sdr_peaks (
    time                    TIMESTAMPTZ      NOT NULL,
    source                  TEXT             NOT NULL,

    timestamp_unix          DOUBLE PRECISION,

    center_freq_hz          DOUBLE PRECISION,
    sample_rate_hz          DOUBLE PRECISION,
    fft_size                INTEGER,

    min_freq_hz             DOUBLE PRECISION,
    max_freq_hz             DOUBLE PRECISION,

    avg_alpha               DOUBLE PRECISION,

    peak_freq_hz            DOUBLE PRECISION,

    peak_power_db_relative  DOUBLE PRECISION,
    noise_floor_db_relative DOUBLE PRECISION,

    snr_db                  DOUBLE PRECISION,
    snr_threshold_db        DOUBLE PRECISION,

    detected                BOOLEAN          NOT NULL,

    raw_message             JSONB
);

-- Convert table into a Timescale hypertable
SELECT create_hypertable(
    'sdr_peaks',
    'time',
    if_not_exists => TRUE
);

-- Helpful index for queries
CREATE INDEX IF NOT EXISTS sdr_peaks_source_time_idx
ON sdr_peaks (source, time DESC);
