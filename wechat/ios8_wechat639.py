#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# File: ios_wechat.py
# Date: 2015-12-28
# Author: harry

"""
备份iOS系统的微信聊天记录
需要先把微信应用建立符号链接到 /var/mobile/wechat
一个聊天记录表名字的例子 Chat_06a2fa0957bd3a455acb77e63dbb8f04
"""

import os
import sys
import time
import sqlite3
import csv
import hashlib

DATAROOT='/var/mobile/Containers/Data/Application'

def utf_none(un):
    if type(un)==unicode:
        return un.encode('utf-8')
    elif un==None:
        return ''
    else:
        return un

def get_db_connect():
    """搜索第一个可用的聊天数据库位置"""
    fn_db=None
    for appdir in os.listdir(DATAROOT):
        docdir=os.path.join(DATAROOT,appdir,'Documents')
        for accdir in os.listdir(docdir):
            #print docdir,accdir
            fn_try=os.path.join(docdir,accdir,'DB','MM.sqlite')
            if os.path.exists(fn_try):
                fn_db=fn_try
                break
        if fn_db:
            break
    else:
        raise RuntimeError('MM.sqlite not found')
    print fn_db
    assert os.path.isfile(fn_db)
    conn=sqlite3.connect(fn_db)
    return conn

def backup_contacts(conn,logdir):
    """备份通讯录"""
    curr=conn.cursor()
    curr.execute("""SELECT UsrName,NickName,Email,Mobile FROM Friend""")
    dataset=curr.fetchall()
    curr.close()
    fo=open(os.path.join(logdir,'contactlist.csv'),'w')
    writer=csv.writer(fo)
    writer.writerow(('UsrName','NickName','Email','Mobile'))
    contactdict={}
    for r in dataset:
        contactdict[r[0].encode('utf-8')]={
                'UsrName':  r[0].encode('utf-8'),
                'NickName': r[1].encode('utf-8'),
                'Email':    r[2],
                'Mobile':   r[3],
                }
        r=map(utf_none,r)
        writer.writerow(r)
    fo.close()
    return contactdict

def backup_talklog(conn,contactdict,logdir):
    """备份聊天记录"""
    curr=conn.cursor()
    curr.execute('SELECT name FROM sqlite_master')
    ds=curr.fetchall()
    tablelist=map(lambda r:r[0],ds)
    tablelist=filter(lambda n:n.startswith('Chat_') and 'Index' not in n,tablelist)
    #print tablelist
    #print len(tablelist),len(set(tablelist))
    talklist=[]
    for UsrName in contactdict.keys():
        tbname='Chat_'+hashlib.md5(UsrName).hexdigest()
        if tbname in tablelist:
            talklist.append(UsrName)
    print len(talklist),len(tablelist)  #并不一样
    for UsrName in talklist:
        print 'Processing %s'%UsrName
        tbname='Chat_'+hashlib.md5(UsrName).hexdigest()
        sql="SELECT CreateTime,Message,Status,Type,Des FROM %s"%tbname
        curr.execute(sql)
        dataset=curr.fetchall()
        fn_log=os.path.join(logdir,'log_%s.csv'%UsrName)
        fo=open(fn_log,'w')
        writer=csv.writer(fo)
        writer.writerow(('CreateTime','Message','Status','Type','Des'))
        for r in dataset:
            r=map(utf_none,r)
            writer.writerow(r)
        fo.close()
    curr.close()
    return

def main():
    try:
        logdir=time.strftime('tlog_%Y%m%d')
        os.mkdir(logdir)
    except OSError,ex:
        if ex.errno==17:
            pass
        else:
            raise
    conn=get_db_connect()
    curr=conn.cursor()
    try:
        contactdict=backup_contacts(conn,logdir)
        backup_talklog(conn,contactdict,logdir)
    finally:
        curr.close()
        conn.close()
    return

if __name__=='__main__':
    main()
