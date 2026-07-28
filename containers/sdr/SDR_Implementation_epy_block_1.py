"""
Full FFT NATS Publisher for OATS/B200mini debug streaming.

Input:
    float32 vector of FFT power values after:
    FFT -> Complex to Mag^2

Output:
    None

This block:
    - averages the full FFT power spectrum internally
    - publishes the averaged full FFT vector to NATS at a controlled interval
    - uses base64-encoded float32 data
"""

import json
import time
import base64
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
        nats_server="nats://localhost:4222",
        nats_subject="sdr.fft",
        publish_nats=True,
        source_name="b200mini",
        avg_alpha=0.1,
        publish_interval=0.01,
    ):
        gr.sync_block.__init__(
            self,
            name="Full FFT NATS Publisher",
            in_sig=[(np.float32, int(fft_size))],
            out_sig=None,
        )

        self.center_freq = float(center_freq)
        self.samp_rate = float(samp_rate)
        self.fft_size = int(fft_size)
        self.nats_server = str(nats_server)
        self.nats_subject = str(nats_subject)
        self.publish_nats = bool(publish_nats)
        self.source_name = str(source_name)
        self.avg_alpha = float(avg_alpha)
        self.publish_interval = float(publish_interval)

        self.avg_power = None
        self.last_publish_time = 0.0

        self.nc = None
        self.nats_connected = False

        if self.publish_nats:
            self._connect_nats()

    def _connect_nats(self):
        if NATSClient is None:
            print("[FFT] pynats2 not installed. NATS disabled.", flush=True)
            return

        try:
            self.nc = NATSClient(self.nats_server, socket_timeout=2)
            self.nc.connect()
            self.nats_connected = True
            print(
                f"[FFT] Connected to NATS: {self.nats_server}, subject: {self.nats_subject}",
                flush=True,
            )
        except Exception as e:
            self.nats_connected = False
            print(f"[FFT] Could not connect to NATS: {e}", flush=True)

    def _publish(self, payload):
        if not self.publish_nats:
            return

        if not self.nats_connected:
            self._connect_nats()

        if not self.nats_connected:
            return

        try:
            self.nc.publish(subject=self.nats_subject, payload=payload)
        except Exception as e:
            self.nats_connected = False
            print(f"[FFT] NATS publish failed: {e}", flush=True)

    def work(self, input_items, output_items):
        spectra = input_items[0]

        for spectrum in spectra:
            spectrum = np.maximum(spectrum, 1e-20).astype(np.float32)

            # Internal exponential moving average
            if self.avg_power is None:
                self.avg_power = spectrum.copy()
            else:
                self.avg_power = (
                    self.avg_alpha * spectrum
                    + (1.0 - self.avg_alpha) * self.avg_power
                ).astype(np.float32)

            now = time.time()

            # Publish only every publish_interval seconds
            if now - self.last_publish_time < self.publish_interval:
                continue

            self.last_publish_time = now

            # Base64 encode averaged float32 power vector
            fft_b64 = base64.b64encode(self.avg_power.tobytes()).decode("utf-8")

            record = {
                "source": self.source_name,
                "timestamp_unix": now,
                "timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S"),
                "center_freq_hz": self.center_freq,
                "sample_rate_hz": self.samp_rate,
                "span_hz": self.samp_rate,
                "fft_size": self.fft_size,
                "avg_alpha": self.avg_alpha,
                "publish_interval": self.publish_interval,
                "data_type": "float32",
                "scale": "linear_power",
                "encoding": "base64",
                "fft_power_linear": fft_b64,
            }

            json_dump = json.dumps(record)
            self._publish(json_dump)

            print(
                f"[FFT] Published averaged FFT vector: {self.fft_size} bins to {self.nats_subject}",
                flush=True,
            )

        return len(input_items[0])
        
    def stop(self):
        print("[FFT] Stopping block and closing NATS connection...", flush=True)

        try:
            if self.nc is not None:
                self.nc.close()
        except Exception as e:
            print(f"[FFT] Error closing NATS: {e}", flush=True)

        self.nats_connected = False
        return True
