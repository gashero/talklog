# -*- coding: UTF-8 -*-
# File: s60log.py
# Date: 2009-10-11
# Author: gashero

"""
Backup symbian s60 cellphone SMS message.
"""

import md5
import appuifw
import time
import inbox

devlist=[
        (inbox.EInbox,'SMS_inbox_%s.txt'),      #收件箱
        (inbox.ESent,'SMS_sent_%s.txt'),        #已发送短信
        (inbox.EOutbox,'SMS_outbox_%s.txt'),    #发件箱，临时的不存了
        (inbox.EDraft,'SMS_draft_%s.txt'),      #草稿，以后不再存储
        ]

def loaddbidx(filename):
    """载入备份数据库的所有索引，返回索引集合"""
    return

def loadboxidx():
    """载入短信文件夹的所有索引，返回索引字典，以索引为key，短信ID为value"""
    return
#需要记录信息:ts,pfrom,tfrom,pto,tto,nfrom,msg

def backup(box,filename):
    mlist=box.sms_messages()
    f=open('e:\\'+filename,'w')
    #for mid in mlist:
    #    dd={}
    #    dd['id']=mid
    #    dd['time']=box.time(mid)
    #    dd['content']=box.content(mid)
    #    dd['address']=box.address(mid)
    #    f.write(repr(dd)+'\n')
    #    #box.delete(mid)
    mid=mlist[0]
    print dir(box)
    print 'time=',box.time(mid),'address=',box.address(mid),'content=',box.content(mid)
    print help(box.bind)
    f.close()
    return

def main():
    print 'start'
    for (dev,filename) in devlist:
        box=inbox.Inbox(dev)
        filename=filename%time.strftime('%Y%m%d_%H%M%S')
        backup(box,filename)
    print 'finish'
    return

if __name__=='__main__':
    main()
