#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# File: n900mm.py
# Date: 2012-04-21
# Author: gashero

"""
给N900用的备份短信的
必须字段：msg、msgid、tto、ts、tfrom
"""

import os
import sys
import time
import sqlite3

import json

LOCAL_PHONENUMBER='15110036108'
INBOX_FILENAME='../../origin_log/SMS_n900iphone/sms_inbox_%(yyyymm)s.txt'
SENT_FILENAME='../../origin_log/SMS_n900iphone/sms_sent_%(yyyymm)s.txt'
DB_FILENAME='/home/user/.rtcom-eventlogger/el-v1.db'

lastmonth=lambda :time.time()-(time.localtime()[2]+1)*86400

SQL_GETSMS='''SELECT start_time,outgoing,free_text,remote_uid FROM Events WHERE event_type_id=11 AND start_time >= %(start_tick)d AND start_time < %(stop_tick)d ORDER BY start_time'''

def backup_month(start_tick,stop_tick,yyyymm):
    """备份一个月的短信"""
    conn=sqlite3.connect(DB_FILENAME)
    curr=conn.cursor()
    sql=SQL_GETSMS%{
        'start_tick':start_tick,
        'stop_tick':stop_tick,}
    #print sql
    curr.execute(sql)
    dataset=curr.fetchall()
    savedset=set()
    if os.path.exists(INBOX_FILENAME%{'yyyymm':yyyymm}):
        fr_inbox=open(INBOX_FILENAME%{'yyyymm':yyyymm},'r')
        fr_sent=open(SENT_FILENAME%{'yyyymm':yyyymm},'r')
        for line in fr_inbox.xreadlines():
            msgdict=json.read(line)
            savedset.add(msgdict['msgid'])
        for line in fr_sent.xreadlines():
            msgdict=json.read(line)
            savedset.add(msgdict['msgid'])
        fr_inbox.close()
        fr_sent.close()
    msglist=[]
    fw_inbox=open(INBOX_FILENAME%{'yyyymm':yyyymm},'a+')
    fw_sent=open(SENT_FILENAME%{'yyyymm':yyyymm},'a+')
    #print 'len(dataset)=',len(dataset)
    for (starttime,outgoing,freetext,remoteuid) in dataset:
        #print repr(outgoing),repr(freetext),repr(starttime)
        msgdict={
                'msg':freetext.encode('utf-8'),
                'msgid':'%d-%s-%d'%(starttime,
                    remoteuid.encode('utf-8'),len(freetext)),
                'ts':starttime,
                }
        if msgdict['msgid'] in savedset:
            continue
        if outgoing==1:
            msgdict['tfrom']=LOCAL_PHONENUMBER
            msgdict['tto']=remoteuid.encode('utf-8')
            fw_sent.write(json.write(msgdict)+'\n')
        elif outgoing==0:
            msgdict['tto']=LOCAL_PHONENUMBER
            msgdict['tfrom']=remoteuid.encode('utf-8')
            fw_inbox.write(json.write(msgdict)+'\n')
        else:
            raise ValueError('Unknow outgoing=%d'%outgoing)
        #print msgdict
    # do it
    fw_inbox.close()
    fw_sent.close()
    curr.close()
    conn.close()
    return

def main():
    year,month=sys.argv[1].split('-')
    year=int(year)
    month=int(month)
    if month<12:
        next_month='%d-%d'%(year,month+1)
    else:
        next_month='%d-%d'%(year+1,1)
    month_start=int(time.mktime(time.strptime(sys.argv[1],'%Y-%m')))
    month_stop=int(time.mktime(time.strptime(next_month,'%Y-%m')))
    #print month_start,time.ctime(month_start)
    #print month_stop,time.ctime(month_stop)
    backup_month(
            month_start,
            month_stop,
            time.strftime('%Y%m',time.localtime(month_start))
            )
    return

if __name__=='__main__':
    main()
