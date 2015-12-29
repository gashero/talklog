#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# File: lightmsg.py
# Date: 2011-02-17
# Author: gashero

"""
接收来自Android系统的短信备份请求，使用网络
"""

import os
import sys
import time
import struct
import socket
import select
import json

FILENAME_INBOX='../../origin_log/SMS_android/sms_inbox_%(month)s.txt'
FILENAME_SENT='../../origin_log/SMS_android/sms_sent_%(month)s.txt'

def getconn(port):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind(('0.0.0.0',port))
    sock.listen(1)
    client,addr=sock.accept()
    return client,addr

def bkserver(client):
    data=''
    while True:
        rlist,wlist,elist=select.select([client.fileno(),],[],[],500)
        if client.fileno() not in rlist:
            continue
        chunk=client.recv(65536)
        if not chunk:
            break
        data+=chunk
        if len(data)>5:
            pktlen=struct.unpack('!L',data[:4])[0]
            if len(data)>=pktlen:
                process_request(data[:pktlen])
                data=data[pktlen:]
    return

FILE_POOL={}
def process_request(packet):
    pktlen=packet[0:4]
    cmd=packet[4]
    msg=eval(packet[5:])
    msgjson=json.write(msg)
    yyyymm=time.strftime('%Y%m',time.localtime(msg['ts']))
    if cmd=='i':    #收件箱
        filename=FILENAME_INBOX%{'month':yyyymm,}
    elif cmd=='t':  #发件箱
        filename=FILENAME_SENT%{'month':yyyymm,}
    else:
        print 'UNKNOWN:',repr(packet)
        return
    needwrite=False
    if os.path.exists(filename):
        ff=open(filename,'rU')
        for line in ff.xreadlines():
            line=line.strip()
            if line==msgjson:
                needwrite=False
                break
        else:
            needwrite=True
        ff.close()
    else:
        needwrite=True
    if needwrite:
        ff=open(filename,'a+')
        ff.write(msgjson+'\n')
        ff.close()
    return

def main():
    try:
        client,addr=getconn(3022)
        bkserver(client)
    except KeyboardInterrupt:
        print
    return

if __name__=='__main__':
    main()
