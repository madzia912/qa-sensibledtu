# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

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

#DB_DATA = 'edu_mit_media_funf_probe_builtin_BluetoothProbe'
DB_DATA = 'edu_mit_media_funf_probe_builtin_LocationProbe'
#DB_DATA = 'edu_mit_media_funf_probe_builtin_WifiProbe'

TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'

# TODO: move drawing diagrams to another file
# TODO: make the code more optimized in names and run it for WiFi and Location
# see http://stackoverflow.com/questions/17779005/python-stringbuilder-for-mysql-query-execution

def getUserLastScanId(db, user_id, column_name):
    cur = db.cursor()
    cur.execute('SELECT gps_id FROM user_last_scans WHERE user=%s', (user_id))
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
    
def getQualityHour(db, user_id, first_timestamp, last_timestamp, delta):
    quality = []
    while first_timestamp < last_timestamp:
        end_timestamp = first_timestamp + timedelta(hours = delta)
        cur = db.cursor()
        cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and timestamp BETWEEN %s and %s', (user_id, first_timestamp, end_timestamp))
        fetched_data = cur.fetchall() 
        cur.close()
        grade = len(fetched_data) / HOUR_EXP
            
        quality.append( (first_timestamp, end_timestamp, grade, len(fetched_data) ) )        
        first_timestamp = first_timestamp + timedelta(hours = delta)
    return quality
    
def getQualityDay(db, user_id, first_timestamp, last_timestamp, delta):
    quality = []
    while first_timestamp < last_timestamp:
        end_timestamp = first_timestamp + timedelta(days = delta)
        cur = db.cursor()
        cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and timestamp BETWEEN %s and %s', (user_id, first_timestamp, end_timestamp))
        fetched_data = cur.fetchall()  
        cur.close()
        grade = len(fetched_data) / DAY_EXP
            
        quality.append( (first_timestamp, end_timestamp, grade, len(fetched_data) ) )        
        first_timestamp = first_timestamp + timedelta(days = delta)
    return quality
    
def updateQualities(db, db_qual, user_id):
    bluetooth_id = getUserLastScanId(db_qual, user_id, 'location_id')
    print 'BLUETOOTH: ', bluetooth_id
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and id > %s ORDER BY timestamp', (user_id, bluetooth_id))
    fetched_data = cur.fetchall()
    cur.close()
    print len(fetched_data)
    if len(fetched_data) > 0:
        calcDayQuality(db_qual, fetched_data, user_id)
        cur = db.cursor()
        cur.execute('SELECT id FROM researcher WHERE user = %s and id > %s ORDER BY id', (user_id, bluetooth_id))
        fetched_data = cur.fetchall()
        cur.close()
        fetched_data
        print fetched_data[-1][0]
        cur = db_qual.cursor()
        cur.execute('UPDATE user_last_scans SET gps_id = %s WHERE user = %s', (fetched_data[-1][0], user_id))
        db_qual.commit()
        cur.close()

def calcDayQuality(db_qual, data, user_id):
    # TODO: change timestamps to 00:00:00 time
    last_timestamp = data[-1][0]
    first_timestamp = data[0][0]
    current_timestamp = data[0][0]
    idx = 0
    while first_timestamp < last_timestamp and idx < len(data) - 1:
        count = 0
        end_timestamp = first_timestamp + timedelta(days = 1)
        while current_timestamp <= end_timestamp and current_timestamp >= first_timestamp and idx < len(data) - 1:
            count = count + 1
            idx = idx + 1
            current_timestamp = data[idx][0]
        grade = count / DAY_EXP
        # TODO: make one big query
        cur = db_qual.cursor()        
        #cur.execute('INSERT INTO data_quality_daily \
        #(user, start_timestamp, end_timestamp, bluetooth_quality, \
        #wifi_quality, location_quality, bluetooth_count, wifi_count, \
        #location_count) VALUES (%s, %s, %s, %s, 0, 0, %s, 0, 0) \
        #ON DUPLICATE KEY UPDATE bluetooth_quality = %s, bluetooth_count = %s', \
        #(user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        
        cur.execute('INSERT INTO data_quality_daily \
        (user, start_timestamp, end_timestamp, bluetooth_quality, \
        wifi_quality, location_quality, bluetooth_count, wifi_count, \
        location_count) VALUES (%s, %s, %s, 0, %s, 0, 0, %s, 0) \
        ON DUPLICATE KEY UPDATE location_quality = %s, location_count = %s', \
        (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        
        db_qual.commit()
        cur.close()
        print "Key: " + str(first_timestamp) + "Grade:" + str(grade)
        first_timestamp = end_timestamp

db_data = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_DATA)
db_quality = MySQLdb.connect(host = HOST, user = USER, passwd = PWD, db = DB_QUALITY)

users_list = getUsersList(db_data)
user_idx = 0

for single_user in users_list:
    user_idx = user_idx + 1
    user_name = "user" + str(user_idx)
    print user_name    
    updateQualities(db_data, db_quality, single_user[0])
    
db_data.close()
db_quality.close()
    
    
    