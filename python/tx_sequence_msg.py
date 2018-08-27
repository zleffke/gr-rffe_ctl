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

from daemon_interface import *

class tx_sequence_msg(gr.basic_block):
    """
    docstring for block tx_sequence_msg
    """
    def __init__(self, ip="0.0.0.0", port=8000):
        gr.basic_block.__init__(self,
            name="tx_sequence_msg",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern('in'))
        self.message_port_register_in(pmt.intern('in_d'))
        self.message_port_register_out(pmt.intern('out'))
        self.message_port_register_out(pmt.intern('out_d'))

        self.set_msg_handler(pmt.intern('in'), self._handle_msg_data)
        self.set_msg_handler(pmt.intern('in'), self._handle_msg_ctl)
        
        self.connected = False


    def _utc_ts(self):
        return str(date.utcnow()) + " UTC | "

    def _handle_msg_in(self, msg_pmt):
        self.message_port_pub(pmt.intern('out'), msg_pmt)
