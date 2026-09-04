#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import SDR_Implementation_epy_block_0 as epy_block_0  # embedded python block
import SDR_Implementation_epy_block_1 as epy_block_1  # embedded python block
import os
import sip
import threading



class SDR_Implementation(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "SDR_Implementation")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.snr_threshold_db = snr_threshold_db = float(os.getenv("SDR_SNR_THRESHOLD_DB", "10"))
        self.samp_rate = samp_rate = float(os.getenv("SDR_SAMPLE_RATE", "14e6"))
        self.publish_interval = publish_interval = float(os.getenv("SDR_PUBLISH_INTERVAL", "0.01"))
        self.min_freq = min_freq = float(os.getenv("SDR_MIN_FREQ", "200e6"))
        self.max_freq = max_freq = float(os.getenv("SDR_MAX_FREQ", "214e6"))
        self.fft_size = fft_size = int(os.getenv("SDR_FFT_SIZE", "2048"))
        self.center_freq = center_freq = float(os.getenv("SDR_CENTER_FREQ", "207e6"))
        self.avg_alpha = avg_alpha = float(os.getenv("SDR_AVG_ALPHA", "0.1"))

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.uhd_usrp_source_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_gain(30, 0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.epy_block_1 = epy_block_1.blk(center_freq=center_freq, samp_rate=samp_rate, fft_size=fft_size, nats_server="nats://localhost:4222", nats_subject="sdr.fft", publish_nats=True, source_name="sdr:88a29ed9fb92", avg_alpha=avg_alpha, publish_interval=publish_interval)
        self.epy_block_0 = epy_block_0.blk(center_freq=center_freq, samp_rate=samp_rate, fft_size=fft_size, min_freq=min_freq, max_freq=max_freq, avg_alpha=avg_alpha, log_interval=publish_interval, snr_threshold_db=snr_threshold_db, log_dir="/home/iot4ag/sdr/GNUradio_files/data", source_name='sdr:88a29ed9fb92', publish_nats=True, nats_server="nats://localhost:4222", nats_subject="sdr.peaks")
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.epy_block_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "SDR_Implementation")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_snr_threshold_db(self):
        return self.snr_threshold_db

    def set_snr_threshold_db(self, snr_threshold_db):
        self.snr_threshold_db = snr_threshold_db
        self.epy_block_0.snr_threshold_db = self.snr_threshold_db

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.epy_block_0.samp_rate = self.samp_rate
        self.epy_block_1.samp_rate = self.samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_publish_interval(self):
        return self.publish_interval

    def set_publish_interval(self, publish_interval):
        self.publish_interval = publish_interval
        self.epy_block_0.log_interval = self.publish_interval
        self.epy_block_1.publish_interval = self.publish_interval

    def get_min_freq(self):
        return self.min_freq

    def set_min_freq(self, min_freq):
        self.min_freq = min_freq
        self.epy_block_0.min_freq = self.min_freq

    def get_max_freq(self):
        return self.max_freq

    def set_max_freq(self, max_freq):
        self.max_freq = max_freq
        self.epy_block_0.max_freq = self.max_freq

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.epy_block_0.fft_size = self.fft_size
        self.epy_block_1.fft_size = self.fft_size
        self.fft_vxx_0.set_window(window.blackmanharris(self.fft_size))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.epy_block_0.center_freq = self.center_freq
        self.epy_block_1.center_freq = self.center_freq
        self.qtgui_freq_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.center_freq, 0)

    def get_avg_alpha(self):
        return self.avg_alpha

    def set_avg_alpha(self, avg_alpha):
        self.avg_alpha = avg_alpha
        self.epy_block_0.avg_alpha = self.avg_alpha
        self.epy_block_1.avg_alpha = self.avg_alpha




def main(top_block_cls=SDR_Implementation, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
