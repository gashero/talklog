#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# File: iphonesms.py
# Date: 2014-04-17
# Author: gashero

"""
适用于iOS6的短信备份，对应iPhone5

SQLite数据库李的表格：
1. _SqliteDatabaseProperties
2. attachment
3. chat
4. chat_handle_join
5. chat_message_join
6. handle
7. message
8. message_attachment_join

我要关心的应该还是message表。可惜的是iphone4时代的flag字段等几个字段没了，我要重新分析字段。

我需要关心的几个字段：
1. 日期时间：还是叫date字段，但意义不同了，改为Mac绝对时间，相对于2001-01-01 00:00:00 UTC开始的，该时间加上978307200就是Unix TimeStamp了
2. 收发标记：is_from_me，取值0和1
3. 内容：字段名text
4. 对方号码：不再是address，而是放在handle表里，handle_id对应handle表的rowid，然后取id字段即可
5. 注意过滤只要SMS短信：service字段，"SMS"和"iMessage"
"""

import os
import sys
import time
import sqlite3

import json

LOCAL_PHONENUMBER='15110036108'
INBOX_FILENAME='../../origin_log/SMS_n900iphone/sms_inbox_%(yyyymm)s.txt'
SENT_FILENAME='../../origin_log/SMS_n900iphone/sms_sent_%(yyyymm)s.txt'
DB_FILENAME='/var/mobile/Library/SMS/sms.db'
DIFF_MACH=978307200

SQL_GETSMS="""SELECT date,is_from_me,text,service,handle_id FROM message WHERE text IS NOT NULL AND date >=%(start_tick)d AND date< %(stop_tick)d ORDER BY date"""
SQL_GETID="""SELECT id FROM handle WHERE rowid=%(handle_id)d"""

def backup_month(start_tick,stop_tick,yyyymm):
    """备份一个月的短信"""
    conn=sqlite3.connect(DB_FILENAME)
    curr=conn.cursor()
    sql=SQL_GETSMS%{
            'start_tick':start_tick-DIFF_MACH,
            'stop_tick':stop_tick-DIFF_MACH,}
    curr.execute(sql)
    dataset=curr.fetchall()
    savedset=set()
    fn_inbox=INBOX_FILENAME%{'yyyymm':yyyymm}
    fn_sent=SENT_FILENAME%{'yyyymm':yyyymm}
    if os.path.exists(fn_inbox):
        fr_inbox=open(fn_inbox,'r')
        fr_sent=open(fn_sent,'r')
        for line in fr_inbox.xreadlines():
            msgdict=json.read(line)
            savedset.add(msgdict['msgid'])
        for line in fr_sent.xreadlines():
            msgdict=json.read(line)
            savedset.add(msgdict['msgid'])
        fr_inbox.close()
        fr_sent.close()
    msglist=[]
    fw_inbox=open(fn_inbox,'a+')
    fw_sent=open(fn_sent,'a+')
    fixcount=0
    for (mactime,from_me,msg,service,handle_id) in dataset:
        assert service in ('SMS','iMessage')
        assert from_me in (0,1)
        starttime=mactime+DIFF_MACH
        sql=SQL_GETID%{'handle_id':handle_id}
        curr.execute(sql)
        ds_id=curr.fetchall()
        if len(ds_id)!=1:
            print mactime,from_me,msg.encode('utf-8'),service,handle_id
            continue
        address=ds_id[0][0].encode('UTF-8')
        #if address.startswith('+86'):
        #    address=address[3:]
        msgdict={
                'msg':msg.encode('UTF-8'),
                'msgid':'%d-%s-%d'%(starttime,
                    address,len(msg)),
                'ts':starttime,}
        if msgdict['msgid'] in savedset:
            continue
        if from_me==1:  #sent
            msgdict['tfrom']=LOCAL_PHONENUMBER
            msgdict['tto']=address
            fw_sent.write(json.write(msgdict)+'\n')
        elif from_me==0:    #inbox
            msgdict['tto']=LOCAL_PHONENUMBER
            msgdict['tfrom']=address
            fw_inbox.write(json.write(msgdict)+'\n')
        else:
            raise ValueError('Unknown from_me=%d'%from_me)
        fixcount+=1
    curr.close()
    conn.close()
    fw_inbox.close()
    fw_sent.close()
    print 'Saved %d messages'%fixcount
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
