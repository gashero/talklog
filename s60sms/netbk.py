# -*- coding: UTF-8 -*-
# File: netbk.py
# Date: 2011-05-17
# Author: gashero

"""
通过网络备份短信的，以前用蓝牙的用起来太不方便了，尤其是N810的文件系统又坏了。
"""

import time
import struct
import socket

import e32
import inbox
import appuifw

LOCALNUM='15110036108'
_now=lambda :time.strftime('%Y-%m-%d %H:%M:%S')

def cleanmsgdict(msgdict,localnum,isinbox):
    """清理直接返回的msgdict对象"""
    #TODO:continue
    newmd={
            'ts':msgdict['ts'],
            'msg':msgdict['msg'].encode('utf-8'),
            'msgid':str(msgdict['ts'])+msgdict['address'].encode('utf-8'),
            }
    if isinbox:
        newmd['tfrom']=msgdict['address'].encode('utf-8')
        newmd['to']=localnum
    else:
        newmd['tfrom']=localnum
        newmd['to']=msgdict['address'].encode('utf-8')
    return newmd

def backup_box(boxname,sock):
    if boxname=='inbox':
        box=inbox.Inbox(inbox.EInbox)
        isinbox=True
        cmd='i'
    elif boxname=='sent':
        box=inbox.Inbox(inbox.ESent)
        isinbox=False
        cmd='t'
    else:
        print 'Unknown boxname=[%s]'%boxname
        return
    msgidlist=box.sms_messages()
    print 'message count=',len(msgidlist)
    idx=0
    for msgid in msgidlist:
        msg=cleanmsgdict({
            'address':box.address(msgid),
            'ts':int(box.time(msgid)),
            'msg':box.content(msgid),
            },LOCALNUM,isinbox)
        #print msg
        pktdata=repr(msg)
        pkt=struct.pack('!L',len(pktdata)+5)+cmd+pktdata
        sock.send(pkt)
        idx+=1
        if idx%50==0:
            print 'idx=%d'%idx
    return

def wifi_backup():
    serverip=appuifw.query(u'服务器IP','text',u'192.168.39.172')
    serverip=str(serverip)
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((serverip,3022))
    backup_box('inbox',sock)
    backup_box('sent',sock)
    sock.close()
    print 'BackupSMS done!'
    return

def clear_100():
    box=inbox.Inbox(inbox.EInbox)
    msgidlist=box.sms_messages()
    for msgid in msgidlist[100:]:
        box.delete(msgid)
    box=inbox.Inbox(inbox.ESent)
    msgidlist=box.sms_messages()
    for msgid in msgidlist[100:]:
        box.delete(msgid)
    print 'Clear100 done!'
    return

## GUI部门 ####################################################################

APP_MENU=[
        (u'bkservice',      wifi_backup),
        (u'clear100',       clear_100),
        ]

def quit_handler():
    global LOOPING
    LOOPING=False
    applock.signal()
    return

def main():
    global applock
    appuifw.app.title=u'BackupSMS'
    appuifw.app.exit_key_handler=quit_handler
    appuifw.app.menu=APP_MENU
    appuifw.app.screen='normal'
    applock=e32.Ao_lock()
    print '%s BackupSMS start ...'%_now()
    applock.wait()
    return

if __name__=='__main__':
    main()
