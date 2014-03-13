# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:55:00 2014

@author: Magdalena Furman s110848
"""

from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
from matplotlib.dates import DateFormatter
import pylab as pl
import MySQLdb
import csv
from random import randrange

# Diagram layout settings
DATE_FMT = "%d-%m-%y"
YLIM = [0, 1.1]

# Quality settings
HOUR_EXP = 12.0
DAY_EXP = 288.0
MAX_GRADE = 1.0

# Db connection settings
USER = 'magda'
PWD = 'lokus1?'
HOST = 'localhost'

DB_DATA = 'edu_mit_media_funf_probe_builtin_BluetoothProbe'
#DB_DATA = 'edu_mit_media_funf_probe_builtin_LocationProbe'
#DB_DATA = 'edu_mit_media_funf_probe_builtin_WifiProbe'

TB_QUALITY_DAILY = 'data_quality_daily'
TB_QUALITY_HOURLY = 'data_quality_hourly'
TB_LAST_SCANS = 'user_last_scans'

DB_QUALITY = 'data_quality'

# TODO: move diagrams to another file
# TODO: make the code more optimized in names and run it for WiFi and Location
# see http://stackoverflow.com/questions/17779005/python-stringbuilder-for-mysql-query-execution

def getUserLastScanId(db, user_id, column_name):
    cur = db.cursor()
    cur.execute('SELECT bluetooth_id FROM user_last_scans WHERE user=%s', (user_id))
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
    
def getAllDataTimestamps(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s ORDER BY timestamp', (user_id))
    fetched_data = cur.fetchall()
    last_timestamp = fetched_data[-1][0]
    print last_timestamp
    first_timestamp = fetched_data[0][0]
    print first_timestamp
    cur.close()
    last_timestamp = datetime(last_timestamp.year, last_timestamp.month, last_timestamp.day, 0, 0, 0)
    first_timestamp = datetime(first_timestamp.year, first_timestamp.month, first_timestamp.day, 0, 0, 0)
    return [first_timestamp, last_timestamp]
    
def updateQualities(db, db_qual, user_id):
    bluetooth_id = getUserLastScanId(db_qual, user_id, 'bluetooth_id')
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s and id > %s ORDER BY timestamp', (user_id, bluetooth_id))
    fetched_data = cur.fetchall()
    cur.close()
    print len(fetched_data)
    if len(fetched_data) > 0:
        calcDayQuality(db_qual, fetched_data, user_id)
    
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
        cur.execute('INSERT INTO data_quality_daily \
        (user, start_timestamp, end_timestamp, bluetooth_quality, \
        wifi_quality, location_quality, bluetooth_count, wifi_count, \
        location_count) VALUES (%s, %s, %s, %s, 0, 0, %s, 0, 0) \
        ON DUPLICATE KEY UPDATE bluetooth_quality = %s, bluetooth_count = %s', \
        (user_id, first_timestamp, end_timestamp, grade, count, grade, count))
        
        db_qual.commit()
        cur.close()
        print "Key: " + str(first_timestamp) + "Grade:" + str(grade)
        first_timestamp = end_timestamp
    
def getLastWeekTimestamps(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT timestamp FROM researcher WHERE user = %s ORDER BY timestamp DESC', (user_id))
    last_timestamp = cur.fetchall()[0][0]
    cur.close()
    last_timestamp = datetime(last_timestamp.year, last_timestamp.month, last_timestamp.day, 0, 0, 0)
    first_timestamp = last_timestamp - timedelta(days = 7)
    return [first_timestamp, last_timestamp]
   
def getLastMonthTimestamps(db, user_id):
    cur = db.cursor()
    cur.execute('SELECT timestamp FROM researcher WHERE user = %s ORDER BY timestamp DESC', (user_id))
    last_timestamp = cur.fetchall()[0][0]
    cur.close()
    last_timestamp = datetime(last_timestamp.year, last_timestamp.month, last_timestamp.day, 0, 0, 0)
    last_timestamp = last_timestamp - timedelta(days = 7)
    first_timestamp = last_timestamp - timedelta(days = 30)
    return [first_timestamp, last_timestamp]
    
def commonPlotting(user_data, user_id, prefix, xlim=None):
    x = [date2num(row[0]) for row in user_data]
    y = [row[2] for row in user_data]
    colors = getBarColour(y)
    pl.figure()
    pl.subplot(111)
    pl.bar(x,y,color=colors)
    pl.title('Quality of data for ' + user_id)
    pl.xticks(rotation=30)
    ax = pl.gca()
    ax.xaxis.set_major_formatter(DateFormatter(DATE_FMT))
    pl.xlim(xlim)
    plt.show()
    plt.savefig('pictures/' + prefix + user_id + '.png', bbox_inches='tight')
    plt.close()
    
def getBarColour(data):
    colors = []
    for value in data:
        if value >= 1.0:
            colors.append('g')
        else:
            colors.append('r')
    return colors
    
def plotAllData(user_data, user_id):
    commonPlotting(user_data, user_id, 'all_')
    
def plotMonthData(user_data, user_id):
    commonPlotting(user_data, user_id, 'month_')
    
def plotWeekData(user_data, user_id):
    commonPlotting(user_data, user_id, 'week_')
    
def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
    
def plotRandomDays(db, user_id, user_name):
    cur = db.cursor()
    cur.execute('SELECT timestamp FROM researcher WHERE user = %s ORDER BY timestamp DESC', (user_id))
    fetched_data = cur.fetchall()   
    #print fetched_data
    last_timestamp = fetched_data[0][0]
    first_timestamp = fetched_data[-1][0]
    cur.close()
    
    for i in xrange(0, 3):
        date = random_date(first_timestamp, last_timestamp)
        start_date = datetime(date.year, date.month, date.day, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        quality = getQualityHour(db, user_id, start_date, end_date, 1)
        x = [date2num(row[0]) for row in quality]
        y = [row[2] for row in quality]
        
        colors = getBarColour(fetched_data)
        pl.figure()
        pl.subplot(111)
        pl.bar(x,y,width=0.035, color=colors)
        pl.xlim([start_date, end_date])
        pl.title('Quality of data per hour, ' + user_name + " " + date.strftime(DATE_FMT))
        pl.xticks(rotation=30)
        #pl.ylim([0, 1.1])
        ax = pl.gca()
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M")) 
        plt.show()
        plt.savefig('pictures/' + 'day_' + user_name + '_' + str(i) + '.png', bbox_inches='tight')
        plt.close()

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
    
    
    