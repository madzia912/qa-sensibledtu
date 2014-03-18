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

ID = 0
DB_DATA = 'edu_mit_media_funf_probe_builtin_BluetoothProbe'
COL_NAME = 'bluetooth_id'

ID = 1
DB_DATA = 'edu_mit_media_funf_probe_builtin_LocationProbe'
COL_NAME = 'location_id'

ID = 2
DB_DATA = 'edu_mit_media_funf_probe_builtin_WifiProbe'
COL_NAME = 'wifi_id'

TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'

# TODO: make the code more optimized in names and run it for WiFi and Location
# see http://stackoverflow.com/questions/17779005/python-stringbuilder-for-mysql-query-execution
    
def getUserLastScanId(db, user_id, column_name):
    cur = db.cursor()
    
    #TODO: make it nice
    if ID == 0:
        cur.execute('SELECT bluetooth_id FROM user_last_scans WHERE user=%s', (user_id))
    elif ID == 1:
        cur.execute('SELECT gps_id FROM user_last_scans WHERE user=%s', (user_id))
    elif ID == 2:
        cur.execute('SELECT wifi_id FROM user_last_scans WHERE user=%s', (user_id))
        
    result = cur.fetchall()
    cur.close()
    return result[0][0]
    
def getUserData(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT * FROM researcher WHERE user=%s', (user_id))    
    result = cur.fetchall()
    cur.close()
    return result   
    
def getUsersList(db):
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(user) FROM researcher')
    result = cur.fetchall()
    cur.close()
    return result
    
#def getQualityHour(db, user_id, first_timestamp, last_timestamp, delta):
#    quality = []
#    while first_timestamp < last_timestamp:
#        end_timestamp = first_timestamp + timedelta(hours = delta)
#        cur = db.cursor()
#        cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and timestamp BETWEEN %s and %s', (user_id, first_timestamp, end_timestamp))
#        fetched_data = cur.fetchall() 
#        cur.close()
#        grade = len(fetched_data) / HOUR_EXP
#            
#        quality.append( (first_timestamp, end_timestamp, grade, len(fetched_data) ) )        
#        first_timestamp = first_timestamp + timedelta(hours = delta)
#    return quality
#    
#def getQualityDay(db, user_id, first_timestamp, last_timestamp, delta):
#    quality = []
#    while first_timestamp < last_timestamp:
#        end_timestamp = first_timestamp + timedelta(days = delta)
#        cur = db.cursor()
#        cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and timestamp BETWEEN %s and %s', (user_id, first_timestamp, end_timestamp))
#        fetched_data = cur.fetchall()  
#        cur.close()
#        grade = len(fetched_data) / DAY_EXP
#            
#        quality.append( (first_timestamp, end_timestamp, grade, len(fetched_data) ) )        
#        first_timestamp = first_timestamp + timedelta(days = delta)
#    return quality
    
def updateQualities(db, db_qual, user_id):
    scan_id = getUserLastScanId(db_qual, user_id, 'location_id')
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and id > %s ORDER BY timestamp', (user_id, scan_id))
    fetched_data = cur.fetchall()
    cur.close()
    if len(fetched_data) > 0:
        print "Calculating daily quality..."
        calcDayQuality(db_qual, fetched_data, user_id)
        print "Calculating hourly quality..."
        calcHourQuality(db_qual, fetched_data, user_id)
        cur = db.cursor()
        cur.execute('SELECT id FROM researcher WHERE user = %s and id > %s ORDER BY id', (user_id, scan_id))
        fetched_data = cur.fetchall()
        cur.close()
        fetched_data
        cur = db_qual.cursor()
        
        #TODO: make it nice
        if ID == 0:
            cur.execute('UPDATE user_last_scans SET bluetooth_id = %s WHERE user = %s', (fetched_data[-1][0], user_id))
        elif ID == 1:
            cur.execute('UPDATE user_last_scans SET gps_id = %s WHERE user = %s', (fetched_data[-1][0], user_id))
        elif ID == 2:
            cur.execute('UPDATE user_last_scans SET wifi_id = %s WHERE user = %s', (fetched_data[-1][0], user_id))
        
        db_qual.commit()
        cur.close()
    else:
        print 'No new scans arrived'
        
def calcHourQuality(db_qual, data, user_id):
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
        
        #TODO: make it nice
        if ID == 0:
            cur.execute('INSERT INTO data_quality_hourly \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, %s, 0, 0, %s, 0, 0) \
            ON DUPLICATE KEY UPDATE bluetooth_quality = bluetooth_quality + %s, bluetooth_count = bluetooth_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        elif ID == 1:
            cur.execute('INSERT INTO data_quality_hourly \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, 0, %s, 0, 0, %s, 0) \
            ON DUPLICATE KEY UPDATE location_quality = location_quality + %s, location_count = location_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        elif ID == 2:
            cur.execute('INSERT INTO data_quality_hourly \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, 0, 0, %s, 0, 0, %s) \
            ON DUPLICATE KEY UPDATE wifi_quality = wifi_quality + %s, wifi_count = wifi_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        first_timestamp = end_timestamp
    db_qual.commit()
    cur.close()
        

def calcDayQuality(db_qual, data, user_id):
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
        #TODO: make it nice
        if ID == 0:
            cur.execute('INSERT INTO data_quality_daily \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, %s, 0, 0, %s, 0, 0) \
            ON DUPLICATE KEY UPDATE bluetooth_quality = bluetooth_quality + %s, bluetooth_count = bluetooth_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        elif ID == 1:
            cur.execute('INSERT INTO data_quality_daily \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, 0, %s, 0, 0, %s, 0) \
            ON DUPLICATE KEY UPDATE location_quality = location_quality + %s, location_count = location_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        elif ID == 2:
            cur.execute('INSERT INTO data_quality_daily \
            (user, start_timestamp, end_timestamp, bluetooth_quality, \
            wifi_quality, location_quality, bluetooth_count, wifi_count, \
            location_count) VALUES (%s, %s, %s, 0, 0, %s, 0, 0, %s) \
            ON DUPLICATE KEY UPDATE wifi_quality = wifi_quality + %s, wifi_count = wifi_count + %s', \
            (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        first_timestamp = end_timestamp
    db_qual.commit()
    cur.close()
    
    
    
db_data = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_DATA)
print 'Connected to database: ', DB_DATA
db_quality = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_QUALITY)
print 'Connected to database: ', DB_QUALITY

users_list = getUsersList(db_data)
user_idx = 0
before = datetime.now()

for single_user in users_list:
    user_idx = user_idx + 1
    user_name = "user" + str(user_idx)
    print 'Processing ', user_name    
    updateQualities(db_data, db_quality, single_user[0])
    
print 'Execution time: ', datetime.now() - before
db_data.close()
db_quality.close()
    
    
    