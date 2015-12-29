#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# File: light_getsms.py
# Date: 2010-07-21
# Author: gashero

"""
在几种操作系统上使用lightblue来与adaemon通信备份所有短信。
"""

N95_bt_address='00:1F:00:BC:88:C1'

import os
import sys
import time
import socket
import struct
import traceback

import lightblue
import json

LOOPING=True

INBOX_FILENAME='../../origin_log/SMS_light/sms_inbox_%Y%m.txt'
SENT_FILENAME='../../origin_log/SMS_light/sms_sent_%Y%m.txt'

lastmonth=lambda :time.time()-(time.localtime()[2]+1)*86400

#def get_sms(s60_address):
#    """暂时不用了"""
#    svrlist=lightblue.findservices(s60_address)
#    print 'Device [%s] has %d services.'%(s60_address,len(svrlist))
#    channel=None
#    for svr in svrlist:
#        #print repr(svr)
#        print '%s\t%s'%svr[1:]
#        if svr[2]=='adaemon':
#            channel=svr[1]
#    if channel==None:
#        print 'Get Adaemon Service Failed!'
#        return
#    conn=lightblue.socket(lightblue.RFCOMM)
#    conn.connect((s60_address,channel))
#    conn.close()
#    return

#def get_devlist():
#    """暂时不用了"""
#    devlist=lightblue.finddevices()
#    for dev in devlist:
#        print '%s\t%s\t%s'%dev
#    return devlist

def bkservice():
    """备份服务"""
    sock_server=lightblue.socket()
    sock_server.bind(('',0))
    sock_server.listen(1)
    lightblue.advertise(u'bkservice',sock_server,lightblue.RFCOMM)
    conn,addr=sock_server.accept()
    print 'Client [%s] connected!'%repr(addr)
    #conn.settimeout(5)
    #print dir(conn)
    try:
        bksession(conn)
    except:
        traceback.print_exc()
    finally:
        conn.close()
    return

def recvpacket(conn,_buffer):
    """获取一个封装的包"""
    #print repr(conn)
    while LOOPING:
        chunk=conn.recv(1024)
        if not chunk:
            raise ValueError,'Connection closed'
        _buffer+=chunk
        if len(_buffer)<4:
            continue
        pktlen=struct.unpack('!L',_buffer[:4])[0]
        if len(_buffer)>=pktlen:
            return _buffer[4:pktlen],_buffer[pktlen:]

def sendpacket(conn,content):
    """发送一个封装的包"""
    pktlen=struct.pack('!L',len(content)+4)
    return conn.send(pktlen+content)

def bksession(conn):
    global LOOPING
    _buffer=''
    #process inbox
    print 'Processing inbox......'
    sendpacket(conn,'list_sms_inbox')
    packet,_buffer=recvpacket(conn,_buffer)
    msglist=eval(packet)
    msgidlist=map(lambda t:t[0],msglist)
    newmsgidset=set(msgidlist)
    #print repr(packet)
    #print repr(msgidlist)
    filenamelist=(time.strftime(INBOX_FILENAME),
            time.strftime(INBOX_FILENAME,time.localtime(
            lastmonth())),)
    for fname in filenamelist:
        if os.path.exists(fname):
            f=open(fname,'rU')
            for line in f.xreadlines():
                logdict=json.read(line.strip())
                if logdict['msgid'] in newmsgidset:
                    msgidlist.remove(logdict['msgid'])
            f.close()
    print 'Fetching (%d) inbox......'%len(msgidlist)
    sendpacket(conn,'fetch_sms_inbox: '+repr(msgidlist))
    packet,_buffer=recvpacket(conn,_buffer)
    #print repr(packet)
    msglist=eval(packet)
    f=open(time.strftime(INBOX_FILENAME),'a+')
    for msgdict in msglist:
        f.write(json.write(msgdict)+'\n')
    f.close()
    #process sent
    print 'Processing sent......'
    sendpacket(conn,'list_sms_sent')
    packet,_buffer=recvpacket(conn,_buffer)
    msglist=eval(packet)
    msgidlist=map(lambda t:t[0],msglist)
    newmsgidset=set(msgidlist)
    filenamelist=(time.strftime(SENT_FILENAME),
            time.strftime(SENT_FILENAME,time.localtime(
            lastmonth())),)
    for fname in filenamelist:
        if os.path.exists(fname):
            f=open(fname,'rU')
            for line in f.xreadlines():
                logdict=json.read(line.strip())
                if logdict['msgid'] in newmsgidset:
                    msgidlist.remove(logdict['msgid'])
            f.close()
    print 'Fetching (%d) sent......'%len(msgidlist)
    sendpacket(conn,'fetch_sms_sent: '+repr(msgidlist))
    packet,_buffer=recvpacket(conn,_buffer)
    #print repr(packet)
    msglist=eval(packet)
    f=open(time.strftime(SENT_FILENAME),'a+')
    for msgdict in msglist:
        f.write(json.write(msgdict)+'\n')
    f.close()
    #退出
    sendpacket(conn,'exit')
    return

import unittest

class TestALL(unittest.TestCase):

    def test_lastmonth(self):
        self.assertEqual(time.localtime()[1]-\
                time.localtime(lastmonth())[1],1)
        return

def main():
    if len(sys.argv)==1:
        bkservice()
    elif len(sys.argv)==2 and sys.argv[1]=='list':
        get_devlist()
    elif len(sys.argv)==2 and sys.argv[1]=='n95':
        get_sms(N95_bt_address)
    elif len(sys.argv)==2 and sys.argv[1]=='test':
        del sys.argv[1:]
        unittest.main()
    else:
        raise ValueError
    return

if __name__=='__main__':
    main()
