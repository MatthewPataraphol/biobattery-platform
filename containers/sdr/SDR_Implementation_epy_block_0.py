"""
OATS B200mini Peak Detector + JSONL Logger + NATS Publisher

Input:
    float32 vector of FFT power values from:
    UHD Source -> Stream to Vector -> FFT -> Complex to Mag^2

Output:
    None

This block:
    - averages the power spectrum
    - searches for strongest peak from min_freq to max_freq
    - estimates noise floor and SNR
    - prints results to terminal
    - saves one JSON object per line to a .jsonl file
    - publishes the same JSON object to NATS
"""

import os
import json
import time
import numpy as np
from gnuradio import gr

try:
    from pynats2 import NATSClient
except Exception:
    NATSClient = None


class blk(gr.sync_block):
    def __init__(
        self,
        center_freq=209e6,
        samp_rate=10e6,
        fft_size=2048,
        min_freq=205e6,
        max_freq=213e6,
        avg_alpha=0.1,
        log_interval=0.5,
        snr_threshold_db=6.0,
        log_dir="/home/iot4ag/sdr/GNUradio_files/data",
        source_name="b200mini",
        publish_nats=True,
        nats_server="nats://localhost:4222",
        nats_subject="sdr.peaks",
    ):
        gr.sync_block.__init__(
            self,
            name="OATS Peak Detector NATS",
            in_sig=[(np.float32, int(fft_size))],
            out_sig=None,
        )

        self.center_freq = float(center_freq)
        self.samp_rate = float(samp_rate)
        self.fft_size = int(fft_size)
        self.min_freq = float(min_freq)
        self.max_freq = float(max_freq)
        self.avg_alpha = float(avg_alpha)
        self.log_interval = float(log_interval)
        self.snr_threshold_db = float(snr_threshold_db)
        self.log_dir = str(log_dir)
        self.source_name = str(source_name)

        self.publish_nats = bool(publish_nats)
        self.nats_server = str(nats_server)
        self.nats_subject = str(nats_subject)
        self.nc = None
        self.nats_connected = False

        self.avg_power = None
        self.last_log_time = 0.0

        os.makedirs(self.log_dir, exist_ok=True)

        date_str = time.strftime("%Y%m%d")
        self.log_path = os.path.join(
            self.log_dir,
            f"b200mini_peak_log_{date_str}.jsonl"
        )

        # This assumes FFT block has Shift: Yes
        self.freqs = np.linspace(
            self.center_freq - self.samp_rate / 2.0,
            self.center_freq + self.samp_rate / 2.0,
            self.fft_size,
            endpoint=False,
        )

        self.search_mask = (
            (self.freqs >= self.min_freq)
            & (self.freqs <= self.max_freq)
        )

        if not np.any(self.search_mask):
            raise ValueError("Search range does not overlap FFT frequency range.")

        print(f"[OATS] JSONL logging to: {self.log_path}", flush=True)
        print(
            f"[OATS] Search range: {self.min_freq/1e6:.3f} MHz to {self.max_freq/1e6:.3f} MHz",
            flush=True,
        )

        if self.publish_nats:
            self._connect_nats()

    def _connect_nats(self):
        if NATSClient is None:
            print("[OATS] pynats2 is not installed. NATS publishing disabled.", flush=True)
            self.nats_connected = False
            return

        try:
            self.nc = NATSClient(self.nats_server, socket_timeout=2)
            self.nc.connect()
            self.nats_connected = True
            print(
                f"[OATS] Connected to NATS: {self.nats_server}, subject: {self.nats_subject}",
                flush=True,
            )
        except Exception as e:
            self.nats_connected = False
            print(f"[OATS] Could not connect to NATS: {e}", flush=True)

    def _publish_nats(self, json_dump):
        if not self.publish_nats:
            return

        if not self.nats_connected:
            self._connect_nats()

        if not self.nats_connected:
            return

        try:
            self.nc.publish(subject=self.nats_subject, payload=json_dump)
        except Exception as e:
            self.nats_connected = False
            print(f"[OATS] NATS publish failed: {e}", flush=True)

    def work(self, input_items, output_items):
        spectra = input_items[0]

        for power in spectra:
            # Prevent log10(0)
            power = np.maximum(power, 1e-20)

            # Exponential moving average of power spectrum
            if self.avg_power is None:
                self.avg_power = power.copy()
            else:
                self.avg_power = (
                    self.avg_alpha * power
                    + (1.0 - self.avg_alpha) * self.avg_power
                )

            now = time.time()

            # Only print/log/publish every log_interval seconds
            if now - self.last_log_time < self.log_interval:
                continue

            self.last_log_time = now

            search_power = self.avg_power[self.search_mask]
            search_freqs = self.freqs[self.search_mask]

            peak_idx = int(np.argmax(search_power))
            peak_freq_hz = float(search_freqs[peak_idx])

            search_power_db = 10.0 * np.log10(np.maximum(search_power, 1e-20))
            peak_power_db = float(search_power_db[peak_idx])
            noise_floor_db = float(np.median(search_power_db))
            snr_db = float(peak_power_db - noise_floor_db)

            detected = bool(snr_db >= self.snr_threshold_db)

            record = {
                "source": self.source_name,
                "timestamp_unix": now,
                "timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S"),
                "center_freq_hz": self.center_freq,
                "sample_rate_hz": self.samp_rate,
                "fft_size": self.fft_size,
                "min_freq_hz": self.min_freq,
                "max_freq_hz": self.max_freq,
                "avg_alpha": self.avg_alpha,
                "peak_freq_hz": peak_freq_hz,
                "peak_freq_mhz": peak_freq_hz / 1e6,
                "peak_power_db_relative": peak_power_db,
                "noise_floor_db_relative": noise_floor_db,
                "snr_db": snr_db,
                "snr_threshold_db": self.snr_threshold_db,
                "detected": detected,
            }

            json_dump = json.dumps(record)

            print(
                "Peak: {:.6f} MHz | Power: {:.1f} dB rel | Noise: {:.1f} dB rel | SNR: {:.1f} dB | Detected: {}".format(
                    record["peak_freq_mhz"],
                    peak_power_db,
                    noise_floor_db,
                    snr_db,
                    detected,
                ),
                flush=True,
            )

            # Local backup log
            with open(self.log_path, "a") as f:
                f.write(json_dump + "\n")

            # NATS publish
            self._publish_nats(json_dump)
            
        return len(input_items[0])
        
    def stop(self):
        print("[OATS] Stopping block and closing NATS connection...", flush=True)

        try:
            if self.nc is not None:
                self.nc.close()
        except Exception as e:
            print(f"[OATS] Error closing NATS: {e}", flush=True)

        self.nats_connected = False
        return True
