#!/usr/bin/python

# pypad_udp.py
#
# Send PAD updates via UDP
#
#   (C) Copyright 2018 Fred Gleason <fredg@paravelsystems.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

from __future__ import print_function

import sys
import socket
import ConfigParser
import PyPAD

def eprint(*args,**kwargs):
    print(*args,file=sys.stderr,**kwargs)

def ProcessPad(update):
    n=1
    while(True):
        section='Udp'+str(n)
        try:
            fmtstr=config.get(section,'FormatString')
            send_sock.sendto(update.resolvePadFields(fmtstr,int(config.get(section,'Encoding'))),
                             (config.get(section,'IpAddress'),int(config.get(section,'UdpPort'))))
            n=n+1
        except ConfigParser.NoSectionError:
            return

#
# Read Configuration
#
if len(sys.argv)>=2:
    fp=open(sys.argv[1])
    config=ConfigParser.ConfigParser()
    config.readfp(fp)
    fp.close()
else:
    eprint('pypad_udp.py: you must specify a configuration file')
    sys.exit(1)

#
# Create Send Socket
#
send_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

rcvr=PyPAD.Receiver()
rcvr.setCallback(ProcessPad)
rcvr.start("localhost",PyPAD.PAD_TCP_PORT)