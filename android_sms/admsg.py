# -*- coding: UTF-8 -*-
# File: admsg.py
# Date: 2010-12-02
# Author: gashero

"""
Android系统备份短信的网络通信客户端
"""

import struct
import socket

import android
LOCALNUM='15110036108'

#def digest(msgdict):
#    """计算一个短信的校验和，方便计算"""
#    content=msgdict['date']+msgdict['body']+msgdict['_id']+msgdict['address']
#    content=content.encode('utf-8')
#    return hashlib.md5(content).hexdigest()

def cleanmsgdict(msgdict,localnum,isinbox):
    """清理直接返回的msgdict对象"""
    newmd={
            'ts':int(msgdict['date'][:-3]),
            'msg':msgdict['body'].encode('utf-8'),
            'msgid':(msgdict['date'][:-3]+msgdict['address']).encode('utf-8'),
            }
    if isinbox:
        newmd['tfrom']=msgdict['address'].encode('utf-8')
        newmd['tto']=localnum
    else:
        newmd['tfrom']=localnum
        newmd['tto']=msgdict['address'].encode('utf-8')
    return newmd

def backup_box(box,sock,droid):
    retid,msgidlist,error=droid.smsGetMessageIds(False,box)
    if box=='inbox':
        cmd='i'
    elif box=='sent':
        cmd='t'
    else:
        'unknown box'
        return
    msgidlist.sort()
    print '[%s] Message Count=%d'%(box,len(msgidlist))
    idx=0
    for msgid in msgidlist:
        retid,msg,error=droid.smsGetMessageById(msgid)
        msg=cleanmsgdict(msg,LOCALNUM,isinbox=True)
        pktdata=repr(msg)
        pkt=struct.pack('!L',len(pktdata)+5)+cmd+pktdata
        sock.send(pkt)
        idx+=1
        if idx%50==0:
            print 'idx=%d'%idx
    return

def main():
    droid=android.Android()
    retid,serverip,error=droid.dialogGetInput(u'输入IP',u'IP:',u'192.168.39.172')
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((serverip,3022))
    backup_box('inbox',sock,droid)
    backup_box('sent',sock,droid)
    sock.close()
    return

if __name__=='__main__':
    main()
