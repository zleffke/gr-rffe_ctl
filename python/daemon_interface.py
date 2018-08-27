#!/usr/bin/env python
#############################################
#   Title: RF Front End Daemon Interface    #
# Project: VTGS                             #
# Version: 0.0.0                            #
#    Date: Aug 2018                         #
#  Author: Zach Leffke, KJ4QLP              #
# Comment:                                  #
# -Interface to RF Front End Control Daemon #
# -Initial version for TCP CONNECTION       #
#############################################


class RFFE_Daemon_Interface_TCP(threading.Thread):
    def __init__ (self, ip="0.0.0.0", port=8000):
        threading.Thread.__init__(self, name = 'RFFE_INT_TCP')
        self.ip     = args.ip
        self.port   = args.port

        self.connected  = False
        self.tx_q       = Queue() #messages into thread
        self.rx_q       = Queue() #messages from thread

    def run(self):
        print "{:s} Started...".format(self.name)
        if (not self.connected):
            self._connect()
        while (not self._stop.isSet()):
            if self.connected:
                if (not self.tx_q.empty()): #Message for Relay Bank Received
                    msg = self.tx_q.get()
                    print '{:s} | {:s}'.format(self.name, msg)
                    if 'READ' in msg:
                        self.read_all_relays()
                        self.rx_q.put(self.state)

            else:
                time.sleep(5)
                self._connect()

            time.sleep(0.01) #Needed to throttle CPU

        sys.exit()

    def _connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect((self.ip, self.port))
                self.connected = True
                print self._utc_ts() + "Connected to Daemon..."
        except:
            print 'Failed to connect to RFFE Daemon: {:s}:{:d}'.format(self.ip, self.port))
            self.connected = False

    def _Handle_Connection_Exception(self,e):
        print

    def _utc_ts(self):
        return str(date.utcnow()) + " UTC | "
