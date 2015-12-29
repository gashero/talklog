#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
# File: deleteold.py
# Date: 2014-04-17
# Author: gashero

"""
删除太旧的短信，反正已经备份了
"""

import os
import sys
import time
import sqlite3

DB_FILENAME='/var/mobile/Library/SMS/sms.db'
DIFF_MACH=978307200

SQL_COUNTMONTH="""SELECT COUNT(*) FROM message WHERE date >= %(start_tick)d AND date < %(stop_tick)d"""
SQL_DELMONTH="""DELETE FROM message WHERE date >= %(start_tick)d AND date < %(stop_tick)d"""

def delete_month(start_tick,stop_tick):
    """删除一个月的短信"""
    conn=sqlite3.connect(DB_FILENAME)
    curr=conn.cursor()
    sql=SQL_COUNTMONTH%{
            'start_tick':start_tick-DIFF_MACH,
            'stop_tick':stop_tick-DIFF_MACH,}
    curr.execute(sql)
    dataset=curr.fetchall()
    print 'Delete %d messages?[y/n]'%dataset[0][0]
    yn=raw_input()
    if yn!='y':
        print 'abort[%s]'%repr(yn)
        return
    sql=SQL_DELMONTH%{
            'start_tick':start_tick-DIFF_MACH,
            'stop_tick':stop_tick-DIFF_MACH,}
    curr.execute(sql)
    conn.commit()
    curr.close()
    conn.close()
    print 'Delete done!'
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
    delete_month(month_start,month_stop)
    return

if __name__=='__main__':
    main()
