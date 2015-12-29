#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# File: ipsms.py
# Date: 2012-04-26
# Author: gashero

"""
给iPhone4备份短信的
"""

import os
import sys
import time
import sqlite3

import json

LOCAL_PHONENUMBER='18618298562'
INBOX_FILENAME='../../origin_log/SMS_n900iphone/sms_inbox_%(yyyymm)s.txt'
SENT_FILENAME='../../origin_log/SMS_n900iphone/sms_sent_%(yyyymm)s.txt'
DB_FILENAME='/var/mobile/Library/SMS/sms.db'

SQL_GETSMS="""SELECT date,flags,text,address FROM message WHERE text IS NOT NULL AND date >= %(start_tick)d AND date < %(stop_tick)d ORDER BY date"""
#TODO:直接忽略了内容为空的短信，不知怎么回事呢

lastmonth=lambda :time.time()-(time.localtime()[2]+1)*86400

def backup_month(start_tick,stop_tick,yyyymm):
    """备份一个月的短信"""
    conn=sqlite3.connect(DB_FILENAME)
    curr=conn.cursor()
    sql=SQL_GETSMS%{
            'start_tick':start_tick,
            'stop_tick':stop_tick,}
    curr.execute(sql)
    dataset=curr.fetchall()
    curr.close()
    conn.close()
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
    for (starttime,flag,msg,addr) in dataset:
        msgdict={
                'msg':msg.encode('utf-8'),
                'msgid':'%d-%s-%d'%(starttime,
                    addr.encode('utf-8'),len(msg)),
                'ts':starttime,}
        if msgdict['msgid'] in savedset:
            continue
        if flag==3: #sent
            msgdict['tfrom']=LOCAL_PHONENUMBER
            msgdict['to']=addr.encode('utf-8')
            fw_sent.write(json.write(msgdict)+'\n')
        elif flag==2:   #inbox
            msgdict['tto']=LOCAL_PHONENUMBER
            msgdict['tfrom']=addr.encode('utf-8')
            fw_inbox.write(json.write(msgdict)+'\n')
        else:
            raise ValueError('Unknown flags=%d'%flags)
    fw_inbox.close()
    fw_sent.close()
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
    backup_month(
            month_start,
            month_stop,
            time.strftime('%Y%m',time.localtime(month_start))
            )
    return

if __name__=='__main__':
    main()
