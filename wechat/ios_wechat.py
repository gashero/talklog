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

def main():
    db_root=sys.argv[1]
    fn_db=os.path.join(db_root,'DB','MM.sqlite')
    assert os.path.exists(fn_db)
    assert os.path.isfile(fn_db)
    conn=sqlite3.connect(fn_db)
    curr=conn.cursor()
    try:
        curr.execute('SELECT name FROM sqlite_master')
        ds=curr.fetchall()
        tablelist=map(lambda r:r[0],ds)
        tablelist=filter(lambda n:n.startswith('Chat_') and 'Index' not in n,tablelist)
        print tablelist
        print len(tablelist),len(set(tablelist))
    finally:
        curr.close()
        conn.close()
    return

if __name__=='__main__':
    main()
