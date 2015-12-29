# -*- coding: UTF-8 -*-
# File: clearsms.py
# Date: 2011-02-20
# Author: gashero

"""
清理多余短信的
"""

import time

import android

def clear_box(box,ts,droid):
    """清理超过比ts还老的短信的短信"""
    retid,msgidlist,error=droid.smsGetMessageIds(False,box)
    msgidlist.sort()
    print '[%s] Message Count: %d'%(box,len(msgidlist))
    idx=0
    for msgid in msgidlist:
        retid,msg,error=droid.smsGetMessageById(msgid)
        msg['ts']=int(msg['date'][:-3])
        if msg['ts']<ts:
            #print "NEED DELETE",repr(msg)
            retid,ret,error=droid.smsDeleteMessage(msgid)
        else:
            #print "NOT DELETE",repr(msg)
            pass
        idx+=1
        if idx%50==0:
            print 'idx=%d'%idx
    return

def main():
    droid=android.Android()
    retid,days,error=droid.dialogGetInput(u'删除超过N天的短信',u'天数',u'7')
    days=int(days)
    ts=int(time.time())-days*86400
    clear_box('inbox',ts,droid)
    clear_box('sent',ts,droid)
    return

if __name__=='__main__':
    main()
