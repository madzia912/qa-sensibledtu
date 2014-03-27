# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

from datetime import datetime
from datetime import timedelta
import MySQLdb

# Quality settings
MONTH_EXP = 8640.0
WEEK_EXP = 2016.0
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
TB_STATS_HOURLY = 'stats_hourly'
TB_STATS_DAILY = 'stats_daily'

DB_QUALITY = 'data_quality'
   
def get_first_last_timestamp(db, user_id, column, table_name):
    cur = db.cursor()
    query = 'SELECT start_timestamp, %s FROM %s WHERE user = %%s ORDER BY start_timestamp DESC' % (column + '_quality', table_name)
    cur.execute(query, (user_id))
    fetched_data = cur.fetchall()
    cur.close()
    return (fetched_data[-1][0], fetched_data[0][0])
    
def get_last_week_data(db, user_id, column, table_name):
    (first_timestamp, last_timestamp) = get_first_last_timestamp(db, user_id, column, table_name)
    cur = db.cursor()
    query = 'SELECT %s FROM %s WHERE user = %%s AND start_timestamp > DATE_SUB(%%s, INTERVAL 7 DAY)' % (column + '_count', table_name)
    cur.execute(query, (user_id, last_timestamp))    
    fetched_data = cur.fetchall()
    cur.close()
    return sum(fetched_data[0])
    
def get_last_month_data(db, user_id, column, table_name):
    (first_timestamp, last_timestamp) = get_first_last_timestamp(db, user_id, column, table_name)
    cur = db.cursor()
    query = 'SELECT %s FROM %s WHERE user = %%s AND start_timestamp > DATE_SUB(%%s, INTERVAL 37 DAY) AND start_timestamp <= DATE_SUB(%%s, INTERVAL 7 DAY)' % (column + '_count', table_name)
    cur.execute(query, (user_id, last_timestamp, last_timestamp))    
    fetched_data = cur.fetchall()
    cur.close()
    return sum(fetched_data[0])
    
def insert_into_qual(db, table_name, user, start_timestamp, end_timestamp, column, grade, count):
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
      
def print_stats(users_list, db_qual, column):
    column_names = "username\tall\tmonth\tweek\n"
    file_name = "data" + column + ".tsv"
    # write to file
    with open(file_name, 'w') as f_handle:
        f_handle.write(column_names)
        for user in users_list:
            # get user stats all / month / week for quality specified as column
            cur = db_qual.cursor()
            query = "SELECT all_count, all_max, month_count, week_count FROM stats_daily WHERE user=%s and type=%s"
            cur.execute(query, (user[0], column))
            result = cur.fetchall()
            cur.close()
           
            all_quality = result[0][0] / float(result[0][1])
            month_quality = result[0][2] / MONTH_EXP
            week_quality = result[0][3] / WEEK_EXP
      
            row = user[0] + "\t" + str(all_quality) + "\t" + str(month_quality) + "\t" + str(week_quality) + "\n"
            f_handle.write(row)
    
def calc_hour_quality(db_qual, data, user_id, column):
    last_timestamp = data[-1][0]
    first_timestamp = datetime(data[0][0].year, data[0][0].month, data[0][0].day, data[0][0].hour, 0)
    current_timestamp = first_timestamp
    idx = 0
    cur = db_qual.cursor()
    all_count = 0
    all_count_max = 0
    while first_timestamp < last_timestamp and idx < len(data) - 1:
        count = 0
        end_timestamp = first_timestamp + timedelta(hours = 1)
        while current_timestamp <= end_timestamp and current_timestamp >= first_timestamp and idx < len(data) - 1:
            count = count + 1
            idx = idx + 1
            current_timestamp = data[idx][0]
        grade = count / HOUR_EXP
        insert_into_qual(db_qual, TB_QUALITY_HOURLY, user_id, first_timestamp, end_timestamp, column, grade, count)
        first_timestamp = end_timestamp
        all_count = all_count + count
        all_count_max = all_count_max + HOUR_EXP
    db_qual.commit()
    cur.close()
    update_hour_stats(db_qual, data, user_id, column, all_count, all_count_max)
        
def update_hour_stats(db_qual, data, user_id, typ, all_count, all_count_max):
    # get all count from DB
    [all_count_db, all_count_max_db] = get_stats_all(db_qual, user_id, typ, TB_STATS_HOURLY)
    all_count = all_count + all_count_db
    all_count_max = all_count_max + all_count_max_db
    
    # get month count
    month_count = get_last_month_data(db_qual, user_id, typ, TB_QUALITY_HOURLY)
    # get week count
    week_count = get_last_week_data(db_qual, user_id, typ, TB_QUALITY_HOURLY)
    
    insert_info_stats(db_qual, TB_STATS_HOURLY, user_id, typ, all_count, all_count_max, month_count, week_count)
    
def update_day_stats(db_qual, data, user_id, typ, all_count, all_count_max):
    # get all count from DB
    [all_count_db, all_count_max_db] = get_stats_all(db_qual, user_id, typ, TB_STATS_DAILY)
    all_count = all_count + all_count_db
    all_count_max = all_count_max + all_count_max_db
    
    # get month count
    month_count = get_last_month_data(db_qual, user_id, typ, TB_QUALITY_DAILY)
    # get week count
    week_count = get_last_week_data(db_qual, user_id, typ, TB_QUALITY_DAILY)
    
    insert_info_stats(db_qual, TB_STATS_DAILY, user_id, typ, all_count, all_count_max, month_count, week_count)
    
def insert_info_stats(db, table_name, user_id, typ, all_count, all_count_max, month_count, week_count):
    cur = db.cursor()
    query = 'INSERT INTO %s (user, type, all_count, all_max, month_count, week_count) ' % table_name
    query = query + 'VALUES (%s, %s, %s, %s, %s, %s) '  
    query = query + 'ON DUPLICATE KEY UPDATE all_count = all_count + %%s, all_max = all_max + %%s, month_count = %%s, week_count = %%s ' % ()
    cur.execute(query, (user_id, typ, all_count, all_count_max, month_count, week_count, all_count, all_count_max, month_count, week_count))
    db.commit()
    cur.close()
    
def get_stats_all(db_qual, user_id, typ, table_name):
    cur = db_qual.cursor()
    query = "SELECT all_count, all_max FROM %s WHERE user=%%s and type=%%s" % (table_name)
    cur.execute(query, (user_id, typ))
    result = cur.fetchall()
    cur.close()
    if len(result) == 0:
        return [0, 0]
    return result[0]
    
def calc_day_quality(db_qual, data, user_id, column):
    last_timestamp = data[-1][0]
    first_timestamp = datetime(data[0][0].year, data[0][0].month, data[0][0].day, 0, 0)
    current_timestamp = first_timestamp
    idx = 0
    cur = db_qual.cursor() 
    all_count = 0
    all_count_max = 0
    while first_timestamp < last_timestamp and idx < len(data) - 1:
        count = 0
        end_timestamp = first_timestamp + timedelta(days = 1)
        while current_timestamp <= end_timestamp and current_timestamp >= first_timestamp and idx < len(data) - 1:
            count = count + 1
            idx = idx + 1
            current_timestamp = data[idx][0]
        grade = count / DAY_EXP
        insert_into_qual(db_qual, TB_QUALITY_DAILY, user_id, first_timestamp, end_timestamp, column, grade, count)
        first_timestamp = end_timestamp
        all_count = all_count + count
        all_count_max = all_count_max + DAY_EXP
    db_qual.commit()
    cur.close()
    update_day_stats(db_qual, data, user_id, column, all_count, all_count_max)
    
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
    print_stats(users_list, db_quality, DB_CONN[connection])

db_quality.close()