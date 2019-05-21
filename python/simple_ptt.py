#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2018 Zach, KJ4QLP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import numpy
from gnuradio import gr
import pmt, datetime, time

class simple_ptt(gr.sync_block):
    """
    docstring for block simple_ptt
    """
    def __init__(self, delay = 1000, samp_rate = 0):
        gr.sync_block.__init__(self,
            name="simple_ptt",
            in_sig=[numpy.complex64],
            out_sig=[numpy.complex64])
        self.delay=delay
        self.samp_rate = samp_rate
        self.STATE = 'RX'
        self.message_port_register_in(pmt.intern('trigger'))
        self.set_msg_handler(pmt.intern('trigger'), self.handler)
        self.message_port_register_out(pmt.intern('ptt_out'))

        self.sample_ts = datetime.datetime.utcnow()
        self.samp_sum = 0

    def work(self, input_items, output_items):
        self.sample_ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.samp_sum += len(input_items[0])
        print "{:s} | Sample!!, {:d}, {:d}".format(self.sample_ts, len(input_items[0]), self.samp_sum)
        self.message_port_pub(pmt.intern('ptt_out'),
                              pmt.cons(pmt.intern("trigger"),
                              pmt.intern(self.sample_ts)))
        #time.sleep(self.delay/1000.0)
        output_items[0][:] = (input_items[0])
        return len(output_items[0])

    def handler(self,pdu):
        ts = datetime.datetime.utcnow()
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        print "{:s} | Trigger!".format(ts_str)
        ax25_raw = pmt.to_python(pmt.cdr(pdu))
        len_frame = len(ax25_raw) + 128
        samp_len = int(len_frame*self.samp_rate)
        print "{:s} | Trigger! | Length: {:d} | Samp Len: {:d}".format(ts_str, len_frame, samp_len)

    def set_delay(self, delay):
        self.delay = delay

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
