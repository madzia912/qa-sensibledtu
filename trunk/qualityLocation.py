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
DB = 'edu_mit_media_funf_probe_builtin_LocationProbe'
    
def getUserData(db, user_id):
    cur= db.cursor()
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
    cur.execute('SELECT DISTINCT(timestamp) FROM researcher WHERE user = %s ORDER BY timestamp DESC', (user_id))
    fetched_data = cur.fetchall()
    last_timestamp = fetched_data[0][0]
    first_timestamp = fetched_data[-1][0]
    cur.close()
    last_timestamp = datetime(last_timestamp.year, last_timestamp.month, last_timestamp.day, 0, 0, 0)
    first_timestamp = datetime(first_timestamp.year, first_timestamp.month, first_timestamp.day, 0, 0, 0)
    return [first_timestamp, last_timestamp]
    
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
    #pl.ylim([0, 1.1])
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
    
#def getDaysList(user_data):
#    day_list = []
#    temp_scan = user_data[0]
#    for scan in user_data:
#        if( not scan[0].year == temp_scan[0].year or scan[0].month == temp_scan[0].month or scan[0].day == temp_scan[0].day):
#            day_list.append(scan)
#            temp_scan = scan
#    return day_list
#        
#def getDayData(user_data, idx):
#    tempScan = user_data[idx]
#    scan_list = []
#    for scan in user_data:
#        if scan[0].year == tempScan[0].year and scan[0].month == tempScan[0].month and scan[0].day == tempScan[0].day:           
#            scan_list.append(scan)
#            
#    begin_date = datetime(tempScan[0].year, tempScan[0].month, tempScan[0].day, 0)
#    end_date = datetime(tempScan[0].year, tempScan[0].month, tempScan[0].day, 0) + timedelta(days = 1)
#    return [scan_list, [begin_date, end_date]]
      
#def calcStats(user_data):
#    stats = []
#    all_data = [data[1] for data in user_data]
#    week_data = [data[1] for data in getWeekData(user_data)[0]] 
#    month_data = [data[1] for data in getMonthData(user_data)[0]] 
#    delta = user_data[-1][0] - user_data[0][0]
#    stats.append(sum(all_data) / delta.days)
#    stats.append(sum(month_data) / 30.0)
#    stats.append(sum(week_data) / 7.0)
#    return stats

db = MySQLdb.connect(host = HOST, user = USER, passwd=PWD, db = DB)
users_list = getUsersList(db)

user_idx = 0
#stats = []

for single_user in users_list:

    user_idx = user_idx + 1
    user_name = "user" + str(user_idx)

    [first_timestamp, last_timestamp] = getLastWeekTimestamps(db, single_user[0])
    qualityHour = getQualityHour(db, single_user[0], first_timestamp, last_timestamp, 1)

    with open(user_name + "_qualityHourLastWeek.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityHour)    
    
    [first_timestamp, last_timestamp] = getLastMonthTimestamps(db, single_user[0])
    qualityHour = getQualityHour(db, single_user[0], first_timestamp, last_timestamp, 1)

    with open(user_name + "_qualityHourLastMonth.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityHour) 
        
    [first_timestamp, last_timestamp] = getLastWeekTimestamps(db, single_user[0])
    qualityDay = getQualityDay(db, single_user[0], first_timestamp, last_timestamp, 1)

    with open(user_name + "_qualityDayLastWeek.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityDay)
     
    plotWeekData(qualityDay, user_name)    

    [first_timestamp, last_timestamp] = getLastMonthTimestamps(db, single_user[0])
    qualityDay = getQualityDay(db, single_user[0], first_timestamp, last_timestamp, 1)

    with open(user_name + "_qualityDayLastMonth.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityDay) 
        
    plotMonthData(qualityDay, user_name)
    
    [first_timestamp, last_timestamp] = getAllDataTimestamps(db, single_user[0])
    qualityDay = getQualityDay(db, single_user[0], first_timestamp, last_timestamp, 1)
    
    with open(user_name + "_qualityDayAll.csv", 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(qualityDay) 
        
    plotAllData(qualityDay, user_name)
    plotRandomDays(db, single_user[0], user_name) 
    
db.close()
    
    
    