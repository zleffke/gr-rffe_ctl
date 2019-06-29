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
import pmt
import binascii
import datetime
import json
from gnuradio import gr

SEARCH = 0 #Search State, looking for SOB tag
DETECT = 1 #Detect state, have found SOB, looking for tx_time and eob tags

class tag_ptt_pdu(gr.sync_block):
    """
    docstring for block tag_ptt_pdu
    """
    def __init__(self, samp_rate, sob_key, eob_key, tx_time_key, ptt_mode):
        gr.sync_block.__init__(self,
            name="tag_ptt_pdu",
            in_sig=[numpy.complex64],
            out_sig=[])

        self.message_port_register_out(pmt.intern("ptt"))

        self.samp_rate      = samp_rate #sample rate, used to compute message duration
        self.uhd_sob_key    = sob_key   #start of burst key, usually 'sob', used by UHD
        self.uhd_eob_key    = eob_key   #end of burst key, usually 'eob', used by UHD
        self.uhd_tx_time_key= tx_time_key #tx_time key, usually 'tx_time', used by UHD, delays until
        self.ptt_mode       = ptt_mode

        self._init_ptt_msg()

    def _init_ptt_msg(self):
        self.sob_idx    = 0
        self.eob_idx    = 0
        self.burst_sec  = 0     #Burst duration in seconds, computed from sob and eob tags
        self.int_sec    = 0     #integer number of second, from tx_time
        self.frac_sec   = 0.0   #fractional number of seconds, from tx_time
        self.ptt_msg = {
            "uhd":{},
            "ptt_mode":self.ptt_mode
        }
        self.state = SEARCH

    def _update_msg_time(self, t):
        t_val = pmt.to_python(t.value)
        self.int_sec = t_val[0]
        self.frac_sec = t_val[1]
        #print self.state, self.int_sec, self.frac_sec
        ts = numpy.datetime64(datetime.datetime.utcfromtimestamp(self.int_sec))
        ts = ts + numpy.timedelta64(int(self.frac_sec*1e9), 'ns')
        ts_ns = numpy.datetime_as_string(ts) +"Z"
        self.ptt_msg['uhd'].update({
            'tx_sec':self.int_sec,
            'tx_frac':self.frac_sec,
            'tx_datetime64':ts_ns
        })

    def _compute_duration(self):
        burst_len = self.eob_idx - self.sob_idx
        burst_sec = burst_len / self.samp_rate
        #print self.state, burst_len, burst_sec
        #print "Burst Duration [s]", burst_sec
        self.ptt_msg.update({'burst_sec':burst_sec})


    def _emit_msg(self):
        ts_ptt = numpy.datetime64(datetime.datetime.utcnow())
        #ts_tx = numpy.datetime64(self.ptt_msg['uhd']['tx_datetime64'])
        #sec_remain = (ts_ptt - ts_tx).item()*1e-9
        ts_ns = numpy.datetime_as_string(ts_ptt) +"Z"
        #self.ptt_msg.update({'ptt_datetime':ts_ns, 'sec_remain':sec_remain})
        self.ptt_msg.update({'ptt_datetime':ts_ns})
        msg_str = json.dumps(self.ptt_msg)
        vector = pmt.init_u8vector(len(msg_str)+1, bytearray(msg_str +'\n'))
        self.message_port_pub(pmt.intern('ptt'),
                              pmt.cons(pmt.PMT_NIL,vector))
        print "Sent PTT: {:s}".format(msg_str)
        self._init_ptt_msg()

    def work(self, input_items, output_items):
        in0 = input_items[0]
        num_input_items = len(in0)
        return_value = num_input_items
        #nread = self.nitems_read(0)

        tags = self.get_tags_in_window(0, 0, num_input_items)
        if len(tags) > 0:
            #print "Tags Detected"
            for t in tags:
                t_key = pmt.symbol_to_string(t.key)
                t_val = pmt.to_python(t.value)
                t_offset = t.offset
                #print self.count, t_offset, t_key, t_val
                if self.state == SEARCH:
                    if t_key == self.uhd_sob_key: #Start of Burst
                        self.sob_idx = t.offset
                        print self.state, self.sob_idx
                        self.state = DETECT
                elif self.state == DETECT:
                    if t_key == self.uhd_tx_time_key: #time tag Detected
                        self._update_msg_time(t)
                    elif t_key == self.uhd_eob_key: #Start of Burst
                        self.eob_idx = t.offset
                        print self.state, self.sob_idx
                        self._compute_duration()
                        self._emit_msg()

        return return_value
