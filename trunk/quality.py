# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

from datetime import datetime
from datetime import timedelta
import MySQLdb

# Quality settings
HOUR_EXP = 12.0
DAY_EXP = 288.0
MAX_GRADE = 1.0

# Db connection settings
USER = 'magda'
PWD = 'lokus1?'
HOST = 'localhost'

DB_CONN = {'edu_mit_media_funf_probe_builtin_BluetoothProbe' : 'bluetooth',
           'edu_mit_media_funf_probe_builtin_LocationProbe'  : 'location',
           'edu_mit_media_funf_probe_builtin_WifiProbe'      : 'wifi'}

TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'
   
def insert_into(db, table_name, user, start_timestamp, end_timestamp, column, grade, count):
    cur = db.cursor()
    query = 'INSERT INTO %s (user, start_timestamp, end_timestamp, bluetooth_quality, wifi_quality, location_quality, bluetooth_count, wifi_count, location_count) ' % table_name
    if column == 'bluetooth':
        query = query + 'VALUES (%s, %s, %s, %s, 0, 0, %s, 0, 0) '
    elif column == 'location':
        query = query + 'VALUES (%s, %s, %s, 0, %s, 0, 0, %s, 0) '
    elif column == 'wifi':
        query = query + 'VALUES (%s, %s, %s, 0, 0, %s, 0, 0, %s) '
        
    query = query + 'ON DUPLICATE KEY UPDATE %s = %s + %%s, %s = %s + %%s ' % (column + '_quality', column + '_quality', column + '_count', column + '_count')
    cur.execute(query, (user, start_timestamp, end_timestamp, grade, count, grade, count))
    
def get_user_last_scan_id(db, user_id, column_name):
    cur = db.cursor()
    query = "SELECT %s FROM user_last_scans WHERE user=%%s" % (column_name + '_id')
    cur.execute(query, (user_id))
    result = cur.fetchall()
    cur.close()
    return result[0][0] 
    
def get_users_list(db):
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(user) FROM researcher')
    result = cur.fetchall()
    cur.close()
    return result
    
def update_qualities(db, db_qual, user_id, column_name):
    scan_id = get_user_last_scan_id(db_qual, user_id, column_name)
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and id > %s ORDER BY timestamp', (user_id, scan_id))
    fetched_data = cur.fetchall()
    cur.close()
    if len(fetched_data) > 0:
        print "Calculating daily quality..."
        calc_day_quality(db_qual, fetched_data, user_id, column_name)
        print "Calculating hourly quality..."
        calc_hour_quality(db_qual, fetched_data, user_id, column_name)
        
        cur = db.cursor()
        cur.execute('SELECT id FROM researcher WHERE user = %s and id > %s ORDER BY id', (user_id, scan_id))
        fetched_data = cur.fetchall()
        cur.close()
        
        cur = db_qual.cursor()
        query = 'UPDATE user_last_scans SET %s = %%s WHERE user = %%s' % (column_name + '_id')
        cur.execute(query, (fetched_data[-1][0], user_id))
        db_qual.commit()
        cur.close()
    else:
        print 'No new scans arrived'
        
def calc_hour_quality(db_qual, data, user_id, column):
    last_timestamp = data[-1][0]
    first_timestamp = datetime(data[0][0].year, data[0][0].month, data[0][0].day, data[0][0].hour, 0)
    current_timestamp = first_timestamp
    idx = 0
    cur = db_qual.cursor() 
    while first_timestamp < last_timestamp and idx < len(data) - 1:
        count = 0
        end_timestamp = first_timestamp + timedelta(hours = 1)
        while current_timestamp <= end_timestamp and current_timestamp >= first_timestamp and idx < len(data) - 1:
            count = count + 1
            idx = idx + 1
            current_timestamp = data[idx][0]
        grade = count / HOUR_EXP
        insert_into(db_qual, TB_QUALITY_HOURLY, user_id, first_timestamp, end_timestamp, column, grade, count)
        first_timestamp = end_timestamp
    db_qual.commit()
    cur.close()
        
def calc_day_quality(db_qual, data, user_id, column):
    last_timestamp = data[-1][0]
    first_timestamp = datetime(data[0][0].year, data[0][0].month, data[0][0].day, 0, 0)
    current_timestamp = first_timestamp
    idx = 0
    cur = db_qual.cursor() 
    while first_timestamp < last_timestamp and idx < len(data) - 1:
        count = 0
        end_timestamp = first_timestamp + timedelta(days = 1)
        while current_timestamp <= end_timestamp and current_timestamp >= first_timestamp and idx < len(data) - 1:
            count = count + 1
            idx = idx + 1
            current_timestamp = data[idx][0]
        grade = count / DAY_EXP
        insert_into(db_qual, TB_QUALITY_DAILY, user_id, first_timestamp, end_timestamp, column, grade, count)
        first_timestamp = end_timestamp
    db_qual.commit()
    cur.close()
    
try:
    db_quality = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_QUALITY)
    print 'Connected to database: ', DB_QUALITY
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
  
for connection in DB_CONN.keys():
    try:
        db_data = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = connection)
        print 'Connected to database: ', connection
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        break
    
    users_list = get_users_list(db_data)
    user_idx = 0
    before = datetime.now()
    
    for single_user in users_list:
        user_idx = user_idx + 1
        user_name = "user" + str(user_idx)
        print 'Processing ', user_name    
        update_qualities(db_data, db_quality, single_user[0], DB_CONN[connection])
    print 'Execution time: ', datetime.now() - before
    db_data.close()
    
db_quality.close()