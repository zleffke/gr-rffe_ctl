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

class time_tag_to_pdu(gr.sync_block):
    """
    docstring for block time_tag_to_pdu
    """
    def __init__(self, tag_name):
        gr.sync_block.__init__(self,
            name="time_tag_to_pdu",
            in_sig=[numpy.complex64],
            out_sig=[])

        self.tag_name = tag_name
        self.message_port_register_out(pmt.intern("pdu"))

    def work(self, input_items, output_items):
        in0 = input_items[0]
        num_input_items = len(in0)
        return_value = num_input_items
        nread = self.nitems_read(0)

        tags = self.get_tags_in_window(0, 0, num_input_items)
        if len(tags) > 0:
            #print "Tags Detected"
            for t in tags:
                t_key = pmt.symbol_to_string(t.key)
                if t_key == self.tag_name:
                    t_val = pmt.to_python(t.value)
                    #print t, t_key, t_val
                    #print type(t_val[0])
                    #print type(t_val[1])
                    msg = {'sec':t_val[0], 'frac':t_val[1]}
                    #msg_str = "{:d} {:f}\n".format(t_val[0], t_val[1])

                    #ts = numpy.datetime64.fromtimestamp(t_val[0])
                    ts = numpy.datetime64(datetime.datetime.utcfromtimestamp(t_val[0]))
                    ts = ts + numpy.timedelta64(int(t_val[1]*1e9), 'ns')
                    #print type(ts), ts
                    ts_ns = numpy.datetime_as_string(ts) +"Z"
                    #print ts_ns
                    #ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    msg.update({'ts_str':ts_ns})
                    msg_str = json.dumps(msg)
                    print "Sent PTT: {:s}".format(msg_str)
                    #print ts_str
                    vector = pmt.init_u8vector(len(msg_str)+1, bytearray(msg_str +'\n'))
                    self.message_port_pub(pmt.intern('pdu'),
                                          pmt.cons(pmt.PMT_NIL,vector))

        return return_value
